# Orchestration Protocols

Handoff Protocols govern the geometric routing of execution control from one Antigravity persona to another (or to the human USER). Utilize this reference matrix to construct Section 4 of the `.md` profiles.

## 1. Synchronous Linear Handoff
The most robust, deterministic pattern. An agent completes its objective, logs a summary artifact, and explicitly summons the downstream agent via a trigger phrase.
- **Syntax:** `"Handoff to <Next_Agent>: <Execution Context / Summary>"`
- **Implementation:** The `Backend_Coder` finalizes the logic and outputs `"Handoff to QA_Tester: API architecture assembled, endpoints active on port 8080."`

## 2. Round-Trip Reciprocal Handoff (The Rejection Loop)
The standard protocol for QA iteration loops.
- **Syntax:** `"Handoff return to <Upstream_Agent>: <Failure Analytics>"`
- **Implementation:** The `QA_Tester` evaluates injected code, triggers a failure state, and pivots execution back upstream: `"Handoff return to Backend_Coder: Integration suite failed on Test 3. Review NullPointer Exception on payload parser."`

## 3. Broadcast Orchestration (Multicast)
An advanced variant where a primary Orchestrator dispatches multiple parallel threads to distinct specialists. Strongly discouraged unless Antigravity native concurrency mechanisms are active.
- **Syntax:** `"Handoff Broadcast: Modules defined. Summoning [Frontend_Coder, Backend_Coder] for asynchronous parallel assembly."`
- **Implementation:** Mass initialization of uncoupled components. 

## 4. Terminal Exit Node
The protocol invoked when the assembly line halts, demanding human-in-the-loop intervention or indicating total epic completion.
- **Syntax:** `"Pipeline Complete: Waiting for USER approval / notify_user."`
- **Implementation:** Executed by DevOps deployment agents or final verification proxy nodes.
