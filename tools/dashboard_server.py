#!/usr/bin/env python3
"""
dashboard_server.py — AIRON-Cast Dashboard Backend

Levanta un servidor HTTP minimo que sirve el dashboard HTML y
endpoints JSON consultando central_intelligence.db.

Usage:
    python tools/dashboard_server.py
    # Abrir http://localhost:8765 en el navegador
"""

import http.server
import json
import os
import re
import sqlite3
import sys
import time
import yaml
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from core.service_supervisor import (  # noqa: E402
    DB_PATH as CORE_DB_PATH,
    LOG_DIR,
    PID_FILE,
    is_supervisor_alive,
    mark_inside_dashboard_process,
)

PORT = 8765
DB_PATH = Path(__file__).resolve().parent.parent / "central_intelligence.db"
DASHBOARD_HTML = Path(__file__).resolve().parent.parent / "dashboard" / "index.html"

# Marcar este proceso para que quick_healthcheck() no haga self-socket-connect
# (el handler BaseHTTPRequestHandler es serial y eso causaria self-deadlock).
mark_inside_dashboard_process()


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def json_endpoint(handler, data):
    handler.send_response(200)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(json.dumps(data, default=str).encode("utf-8"))


def get_all_agents_info():
    """
    Descubre dinámicamente todos los agentes fusionando:
    1. manifest.json (contratos formales, circle, can_read, can_write, forbidden)
    2. Perfiles Markdown en .agent/agents/ y .agents/profiles/
    3. central_intelligence.db (tarea actual IN_PROGRESS, tareas READY, métricas, logs)
    """
    manifest_file = REPO_ROOT / "manifest.json"
    manifest_agents = {}
    if manifest_file.exists():
        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest_agents = json.load(f).get("agents", {})
        except Exception:
            pass

    # Descubrir carpetas de perfiles
    profile_dirs = [REPO_ROOT / ".agent" / "agents", REPO_ROOT / ".agents" / "profiles"]
    discovered_files = {}
    for pdir in profile_dirs:
        if pdir.exists():
            for p in pdir.glob("*.md"):
                if p.stem not in discovered_files:
                    discovered_files[p.stem] = p

    # Identificar todas las skills válidas del sistema
    valid_skills = set()
    skills_dirs = [REPO_ROOT / ".agent" / "skills", REPO_ROOT / ".agents" / "skills"]
    for sdir in skills_dirs:
        if sdir.exists():
            for d in sdir.iterdir():
                if d.is_dir():
                    valid_skills.add(d.name)

    all_slugs = sorted(set(list(manifest_agents.keys()) + list(discovered_files.keys())))

    conn = get_db()
    results = []

    for slug in all_slugs:
        m = manifest_agents.get(slug, {})
        p = discovered_files.get(slug)

        fm = {}
        content = ""
        matched_skills = []
        upstream = None
        downstream = None
        version = "1.0.0"

        if p and p.exists():
            try:
                content = p.read_text(encoding="utf-8")
                # Extraer frontmatter
                fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
                if fm_match:
                    fm = yaml.safe_load(fm_match.group(1)) or {}

                # Extraer skills comparando contra valid_skills
                words = re.findall(r"[a-zA-Z0-9_-]+", content)
                matched_skills = sorted(list(set(w for w in words if w in valid_skills)))

                # Extraer Upstream / Downstream
                up_match = re.search(r"-\s+\*\*Upstream:\*\*\s*(.*?)\n", content)
                if up_match:
                    upstream = up_match.group(1).strip()
                down_match = re.search(r"-\s+\*\*Downstream:\*\*\s*(.*?)\n", content)
                if down_match:
                    downstream = down_match.group(1).strip()

                version = str(fm.get("version", "1.0.0"))
            except Exception:
                pass

        # Si en manifest.json hay skills en can_read, agregarlas
        if "can_read" in m:
            for rpath in m["can_read"]:
                for s in valid_skills:
                    if s in rpath and s not in matched_skills:
                        matched_skills.append(s)
        matched_skills.sort()

        circle = fm.get("circle", m.get("circle", 3))
        scope = fm.get("scope", "restricted")
        description = m.get("description") or fm.get("role") or slug.replace("_", " ").title()
        name = slug.replace("_", " ").title()

        # Consultar DB: tarea actual en proyectos ACTIVE
        cur_task = conn.execute(
            """
            SELECT t.id, t.title, p.slug, t.priority, t.status, t.started_at
            FROM tasks t
            JOIN projects p ON p.id = t.project_id
            WHERE t.assigned_agent = ? AND t.status = 'IN_PROGRESS' AND p.status = 'ACTIVE'
            ORDER BY t.started_at DESC LIMIT 1
            """,
            (slug,),
        ).fetchone()

        # Tareas en espera en proyectos ACTIVE
        ready_tasks = conn.execute(
            """
            SELECT t.id, t.title, p.slug, t.priority
            FROM tasks t
            JOIN projects p ON p.id = t.project_id
            WHERE t.assigned_agent = ? AND t.status = 'READY' AND p.status = 'ACTIVE'
            ORDER BY t.priority DESC, t.created_at ASC
            """,
            (slug,),
        ).fetchall()

        # Conteo completadas y fallidas
        stats = conn.execute(
            """
            SELECT
                SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed
            FROM tasks WHERE assigned_agent = ?
            """,
            (slug,),
        ).fetchone()

        # Último log en execution_logs
        last_log = conn.execute(
            """
            SELECT created_at, outcome, tokens_used
            FROM execution_logs
            WHERE agent_name = ?
            ORDER BY created_at DESC LIMIT 1
            """,
            (slug,),
        ).fetchone()

        # Tokens totales
        tokens_row = conn.execute(
            "SELECT SUM(tokens_used) as t FROM execution_logs WHERE agent_name = ?",
            (slug,),
        ).fetchone()
        total_tokens = tokens_row["t"] if tokens_row and tokens_row["t"] else 0

        # Determinar Estatus
        if cur_task:
            status = "activo"
        elif (stats["failed"] and stats["failed"] > 0) or (last_log and last_log["outcome"] == "failure"):
            status = "dañado"
        elif len(ready_tasks) > 0:
            status = "en_espera"
        else:
            status = "reposo"

        last_used = None
        if last_log and last_log["created_at"]:
            last_used = str(last_log["created_at"])
        elif fm.get("last_used"):
            last_used = str(fm.get("last_used"))

        results.append({
            "slug": slug,
            "name": name,
            "circle": circle,
            "scope": scope,
            "version": version,
            "status": status,
            "skills": matched_skills,
            "skills_count": len(matched_skills),
            "current_task": dict(cur_task) if cur_task else None,
            "ready_tasks_count": len(ready_tasks),
            "completed_tasks": stats["completed"] or 0,
            "failed_tasks": stats["failed"] or 0,
            "upstream": upstream,
            "downstream": downstream,
            "last_used": last_used,
            "total_tokens": total_tokens,
            "description": description,
            "has_manifest": bool(m),
            "has_profile": bool(p),
        })

    conn.close()
    results.sort(key=lambda x: (x["circle"], x["slug"]))
    return results


