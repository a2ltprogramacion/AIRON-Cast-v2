-- =============================================================================
-- AIRON-Cast: Blacksmithing Development Framework
-- Artificial Intelligence Reinforced Orchestration Network
-- Schema Principal: airon.sqlite
-- Versión: 1.0.0
-- =============================================================================

PRAGMA journal_mode = WAL;       -- Escritura concurrente segura
PRAGMA foreign_keys = ON;        -- Integridad referencial obligatoria
PRAGMA synchronous = NORMAL;     -- Balance entre seguridad y rendimiento

-- =============================================================================
-- BLOQUE 1: PROYECTOS
-- Registro central de todos los proyectos gestionados por AIRON-Cast
-- =============================================================================

CREATE TABLE IF NOT EXISTS projects (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    slug                TEXT NOT NULL UNIQUE,               -- erp-pos-core, web-site-authority
    name                TEXT NOT NULL,                      -- Nombre legible del proyecto
    client              TEXT DEFAULT 'interno',             -- Cliente o 'interno' para propios
    project_type        TEXT NOT NULL CHECK(project_type IN (
                            'web-design',
                            'web-app',
                            'desktop-app',
                            'mobile-app',
                            'ghl-admin',
                            'ghl-bot',
                            'ghl-snapshot',
                            'erp-module',
                            'custom'
                        )),
    active_workflow     TEXT NOT NULL,                      -- Referencia: workflows/web-dev.md
    root_path           TEXT NOT NULL,                      -- output/erp-pos-core/
    status              TEXT NOT NULL CHECK(status IN (
                            'DRAFT',
                            'ACTIVE',
                            'PAUSED',
                            'REVIEW',
                            'COMPLETED',
                            'ARCHIVED'
                        )) DEFAULT 'DRAFT',
    priority            INTEGER DEFAULT 5 CHECK(priority BETWEEN 1 AND 10),
    notes               TEXT,                               -- Notas libres del proyecto
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Trigger: actualiza updated_at automáticamente en cada modificación
CREATE TRIGGER IF NOT EXISTS projects_updated_at
    AFTER UPDATE ON projects
    FOR EACH ROW
BEGIN
    UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- =============================================================================
-- BLOQUE 2: MÁQUINA DE ESTADOS DE TAREAS
-- Candado de secuencia: ninguna tarea avanza sin autorización explícita
-- =============================================================================

CREATE TABLE IF NOT EXISTS tasks (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id          INTEGER NOT NULL,
    parent_task_id      INTEGER DEFAULT NULL,               -- Para sub-tareas
    title               TEXT NOT NULL,
    description         TEXT,
    assigned_agent      TEXT NOT NULL,                      -- strategist, frontend, backend, qa
    priority            INTEGER DEFAULT 5 CHECK(priority BETWEEN 1 AND 10),
    status              TEXT NOT NULL CHECK(status IN (
                            'LOCKED',                       -- Bloqueada por dependencias
                            'READY',                        -- Lista para ejecutar
                            'IN_PROGRESS',                  -- Agente trabajando
                            'REVIEW',                       -- Esperando revisión humana
                            'APPROVED',                     -- Revisión aprobada
                            'COMPLETED',                    -- Finalizada y validada
                            'FAILED',                       -- Falló después de 3 reintentos
                            'SKIPPED'                       -- Omitida con justificación
                        )) DEFAULT 'LOCKED',
    dependencies        TEXT DEFAULT '[]',                  -- JSON array de task IDs requeridos
    retry_count         INTEGER DEFAULT 0,
    max_retries         INTEGER DEFAULT 3,
    model_used          TEXT,                               -- gemini-flash, gemini-pro, claude-sonnet
    suggested_model     TEXT,                               -- Modelo sugerido (switch manual)
    estimated_tokens    INTEGER,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at          DATETIME,
    completed_at        DATETIME,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_task_id) REFERENCES tasks(id)
);

-- Índice para consultas frecuentes por proyecto y estado
CREATE INDEX IF NOT EXISTS idx_tasks_project_status
    ON tasks(project_id, status);

