#!/usr/bin/env python3
"""
airon_nl.py - Interfaz de Lenguaje Natural para AIRON-Cast
"Haz X en proyecto Y" -> mapea a airon_executor.py subcomando
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

PATTERNS = [
    # DASHBOARD / SERVIDOR (más específicos primero)
    (r'^(inicia|levanta|arranca|start)\s+(?:el\s+)?(?:dashboard|servidor|server)', 
     lambda m: ('start_dashboard', {})),
    (r'^(para|detiene|stop|mata)\s+(?:el\s+)?(?:dashboard|servidor|server)', 
     lambda m: ('stop_dashboard', {})),
    
    # DISPATCH / TRABAJAR / SIGUIENTE
    (r'^(trabaja|trabajar|haz|ejecuta|despacha|siguiente|continua|dale)\b.*?(?:en|de)\s+(\w[\w-]*)', 
     lambda m: ('dispatch', {'slug': m.group(2)})),
    
    # CREATE TASK AD-HOC
    (r'^(crea|agrega|anade)\s+(?:tarea|task)\s+(.+?)\s+(?:en|de)\s+(\w[\w-]*)', 
     lambda m: ('create_task', {'title': m.group(2).strip(), 'slug': m.group(3)})),
    (r'^(crea|haz)\s+(.+?)\s+(?:en|de)\s+(\w[\w-]*)', 
     lambda m: ('create_task', {'title': m.group(2).strip(), 'slug': m.group(3)})),
    
    # FINALIZE / FINALIZAR (más específico - antes que complete)
    (r'^(finaliza|finalizar)\s+(?:la\s+)?tarea\s+(\d+)\s+(?:en|de)\s+(\w[\w-]*)', 
     lambda m: ('finalize', {'task_id': int(m.group(2)), 'slug': m.group(3)})),
    (r'^(finaliza|finalizar)\s+(?:tarea|task)?\s*(\d+)', 
     lambda m: ('finalize', {'task_id': int(m.group(2)), 'slug': None})),
    
    # COMPLETE / TERMINAR
    (r'^(termina|completa|ok|listo)\s+(?:tarea|task)?\s*(\d+)', 
     lambda m: ('complete', {'task_id': int(m.group(2)), 'slug': None})),
    (r'^(termina|completa)\s+(?:la\s+)?tarea\s+(\d+)\s+(?:en|de)\s+(\w[\w-]*)', 
     lambda m: ('complete', {'task_id': int(m.group(2)), 'slug': m.group(3)})),
    
    # FAIL / FALLO
    (r'^(falla|fallo|error|rompe)\s+(?:tarea|task)?\s*(\d+)', 
     lambda m: ('fail', {'task_id': int(m.group(2)), 'slug': None})),
    (r'^(falla|fallo)\s+(?:la\s+)?tarea\s+(\d+)\s+(?:en|de)\s+(\w[\w-]*)', 
     lambda m: ('fail', {'task_id': int(m.group(2)), 'slug': m.group(3)})),
    
    # STATUS / COMO VA / ESTADO
    (r'^(estado|status|como va|que tal|progreso)\s+(?:de\s+)?(\w[\w-]*)', 
     lambda m: ('status', {'slug': m.group(2)})),
    (r'^(estado|status|como va|progreso)$', 
     lambda m: ('status_all', {})),
    
    # BOOTSTRAP / INICIAR PROYECTO
    (r'^(inicia|bootstrap|arranca)\s+(?:proyecto\s+)?(\w[\w-]*)', 
     lambda m: ('bootstrap', {'slug': m.group(2)})),
    
    # HEALTH / SALUD
    (r'^(salud|health|diagnostico)', 
     lambda m: ('health', {})),
    
    # APPROVE / APROBAR
    (r'^(aprueba|aprobado)\s+(?:tarea|task)?\s*(\d+)', 
     lambda m: ('approve', {'task_id': int(m.group(2)), 'slug': None})),
    
    # LIST TASKS / TAREAS
    (r'^(tareas|tasks|cola|queue)\s+(?:de\s+)?(\w[\w-]*)', 
     lambda m: ('list_tasks', {'slug': m.group(2)})),
]

def parse_intent(text):
    """Clasifica intencion y extrae entidades."""
    text = text.strip().lower()
    for pattern, extractor in PATTERNS:
        match = re.match(pattern, text, re.IGNORECASE)
        if match:
            try:
                cmd, args = extractor(match)
                return cmd, args
            except Exception:
                continue
    return None, {}

def run_executor(cmd, args):
    """Ejecuta airon_executor.py o scripts de dashboard."""
    if cmd in ('start_dashboard', 'stop_dashboard'):
        script = 'tools/dashboard_server.py' if cmd == 'start_dashboard' else 'tools/stop_supervisor.py'
        base = ['pythonw.exe', script] if cmd == 'start_dashboard' else ['python', script, '--stop-dashboard', '--force']
        # Para pythonw (background), usar Popen con timeout corto
        try:
            proc = subprocess.Popen(base, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                    encoding='utf-8', errors='replace', cwd=Path(__file__).resolve().parent.parent)
            # Esperar un poco para que arranque
            try:
                stdout, stderr = proc.communicate(timeout=3)
                return proc.returncode, stdout, stderr
            except subprocess.TimeoutExpired:
                # Proceso corriendo en background (normal para pythonw)
                return 0, f"Proceso iniciado en background (PID: {proc.pid})", ""
        except Exception as e:
            return 1, "", str(e)
    
    base = ['python', 'tools/airon_executor.py', cmd]
    
    if args.get('slug'):
        base.append(args['slug'])
    
    if args.get('task_id') is not None:
        base.append(str(args['task_id']))
    
    result = subprocess.run(base, capture_output=True, text=True, encoding='utf-8', errors='replace', cwd=Path(__file__).resolve().parent.parent)
    return result.returncode, result.stdout, result.stderr

def resolve_slug_for_task(task_id):
    """Busca el slug del proyecto dado un task_id."""
    import sqlite3
    conn = sqlite3.connect('central_intelligence.db')
    c = conn.cursor()
    row = c.execute('SELECT p.slug FROM tasks t JOIN projects p ON p.id = t.project_id WHERE t.id = ?', (task_id,)).fetchone()
    conn.close()
    return row[0] if row else None

def main():
    if len(sys.argv) < 2:
        print('Uso: airon "instruccion en lenguaje natural"')
        print()
        print('Ejemplos:')
        print('  airon "trabaja en quickreply"')
        print('  airon "crea endpoint /api/users en quickreply"')
        print('  airon "como va banesco"')
        print('  airon "termina tarea 42"')
        print('  airon "falla tarea 5 error de migracion"')
        print('  airon "inicia proyecto mi-app"')
        print('  airon "salud"')
        return 0
    
    instruction = ' '.join(sys.argv[1:])
    print(f'Interpretando: "{instruction}"')
    
    cmd, args = parse_intent(instruction)
    
    if not cmd:
        print(f'No entendi: "{instruction}"')
        print('Intenta: airon "trabaja en quickreply"')
        return 1
    
    print(f'Comando: {cmd} | Args: {args}')
    
    if cmd in ('complete', 'fail', 'approve') and args.get('slug') is None:
        task_id = args.get('task_id')
        if task_id:
            slug = resolve_slug_for_task(task_id)
            if slug:
                args['slug'] = slug
                print(f'Slug resuelto para tarea {task_id}: {slug}')
            else:
                print(f'No encontre proyecto para tarea {task_id}')
                return 1
    
    code, stdout, stderr = run_executor(cmd, args)
    
    if stdout:
        try:
            data = json.loads(stdout)
            print(json.dumps(data, indent=2, ensure_ascii=True))
        except:
            print(stdout.encode('ascii', errors='replace').decode())
    
    if stderr and code != 0:
        print(f'stderr: {stderr}', file=sys.stderr)
    
    return code

if __name__ == '__main__':
    sys.exit(main())