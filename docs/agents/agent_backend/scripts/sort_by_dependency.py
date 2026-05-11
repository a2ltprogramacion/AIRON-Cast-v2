#!/usr/bin/env python3
# agents/agent_backend/scripts/sort_by_dependency.py
# La Forja — Topological sort of DB entities by FK dependencies
# Version: 1.0 — BL.015

import argparse
import json
import sys
from collections import defaultdict, deque


def build_dependency_graph(entities):
    graph     = defaultdict(set)
    in_degree = {e["name"]: 0 for e in entities}

    for entity in entities:
        name = entity["name"]
        for rel in entity.get("relationships", []):
            target = rel.get("target")
            if not target: continue
            # BL.015 — self-FK: skip from ordering (nullable deferrable)
            if target == name: continue
            if target in in_degree:
                if target not in graph[name]:
                    graph[name].add(target)
                    in_degree[name] += 1

    return dict(graph), in_degree


def topological_sort(entities):
    graph, in_degree = build_dependency_graph(entities)

    # Detect self-FKs
    self_fks = []
    for entity in entities:
        name = entity["name"]
        for rel in entity.get("relationships", []):
            if rel.get("target") == name:
                self_fks.append(name)

    # Kahn's algorithm
    queue  = deque(n for n in in_degree if in_degree[n] == 0)
    sorted_entities = []

    while queue:
        node = queue.popleft()
        sorted_entities.append(node)
        for entity_name, deps in graph.items():
            if node in deps:
                deps.discard(node)
                in_degree[entity_name] -= 1
                if in_degree[entity_name] == 0:
                    queue.append(entity_name)

    circular = [n for n, d in in_degree.items()
                if d > 0 and n not in sorted_entities]

    if circular:
        return {"ok": False, "sorted": sorted_entities,
                "self_fks": self_fks, "circular": circular,
                "error": f"Circular dependency: {circular}"}

    return {"ok": True, "sorted": sorted_entities,
            "self_fks": self_fks, "circular": [], "error": None}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema_json", required=True)
    args = parser.parse_args()

    try:
        data     = json.loads(args.schema_json)
        entities = data if isinstance(data, list) else data.get("entities", [])
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(2)

    result = topological_sort(entities)

    if not result["ok"]:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if result["self_fks"]:
        print(f"INFO: Self-FK entities (nullable deferrable): {result['self_fks']}",
              file=sys.stderr)

    print(json.dumps({"sorted": result["sorted"], "self_fks": result["self_fks"]}))
    sys.exit(0)


if __name__ == "__main__":
    main()
