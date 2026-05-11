import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core.memory_manager import MemoryManager
from core.hitl_gateway import HITLGateway


class VerificationReport:
    """Reporte de verificación de integridad de artefactos."""
    def __init__(self):
        self.total = 0
        self.verified_ok = 0
        self.compromised: List[Dict] = []   # cada dict: artifact_id, file_path, expected, actual
        self.missing: List[Dict] = []       # cada dict: artifact_id, file_path, error

    def to_dict(self) -> Dict:
        return {
            "total": self.total,
            "verified_ok": self.verified_ok,
            "compromised": self.compromised,
            "missing": self.missing,
        }


class ChecksumVerifier:
    """
    Módulo para verificar integridad de artefactos usando checksum SHA256.
    Extiende la funcionalidad de MemoryManager.
    """

    def __init__(self, mm: Optional[MemoryManager] = None):
        self.mm = mm or MemoryManager()
        self.hitl = HITLGateway(self.mm)

    def verify_project_artifacts(self, project_slug: str) -> VerificationReport:
        """
        Verifica todos los artefactos de un proyecto.

        Args:
            project_slug: Slug del proyecto.

        Returns:
            VerificationReport con los resultados.
        """
        # Obtener project_id
        project = self.mm.get_project(project_slug)
        if not project:
            raise ValueError(f"Proyecto {project_slug} no encontrado")
        project_id = project["id"]

        # Obtener todos los artefactos del proyecto
        conn = sqlite3.connect(self.mm.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id, file_path, checksum FROM artifacts WHERE project_id = ?", (project_id,))
        artifacts = cur.fetchall()
        conn.close()

        report = VerificationReport()
        report.total = len(artifacts)

        for art in artifacts:
            art_id = art["id"]
            file_path = art["file_path"]
            expected_checksum = art["checksum"]

            # Verificar usando memory_manager
            # Nota: verify_artifact actualiza la tabla si el checksum no coincide,
            # pero no devuelve el resultado. Vamos a usarlo y luego verificar estado.
            # Como verify_artifact modifica la base, lo hacemos de manera segura.
            # Alternativa: calcular directamente y comparar.
            # Usaremos cálculo directo para evitar modificar estado.
            path = Path(file_path)
            if not path.exists():
                report.missing.append({
                    "artifact_id": art_id,
                    "file_path": file_path,
                    "error": "Archivo no encontrado"
                })
                # Llamar a hitl si está comprometido
                self._escalate_if_compromised(project_slug, art_id, "missing", file_path)
                continue

            # Calcular checksum actual
            import hashlib
            with open(path, "rb") as f:
                actual_checksum = hashlib.sha256(f.read()).hexdigest()

            if actual_checksum != expected_checksum:
                report.compromised.append({
                    "artifact_id": art_id,
                    "file_path": file_path,
                    "expected_checksum": expected_checksum,
                    "actual_checksum": actual_checksum,
                })
                # Llamar a hitl
                self._escalate_if_compromised(project_slug, art_id, "compromised", file_path)
            else:
                report.verified_ok += 1

        return report

    def verify_single(self, artifact_id: int) -> bool:
        """
        Verifica un único artefacto usando la función de MemoryManager.

        Args:
            artifact_id: ID del artefacto.

        Returns:
            True si el checksum coincide, False en caso contrario.
        """
        # Delegate to memory_manager
        return self.mm.verify_artifact(artifact_id)

    def generate_integrity_report(self, project_slug: str) -> str:
        """
        Genera un reporte de integridad en markdown dentro de docs/.

        Args:
            project_slug: Slug del proyecto.

        Returns:
            Ruta al archivo generado.
        """
        report = self.verify_project_artifacts(project_slug)

        # Crear directorio docs si no existe
        docs_dir = Path("output") / project_slug / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        report_path = docs_dir / "integrity-report.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# Reporte de Integridad de Artefactos\n\n")
            f.write(f"- **Proyecto:** {project_slug}\n")
            f.write(f"- **Fecha:** {datetime.now().isoformat()}\n\n")
            f.write(f"## Resumen\n\n")
            f.write(f"- Total artefactos: {report.total}\n")
            f.write(f"- Verificados OK: {report.verified_ok}\n")
            f.write(f"- Comprometidos: {len(report.compromised)}\n")
            f.write(f"- Faltantes: {len(report.missing)}\n\n")

            if report.compromised:
                f.write("## Artefactos comprometidos\n\n")
                f.write("| ID | Ruta | Checksum esperado | Checksum actual |\n")
                f.write("|----|------|-------------------|-----------------|\n")
                for c in report.compromised:
                    f.write(f"| {c['artifact_id']} | {c['file_path']} | {c['expected_checksum']} | {c['actual_checksum']} |\n")
                f.write("\n")

            if report.missing:
                f.write("## Artefactos faltantes\n\n")
                f.write("| ID | Ruta |\n")
                f.write("|----|------|\n")
                for m in report.missing:
                    f.write(f"| {m['artifact_id']} | {m['file_path']} |\n")
                f.write("\n")

        return str(report_path)

    def _escalate_if_compromised(self, project_slug: str, artifact_id: int,
                                 issue_type: str, file_path: str) -> None:
        """
        Escala a HITL si se detecta un artefacto comprometido.
        """
        # Evitar escalar si ya hay una escalación pendiente para el mismo proyecto?
        # Por simplicidad, siempre escalamos.
        # Obtenemos un task_id? No tenemos contexto. Usaremos 0 como placeholder.
        # En un uso real, el verificador debe recibir el task_id correspondiente.
        # Aquí asumimos que el proyecto tiene tareas asociadas; tomamos la primera tarea activa.
        # Para evitar errores, escalamos con task_id=0 y luego se registra.
        # Mejor: buscar una tarea asociada al proyecto.
        conn = sqlite3.connect(self.mm.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id FROM tasks WHERE project_id = (SELECT project_id FROM artifacts WHERE id = ?) LIMIT 1", (artifact_id,))
        row = cur.fetchone()
        conn.close()
        task_id = row[0] if row else 0

        context = {
            "artifact_id": artifact_id,
            "file_path": file_path,
            "issue_type": issue_type,
        }
        self.hitl.escalate(
            project_slug,
            task_id,
            "checksum_verifier",
            "Integridad de artefacto comprometida (checksum_verified = 2)",
            context
        )


if __name__ == "__main__":
    import tempfile
    import os

    # Configurar entorno temporal
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)
    mm = MemoryManager(db_path)

    # Crear esquema base (mínimo para pruebas)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY,
            slug TEXT UNIQUE,
            name TEXT,
            status TEXT,
            root_path TEXT
        );
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY,
            project_id INTEGER,
            title TEXT,
            assigned_agent TEXT,
            status TEXT,
            description TEXT,
            priority INTEGER,
            dependencies TEXT
        );
        CREATE TABLE artifacts (
            id INTEGER PRIMARY KEY,
            task_id INTEGER,
            project_id INTEGER,
            file_path TEXT,
            file_type TEXT,
            checksum TEXT,
            metadata TEXT
        );
        CREATE TABLE execution_logs (
            id INTEGER PRIMARY KEY,
            project_id INTEGER,
            task_id INTEGER,
            agent_name TEXT,
            action_type TEXT,
            details TEXT,
            timestamp TEXT
        );
    """)
    conn.commit()

    # Insertar proyecto
    cur.execute("INSERT INTO projects (slug, name, status, root_path) VALUES (?, ?, ?, ?)",
                ("test-proj", "Test", "RUNNING", "/fake"))
    project_id = cur.lastrowid
    cur.execute("INSERT INTO tasks (project_id, title, assigned_agent, status, description, priority, dependencies) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (project_id, "Tarea", "agent", "READY", "desc", 1, "[]"))
    task_id = cur.lastrowid

    # Crear archivo temporal y registrarlo como artefacto
    import hashlib
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("contenido original")
        temp_path = f.name
    with open(temp_path, "rb") as f:
        checksum = hashlib.sha256(f.read()).hexdigest()
    cur.execute("INSERT INTO artifacts (task_id, project_id, file_path, file_type, checksum, metadata) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (task_id, project_id, temp_path, "text", checksum, "{}"))
    artifact_id = cur.lastrowid
    conn.commit()
    conn.close()

    # Verificar
    verifier = ChecksumVerifier(mm)
    report = verifier.verify_project_artifacts("test-proj")
    print("Reporte inicial:", report.to_dict())
    assert report.total == 1
    assert report.verified_ok == 1
    assert len(report.compromised) == 0
    assert len(report.missing) == 0

    # Modificar archivo
    with open(temp_path, "a") as f:
        f.write(" modificado")

    # Verificar nuevamente
    report = verifier.verify_project_artifacts("test-proj")
    print("Reporte después de modificar:", report.to_dict())
    assert len(report.compromised) == 1
    assert report.compromised[0]["artifact_id"] == artifact_id

    # Generar reporte markdown
    report_path = verifier.generate_integrity_report("test-proj")
    print("Reporte generado:", report_path)
    assert Path(report_path).exists()

    # Limpiar
    os.unlink(temp_path)
    os.unlink(db_path)
    import shutil
    shutil.rmtree("output/test-proj", ignore_errors=True)