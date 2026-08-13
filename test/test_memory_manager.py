import unittest
import sqlite3
import os
from core.memory_manager import MemoryManager


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.mm = MemoryManager(":memory:")


class TestProjects(BaseTest):
    def test_create_project_success(self):
        self.mm.create_project("a", "A", "web-app", "wf", "c", 1)
        self.assertIsNotNone(self.mm.get_project("a"))

    def test_create_duplicate_slug_raises(self):
        self.mm.create_project("a", "A", "web-app", "wf", "c", 1)
        with self.assertRaises(Exception):
            self.mm.create_project("a", "A", "web-app", "wf", "c", 1)

    def test_update_project_status_valid(self):
        self.mm.create_project("a", "A", "web-app", "wf", "c", 1)
        self.mm.update_project_status("a", "ACTIVE")

    def test_update_project_status_invalid_raises(self):
        self.mm.create_project("a", "A", "web-app", "wf", "c", 1)
        with self.assertRaises(Exception):
            self.mm.update_project_status("a", "INVALID")

    def test_get_project_returns_dict(self):
        self.mm.create_project("a", "A", "web-app", "wf", "c", 1)
        self.assertIsInstance(self.mm.get_project("a"), dict)

    def test_get_nonexistent_project_returns_none(self):
        self.assertIsNone(self.mm.get_project("x"))


class TestTasks(BaseTest):
    def setUp(self):
        super().setUp()
        self.mm.create_project("a", "A", "web-app", "wf", "c", 1)
        self.project = self.mm.get_project("a")

    def test_create_task_starts_locked(self):
        t = self.mm.create_task(self.project["id"], "t", "a", "", 1, [])
        task = self.mm.get_ready_tasks("a")
        self.assertEqual(len(task), 0)

    def test_unlock_without_dependencies(self):
        t = self.mm.create_task(self.project["id"], "t", "a", "", 1, [])
        self.mm.unlock_task(t)
        ready = self.mm.get_ready_tasks("a")
        self.assertTrue(len(ready) > 0)

    def test_unlock_blocked_by_pending_dependency(self):
        t1 = self.mm.create_task(self.project["id"], "t1", "a", "", 1, [])
        t2 = self.mm.create_task(self.project["id"], "t2", "a", "", 1, [t1])
        self.mm.unlock_task(t2)
        self.assertEqual(len(self.mm.get_ready_tasks("a")), 0)

    def test_unlock_passes_when_dependency_completed(self):
        t1 = self.mm.create_task(self.project["id"], "t1", "a", "", 1, [])
        t2 = self.mm.create_task(self.project["id"], "t2", "a", "", 1, [t1])

        self.mm.unlock_task(t1)
        self.mm.update_task_status(t1, "COMPLETED", "a", "m")
        self.mm.unlock_task(t2)

        self.assertTrue(len(self.mm.get_ready_tasks("a")) > 0)


class TestArtifacts(BaseTest):
    def test_register_artifact_nonexistent_file_raises(self):
        with self.assertRaises(Exception):
            self.mm.register_artifact(1, 1, "no.file", "txt", {})


class TestCheckpoints(BaseTest):
    def test_write_checkpoint_returns_id(self):
        self.mm.create_project("a", "A", "web-app", "wf", "c", 1)
        p = self.mm.get_project("a")
        t = self.mm.create_task(p["id"], "t", "a", "", 1, [])
        cid = self.mm.write_checkpoint(p["id"], t, "a", 1, "d", "{}")
        self.assertIsNotNone(cid)


class TestStateJson(BaseTest):
    def test_write_and_read_roundtrip(self):
        self.mm.write_state_json("a", {"x": 1})
        data = self.mm.read_state_json("a")
        self.assertEqual(data["x"], 1)


class TestViews(BaseTest):
    def test_v_ready_tasks_filters_correctly(self):
        self.mm.create_project("a", "A", "web-app", "wf", "c", 1)
        p = self.mm.get_project("a")
        t = self.mm.create_task(p["id"], "t", "a", "", 1, [])
        self.mm.unlock_task(t)
        self.assertTrue(len(self.mm.get_ready_tasks("a")) > 0)


if __name__ == "__main__":
    unittest.main()