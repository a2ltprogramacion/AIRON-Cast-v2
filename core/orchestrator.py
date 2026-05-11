import time
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pathlib import Path

from core.memory_manager import MemoryManager


@dataclass
class ExecutionReport:
    project: str
    tasks_completed: int
    tasks_failed: int
    tasks_pending: int
    stop_loss_triggered: bool
    hitl_required: bool
    duration_seconds: float
    timestamp: str


class Orchestrator:
    def __init__(self, project_slug: str, workflow_path: str, memory_manager: Optional[MemoryManager] = None):
        self.project_slug = project_slug
        self.workflow_path = Path(workflow_path)
        self.mm = memory_manager if memory_manager else MemoryManager()
        self.project = None
        self.workflow = {}
        self.hitl_required = False

    def load_workflow(self) -> dict:
        with open(self.workflow_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.workflow = {"raw": content}
        return self.workflow

    def build_task_queue(self) -> list:
        return self.mm.get_ready_tasks(self.project_slug)

    def _execute_task(self, task: dict) -> bool:
        # Simulación: falla si título contiene "FAIL_ONCE" y retry_count == 0
        if "FAIL_ONCE" in task["title"] and task.get("retry_count", 0) == 0:
            raise Exception("Simulated failure")
        return True

    def _handle_failure(self, task: dict, error: str) -> None:
        task_id = task["id"]
        retry_count = task.get("retry_count", 0)

        if retry_count < 2:
            self.mm.update_task_status(task_id, "READY", "orchestrator", "sim")
        else:
            self.mm.update_task_status(task_id, "FAILED", "orchestrator", "sim")
            self.hitl_required = True

    def _should_stop(self) -> bool:
        alerts = self.mm.get_integrity_alerts()
        if alerts:
            return True

        state = self.mm.read_state_json(self.project_slug)
        if state and state.get("estado") == "PAUSED":
            return True

        tasks = self.mm.get_ready_tasks(self.project_slug)
        for t in tasks:
            if t.get("status") == "FAILED" and t.get("retry_count", 0) >= 3:
                return True

        return False

    def resume_from_checkpoint(self) -> bool:
        project = self.mm.get_project(self.project_slug)
        if not project:
            return False

        checkpoint = self.mm.get_last_checkpoint(project["id"])
        if not checkpoint:
            return False

        state = json.loads(checkpoint["state_snapshot"])
        self.mm.write_state_json(self.project_slug, state)
        return True

    def run(self) -> ExecutionReport:
        start = time.time()

        self.load_workflow()

        self.project = self.mm.get_project(self.project_slug)
        if not self.project or self.project["status"] != "ACTIVE":
            raise Exception("Project not ACTIVE or not found")

        tasks_completed = 0
        tasks_failed = 0

        while True:
            queue = self.build_task_queue()
            if not queue:
                break

            for task in queue:
                if self._should_stop():
                    break

                task_id = task["id"]

                # checkpoint BEFORE execution
                state = self.mm.read_state_json(self.project_slug) or {}
                self.mm.write_checkpoint(
                    self.project["id"],
                    task_id,
                    "orchestrator",
                    0,
                    "before execution",
                    json.dumps(state),
                )

                self.mm.update_task_status(task_id, "IN_PROGRESS", "orchestrator", "sim")

                try:
                    self._execute_task(task)

                    # simulate validation OK
                    self.mm.update_task_status(task_id, "COMPLETED", "orchestrator", "sim")
                    tasks_completed += 1

                    # unlock dependents
                    all_tasks = self.mm.get_ready_tasks(self.project_slug)
                    for t in all_tasks:
                        self.mm.unlock_task(t["id"])

                except Exception as e:
                    self._handle_failure(task, str(e))
                    tasks_failed += 1

            if self._should_stop():
                break

        end = time.time()

        all_tasks = self.mm.get_project_status(self.project_slug)
        total = all_tasks[0]["total_tasks"] if all_tasks else 0

        report = ExecutionReport(
            project=self.project_slug,
            tasks_completed=tasks_completed,
            tasks_failed=tasks_failed,
            tasks_pending=total - tasks_completed - tasks_failed,
            stop_loss_triggered=self._should_stop(),
            hitl_required=self.hitl_required,
            duration_seconds=round(end - start, 2),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        return report


if __name__ == "__main__":
    mm = MemoryManager()

    slug = "test_project"
    mm.create_project(slug, "Test", "web", "wf.md", "client", 1)
    mm.update_project_status(slug, "ACTIVE")
    project = mm.get_project(slug)

    t1 = mm.create_task(project["id"], "Task 1", "agent", "", 1, [])
    t2 = mm.create_task(project["id"], "Task 2 FAIL_ONCE", "agent", "", 1, [t1])
    t3 = mm.create_task(project["id"], "Task 3", "agent", "", 1, [t2])

    mm.unlock_task(t1)

    orch = Orchestrator(slug, "workflows/system.md")
    report = orch.run()

    print(asdict(report))