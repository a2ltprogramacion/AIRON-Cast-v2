"""Tests unitarios de service_supervisor.

Mockeamos subprocess y urllib para no depender de procesos reales.
"""
import sys
from pathlib import Path
from unittest import mock

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core import service_supervisor as ss  # noqa: E402


@pytest.fixture
def clean_pidfile():
    """Asegura que el PID file este limpio antes y despues de cada test."""
    ss.PID_FILE.unlink(missing_ok=True)
    yield
    ss.PID_FILE.unlink(missing_ok=True)


class TestIsSupervisorAlive:
    def test_false_sin_pidfile(self, clean_pidfile):
        assert ss.is_supervisor_alive() is False

    def test_false_con_pidfile_corrupto(self, clean_pidfile):
        ss.PID_FILE.write_text("no-es-un-numero", encoding="utf-8")
        assert ss.is_supervisor_alive() is False
        assert not ss.PID_FILE.exists()

    def test_true_con_tasklist_reportando_pid(self, clean_pidfile):
        ss.PID_FILE.write_text("1234", encoding="utf-8")
        fake_stdout = (
            'INFO: Tasks shown based on the specified criteria.\n\n'
            '"System Idle Process","0","Services","0","24 K"\n'
            '"python.exe","1234","Console","1","15,000 K"\n'
        )
        with mock.patch.object(ss.subprocess, "run", return_value=mock.Mock(stdout=fake_stdout)):
            assert ss.is_supervisor_alive() is True
        assert ss.PID_FILE.exists()

    def test_false_con_tasklist_sin_pid_limpia_archivo(self, clean_pidfile):
        ss.PID_FILE.write_text("9999", encoding="utf-8")
        fake_stdout = 'INFO: No tasks are running...\n'
        with mock.patch.object(ss.subprocess, "run", return_value=mock.Mock(stdout=fake_stdout)):
            assert ss.is_supervisor_alive() is False
        assert not ss.PID_FILE.exists()

    def test_false_cuando_tasklist_falla(self, clean_pidfile):
        ss.PID_FILE.write_text("1234", encoding="utf-8")
        with mock.patch.object(ss.subprocess, "run", side_effect=OSError("tasklist not found")):
            assert ss.is_supervisor_alive() is False


class TestEnsureSupervisorRunning:
    def test_no_relanza_si_ya_vive(self, clean_pidfile):
        ss.PID_FILE.write_text("1234", encoding="utf-8")
        with mock.patch.object(ss, "is_supervisor_alive", return_value=True):
            with mock.patch.object(ss, "launch_supervisor_detached") as mock_launch:
                result = ss.ensure_supervisor_running()
        assert result["status"] == "running"
        assert result["action"] == "none"
        mock_launch.assert_not_called()

    def test_lanza_si_no_existe(self, clean_pidfile):
        with mock.patch.object(ss, "is_supervisor_alive", side_effect=[False, True]):
            with mock.patch.object(ss, "launch_supervisor_detached", return_value=4321) as mock_launch:
                with mock.patch.object(ss.time, "sleep"):
                    result = ss.ensure_supervisor_running()
        assert result["status"] == "launched"
        assert result["pid"] == 4321
        mock_launch.assert_called_once()

    def test_lanza_aunque_supervisor_no_confirme_aun(self, clean_pidfile):
        with mock.patch.object(ss, "is_supervisor_alive", return_value=False):
            with mock.patch.object(ss, "launch_supervisor_detached", return_value=5555):
                with mock.patch.object(ss.time, "sleep"):
                    result = ss.ensure_supervisor_running()
        assert result["status"] in ("launch_pending", "launched")
        assert result["pid"] == 5555


