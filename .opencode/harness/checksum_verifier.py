#!/usr/bin/env python3
"""
Checksum Verifier — OpenCode ⊕ AIRON-Cast Fusion
Integridad de artefactos via SHA256 + Engram.
"""
import hashlib
import sqlite3
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

class ChecksumVerifier:
    def __init__(self, project_slug: str):
        self.project_slug = project_slug
        self.db_path = Path.home() / ".engram" / f"airon_{project_slug}.db"
        self._init_db()
    
    def _init_db(self):
        """Inicializa tabla de checksums si no existe."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS artifact_checksums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filepath TEXT NOT NULL,
                checksum TEXT NOT NULL,
                size INTEGER NOT NULL,
                agent TEXT NOT NULL,
                file_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verified INTEGER DEFAULT 0,
                UNIQUE(filepath, checksum)
            )
        """)
        conn.commit()
        conn.close()
    
    def calculate_checksum(self, filepath: str) -> str:
        """Calcula SHA256 de archivo."""
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def register(self, filepath: str, agent: str, file_type: str = "source") -> Dict[str, Any]:
        """Registra artefacto con checksum."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(filepath)
        
        checksum = self.calculate_checksum(filepath)
        size = os.path.getsize(filepath)
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO artifact_checksums 
            (filepath, checksum, size, agent, file_type, verified)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (filepath, checksum, size, agent, file_type))
        conn.commit()
        conn.close()
        
        return {"checksum": checksum, "size": size, "verified": True}
    
    def verify(self, filepath: str) -> Dict[str, Any]:
        """Verifica integridad de archivo contra registro."""
        if not os.path.exists(filepath):
            return {"verified": False, "reason": "file_not_found"}
        
        current_checksum = self.calculate_checksum(filepath)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT checksum, size, agent FROM artifact_checksums WHERE filepath = ?",
            (filepath,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {"verified": False, "reason": "not_registered"}
        
        stored_checksum, stored_size, agent = row
        current_size = os.path.getsize(filepath)
        
        if current_checksum != stored_checksum:
            return {
                "verified": False, 
                "reason": "checksum_mismatch",
                "expected": stored_checksum,
                "actual": current_checksum
            }
        
        if current_size != stored_size:
            return {
                "verified": False,
                "reason": "size_mismatch",
                "expected_size": stored_size,
                "actual_size": current_size
            }
        
        return {"verified": True, "checksum": current_checksum, "agent": agent}
    
    def list_artifacts(self, agent: str = None) -> list:
        """Lista artefactos registrados."""
        conn = sqlite3.connect(self.db_path)
        if agent:
            cursor = conn.execute(
                "SELECT filepath, checksum, size, agent, file_type, created_at, verified "
                "FROM artifact_checksums WHERE agent = ? ORDER BY created_at DESC",
                (agent,)
            )
        else:
            cursor = conn.execute(
                "SELECT filepath, checksum, size, agent, file_type, created_at, verified "
                "FROM artifact_checksums ORDER BY created_at DESC"
            )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "filepath": r[0], "checksum": r[1], "size": r[2],
                "agent": r[3], "file_type": r[4], "created_at": r[5], "verified": bool(r[6])
            }
            for r in rows
        ]


# Singleton por proyecto
_verifiers = {}

def get_checksum_verifier(project_slug: str) -> ChecksumVerifier:
    if project_slug not in _verifiers:
        _verifiers[project_slug] = ChecksumVerifier(project_slug)
    return _verifiers[project_slug]


if __name__ == "__main__":
    cv = get_checksum_verifier("test-project")
    print("ChecksumVerifier inicializado")