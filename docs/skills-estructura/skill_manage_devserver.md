# skill_manage_devserver
# Agent: agent_infra
# Version: 1.0
# Pattern: Deterministic (SKILL.md + scripts/)

---

## DESCRIPTION
Manages Django development server lifecycle for testing.
Starts, stops, and checks server on localhost.
Used exclusively as prerequisite for skill_run_api_smoke.
Activate when: orchestrator needs server running before smoke tests,
or needs to stop it after tests complete.
Do NOT use in production. Development and staging only.
Do NOT leave server running after tests complete.

---

## INPUT CONTRACT
{
  "task_id":    "{str}",
  "workflow_id":"{str}",
  "operation":  "start | stop | status",
  "project_dir":"{str}",
  "port":       8000,
  "db_target":  "development | test"
}

---

## EXECUTION FLOW

STEP 1 — VALIDATE ENVIRONMENT
  Call: python scripts/check_django_env.py
        --project_dir "{project_dir}"
  EXIT 1 if production DB detected. Hard block.

STEP 2 — EXECUTE OPERATION

  status:
    Call: python scripts/server_lifecycle.py
          --operation status --port {port}
    Returns: { running: bool, pid: int | null }

  start:
    Run status first.
    If already running: return ok with existing PID.
    Call: python scripts/server_lifecycle.py
          --operation start
          --project_dir "{project_dir}"
          --port {port}
    Wait up to 10s for HTTP response.
    EXIT 1 if no response within 10s.
    Write PID to .devserver.pid in project_dir.

  stop:
    Read PID from .devserver.pid.
    Call: python scripts/server_lifecycle.py
          --operation stop --pid {pid}
    Verify server no longer responds.
    Delete .devserver.pid.

---

## WORKFLOW INTEGRATION PATTERN
Any workflow using skill_run_api_smoke must include:
  [N]   agent_infra  -> skill_manage_devserver (operation: start)
  [N+1] agent_tester -> skill_run_api_smoke
  [N+2] agent_infra  -> skill_manage_devserver (operation: stop)

---

## SCRIPTS

### server_lifecycle.py
start:  subprocess.Popen(["python", "manage.py", "runserver", port])
        writes PID to .devserver.pid
stop:   reads PID, sends SIGTERM, waits up to 5s
status: checks PID alive + HTTP response on port
EXIT 0: success | EXIT 1: failed

---

## OUTPUT FORMAT
{
  "agent":   "agent_infra",
  "task_id": "{task_id}",
  "skill":   "skill_manage_devserver",
  "status":  "completed | failed",
  "output": {
    "operation": "{str}",
    "running":   true | false,
    "pid":       {int} | null,
    "port":      {int},
    "url":       "http://127.0.0.1:{port}"
  },
  "tokens":  {int},
  "error":   null | "{description}"
}
