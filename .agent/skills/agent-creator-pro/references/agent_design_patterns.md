# Agent Design Patterns

A guide for selecting the correct behavioral architecture when forging new agent profiles in `.agent/agents/`.

## 1. Pure Executor
**Target Use Case:** Atomic, high-friction, or highly repetitive tasks.
**Behavior:**
- Makes zero architectural decisions.
- Ingests structured input, applies a deterministic transformation, yields output.
**Examples:**
- `PDF_Rotator` (Ingests file -> Rotates -> Outputs).
- `Log_Parser` (Ingests raw text -> Extracts Regex -> Outputs JSON).

## 2. Gatekeeper (Validator)
**Target Use Case:** Quality Assurance (QA), Security Auditing, PR Approvals.
**Behavior:**
- Acts as a conditional bottleneck in the Orchestration Handoff.
- Handoff Phrase bifurcates: Approval (Pass to downstream worker) or Rejection (Return artifact to upstream worker).
**Examples:**
- `Schema_Validator` (Reviews SQL migration -> Approves/Rejects).
- `SecurityOps` (Reviews delta code -> Rejects dynamically if vulnerability detected).

## 3. Transformer / Refactorer
**Target Use Case:** Version upgrades, dialect translation, Technical Debt resolution.
**Behavior:**
- Strips presentation from logic. Does not mutate business rules; exclusively mutates the underlying syntactic structure.
**Examples:**
- `Python2_To_3_Upgrader`
- `Tailwind_Migrator`

## 4. Orchestrator (Planner / Dispatcher)
**Target Use Case:** Massive epics requiring sub-task decomposition.
**Behavior:**
- Rarely executes mutating terminal commands (`mkdir`, `touch`, `sed`).
- Primary objective is generating execution matrix lists (`task.md`) and invoking Handoffs to Executor agents. Functions as "The Manager".
**Examples:**
- `Project_Lead`
- `Sprint_Planner`

## 5. Proxy Node (User Interface)
**Target Use Case:** Interfacing with humans (USER) or unpredictable external dependencies.
**Behavior:**
- Translates unstructured "Business Speak" from the USER into structured "Tech Speak" for technical agents, and vice versa.
- Exclusively utilizes the `notify_user` protocol as its continuous Handoff mechanism.
**Examples:**
- `Requirements_Analyst`
- `Documentation_Writer` (Documents code and pauses execution to prompt USER for final sign-off).
