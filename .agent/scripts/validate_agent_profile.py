#!/usr/bin/env python3
"""
validate_agent_profile.py — Validador estructural de perfiles de agente AIRON-Cast.

Verifica que un archivo .md de perfil de agente cumple con el schema
obligatorio definido por agent-creator-pro.

Uso:
    python .agent/scripts/validate_agent_profile.py --path .agent/agents/strategist.md
    python .agent/scripts/validate_agent_profile.py --dir .agent/agents/ --recursive

Códigos de salida:
    0 — Validación exitosa (puede incluir warnings)
    1 — Error fatal (estructura inválida)
"""

import argparse
import os
import re
import sys
from pathlib import Path


# Secciones obligatorias del perfil (regex flexible)
SECCIONES_OBLIGATORIAS = [
    (r"##\s+1\.\s+Core Identity", "Core Identity"),
    (r"##\s+2\.\s+Authorized Scope", "Authorized Scope & Constraints"),
]

CAMPOS_CORE_IDENTITY = [
    (r"\*\*Role Name:\*\*", "Role Name"),
    (r"\*\*Primary Objective:\*\*", "Primary Objective"),
]

CAMPOS_SCOPE = [
    (r"\*\*Allowed:\*\*", "Allowed"),
    (r"\*\*Prohibited:\*\*", "Prohibited"),
]

# Secciones recomendadas (warning si faltan)
SECCIONES_RECOMENDADAS = [
    (r"##\s+\d+\.\s+Rules", "Rules"),
    (r"##\s+\d+\.\s+Assigned Skills", "Assigned Skills"),
    (r"Orchestration.*Handoff", "Orchestration & Handoff Protocol"),
    (r"Output Contract", "Output Contract"),
]

CAMPOS_HANDOFF = [
    (r"\*\*Upstream:\*\*", "Upstream"),
    (r"\*\*Downstream:\*\*", "Downstream"),
    (r"\*\*Trigger Condition:\*\*", "Trigger Condition"),
    (r"Handoff Phrase \(Success\)", "Handoff Phrase (Success)"),
]


class ResultadoValidacion:
    """Acumula resultados de validación para un archivo."""

    def __init__(self, ruta: str):
        self.ruta = ruta
        self.errores = []
        self.warnings = []

    def error(self, mensaje: str):
        """Registra un error fatal."""
        self.errores.append(mensaje)

    def warning(self, mensaje: str):
        """Registra un warning no fatal."""
        self.warnings.append(mensaje)

    @property
    def es_valido(self) -> bool:
        """El perfil es válido si no tiene errores fatales."""
        return len(self.errores) == 0

    def imprimir(self):
        """Imprime resultados formateados."""
        estado = "✅ VALID" if self.es_valido else "❌ FAILED"
        print(f"\n{estado}  {self.ruta}")

        for err in self.errores:
            print(f"  ❌ FATAL: {err}")

        for warn in self.warnings:
            print(f"  ⚠️  WARN: {warn}")

        if self.es_valido and not self.warnings:
            print("  ✅ Todas las validaciones pasaron.")


def validar_perfil(ruta: str) -> ResultadoValidacion:
    """Valida un archivo .md de perfil de agente."""
    resultado = ResultadoValidacion(ruta)

    # Verificar existencia
    if not os.path.isfile(ruta):
        resultado.error(f"Archivo no encontrado: {ruta}")
        return resultado

    with open(ruta, 'r', encoding='utf-8') as f:
        contenido = f.read()

    lineas = contenido.split('\n')

    # Verificar header: debe empezar con # Agent Profile
    if not lineas or not re.match(r'^#\s+Agent Profile:', lineas[0]):
        resultado.error("El archivo debe iniciar con '# Agent Profile: <Nombre>'")

    # Verificar secciones obligatorias
    for patron, nombre in SECCIONES_OBLIGATORIAS:
        if not re.search(patron, contenido):
            resultado.error(f"Sección obligatoria faltante: {nombre}")

    # Verificar campos de Core Identity
    for patron, nombre in CAMPOS_CORE_IDENTITY:
        if not re.search(patron, contenido):
            resultado.error(f"Campo obligatorio faltante en Core Identity: {nombre}")
        else:
            # Verificar que no esté vacío
            match = re.search(rf"{patron}\s*(.*)", contenido)
            if match and not match.group(1).strip():
                resultado.error(f"Campo vacío: {nombre}")

    # Verificar campos de Scope
    for patron, nombre in CAMPOS_SCOPE:
        if not re.search(patron, contenido):
            resultado.error(f"Campo obligatorio faltante en Scope: {nombre}")

    # Verificar secciones recomendadas
    for patron, nombre in SECCIONES_RECOMENDADAS:
        if not re.search(patron, contenido):
            resultado.warning(f"Sección recomendada faltante: {nombre}")

    # Verificar campos de Handoff si la sección existe
    if re.search(r"Orchestration.*Handoff", contenido):
        for patron, nombre in CAMPOS_HANDOFF:
            if not re.search(patron, contenido):
                resultado.warning(f"Campo de Handoff faltante: {nombre}")

    # Verificar que tiene al menos una skill
    if re.search(r"Assigned Skills", contenido):
        skill_section = re.search(r"Assigned Skills.*?(?=##|\Z)", contenido, re.DOTALL)
        if skill_section:
            skill_text = skill_section.group()
            if not re.search(r'`skill_\w+`|`\w+-\w+`', skill_text):
                resultado.warning("No se encontraron skills asignadas (formato `skill_name`)")

    # Verificar longitud del archivo
    total_lineas = len(lineas)
    if total_lineas > 300:
        resultado.warning(f"Perfil excede 300 líneas ({total_lineas} líneas). Considerar mover contenido a references/.")
    elif total_lineas < 10:
        resultado.error(f"Perfil demasiado corto ({total_lineas} líneas). Probablemente incompleto.")

    return resultado


def validar_directorio(directorio: str, recursivo: bool = False) -> list:
    """Valida todos los .md en un directorio."""
    resultados = []
    ruta = Path(directorio)

    if recursivo:
        archivos = list(ruta.rglob("*.md"))
    else:
        archivos = list(ruta.glob("*.md"))

    for archivo in sorted(archivos):
        resultados.append(validar_perfil(str(archivo)))

    return resultados


def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Validador estructural de perfiles de agente AIRON-Cast"
    )
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--path", help="Ruta a un archivo .md específico")
    grupo.add_argument("--dir", help="Directorio con archivos .md")
    parser.add_argument("--recursive", action="store_true",
                        help="Buscar recursivamente en subdirectorios")

    args = parser.parse_args()

    if args.path:
        resultados = [validar_perfil(args.path)]
    else:
        resultados = validar_directorio(args.dir, args.recursive)

    if not resultados:
        print("[INFO] No se encontraron archivos .md para validar.")
        sys.exit(0)

    # Resumen
    total = len(resultados)
    validos = sum(1 for r in resultados if r.es_valido)
    fallidos = total - validos
    total_warnings = sum(len(r.warnings) for r in resultados)

    for r in resultados:
        r.imprimir()

    print(f"\n{'='*60}")
    print(f"RESUMEN: {validos}/{total} válidos, {fallidos} fallidos, {total_warnings} warnings")
    print(f"{'='*60}")

    sys.exit(1 if fallidos > 0 else 0)


if __name__ == "__main__":
    main()
