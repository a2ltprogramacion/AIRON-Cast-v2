#!/usr/bin/env python3
"""
list_agents.py — Listado de agentes AIRON-Cast con geometría de Handoff.

Escanea .agent/agents/ recursivamente, extrae metadata de cada perfil
y muestra una tabla formateada con nombre, fase, upstream, downstream
y número de skills asignadas.

Uso:
    python .agent/scripts/list_agents.py
    python .agent/scripts/list_agents.py --format json
    python .agent/scripts/list_agents.py --agents-dir .agent/agents/
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def extraer_campo(contenido: str, patron: str) -> str:
    """Extrae el valor de un campo markdown del tipo **Campo:** valor."""
    match = re.search(rf"\*\*{patron}:\*\*\s*(.*)", contenido)
    if match:
        return match.group(1).strip()
    return "—"


def extraer_nombre(contenido: str) -> str:
    """Extrae el nombre del agente del header."""
    match = re.match(r'^#\s+Agent Profile:\s*(.*)', contenido)
    if match:
        return match.group(1).strip()
    return "Desconocido"


def contar_skills(contenido: str) -> int:
    """Cuenta skills asignadas en el perfil."""
    return len(re.findall(r'`skill_\w+`', contenido))


def extraer_fase(contenido: str) -> str:
    """Extrae la fase del agente."""
    match = re.search(r'\*\*Phase:\*\*\s*(.*)', contenido)
    if match:
        return match.group(1).strip()
    return "—"


def extraer_circle(contenido: str) -> str:
    """Extrae el círculo del agente."""
    match = re.search(r'\*\*Circle:\*\*\s*(.*)', contenido)
    if match:
        return match.group(1).strip()
    return "—"


def analizar_agente(ruta: str) -> dict:
    """Extrae metadata de un archivo de perfil de agente."""
    with open(ruta, 'r', encoding='utf-8') as f:
        contenido = f.read()

    return {
        "archivo": str(Path(ruta).relative_to(Path(ruta).parents[2])),
        "nombre": extraer_nombre(contenido),
        "fase": extraer_fase(contenido),
        "circulo": extraer_circle(contenido),
        "upstream": extraer_campo(contenido, "Upstream"),
        "downstream": extraer_campo(contenido, "Downstream"),
        "trigger": extraer_campo(contenido, "Trigger Condition"),
        "skills": contar_skills(contenido),
        "lineas": len(contenido.split('\n')),
    }


def imprimir_tabla(agentes: list):
    """Imprime tabla formateada de agentes."""
    # Encabezados
    cols = {
        "Archivo": max(len(a["archivo"]) for a in agentes),
        "Nombre": max(len(a["nombre"]) for a in agentes),
        "Fase": max(len(a["fase"]) for a in agentes),
        "Círculo": max(len(a["circulo"]) for a in agentes),
        "Upstream": min(30, max(len(a["upstream"]) for a in agentes)),
        "Downstream": min(30, max(len(a["downstream"]) for a in agentes)),
        "Skills": 6,
        "Líneas": 6,
    }

    # Ajustar mínimos con headers
    for k in cols:
        cols[k] = max(cols[k], len(k))

    # Header
    header = " | ".join(k.ljust(cols[k]) for k in cols)
    sep = "-+-".join("-" * cols[k] for k in cols)

    print(f"\n📋 AIRON-Cast — Agent Registry")
    print(f"{'='*len(header)}")
    print(header)
    print(sep)

    # Filas
    for a in sorted(agentes, key=lambda x: (x["circulo"], x["nombre"])):
        fila = {
            "Archivo": a["archivo"],
            "Nombre": a["nombre"],
            "Fase": a["fase"],
            "Círculo": a["circulo"],
            "Upstream": a["upstream"][:30],
            "Downstream": a["downstream"][:30],
            "Skills": str(a["skills"]),
            "Líneas": str(a["lineas"]),
        }
        print(" | ".join(fila[k].ljust(cols[k]) for k in cols))

    print(f"{'='*len(header)}")
    print(f"Total: {len(agentes)} agentes registrados\n")


def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Listado de agentes AIRON-Cast con geometría de Handoff"
    )
    parser.add_argument(
        "--agents-dir",
        default=".agent/agents",
        help="Directorio raíz de agentes (default: .agent/agents)"
    )
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Formato de salida"
    )

    args = parser.parse_args()

    ruta_base = Path(args.agents_dir)
    if not ruta_base.is_dir():
        print(f"[ERROR] Directorio no encontrado: {args.agents_dir}", file=sys.stderr)
        sys.exit(1)

    archivos = list(ruta_base.rglob("*.md"))
    if not archivos:
        print("[INFO] No se encontraron archivos .md en el directorio.")
        sys.exit(0)

    agentes = []
    for archivo in archivos:
        try:
            agente = analizar_agente(str(archivo))
            agentes.append(agente)
        except Exception as e:
            print(f"[WARN] Error al analizar {archivo}: {e}", file=sys.stderr)

    if args.format == "json":
        print(json.dumps(agentes, indent=2, ensure_ascii=False))
    else:
        imprimir_tabla(agentes)

    sys.exit(0)


if __name__ == "__main__":
    main()
