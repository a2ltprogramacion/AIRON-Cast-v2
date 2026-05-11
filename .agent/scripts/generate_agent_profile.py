#!/usr/bin/env python3
"""
generate_agent_profile.py — Generador de perfiles de agente AIRON-Cast.

Genera un archivo .md con la plantilla estándar de Agent Profile
desde argumentos CLI. Compatible con agent-creator-pro.

Uso:
    python .agent/scripts/generate_agent_profile.py \
        --name "Backend Developer" \
        --goal "Generar código backend Django de calidad productiva" \
        --phase "Development" \
        --circle "3" \
        --allowed "Generar modelos, serializers, viewsets" \
        --prohibited "Ejecutar migraciones, modificar frontend" \
        --rules "R01:Validar sintaxis Python,R02:Incluir timestamps" \
        --skills "skill_gen_django_app:Boilerplate Django,skill_gen_schema_sql:SQL schemas" \
        --upstream "orchestrator" \
        --downstream "tester,qa" \
        --trigger "Tarea asignada con assigned_agent=backend" \
        --handoff-success "Backend task completada" \
        --handoff-failure "Conflicto de schema detectado" \
        --output .agent/agents/taskforce/
"""

import argparse
import os
import sys
import re
from datetime import datetime, timezone


def sanitizar_nombre_archivo(nombre: str) -> str:
    """Convierte nombre de agente a nombre de archivo válido."""
    nombre_limpio = nombre.lower().strip()
    nombre_limpio = re.sub(r'[^a-z0-9\s]', '', nombre_limpio)
    nombre_limpio = re.sub(r'\s+', '_', nombre_limpio)
    return nombre_limpio


def parsear_lista_clave_valor(texto: str) -> list:
    """Parsea 'clave1:valor1,clave2:valor2' en lista de tuplas."""
    if not texto:
        return []
    items = []
    for par in texto.split(','):
        if ':' in par:
            clave, valor = par.split(':', 1)
            items.append((clave.strip(), valor.strip()))
        else:
            items.append((par.strip(), ''))
    return items


def generar_perfil(args) -> str:
    """Genera el contenido Markdown del perfil de agente."""
    lineas = []

    # Sección 1: Core Identity
    lineas.append(f"# Agent Profile: {args.name}\n")
    lineas.append("## 1. Core Identity\n")
    lineas.append(f"- **Role Name:** {args.name}")
    lineas.append(f"- **Primary Objective:** {args.goal}")
    lineas.append(f"- **Phase:** {args.phase}")
    lineas.append(f"- **Circle:** {args.circle}\n")

    # Sección 2: Authorized Scope & Constraints
    lineas.append("## 2. Authorized Scope & Constraints\n")
    lineas.append("- **Allowed:**")
    for item in args.allowed.split(','):
        item = item.strip()
        if item:
            lineas.append(f"  - {item}")
    lineas.append("")
    lineas.append("- **Prohibited:**")
    for item in args.prohibited.split(','):
        item = item.strip()
        if item:
            lineas.append(f"  - {item}")
    lineas.append("")

    # Sección 3: Rules
    reglas = parsear_lista_clave_valor(args.rules)
    if reglas:
        lineas.append("## 3. Rules\n")
        for rid, desc in reglas:
            lineas.append(f"- {rid} — {desc}")
        lineas.append("")

    # Sección 4: Assigned Skills
    skills = parsear_lista_clave_valor(args.skills)
    if skills:
        lineas.append("## 4. Assigned Skills\n")
        for nombre_skill, desc_skill in skills:
            if desc_skill:
                lineas.append(f"- `{nombre_skill}` → {desc_skill}")
            else:
                lineas.append(f"- `{nombre_skill}`")
        lineas.append("")

    # Sección 5: Orchestration & Handoff Protocol
    lineas.append("## 5. Orchestration & Handoff Protocol\n")
    lineas.append(f"- **Upstream:** {args.upstream}")
    lineas.append(f"- **Downstream:** {args.downstream}")
    lineas.append(f"- **Trigger Condition:** {args.trigger}")
    lineas.append(f'- **Handoff Phrase (Success):** `"{args.handoff_success}"`')
    lineas.append(f'- **Handoff Phrase (Failure):** `"{args.handoff_failure}"`')
    lineas.append("")

    # Sección 6: Output Contract
    nombre_agente = sanitizar_nombre_archivo(args.name)
    lineas.append("## 6. Output Contract\n")
    lineas.append("```json")
    lineas.append("{")
    lineas.append(f'  "agent":   "{nombre_agente}",')
    lineas.append('  "task_id": "{str}",')
    lineas.append('  "skill":   "{skill_name}",')
    lineas.append('  "status":  "completed | failed",')
    lineas.append('  "output":  {},')
    lineas.append('  "tokens":  0,')
    lineas.append('  "error":   null')
    lineas.append("}")
    lineas.append("```")

    return "\n".join(lineas)


def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Generador de perfiles de agente AIRON-Cast"
    )
    parser.add_argument("--name", required=True, help="Nombre del rol del agente")
    parser.add_argument("--goal", required=True, help="Objetivo principal (una oración)")
    parser.add_argument("--phase", default="Development",
                        help="Fase: Discovery|Design|Development|Testing|Review|Content|Delivery|Evolution")
    parser.add_argument("--circle", default="3", help="Círculo de autoridad: 0|1|2|3")
    parser.add_argument("--allowed", required=True, help="Operaciones permitidas (separadas por coma)")
    parser.add_argument("--prohibited", required=True, help="Operaciones prohibidas (separadas por coma)")
    parser.add_argument("--rules", default="", help="Reglas (formato R01:Descripción,R02:Descripción)")
    parser.add_argument("--skills", default="", help="Skills (formato skill_name:Descripción,skill2:Desc)")
    parser.add_argument("--upstream", required=True, help="Agente(s) que asignan trabajo")
    parser.add_argument("--downstream", required=True, help="Agente(s) que reciben output")
    parser.add_argument("--trigger", required=True, help="Condición de activación")
    parser.add_argument("--handoff-success", required=True, help="Frase de handoff exitoso")
    parser.add_argument("--handoff-failure", required=True, help="Frase de handoff fallido")
    parser.add_argument("--output", required=True, help="Directorio de salida")

    args = parser.parse_args()

    # Verificar directorio de salida
    if not os.path.isdir(args.output):
        os.makedirs(args.output, exist_ok=True)
        print(f"[INFO] Directorio creado: {args.output}")

    # Generar contenido
    contenido = generar_perfil(args)

    # Escribir archivo
    nombre_archivo = sanitizar_nombre_archivo(args.name) + ".md"
    ruta_completa = os.path.join(args.output, nombre_archivo)

    if os.path.exists(ruta_completa):
        print(f"[ERROR] El archivo ya existe: {ruta_completa}", file=sys.stderr)
        print("[INFO] Use --force (no implementado aún) para sobreescribir.", file=sys.stderr)
        sys.exit(1)

    with open(ruta_completa, 'w', encoding='utf-8') as f:
        f.write(contenido)

    print(f"[OK] Perfil de agente generado: {ruta_completa}")
    print(f"[INFO] Timestamp: {datetime.now(timezone.utc).isoformat()}")
    sys.exit(0)


if __name__ == "__main__":
    main()
