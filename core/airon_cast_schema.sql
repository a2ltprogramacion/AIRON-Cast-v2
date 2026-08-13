-- ============================================================================
-- AIRON-CAST: Esquema central de base de datos (SQLite)
-- Ecosistema de orquestación de agentes con Round-Robin y pizarra compartida
-- Versión: 1.1.0 — Fase E completada (model_usage, checkpoints_cleanup,
--            v_last_checkpoint, CHECK constraints, v_project_status mejorada)
-- ============================================================================

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- TABLAS
-- ---------------------------------------------------------------------------

-- Proyectos gestionados por el ecosistema
CREATE TABLE IF NOT EXISTS projects (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    slug            TEXT    NOT NULL UNIQUE,
    name            TEXT    NOT NULL,
    client          TEXT,
    project_type    TEXT,
    active_workflow TEXT,
    root_path       TEXT,
    status          TEXT    NOT NULL DEFAULT 'DRAFT'
                            CHECK (status IN ('DRAFT','ACTIVE','PAUSED','ARCHIVED','COMPLETED')),
    priority        INTEGER NOT NULL DEFAULT 0,
    notes           TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Trigger para mantener actualizado el timestamp en projects
CREATE TRIGGER IF NOT EXISTS trg_projects_updated_at
    AFTER UPDATE ON projects
    FOR EACH ROW
BEGIN
    UPDATE projects SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- Tareas que componen un flujo de trabajo; orquestadas por Round-Robin
CREATE TABLE IF NOT EXISTS tasks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id      INTEGER NOT NULL,
    title           TEXT    NOT NULL,
    description     TEXT,
    assigned_agent  TEXT,
    status          TEXT    NOT NULL DEFAULT 'READY'
                            CHECK (status IN ('LOCKED','READY','IN_PROGRESS','REVIEW',
                                              'APPROVED','COMPLETED','FAILED','SKIPPED')),
    priority        INTEGER NOT NULL DEFAULT 0,
    dependencies    TEXT,                           -- JSON array de task_ids
    parent_task_id  INTEGER,
    retry_count     INTEGER NOT NULL DEFAULT 0,
    max_retries     INTEGER NOT NULL DEFAULT 3,
    started_at      TEXT,
    completed_at    TEXT,
    model_used      TEXT,
    suggested_model TEXT,
    error_message   TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (project_id)    REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_task_id) REFERENCES tasks(id)    ON DELETE SET NULL
);

-- Artefactos producidos por las tareas (archivos, documentos, binarios)
CREATE TABLE IF NOT EXISTS artifacts (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id           INTEGER NOT NULL,
    project_id        INTEGER NOT NULL,
    file_path         TEXT    NOT NULL,
    file_type         TEXT    NOT NULL
                              CHECK (file_type IN ('source','asset','config','doc','report','other')),
    checksum          TEXT,
    checksum_verified INTEGER NOT NULL DEFAULT 0
                              CHECK (checksum_verified IN (0,1,2)),
                              -- 0=sin verificar, 1=verificado OK, 2=verificado con error
    verified_at       TEXT,
    metadata          TEXT,                         -- JSON con metadatos extendidos
    created_at        TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (task_id)    REFERENCES tasks(id)    ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Bitácora de ejecución: cada acción de un agente queda registrada
CREATE TABLE IF NOT EXISTS execution_logs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id    INTEGER NOT NULL,
    task_id       INTEGER,
    agent_name    TEXT    NOT NULL,
    action_type   TEXT    NOT NULL
                      CHECK (action_type IN ('workflow_start','start','tool_call','checkpoint','qa_review',
                                             'artifact_registration','handoff','finish','error',
                                             'hitl_escalation')),
    action_detail TEXT,
    outcome       TEXT    NOT NULL DEFAULT 'pending'
                          CHECK (outcome IN ('pending','success','partial','failure')),
    model_used    TEXT,
    error_message TEXT,
    duration_ms   INTEGER,
    tokens_used   INTEGER,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id)    REFERENCES tasks(id)    ON DELETE SET NULL
);

-- Puntos de control que permiten recuperación ante fallos
CREATE TABLE IF NOT EXISTS checkpoints (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id       INTEGER NOT NULL,
    task_id          INTEGER,
    agent_name       TEXT    NOT NULL,
    step_number      INTEGER NOT NULL DEFAULT 1,
    step_description TEXT,
    state_snapshot   TEXT,                          -- JSON con estado completo del paso
    is_recovery_point INTEGER NOT NULL DEFAULT 1,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id)    REFERENCES tasks(id)    ON DELETE SET NULL
);