CREATE INDEX IF NOT EXISTS idx_tasks_agent
    ON tasks(assigned_agent, status);

-- =============================================================================
-- BLOQUE 3: ARTEFACTOS
-- Registro de todo archivo generado — evita código huérfano
-- =============================================================================

CREATE TABLE IF NOT EXISTS artifacts (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id             INTEGER NOT NULL,
    project_id          INTEGER NOT NULL,
    file_path           TEXT NOT NULL,                      -- Ruta relativa desde root del proyecto
    file_type           TEXT NOT NULL CHECK(file_type IN (
                            'source',                       -- Código fuente
                            'config',                       -- Archivos de configuración
                            'test',                         -- Tests automatizados
                            'doc',                          -- Documentación
                            'asset',                        -- Imágenes, fuentes, etc.
                            'spec',                         -- Especificaciones
                            'migration',                    -- Migraciones de DB
                            'other'
                        )),
    checksum            TEXT,                               -- SHA256 del archivo al generarse
    checksum_verified   INTEGER DEFAULT 0,                  -- 0=pendiente, 1=ok, 2=alterado
    metadata            TEXT DEFAULT '{}',                  -- JSON: specs técnicas aplicadas
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    verified_at         DATETIME,
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_artifacts_project
    ON artifacts(project_id);

CREATE INDEX IF NOT EXISTS idx_artifacts_checksum
    ON artifacts(checksum_verified);

-- =============================================================================
-- BLOQUE 4: CHECKPOINTS
-- Recuperación ante fallos — escribe ANTES de ejecutar cada paso
-- =============================================================================

CREATE TABLE IF NOT EXISTS checkpoints (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id          INTEGER NOT NULL,
    task_id             INTEGER NOT NULL,
    agent_name          TEXT NOT NULL,
    step_number         INTEGER NOT NULL,                   -- Paso dentro de la tarea
    step_description    TEXT,                               -- Qué se iba a hacer en este paso
    state_snapshot      TEXT NOT NULL,                      -- JSON completo del state.json
    is_recovery_point   INTEGER DEFAULT 1,                  -- 1=puede restaurarse desde aquí
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- Solo conservar los últimos 10 checkpoints por proyecto (limpieza automática)
CREATE TRIGGER IF NOT EXISTS checkpoints_cleanup
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

-- =============================================================================
-- BLOQUE 5: LOGS DE EJECUCIÓN
-- Auditoría completa — qué hizo cada agente, cuándo y con qué resultado
-- =============================================================================

CREATE TABLE IF NOT EXISTS execution_logs (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id          INTEGER NOT NULL,
    task_id             INTEGER,
    agent_name          TEXT NOT NULL,
    action_type         TEXT NOT NULL CHECK(action_type IN (
                            'TASK_START',
                            'TASK_COMPLETE',
                            'TASK_FAIL',
                            'TASK_RETRY',
                            'CHECKPOINT_WRITE',
                            'ARTIFACT_CREATE',
                            'ARTIFACT_VERIFY',
                            'HITL_ESCALATION',           -- Escalación a revisión humana
                            'WORKFLOW_START',
                            'WORKFLOW_COMPLETE',
                            'MCP_CALL',                  -- Llamada a servidor MCP
                            'MODEL_SWITCH',              -- Cambio de modelo IA
                            'ERROR'
                        )),
    action_detail       TEXT,                               -- Descripción legible
    outcome             TEXT CHECK(outcome IN (
                            'SUCCESS',
                            'FAILURE',
                            'PENDING',
                            'SKIPPED'
                        )),
    model_used          TEXT,
    error_message       TEXT,
    duration_ms         INTEGER,                            -- Duración en milisegundos
    tokens_used         INTEGER,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

CREATE INDEX IF NOT EXISTS idx_logs_project
    ON execution_logs(project_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_logs_action_type
    ON execution_logs(action_type, outcome);

-- =============================================================================
-- BLOQUE 6: HISTORIAL DE MODELOS IA
-- Control de qué modelo se usó en cada decisión crítica
-- =============================================================================

CREATE TABLE IF NOT EXISTS model_usage (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id             INTEGER NOT NULL,
    model_name          TEXT NOT NULL,                      -- gemini-flash, gemini-pro, claude-sonnet
    model_role          TEXT NOT NULL CHECK(model_role IN (
                            'execution',                    -- Tarea principal
                            'review',                       -- Revisión de output
                            'validation',                   -- Validación técnica
                            'fallback'                      -- Reintento con otro modelo
                        )),
    tokens_input        INTEGER,
    tokens_output       INTEGER,
    latency_ms          INTEGER,
    success             INTEGER DEFAULT 1,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- =============================================================================
-- BLOQUE 7: VISTAS DE CONSULTA RÁPIDA
-- Panel de control sin escribir SQL complejo
-- =============================================================================

-- Vista: Estado actual de todos los proyectos activos
CREATE VIEW IF NOT EXISTS v_project_status AS
SELECT
    p.slug,
    p.name,
    p.client,
    p.project_type,
    p.status AS project_status,
    p.active_workflow,
    COUNT(t.id)                                         AS total_tasks,
    SUM(CASE WHEN t.status = 'COMPLETED' THEN 1 END)   AS completed,
    SUM(CASE WHEN t.status = 'IN_PROGRESS' THEN 1 END) AS in_progress,
    SUM(CASE WHEN t.status = 'LOCKED' THEN 1 END)      AS locked,
    SUM(CASE WHEN t.status = 'FAILED' THEN 1 END)      AS failed,
    ROUND(
        100.0 * SUM(CASE WHEN t.status = 'COMPLETED' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(t.id), 0), 1
    )                                                   AS progress_pct,
    p.updated_at
FROM projects p
LEFT JOIN tasks t ON t.project_id = p.id
WHERE p.status NOT IN ('ARCHIVED')
GROUP BY p.id
ORDER BY p.priority DESC, p.updated_at DESC;

-- Vista: Tareas listas para ejecutar (READY sin dependencias pendientes)
CREATE VIEW IF NOT EXISTS v_ready_tasks AS
SELECT
    t.id,
    p.slug          AS project,
    t.title,
    t.assigned_agent,
    t.priority,
    t.retry_count,
    t.created_at
FROM tasks t
JOIN projects p ON p.id = t.project_id
WHERE t.status = 'READY'
ORDER BY t.priority DESC, t.created_at ASC;

-- Vista: Último checkpoint recuperable por proyecto
CREATE VIEW IF NOT EXISTS v_last_checkpoint AS
SELECT
    c.project_id,
    p.slug          AS project,
    c.task_id,
    c.agent_name,
    c.step_number,
    c.step_description,
    c.state_snapshot,
    c.created_at    AS checkpoint_time
FROM checkpoints c
JOIN projects p ON p.id = c.project_id
WHERE c.is_recovery_point = 1
  AND c.id = (
      SELECT MAX(id) FROM checkpoints
      WHERE project_id = c.project_id
        AND is_recovery_point = 1
  );

-- Vista: Artefactos con checksum alterado (integridad comprometida)
CREATE VIEW IF NOT EXISTS v_integrity_alerts AS
SELECT
    a.file_path,
    p.slug          AS project,
    t.title         AS from_task,
    a.checksum,
    a.verified_at
FROM artifacts a
JOIN projects p ON p.id = a.project_id
JOIN tasks t ON t.id = a.task_id
WHERE a.checksum_verified = 2;

-- =============================================================================
-- BLOQUE 8: DATOS INICIALES
-- Configuración base del sistema
-- =============================================================================

-- Registro del sistema AIRON-Cast como proyecto interno
INSERT OR IGNORE INTO projects (slug, name, client, project_type, active_workflow, root_path, status, priority)
VALUES ('airon-cast', 'AIRON-Cast Framework', 'interno', 'custom', 'workflows/system.md', './', 'ACTIVE', 10);
