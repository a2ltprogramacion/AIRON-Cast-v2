#!/usr/bin/env python3
# journal_query.py — AIRON‑Cast
# Text-based search across journal entries.
# Usage: python journal_query.py --term <text> --project-slug <slug> [--type <type>]

import os
import sys
import re
import argparse


VALID_TYPES = {"task", "problem", "adr", "pattern", "field"}


def find_project_root(start: str) -> str:
    current = os.path.abspath(start)
    for _ in range(10):
        if os.path.exists(os.path.join(current, "AGENTS.md")):
            return current
        if os.path.exists(os.path.join(current, "central_intelligence.db")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return os.path.abspath(start)


def search_entries(
    entries_dir: str,
    term: str,
    entry_type: str | None = None,
    max_results: int = 20
) -> list[dict]:
    if not os.path.exists(entries_dir):
        return []

    results = []
    term_lower = term.lower()

    for fname in sorted(os.listdir(entries_dir), reverse=True):
        if not fname.endswith(".md"):
            continue

        # Filter by type if specified
        if entry_type:
            type_match = re.match(r'^\d{8}-\d{6}_([a-z]+)_', fname)
            if not type_match or type_match.group(1) != entry_type:
                # also check ADR pattern
                if entry_type == "adr" and fname.startswith("ADR-"):
                    pass
                else:
                    continue

        fpath = os.path.join(entries_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()
        except Exception:
            continue

        if term_lower not in content.lower():
            continue

        # Extract title
        h1_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        title = h1_match.group(1).strip() if h1_match else fname

        # Extract type from comment
        type_tag_match = re.search(r'\[JOURNAL\] type:(\w+)', content)
        etype = type_tag_match.group(1) if type_tag_match else "unknown"

        # Find matching lines with context
        matched_lines = []
        for i, line in enumerate(lines):
            if term_lower in line.lower():
                matched_lines.append({
                    "line_number": i + 1,
                    "content": line.strip()[:120]
                })
                if len(matched_lines) >= 3:
                    break

        results.append({
            "filename":     fname,
            "type":         etype,
            "title":        title,
            "matched_lines": matched_lines,
        })

        if len(results) >= max_results:
            break

    return results


def format_results(results: list[dict], term: str) -> None:
    if not results:
        print(f"[Journal] No results for: '{term}'")
        return

    print(f"[Journal] {len(results)} entry(s) found for: '{term}'\n")
    print("=" * 70)

    for r in results:
        print(f"\n[{r['type'].upper()}] {r['title']}")
        print(f"  File: {r['filename']}")
        if r["matched_lines"]:
            print("  Matches:")
            for ml in r["matched_lines"]:
                print(f"    L{ml['line_number']}: {ml['content']}")
        print("-" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="AIRON‑Cast Journal — Search entries."
    )
    parser.add_argument(
        "--term",
        required=True,
        help="Search term (case-insensitive)."
    )
    parser.add_argument(
        "--type",
        choices=list(VALID_TYPES),
        default=None,
        help="Filter by entry type."
    )
    parser.add_argument(
        "--project-slug",
        required=True,
        help="Project slug (e.g., landing-01)."
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=20,
        help="Max results to show (default: 20)."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON."
    )
    args = parser.parse_args()

    root = find_project_root(os.getcwd())
    journal_dir = os.path.join(root, "workspace", args.project_slug, "journal")
    entries_dir = os.path.join(journal_dir, "entries")

    if not os.path.exists(entries_dir):
        print(f"ERROR: Entries directory not found: {entries_dir}", file=sys.stderr)
        sys.exit(2)

    results = search_entries(
        entries_dir=entries_dir,
        term=args.term,
        entry_type=args.type,
        max_results=args.max_results
    )

    if args.json:
        import json
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        format_results(results, args.term)

    sys.exit(0 if results else 1)


if __name__ == "__main__":
    main()