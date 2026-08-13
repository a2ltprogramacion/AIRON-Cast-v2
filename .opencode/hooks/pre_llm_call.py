#!/usr/bin/env python3
"""
Pre-LLM Call Hook — OpenCode ⊕ AIRON-Cast Fusion
Inyecta contexto relevante (ADRs, skills, feedback) antes de cada llamada al LLM.
"""
import sys
import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Caché simple para evitar búsquedas repetidas en mismo turno
_context_cache = {}

def get_relevant_adrs(query, project_slug, limit=5):
    """Busca ADRs relevantes via Engram FTS5 (placeholder)."""
    # TODO: Integrar con Engram mem_search
    return []

def get_relevant_feedback(agent, project_slug, limit=5):
    """Busca feedback aplicable al agente (placeholder)."""
    # TODO: Integrar con Engram mem_search
    return []

def get_relevant_skills(agent, task_description, limit=3):
    """Determina skills relevantes para la tarea (placeholder)."""
    # TODO: Skill registry con búsqueda semántica
    skill_keywords = {
        "backend_specialist": ["django-patterns", "api-patterns", "database-architecture", "testing-tdd-architecture"],
        "frontend_worker": ["astro-landing-kit", "tailwind-architecture", "ui-ux-pro-max"],
        "tester": ["testing-tdd-architecture"],
        "qa_auditor": ["audit-code-review", "testing-tdd-architecture"],
        "ux-ui_specialist": ["ui-ux-pro-max", "tailwind-architecture", "a2lt-brand-kit"],
        "writer": ["architecture-documentation", "seo-content-strategy", "geo-optimization"],
        "requirements_architect": ["brainstorming", "institutional-memory"],
    }
    return skill_keywords.get(agent, [])

def build_context_injection(agent, task_context, project_slug):
    """Construye bloque de contexto para inyectar."""
    parts = []
    
    # 1. ADRs relevantes
    adrs = get_relevant_adrs(task_context, project_slug)
    if adrs:
        parts.append("## ADRs Relevantes\n" + "\n".join(f"- {adr}" for adr in adrs))
    
    # 2. Feedback aplicable
    feedback = get_relevant_feedback(agent, project_slug)
    if feedback:
        parts.append("## Feedback Previo (Aplicar)\n" + "\n".join(f"- {fb}" for fb in feedback))
    
    # 3. Skills sugeridas
    skills = get_relevant_skills(agent, task_context)
    if skills:
        parts.append(f"## Skills Sugeridas: {', '.join(skills)}")
    
    return "\n\n".join(parts) if parts else ""

def main():
    # Input: agent, task_context, project_slug via env vars
    agent = os.environ.get("OPENCODE_AGENT", "orchestrator")
    task_context = os.environ.get("OPENCODE_TASK_CONTEXT", "")
    project_slug = os.environ.get("OPENCODE_PROJECT_SLUG", "")
    
    cache_key = f"{agent}:{hash(task_context)}"
    if cache_key in _context_cache:
        injection = _context_cache[cache_key]
    else:
        injection = build_context_injection(agent, task_context, project_slug)
        _context_cache[cache_key] = injection
    
    if injection:
        # Output para que OpenCode lo injete en system prompt
        print(f"CONTEXT_INJECTION:{injection}")
    
    sys.exit(0)

if __name__ == "__main__":
    main()