class TestQuickHealthcheck:
    def _mock_socket_connect(self, side_effect):
        mock_sock = mock.MagicMock()
        mock_sock.__enter__.return_value = mock_sock
        return mock.patch.object(ss.socket, "socket", return_value=mock_sock).__enter__() or mock.patch.object(
            mock_sock, "connect", side_effect=side_effect
        )

    def test_dashboard_down_retorna_false(self, clean_pidfile):
        mock_sock = mock.MagicMock()
        mock_sock.__enter__.return_value = mock_sock
        with mock.patch.object(ss.socket, "socket", return_value=mock_sock):
            with mock.patch.object(mock_sock, "connect", side_effect=ConnectionRefusedError("refused")):
                result = ss.quick_healthcheck()
        assert result["dashboard_up"] is False
        assert result["dashboard_error"] == "ConnectionRefusedError"
        assert "dashboard_url" in result

    def test_dashboard_up_retorna_true(self, clean_pidfile):
        mock_sock = mock.MagicMock()
        mock_sock.__enter__.return_value = mock_sock
        with mock.patch.object(ss.socket, "socket", return_value=mock_sock):
            with mock.patch.object(mock_sock, "connect", return_value=None):
                result = ss.quick_healthcheck()
        assert result["dashboard_up"] is True
        assert result["dashboard_error"] is None

    def test_incluye_db_size(self, clean_pidfile, tmp_path):
        ss.DB_PATH = tmp_path / "fake.db"
        ss.DB_PATH.write_bytes(b"x" * 1024)
        mock_sock = mock.MagicMock()
        mock_sock.__enter__.return_value = mock_sock
        with mock.patch.object(ss.socket, "socket", return_value=mock_sock):
            with mock.patch.object(mock_sock, "connect", side_effect=ConnectionRefusedError):
                result = ss.quick_healthcheck()
        assert result["db_exists"] is True
        assert result["db_size_bytes"] == 1024

    def test_db_inexistente(self, clean_pidfile, tmp_path):
        ss.DB_PATH = tmp_path / "no-existe.db"
        mock_sock = mock.MagicMock()
        mock_sock.__enter__.return_value = mock_sock
        with mock.patch.object(ss.socket, "socket", return_value=mock_sock):
            with mock.patch.object(mock_sock, "connect", side_effect=ConnectionRefusedError):
                result = ss.quick_healthcheck()
        assert result["db_exists"] is False
        assert result["db_size_bytes"] == 0


class TestLaunchSupervisorDetached:
    def test_crea_directorio_logs(self, clean_pidfile, tmp_path):
        ss.LOG_DIR = tmp_path / "logs-nuevos"
        ss.SUPERVISOR_LOG = ss.LOG_DIR / "supervisor.log"
        mock_proc = mock.Mock(pid=9999)
        with mock.patch.object(ss.subprocess, "Popen", return_value=mock_proc):
            pid = ss.launch_supervisor_detached()
        assert pid == 9999
        assert ss.LOG_DIR.exists()

    def test_usa_creationflags_en_windows(self, clean_pidfile):
        with mock.patch.object(sys, "platform", "win32"):
            with mock.patch.object(ss.subprocess, "Popen", return_value=mock.Mock(pid=1111)) as mp:
                ss.launch_supervisor_detached()
        _, kwargs = mp.call_args
        assert "creationflags" in kwargs
        assert kwargs["creationflags"] == 0x00000008 | 0x00000200

    def test_usa_start_new_session_en_unix(self, clean_pidfile):
        with mock.patch.object(sys, "platform", "linux"):
            with mock.patch.object(ss.subprocess, "Popen", return_value=mock.Mock(pid=2222)) as mp:
                ss.launch_supervisor_detached()
        _, kwargs = mp.call_args
        assert kwargs.get("start_new_session") is True
        assert "creationflags" not in kwargs


class TestGitignore:
    def test_pidfile_listed(self):
        gitignore = REPO_ROOT / ".gitignore"
        if not gitignore.exists():
            pytest.skip("no .gitignore en este entorno")
        content = gitignore.read_text(encoding="utf-8")
        assert ".airon_supervisor.pid" in content
        assert "logs/" in content