class DashboardHandler(http.server.BaseHTTPRequestHandler):
    # Timeout para que un cliente que cierre la conexion no deje el handler
    # colgado indefinidamente. Con ThreadingHTTPServer, cada request corre
    # en su propio thread, pero igualmente este timeout previene fuga de
    # threads si el browser aborta el fetch.
    timeout = 5

    def _handle_health(self):
        """Estado completo del ecosistema para el widget Health del dashboard.

        Importante: este handler se invoca DENTRO del dashboard server, asi que
        el dashboard siempre esta vivo (up=True) mientras respondemos. No hacer
        socket connect a 8765 porque el handler de BaseHTTPRequestHandler es
        serial y eso causaria self-deadlock intermitente (parpadeo rojo/verde).

        Usa quick_healthcheck() que ya sabe que estamos dentro del proceso
        del dashboard (gracias a mark_inside_dashboard_process()).
        """
        from core.service_supervisor import quick_healthcheck, is_supervisor_alive
        from pathlib import Path as _P
        from datetime import datetime as _dt

        base = quick_healthcheck()
        sup_pid = None
        sup_started = None
        if PID_FILE.exists():
            try:
                sup_pid = int(PID_FILE.read_text(encoding="utf-8").strip())
            except Exception:
                sup_pid = None

        sup_log_size = 0
        sup_log_mtime = None
        sup_log = LOG_DIR / "supervisor.log"
        if sup_log.exists():
            try:
                st = sup_log.stat()
                sup_log_size = st.st_size
                sup_log_mtime = _dt.fromtimestamp(st.st_mtime).isoformat()
            except Exception:
                pass

        db_mtime = None
        if CORE_DB_PATH.exists():
            try:
                db_mtime = _dt.fromtimestamp(CORE_DB_PATH.stat().st_mtime).isoformat()
            except Exception:
                pass

        json_endpoint(self, {
            "ts": _dt.now().isoformat(timespec="seconds"),
            "supervisor": {
                "alive": base["supervisor_alive"],
                "pid": sup_pid,
                "started_at": None,
                "log_size_bytes": sup_log_size,
                "log_mtime": sup_log_mtime,
                "log_path": str(sup_log.relative_to(REPO_ROOT)) if sup_log.exists() else None,
            },
            "db": {
                "exists": base["db_exists"],
                "size_bytes": base["db_size_bytes"],
                "mtime": db_mtime,
            },
            "dashboard": {
                "url": base["dashboard_url"],
                "up": base["dashboard_up"],
                "error": base["dashboard_error"],
                "self_pid": os.getpid(),
            },
        })

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # Servir el HTML principal
        if path == "/" or path == "/index.html":
            if not DASHBOARD_HTML.exists():
                self.send_error(404, "dashboard/index.html not found")
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(DASHBOARD_HTML, "rb") as f:
                self.wfile.write(f.read())
            return

        if path == "/healthz":
            from datetime import datetime
            json_endpoint(self, {
                "status": "ok",
                "service": "dashboard",
                "ts": datetime.now().isoformat(timespec="seconds"),
            })
            return

        if path == "/api/health":
            self._handle_health()
            return

        # Endpoint: lista dinámica de agentes con estatus, skills, actividad y métricas
        if path == "/api/agents":
            agents = get_all_agents_info()
            json_endpoint(self, agents)
            return

        # Endpoint: proyectos
        if path == "/api/projects":
            conn = get_db()
            rows = conn.execute(
                """
                SELECT p.id, v.slug, v.name, v.project_status, v.total_tasks,
                       v.completed_tasks, v.failed_tasks, v.in_progress_tasks,
                       v.pending_tasks, v.progress_pct, v.last_activity
                FROM v_project_status v
                JOIN projects p ON p.slug = v.slug
                ORDER BY p.id ASC
                """
            ).fetchall()
            conn.close()
            json_endpoint(self, [dict(r) for r in rows])
            return


        # Endpoint: tareas
        if path == "/api/tasks":
            slug = params.get("slug", [None])[0]
            conn = get_db()
            if slug:
                rows = conn.execute(
                    "SELECT t.id, t.title, t.assigned_agent, t.status, t.priority, t.retry_count, p.slug FROM tasks t JOIN projects p ON p.id = t.project_id WHERE p.slug = ? ORDER BY t.priority DESC, t.created_at ASC",
                    (slug,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT t.id, t.title, t.assigned_agent, t.status, t.priority, t.retry_count, p.slug FROM tasks t JOIN projects p ON p.id = t.project_id ORDER BY p.slug, t.priority DESC"
                ).fetchall()
            conn.close()
            json_endpoint(self, [dict(r) for r in rows])
            return

        # Endpoint: checkpoints
        if path == "/api/checkpoints":
            slug = params.get("slug", [None])[0]
            limit = int(params.get("limit", [20])[0])
            conn = get_db()
            if slug:
                rows = conn.execute(
                    "SELECT c.id, c.agent_name, c.step_number, c.step_description, c.created_at FROM checkpoints c JOIN projects p ON p.id = c.project_id WHERE p.slug = ? ORDER BY c.created_at DESC LIMIT ?",
                    (slug, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT c.id, c.agent_name, c.step_number, c.step_description, c.created_at, p.slug FROM checkpoints c JOIN projects p ON p.id = c.project_id ORDER BY c.created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            conn.close()
            json_endpoint(self, [dict(r) for r in rows])
            return

        # Endpoint: resumen general
        if path == "/api/summary":
            conn = get_db()
            projects = conn.execute("SELECT COUNT(*) as total FROM projects").fetchone()["total"]
            tasks = conn.execute("SELECT COUNT(*) as total FROM tasks").fetchone()["total"]
            completed = conn.execute("SELECT COUNT(*) as total FROM tasks WHERE status = 'COMPLETED'").fetchone()["total"]
            failed = conn.execute("SELECT COUNT(*) as total FROM tasks WHERE status = 'FAILED'").fetchone()["total"]
            agents = conn.execute("SELECT COUNT(DISTINCT agent_name) as total FROM execution_logs").fetchone()["total"]
            artifacts = conn.execute("SELECT COUNT(*) as total FROM artifacts").fetchone()["total"]
            adrs = conn.execute("SELECT COUNT(*) as total FROM adrs").fetchone()["total"]
            status_breakdown = {row["status"]: row["total"] for row in conn.execute(
                "SELECT status, COUNT(*) as total FROM tasks GROUP BY status"
            ).fetchall()}
            conn.close()
            json_endpoint(self, {
                "projects": projects,
                "tasks": tasks,
                "completed": completed,
                "failed": failed,
                "agents": agents,
                "artifacts": artifacts,
                "adrs": adrs,
                "status_breakdown": status_breakdown,
            })
            return

        # Endpoint: siguiente tarea READY (la de mayor prioridad en cualquier proyecto)
        if path == "/api/ready-queue":
            conn = get_db()
            row = conn.execute(
                """
                SELECT t.id, t.title, t.assigned_agent, t.priority, t.retry_count, p.slug AS project_slug, p.name AS project_name
                FROM tasks t JOIN projects p ON p.id = t.project_id
                WHERE t.status = 'READY' AND p.status = 'ACTIVE'
                ORDER BY t.priority DESC, t.created_at ASC
                LIMIT 1
                """
            ).fetchone()
            count = conn.execute(
                "SELECT COUNT(*) as total FROM tasks t JOIN projects p ON p.id = t.project_id WHERE t.status = 'READY' AND p.status = 'ACTIVE'"
            ).fetchone()["total"]
            conn.close()
            json_endpoint(self, {
                "next": dict(row) if row else None,
                "ready_total": count,
            })
            return

        # Endpoint: distribucion de artefactos por tipo
        if path == "/api/artifacts-by-type":
            conn = get_db()
            rows = conn.execute(
                "SELECT file_type, COUNT(*) AS total FROM artifacts GROUP BY file_type ORDER BY total DESC"
            ).fetchall()
            conn.close()
            json_endpoint(self, [dict(r) for r in rows])
            return

        # Endpoint: productividad por agente
        if path == "/api/agent-stats":
            conn = get_db()
            rows = conn.execute(
                """
                SELECT
                    t.assigned_agent AS agent,
                    COUNT(t.id) AS total,
                    SUM(CASE WHEN t.status = 'COMPLETED' THEN 1 ELSE 0 END) AS completed,
                    SUM(CASE WHEN t.status = 'FAILED' THEN 1 ELSE 0 END) AS failed,
                    SUM(CASE WHEN t.status IN ('READY','IN_PROGRESS','REVIEW','APPROVED') THEN 1 ELSE 0 END) AS pending,
                    MAX(t.created_at) AS last_seen
                FROM tasks t
                GROUP BY t.assigned_agent
                ORDER BY completed DESC, total DESC
                """
            ).fetchall()
            conn.close()
            json_endpoint(self, [dict(r) for r in rows])
            return

        # Endpoint: metricas detalladas por agente (tokens, duracion, latencia, estado)
        if path == "/api/agent-metrics":
            conn = get_db()
            rows = conn.execute(
                """
                SELECT
                    t.assigned_agent AS agent,
                    COUNT(t.id) AS total_tasks,
                    SUM(CASE WHEN t.status='COMPLETED' THEN 1 ELSE 0 END) AS completed,
                    SUM(CASE WHEN t.status='FAILED' THEN 1 ELSE 0 END) AS failed,
                    AVG(el.duration_ms) AS avg_duration_ms,
                    SUM(el.tokens_used) AS total_tokens,
                    AVG(mu.latency_ms) AS avg_latency_ms,
                    MAX(el.created_at) AS last_active,
                    CASE
                        WHEN EXISTS(SELECT 1 FROM tasks WHERE assigned_agent=t.assigned_agent AND status='IN_PROGRESS')
                        THEN 'processing'
                        WHEN EXISTS(SELECT 1 FROM tasks WHERE assigned_agent=t.assigned_agent AND status='FAILED')
                        THEN 'error'
                        ELSE 'idle'
                    END AS derived_status
                FROM tasks t
                LEFT JOIN execution_logs el ON el.task_id = t.id
                LEFT JOIN model_usage mu ON mu.agent_name = t.assigned_agent
                GROUP BY t.assigned_agent
                ORDER BY completed DESC
                """
            ).fetchall()
            conn.close()
            json_endpoint(self, [dict(r) for r in rows])
            return

        # Endpoint: uso de modelos LLM
        if path == "/api/model-usage":
            conn = get_db()
            rows = conn.execute(
                """
                SELECT
                    model_name,
                    COUNT(*) AS total_calls,
                    SUM(tokens_input) AS total_input_tokens,
                    SUM(tokens_output) AS total_output_tokens,
                    AVG(latency_ms) AS avg_latency_ms,
                    SUM(CASE WHEN success=1 THEN 1 ELSE 0 END) AS successful,
                    SUM(CASE WHEN success=0 THEN 1 ELSE 0 END) AS failed
                FROM model_usage
                GROUP BY model_name
                ORDER BY total_calls DESC
                """
            ).fetchall()
            conn.close()
            json_endpoint(self, [dict(r) for r in rows])
            return

        # Endpoint: estadisticas de feedback/correcciones
        if path == "/api/feedback-stats":
            conn = get_db()
            rows = conn.execute(
                """
                SELECT error_type, correction, affected_agent, recurrence_count, created_at
                FROM feedback_history
                ORDER BY recurrence_count DESC
                """
            ).fetchall()
            total = conn.execute("SELECT COUNT(*) as c FROM feedback_history").fetchone()["c"]
            conn.close()
            json_endpoint(self, {"total": total, "items": [dict(r) for r in rows]})
            return

        # Endpoint: log de errores (execution_logs + tasks + model_usage)
        if path == "/api/error-log":
            limit = min(50, max(1, int(params.get("limit", [20])[0])))
            conn = get_db()
            rows = conn.execute(
                """
                SELECT
                    'agent' AS source,
                    e.agent_name,
                    e.action_detail AS message,
                    e.action_type,
                    e.created_at,
                    t.title AS task_title,
                    p.slug AS project_slug
                FROM execution_logs e
                LEFT JOIN tasks t ON t.id = e.task_id
                LEFT JOIN projects p ON p.id = t.project_id
                WHERE e.outcome = 'failure' OR e.action_type = 'error'
                UNION ALL
                SELECT
                    'task' AS source,
                    t.assigned_agent AS agent_name,
                    t.error_message AS message,
                    'task_failure' AS action_type,
                    t.completed_at AS created_at,
                    t.title AS task_title,
                    p.slug AS project_slug
                FROM tasks t
                JOIN projects p ON p.id = t.project_id
                WHERE t.status = 'FAILED' AND t.error_message IS NOT NULL
                UNION ALL
                SELECT
                    'model' AS source,
                    mu.agent_name,
                    mu.error_message AS message,
                    'api_failure' AS action_type,
                    mu.created_at,
                    NULL AS task_title,
                    NULL AS project_slug
                FROM model_usage mu
                WHERE mu.success = 0 AND mu.error_message IS NOT NULL
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            total_errors = conn.execute(
                "SELECT COUNT(*) as c FROM execution_logs WHERE outcome='failure' OR action_type='error'"
            ).fetchone()["c"]
            total_task_failures = conn.execute(
                "SELECT COUNT(*) as c FROM tasks WHERE status='FAILED'"
            ).fetchone()["c"]
            total_api_failures = conn.execute(
                "SELECT COUNT(*) as c FROM model_usage WHERE success=0"
            ).fetchone()["c"]
            conn.close()
            json_endpoint(self, {
                "items": [dict(r) for r in rows],
                "summary": {
                    "total_agent_errors": total_errors,
                    "total_task_failures": total_task_failures,
                    "total_api_failures": total_api_failures,
                    "total": total_errors + total_task_failures + total_api_failures,
                },
            })
            return

        # Endpoint: metricas de cache de respuestas
        if path == "/api/cache-stats":
            conn = get_db()
            row = conn.execute(
                """
                SELECT
                    COUNT(*) AS total_entries,
                    COUNT(DISTINCT agent_profile) AS unique_agents,
                    SUM(tokens_used) AS total_tokens_cached,
                    MIN(created_at) AS oldest_entry,
                    MAX(last_used) AS most_recent_use
                FROM response_cache
                """
            ).fetchone()
            conn.close()
            json_endpoint(self, dict(row) if row else {})
            return

        # Endpoint: timeline paginado con busqueda
        if path == "/api/timeline-paginated":
            page = max(1, int(params.get("page", [1])[0]))
            per_page = min(100, max(1, int(params.get("per_page", [25])[0])))
            search = params.get("search", [""])[0].strip()
            agent_filter = params.get("agent", [""])[0].strip()
            action_filter = params.get("action", [""])[0].strip()
            offset = (page - 1) * per_page

            conn = get_db()
            conditions = []
            query_params = []

            if search:
                conditions.append("(e.agent_name LIKE ? OR t.title LIKE ? OR e.action_detail LIKE ?)")
                query_params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
            if agent_filter:
                conditions.append("e.agent_name = ?")
                query_params.append(agent_filter)
            if action_filter:
                conditions.append("e.action_type = ?")
                query_params.append(action_filter)

            where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

            total = conn.execute(
                f"SELECT COUNT(*) as c FROM execution_logs e LEFT JOIN tasks t ON t.id = e.task_id {where}",
                query_params,
            ).fetchone()["c"]

            query_params.extend([per_page, offset])
            rows = conn.execute(
                f"""
                SELECT e.agent_name, e.action_type, e.action_detail, e.outcome, e.task_id,
                       e.created_at, e.duration_ms, e.tokens_used,
                       t.title AS task_title, p.slug AS project_slug
                FROM execution_logs e
                LEFT JOIN tasks t ON t.id = e.task_id
                LEFT JOIN projects p ON p.id = t.project_id
                {where}
                ORDER BY e.created_at DESC
                LIMIT ? OFFSET ?
                """,
                query_params,
            ).fetchall()
            conn.close()
            json_endpoint(self, {
                "items": [dict(r) for r in rows],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": max(1, -(-total // per_page)),
                },
            })
            return

        # Endpoint: tareas paginadas con busqueda
        if path == "/api/tasks-paginated":
            page = max(1, int(params.get("page", [1])[0]))
            per_page = min(100, max(1, int(params.get("per_page", [25])[0])))
            search = params.get("search", [""])[0].strip()
            status_filter = params.get("status", [""])[0].strip()
            slug = params.get("slug", [None])[0]
            sort = params.get("sort", ["time_desc"])[0]  # time_desc, time_asc, priority_desc, created_desc
            offset = (page - 1) * per_page

            conn = get_db()
            conditions = []
            query_params = []

            if slug:
                conditions.append("p.slug = ?")
                query_params.append(slug)
            if search:
                conditions.append("(t.title LIKE ? OR t.assigned_agent LIKE ? OR p.slug LIKE ?)")
                query_params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
            if status_filter:
                conditions.append("t.status = ?")
                query_params.append(status_filter)

            where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

            # Ordenamiento
            order_map = {
                "time_desc": "COALESCE(t.started_at, t.completed_at, t.created_at) DESC",
                "time_asc": "COALESCE(t.started_at, t.completed_at, t.created_at) ASC",
                "priority_desc": "t.priority DESC, t.created_at ASC",
                "created_desc": "t.created_at DESC",
            }
            order_by = order_map.get(sort, order_map["time_desc"])

            total = conn.execute(
                f"SELECT COUNT(*) as c FROM tasks t JOIN projects p ON p.id = t.project_id {where}",
                query_params,
            ).fetchone()["c"]

            query_params.extend([per_page, offset])
            rows = conn.execute(
                f"""
                SELECT t.id, t.title, t.assigned_agent, t.status, t.priority,
                       t.retry_count, t.started_at, t.completed_at, t.created_at, t.error_message,
                       p.slug
                FROM tasks t
                JOIN projects p ON p.id = t.project_id
                {where}
                ORDER BY {order_by}
                LIMIT ? OFFSET ?
                """,
                query_params,
            ).fetchall()
            conn.close()
            json_endpoint(self, {
                "items": [dict(r) for r in rows],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": max(1, -(-total // per_page)),
                },
                "sort": sort,
            })
            return

        # Endpoint: proyectos paginados con busqueda
        if path == "/api/projects-paginated":
            page = max(1, int(params.get("page", [1])[0]))
            per_page = min(100, max(1, int(params.get("per_page", [25])[0])))
            search = params.get("search", [""])[0].strip()
            status_filter = params.get("status", [""])[0].strip()
            sort = params.get("sort", ["time_desc"])[0]  # time_desc, completed_desc, name
            offset = (page - 1) * per_page

            conn = get_db()
            conditions = []
            query_params = []

            if search:
                conditions.append("(p.name LIKE ? OR p.slug LIKE ? OR p.client LIKE ?)")
                query_params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
            if status_filter:
                conditions.append("p.status = ?")
                query_params.append(status_filter)

            where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

            order_map = {
                "time_desc": "last_worked DESC",
                "time_asc": "last_worked ASC",
                "completed_desc": "p.completed_tasks DESC",
                "name": "p.name ASC",
            }
            order_by = order_map.get(sort, order_map["time_desc"])

            total = conn.execute(
                f"SELECT COUNT(*) as c FROM projects p {where}",
                query_params,
            ).fetchone()["c"]

            query_params.extend([per_page, offset])
            rows = conn.execute(
                f"""
                SELECT p.slug, p.name, p.project_status, p.total_tasks, p.completed_tasks,
                       p.failed_tasks, p.in_progress_tasks, p.pending_tasks, p.progress_pct,
                       p.last_activity,
                       pr.updated_at,
                       COALESCE(
                           (SELECT MAX(el.created_at) FROM execution_logs el
                            JOIN tasks t2 ON t2.id = el.task_id
                            WHERE t2.project_id = p.id),
                           (SELECT MAX(t3.completed_at) FROM tasks t3 WHERE t3.project_id = p.id),
                           pr.updated_at
                       ) AS last_worked
                FROM v_project_status p
                JOIN projects pr ON pr.id = p.id
                {where}
                ORDER BY {order_by}
                LIMIT ? OFFSET ?
                """,
                query_params,
            ).fetchall()
            conn.close()
            json_endpoint(self, {
                "items": [dict(r) for r in rows],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": max(1, -(-total // per_page)),
                },
                "sort": sort,
            })
            return

        # Endpoint: ADRs indexados
        if path == "/api/adrs":
            conn = get_db()
            rows = conn.execute(
                "SELECT id, decision_id, title, status, created_at FROM adrs ORDER BY created_at DESC"
            ).fetchall()
            conn.close()
            json_endpoint(self, [dict(r) for r in rows])
            return

        # Endpoint: timeline de actividad (ultimos N eventos)
        if path == "/api/timeline":
            limit = int(params.get("limit", [10])[0])
            conn = get_db()
            rows = conn.execute(
                """
                SELECT e.agent_name, e.action_type, e.action_detail, e.outcome, e.task_id, e.created_at,
                       t.title AS task_title, p.slug AS project_slug
                FROM execution_logs e
                LEFT JOIN tasks t ON t.id = e.task_id
                LEFT JOIN projects p ON p.id = t.project_id
                ORDER BY e.created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            conn.close()
            json_endpoint(self, [dict(r) for r in rows])
            return

        # Endpoint: last-modified (timestamp del ultimo INSERT/UPDATE en logs/artifacts/tasks)
        if path == "/api/last-modified":
            conn = get_db()
            row = conn.execute(
                """
                SELECT MAX(ts) AS last_modified FROM (
                    SELECT MAX(created_at) AS ts FROM execution_logs
                    UNION ALL
                    SELECT MAX(created_at) FROM artifacts
                    UNION ALL
                    SELECT MAX(created_at) FROM tasks
                    UNION ALL
                    SELECT MAX(updated_at) FROM projects
                )
                """
            ).fetchone()
            conn.close()
            json_endpoint(self, {"last_modified": row["last_modified"] if row else None})
            return

        # 404
        self.send_error(404, f"Endpoint not found: {path}")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Endpoint: apagar dashboard + supervisor
        if path == "/api/shutdown":
            json_endpoint(self, {"status": "shutting_down", "message": "Apagando en 2 segundos..."})
            my_pid = os.getpid()
            # Matar supervisor
            try:
                if PID_FILE.exists():
                    pid = int(PID_FILE.read_text(encoding="utf-8").strip())
                    try: os.kill(pid, 9)
                    except: pass
                    try: PID_FILE.unlink()
                    except: pass
            except: pass
            # Matar dashboard via PowerShell externo (Stop-Process es lo
            # mas confiable en Windows; no se puede self-kill desde thread).
            import subprocess
            subprocess.Popen(
                ["powershell", "-NoProfile", "-Command",
                 f"Start-Sleep -Seconds 2; Stop-Process -Id {my_pid} -Force"],
                creationflags=0x08000000,  # CREATE_NO_WINDOW
                close_fds=True
            )
            return

        self.send_error(404, f"Endpoint not found: {path}")

    def log_message(self, format, *args):
        print(f"[Dashboard] {args[0]}")


if __name__ == "__main__":
    if not DB_PATH.exists():
        print(f"ERROR: Database not found: {DB_PATH}")
        print("       Run init_ecosystem.py first to create the database.")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f" AIRON-Cast Dashboard")
    print(f" {'='*60}")
    print(f" Server: http://localhost:{PORT}")
    print(f" Database: {DB_PATH}")
    print(f" Press Ctrl+C to stop")
    print(f"{'='*60}\n")

    # ThreadingHTTPServer: cada request corre en su propio thread. Esto
    # es CRITICO para evitar que un handler lento (ej: is_supervisor_alive
    # con tasklist que tarda 2s en Windows) bloquee todo el resto de las
    # requests del dashboard. Ver bug §6.9.
    server = http.server.ThreadingHTTPServer(("localhost", PORT), DashboardHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print("\nDashboard stopped.")
        try:
            server.server_close()
        except Exception:
            pass
        os._exit(0)
