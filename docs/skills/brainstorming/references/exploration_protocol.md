# Exploration Protocol: Requirement Extraction & Adversarial Questioning

**Purpose:** To fully understand the problem space, surface hidden assumptions, and establish unambiguous success criteria before any design work begins. This phase is driven entirely by questions—no solutions are proposed.

## 1. Contextual Inquiry

- **Check existing artifacts:** Scan project files, documentation, recent commits, and issue trackers using available tools (e.g., `file_read`, `grep`, `ls`).
- **Identify stakeholders:** Who will use/consume the output? What are their known preferences?
- **Environmental scan:** What systems, APIs, or frameworks are already in place? What are their constraints?

## 2. Phased Questioning (One at a Time)

Deliver questions sequentially. Never dump a list. Use the following taxonomy to guide your probe:

### A. Core Purpose

- “What is the primary goal this task must achieve?”
- “What problem does it solve, and for whom?”
- “Can you describe a concrete example of the desired outcome?”

### B. Constraints & Boundaries

- **Technical:** “Are there any must‑use technologies, libraries, or platforms?”
- **Temporal:** “Is there a hard deadline, or an expected time frame?”
- **Resource:** “Are there limitations on team size, budget, or third‑party services?”
- **Regulatory:** “Does this need to comply with any standards (GDPR, WCAG, etc.)?”

### C. Success Criteria

- “How will we know this task is successful? What measurable outcomes define done?”
- “What are the non‑negotiable requirements (must‑haves) versus nice‑to‑haves?”
- “What would make this a failure?”

### D. Adversarial Probing (Challenge Assumptions)

- “What could go wrong with the simplest solution you have in mind?”
- “Why might the current approach (if any) be insufficient?”
- “If we had to build this with half the resources, what would we cut?”
- “Who might oppose this change, and why?”
- “What assumptions are we making about user behavior, data volume, or system reliability?”

### E. Multiple‑Choice Probes (Cognitive Load Reduction)

- “Would you prefer a solution that prioritizes speed, maintainability, or feature completeness?”
- “Should the output be a proof‑of‑concept, a production‑ready component, or something in between?”
- “Is the integration point A, B, or C? (list options based on context)”

## 3. Domain‑Specific Exploration Templates

When the context is known, adapt the generic questions to the domain.

### Code / Architecture

- “What are the expected load patterns (concurrent users, requests per second)?”
- “Which parts of the system will interact with this component?”
- “What are the data persistence and consistency requirements?”
- “Are there existing design patterns or architectural principles we must follow?”

### Marketing Campaign

- “Who is the target audience segment?”
- “What is the primary call‑to‑action?”
- “Which channels (email, social, ads) will be used, and how do they integrate?”
- “What metrics define campaign success (CTR, conversions, brand lift)?”

### Content Creation

- “What format (blog post, video, infographic) and length?”
- “What is the core message or thesis?”
- “Which sources or data must be referenced?”
- “What tone and style guidelines apply?”

## 4. Documenting the Exploration

- As you receive answers, distill them into a concise **Problem Statement** that includes:
  - Goal
  - Key constraints
  - Success criteria
  - Open questions (if any remain)
- This statement becomes the input to the **Design Presentation Protocol**.

## 5. Transition to Design

Proceed to design only when:

- All critical questions have been answered, or
- The user explicitly agrees to proceed with the current level of understanding, acknowledging any remaining ambiguities.