-- Limpieza automática de checkpoints: conserva solo los últimos 10 por proyecto
CREATE TRIGGER IF NOT EXISTS trg_checkpoints_cleanup
    AFTER INSERT ON checkpoints
    FOR EACH ROW
BEGIN
    DELETE FROM checkpoints
    WHERE project_id = NEW.project_id
      AND id NOT IN (
          SELECT id FROM checkpoints
          WHERE project_id = NEW.project_id
          ORDER BY created_at DESC
          LIMIT 10
      );
END;

-- Registro de decisiones de arquitectura (ADR) con soporte FTS5
CREATE TABLE IF NOT EXISTS adrs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id      INTEGER,
    decision_id     TEXT    NOT NULL,               -- p.ej. 'ADR-001' (unico por proyecto)
    UNIQUE (project_id, decision_id),
    title           TEXT    NOT NULL,
    rationale       TEXT,
    applied_agents  TEXT,                           -- JSON array de agentes afectados
    status          TEXT    NOT NULL DEFAULT 'active'
                            CHECK (status IN ('active','superseded','deprecated')),
    fts_content     TEXT,                           -- contenido indexado para búsqueda semántica
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
);

-- Historial de feedback y correcciones aplicadas sobre errores recurrentes
CREATE TABLE IF NOT EXISTS feedback_history (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id       INTEGER NOT NULL,
    ticket_or_task_ref TEXT,
    error_type       TEXT    NOT NULL,
    correction       TEXT    NOT NULL,
    affected_agent   TEXT,
    recurrence_count INTEGER NOT NULL DEFAULT 0,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Caché de respuestas para evitar llamadas repetidas al mismo modelo/agente
CREATE TABLE IF NOT EXISTS response_cache (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_hash   TEXT    NOT NULL,
    agent_profile TEXT    NOT NULL,
    response_text TEXT    NOT NULL,
    tokens_used   INTEGER,
    model_used    TEXT,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    last_used     TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Rastreo detallado de uso de modelos (tokens, latencia, costos)
CREATE TABLE IF NOT EXISTS model_usage (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id    INTEGER,
    task_id       INTEGER,
    agent_name    TEXT    NOT NULL,
    model_name    TEXT    NOT NULL,
    model_role    TEXT    NOT NULL DEFAULT 'primary'
                        CHECK (model_role IN ('primary','fallback','backup')),
    tokens_input  INTEGER NOT NULL DEFAULT 0,
    tokens_output INTEGER NOT NULL DEFAULT 0,
    latency_ms    INTEGER,
    success       INTEGER NOT NULL DEFAULT 1
                        CHECK (success IN (0,1)),
    error_message TEXT,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
    FOREIGN KEY (task_id)    REFERENCES tasks(id)    ON DELETE SET NULL
);

-- ---------------------------------------------------------------------------
-- ÍNDICES
-- ---------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_projects_slug          ON projects(slug);
CREATE INDEX IF NOT EXISTS idx_projects_status         ON projects(status);
CREATE INDEX IF NOT EXISTS idx_tasks_project_id        ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status            ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_agent    ON tasks(assigned_agent);
CREATE INDEX IF NOT EXISTS idx_artifacts_task_id       ON artifacts(task_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_project_id    ON artifacts(project_id);
CREATE INDEX IF NOT EXISTS idx_execution_logs_project  ON execution_logs(project_id);
CREATE INDEX IF NOT EXISTS idx_execution_logs_task     ON execution_logs(task_id);
CREATE INDEX IF NOT EXISTS idx_execution_logs_agent    ON execution_logs(agent_name);
CREATE INDEX IF NOT EXISTS idx_execution_logs_outcome  ON execution_logs(outcome);
CREATE INDEX IF NOT EXISTS idx_checkpoints_project     ON checkpoints(project_id);
CREATE INDEX IF NOT EXISTS idx_adrs_decision_id        ON adrs(decision_id);
CREATE INDEX IF NOT EXISTS idx_feedback_project        ON feedback_history(project_id);
CREATE INDEX IF NOT EXISTS idx_response_cache_lookup   ON response_cache(prompt_hash, agent_profile);
CREATE INDEX IF NOT EXISTS idx_model_usage_project     ON model_usage(project_id);
CREATE INDEX IF NOT EXISTS idx_model_usage_task        ON model_usage(task_id);
CREATE INDEX IF NOT EXISTS idx_model_usage_agent       ON model_usage(agent_name);
CREATE INDEX IF NOT EXISTS idx_model_usage_model       ON model_usage(model_name);
CREATE INDEX IF NOT EXISTS idx_model_usage_created     ON model_usage(created_at);

-- ---------------------------------------------------------------------------
-- VISTAS
-- ---------------------------------------------------------------------------

-- Resumen de proyecto con métricas de tareas y porcentaje de avance
CREATE VIEW IF NOT EXISTS v_project_status AS
SELECT
    p.id,
    p.slug,
    p.name,
    p.status     AS project_status,
    COUNT(t.id)  AS total_tasks,
    SUM(CASE WHEN t.status = 'COMPLETED' THEN 1 ELSE 0 END) AS completed_tasks,
    SUM(CASE WHEN t.status = 'FAILED'    THEN 1 ELSE 0 END) AS failed_tasks,
    SUM(CASE WHEN t.status IN ('IN_PROGRESS','REVIEW','APPROVED') THEN 1 ELSE 0 END) AS in_progress_tasks,
    SUM(CASE WHEN t.status = 'READY'     THEN 1 ELSE 0 END) AS pending_tasks,
    CASE WHEN COUNT(t.id) > 0
         THEN ROUND(SUM(CASE WHEN t.status = 'COMPLETED' THEN 1 ELSE 0 END) * 100.0 / COUNT(t.id), 1)
         ELSE 0.0
    END AS progress_pct,
    MAX(t.created_at) AS last_activity
FROM projects p
LEFT JOIN tasks t ON t.project_id = p.id
GROUP BY p.id, p.slug, p.name, p.status;

-- Tareas listas para ser recogidas por el siguiente agente en el ciclo
CREATE VIEW IF NOT EXISTS v_ready_tasks AS
SELECT
    t.id,
    t.title,
    p.name   AS project_name,
    p.slug   AS project_slug,
    t.assigned_agent,
    t.priority,
    t.dependencies,
    t.created_at
FROM tasks t
JOIN projects p ON p.id = t.project_id
WHERE t.status = 'READY'
ORDER BY t.priority DESC, t.created_at ASC;

-- Último checkpoint recuperable por proyecto
CREATE VIEW IF NOT EXISTS v_last_checkpoint AS
SELECT
    c.id,
    c.project_id,
    p.slug   AS project_slug,
    c.task_id,
    c.agent_name,
    c.step_number,
    c.step_description,
    c.state_snapshot,
    c.created_at
FROM checkpoints c
JOIN projects p ON p.id = c.project_id
WHERE c.id IN (
    SELECT MAX(id)
    FROM checkpoints
    WHERE is_recovery_point = 1
    GROUP BY project_id
);

-- Artefactos con verificación de integridad fallida (checksum_verified = 2)
CREATE VIEW IF NOT EXISTS v_integrity_alerts AS
SELECT
    a.id,
    a.file_path,
    a.file_type,
    a.checksum,
    a.checksum_verified,
    a.verified_at,
    p.name AS project_name,
    t.title AS task_title
FROM artifacts a
JOIN projects p ON p.id = a.project_id
JOIN tasks    t ON t.id = a.task_id
WHERE a.checksum_verified = 2;

-- ---------------------------------------------------------------------------
-- TABLA VIRTUAL FTS5 para búsqueda semántica sobre ADRs
-- ---------------------------------------------------------------------------

CREATE VIRTUAL TABLE IF NOT EXISTS adrs_fts USING fts5(
    decision_id,
    title,
    rationale,
    applied_agents,
    fts_content,
    content=adrs,
    content_rowid=id
);

-- Triggers para mantener sincronizada la tabla FTS con adrs
CREATE TRIGGER IF NOT EXISTS adrs_ai AFTER INSERT ON adrs BEGIN
    INSERT INTO adrs_fts(rowid, decision_id, title, rationale, applied_agents, fts_content)
    VALUES (NEW.id, NEW.decision_id, NEW.title, NEW.rationale, NEW.applied_agents, NEW.fts_content);
END;

CREATE TRIGGER IF NOT EXISTS adrs_ad AFTER DELETE ON adrs BEGIN
    INSERT INTO adrs_fts(adrs_fts, rowid, decision_id, title, rationale, applied_agents, fts_content)
    VALUES ('delete', OLD.id, OLD.decision_id, OLD.title, OLD.rationale, OLD.applied_agents, OLD.fts_content);
END;

CREATE TRIGGER IF NOT EXISTS adrs_au AFTER UPDATE ON adrs BEGIN
    INSERT INTO adrs_fts(adrs_fts, rowid, decision_id, title, rationale, applied_agents, fts_content)
    VALUES ('delete', OLD.id, OLD.decision_id, OLD.title, OLD.rationale, OLD.applied_agents, OLD.fts_content);
    INSERT INTO adrs_fts(rowid, decision_id, title, rationale, applied_agents, fts_content)
    VALUES (NEW.id, NEW.decision_id, NEW.title, NEW.rationale, NEW.applied_agents, NEW.fts_content);
END;