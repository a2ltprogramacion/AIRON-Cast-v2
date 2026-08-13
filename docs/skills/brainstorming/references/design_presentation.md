# Design Presentation & Documentation Protocol

**Purpose:** To translate exploration insights into a structured design, present it incrementally for validation, and obtain explicit approval before implementation. This phase ensures that all stakeholders agree on what will be built and how.

## 1. Design Document Structure

Create a Markdown document (typically `design_doc.md` in the project root or a `docs/` folder). Scale sections according to task complexity, but always include the following core sections:

```
# Design: [Title]

## 1. Overview
- Problem statement (from exploration)
- Goals and non‑goals
- Key stakeholders

## 2. Requirements
- Functional requirements (must‑haves)
- Non‑functional requirements (performance, security, scalability)
- Constraints (technical, temporal, resource)

## 3. Proposed Approach
- Brief description of the recommended solution
- Why this approach fits the constraints and goals

## 4. Alternatives Considered
- 2–3 alternative approaches, each with:
  - Summary
  - Pros / cons
  - Why they were not selected

## 5. Detailed Design
- Architecture diagram (ASCII or reference to image)
- Data flow / control flow
- Component interactions
- Key algorithms or logic
- API definitions (if applicable)
- Database schema changes (if applicable)

## 6. Error Handling & Edge Cases
- How the system behaves under failure scenarios
- Specific edge cases and their handling
- Logging, monitoring, and alerting considerations

## 7. Testing Strategy
- Unit, integration, and end‑to‑end tests
- Performance/load testing (if needed)
- Acceptance criteria mapping

## 8. Implementation Plan
- Step‑by‑step breakdown (phases or milestones)
- Dependencies and prerequisites
- Estimated effort (optional)

## 9. Open Questions
- Any unresolved items that need decision before or during implementation

## 10. Approval
- Placeholder for user sign‑off (e.g., “Approved by [User] on [Date]”)
```

## 2. Presentation Technique

- **Walk through the document section by section.** Do not present everything at once.
- After each major section (Overview, Requirements, Proposed Approach, etc.), ask a validation question:
  - “Does this align with your understanding?”
  - “Are there any missing requirements or constraints?”
  - “Does the proposed approach feel appropriate so far?”
- If the user raises concerns, **stop** and clarify. Update the design document inline, then continue.
- Use multiple‑choice questions to narrow down options (e.g., “Should the caching layer be Redis, Memcached, or none?”).

## 3. Alternatives Analysis

For the **Alternatives Considered** section, present at least two distinct approaches (including the recommended one). For each, discuss:

- **Trade‑offs:** complexity, time, maintainability, performance, cost.
- **Why the recommended approach is optimal** given the exploration constraints.
- **If the user disagrees**, be prepared to swap the recommendation or merge ideas.

## 4. YAGNI Enforcement

- Actively strip any feature or component that does not directly support the requirements.
- If a requirement is marked as “nice‑to‑have,” move it to a future iteration section or remove it entirely.
- Ask: “Is this absolutely necessary for the first deliverable?” If not, cut it.

## 5. Incremental Validation & Sign‑Off

- After walking through the entire document, ask for explicit approval:  
  “Do you approve this design as the basis for implementation?”
- The user may approve, request changes, or reject.
- If changes are requested, update the design and re‑present the affected sections.
- Once approved, **mark the document with the approval date and user’s name**.

## 6. Documentation Artifact

- Save the final design document in a well‑known location (e.g., `designs/`, `docs/`, or project root).
- Ensure it is committed to version control (if applicable) and linked from any relevant tickets or READMEs.
- This artifact becomes the single source of truth for the implementation phase.

## 7. Transition to Implementation

- After approval, you may invoke implementation‑specific skills (e.g., coding, content generation).
- During implementation, refer back to the design document to ensure fidelity.
- If significant deviations become necessary, **pause** and either update the design (with re‑approval) or create a new design for the changes.

## 8. Common Pitfalls & Mitigations

- **Skipping sections because “it’s simple”** – Even for a one‑line change, a minimal design (Overview, Requirements, Proposed Approach) is required.
- **Presenting without validation** – Always ask after each section; silence is not consent.
- **Over‑engineering** – YAGNI is your guard. If a feature isn’t required, it doesn’t belong.
- **Approval without reading** – Gently insist that the user reviews each section; note that approval implies agreement.
