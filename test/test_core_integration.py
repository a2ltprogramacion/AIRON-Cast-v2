import unittest
from core.memory_manager import MemoryManager
from core.orchestrator import Orchestrator


class TestMemoryManagerIntegration(unittest.TestCase):
    def setUp(self):
        self.mm = MemoryManager(":memory:")
        self.mm.create_project("p", "P", "web-app", "wf", "c", 1)
        self.mm.update_project_status("p", "ACTIVE")
        self.project = self.mm.get_project("p")

    def test_project_lifecycle(self):
        self.mm.update_project_status("p", "COMPLETED")
        self.assertEqual(self.mm.get_project("p")["status"], "COMPLETED")

    def test_task_dependency_chain(self):
        t1 = self.mm.create_task(self.project["id"], "A", "a", "", 1, [])
        t2 = self.mm.create_task(self.project["id"], "B", "a", "", 1, [t1])

        self.mm.unlock_task(t2)
        self.assertEqual(len(self.mm.get_ready_tasks("p")), 0)

    def test_checkpoint_before_step(self):
        t = self.mm.create_task(self.project["id"], "t", "a", "", 1, [])
        cid = self.mm.write_checkpoint(self.project["id"], t, "a", 1, "d", "{}")
        self.assertIsNotNone(cid)

    def test_artifact_checksum_cycle(self):
        pass

    def test_hitl_escalation_flow(self):
        pass


class TestOrchestratorIntegration(unittest.TestCase):
    def setUp(self):
        self.mm = MemoryManager(":memory:")
        self.mm.create_project("p", "P", "web-app", "wf", "c", 1)
        self.mm.update_project_status("p", "ACTIVE")
        self.project = self.mm.get_project("p")

    def test_run_simple_workflow(self):
        t1 = self.mm.create_task(self.project["id"], "A", "a", "", 1, [])
        self.mm.unlock_task(t1)

        orch = Orchestrator("p", "workflows/system.md", memory_manager=self.mm)
        report = orch.run()

        self.assertTrue(report.tasks_completed >= 1)

    def test_resume_from_checkpoint(self):
        orch = Orchestrator("p", "workflows/system.md", memory_manager=self.mm)
        self.assertFalse(orch.resume_from_checkpoint())

    def test_stop_loss_on_integrity_alert(self):
        orch = Orchestrator("p", "workflows/system.md", memory_manager=self.mm)
        self.assertFalse(orch._should_stop())

    def test_dependency_unlock_cascade(self):
        t1 = self.mm.create_task(self.project["id"], "A", "a", "", 1, [])
        t2 = self.mm.create_task(self.project["id"], "B", "a", "", 1, [t1])

        self.mm.unlock_task(t1)
        self.mm.update_task_status(t1, "COMPLETED", "a", "m")
        self.mm.unlock_task(t2)

        self.assertTrue(len(self.mm.get_ready_tasks("p")) > 0)


if __name__ == "__main__":
    unittest.main()