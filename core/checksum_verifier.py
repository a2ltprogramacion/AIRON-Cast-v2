"""
AIRON-Cast — Checksum Verifier
===============================
Verifica integridad de artefactos usando SHA256.
Adaptado del Legacy (2026-06-03): rutas workspace/, integración con HITLGateway.
"""

import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from core.memory_manager import MemoryManager
from core.hitl_gateway import HITLGateway


class VerificationReport:
    """Reporte de verificación de integridad de artefactos."""
    def __init__(self):
        self.total = 0
        self.verified_ok = 0
        self.compromised: List[Dict] = []
        self.missing: List[Dict] = []

    def to_dict(self) -> Dict:
        return {
            "total": self.total,
            "verified_ok": self.verified_ok,
            "compromised": self.compromised,
            "missing": self.missing,
        }


class ChecksumVerifier:
    """Verificador de integridad de artefactos."""

    def __init__(self, mm: Optional[MemoryManager] = None):
        self.mm = mm or MemoryManager()
        self.hitl = HITLGateway(self.mm)

    def verify_project_artifacts(self, project_slug: str) -> VerificationReport:
        """Verifica todos los artefactos de un proyecto."""
        project = self.mm.get_project(project_slug)
        if not project:
            raise ValueError(f"Proyecto {project_slug} no encontrado")
        project_id = project["id"]

        conn = sqlite3.connect(str(self.mm.db_path))
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

            path = Path(file_path)
            if not path.exists():
                report.missing.append({
                    "artifact_id": art_id,
                    "file_path": file_path,
                    "error": "Archivo no encontrado"
                })
                self._escalate_if_compromised(project_slug, art_id, "missing", file_path)
                continue

            with open(path, "rb") as f:
                actual_checksum = hashlib.sha256(f.read()).hexdigest()

            if actual_checksum != expected_checksum:
                report.compromised.append({
                    "artifact_id": art_id,
                    "file_path": file_path,
                    "expected_checksum": expected_checksum,
                    "actual_checksum": actual_checksum,
                })
                self._escalate_if_compromised(project_slug, art_id, "compromised", file_path)
            else:
                report.verified_ok += 1

        return report

    def verify_single(self, artifact_id: int) -> bool:
        """Verifica un único artefacto."""
        return self.mm.verify_artifact(artifact_id)

    def generate_integrity_report(self, project_slug: str) -> str:
        """Genera un reporte de integridad en markdown dentro de workspace/<slug>/reports/."""
        report = self.verify_project_artifacts(project_slug)

        reports_dir = Path("workspace") / project_slug / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_path = reports_dir / "integrity-report.md"

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
        """Escala a HITL si se detecta un artefacto comprometido."""
        conn = sqlite3.connect(str(self.mm.db_path))
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM tasks WHERE project_id = (SELECT project_id FROM artifacts WHERE id = ?) LIMIT 1",
            (artifact_id,))
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