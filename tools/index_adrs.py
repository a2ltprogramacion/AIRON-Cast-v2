"""Indexa los ADRs existentes en disco en la tabla adrs + adrs_fts (FTS5).

Script de MIGRACION: para ADRs generados ANTES de que existiera el hook
automatico en Orchestrator.complete_task(). El flujo normal ya no lo
necesita — al hacer `complete` con un artefacto ADR-*.md, el orquestador
lo indexa solo via MemoryManager.register_adr_from_file().

Uso:
    python tools/index_adrs.py [--project-slug cafe-cenit]
    python tools/index_adrs.py --all
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.memory_manager import MemoryManager


def index_adrs_for_project(mm: MemoryManager, slug: str) -> int:
    project = mm.get_project(slug)
    if not project:
        print(f"  Proyecto '{slug}' no existe en la DB.")
        return 0

    adr_dir = Path("workspace") / slug / "adrs"
    if not adr_dir.exists():
        print(f"  {adr_dir} no existe.")
        return 0

    inserted = 0
    for adr_file in sorted(adr_dir.glob("*.md")):
        result = mm.register_adr_from_file(adr_file, project["id"])
        if result["inserted"]:
            print(f"  [INSERT] {result['decision_id']}: {result['title'][:60]}")
            inserted += 1
        elif result["reason"] == "duplicate":
            print(f"  [SKIP]   {result['decision_id']}: ya indexado")
        else:
            print(f"  [WARN]   {adr_file.name}: {result['reason']}")

    return inserted


def main():
    p = argparse.ArgumentParser(description="Indexar ADRs de disco en adrs + FTS5")
    p.add_argument("--project-slug", help="Slug del proyecto (e.g. cafe-cenit)")
    p.add_argument("--all", action="store_true", help="Indexar todos los proyectos")
    args = p.parse_args()

    mm = MemoryManager()

    if args.all:
        projects = mm.list_projects() if hasattr(mm, "list_projects") else []
        if not projects:
            # Fallback: leer todos los slugs via SQL directo
            import sqlite3
            with mm._connect() as conn:
                projects = [dict(r)["slug"] for r in conn.execute("SELECT slug FROM projects").fetchall()]
        total = 0
        for slug in projects:
            print(f"\n[Proyecto: {slug}]")
            total += index_adrs_for_project(mm, slug)
        print(f"\nTotal insertados: {total}")
    elif args.project_slug:
        print(f"\n[Proyecto: {args.project_slug}]")
        n = index_adrs_for_project(mm, args.project_slug)
        print(f"\nTotal insertados: {n}")
    else:
        p.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
