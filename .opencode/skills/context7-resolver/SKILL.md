---
name: context7-resolver
version: 1.0.0
type: utility
subtype: skill
tier: all
description: |
  Integrates the context7 MCP server for searching updated documentation
  and real code examples. Activate when working with third-party libraries
  (Astro, Tailwind, Alpine.js, etc.), when encountering obsolete code or
  model hallucinations, or when the operator requests documentation lookup.
  Trigger phrases: "busca documentación", "resuelve contexto de la librería",
  "cómo se usa la API de", "find docs context7".
  Do NOT activate for standard Python modules or basic HTML5.
triggers:
  primary: ["docs en context7", "verifica la api de", "cómo usar la librería"]
  secondary: ["resuelve contexto código", "ejemplos de código actualizados"]
  context: ["dependencia externa nueva", "evitar alucinaciones", "code gen"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - orchestrator
  - requirements_architect
  - ux-ui_specialist
  - frontend_worker
  - qa_auditor
  - meta_factory
last_used: null
scope: restricted
---

# Context7 Resolver — Instant Documentation Extractor

**Role:** You are the dedicated liaison with the `context7` MCP server.
Your objective is to ensure that all code generated in AIRON‑Cast for
third-party libraries (Astro, Tailwind, Alpine.js, SDKs) is based on
the most recent official documentation, eliminating structural
hallucinations.

This is a **High Freedom** skill. It does not contain external scripts
since the orchestrator has native access to the `context7` MCP server
tools. Its purpose is to dictate the *doctrine* for using these tools
within AIRON‑Cast.

---

## 0. MCP Availability Check (Pre-Flight)

**Objective:** Ensure the Context7 MCP server is installed and available
before attempting any query. Without it, the skill cannot function.

1. **Verify availability:** Attempt to list available MCP tools. Check
   if `resolve-library-id` and `query-docs` are present in the MCP
   server tools.
2. **If NOT available:**
   - Halt execution immediately.
   - Output the following message to the operator:

     ```
     [CONTEXT7 UNAVAILABLE]: The Context7 MCP server is not installed or
     not configured. Please install it by following the instructions at
     https://context7.com/docs/resources/all-clients
     ```

   - Do NOT attempt to use Context7 until the operator confirms the
     MCP server is running.
3. **If available:** Proceed to the operating flow below.

> **Note:** If you are using an IDE with automatic Context7 rules
> (e.g., Gemini with `GEMINI.md`), the MCP server may already be
> configured to inject documentation automatically. The verification
> step confirms this integration is active.

---

## 1. When to Activate (Trigger Conditions)

You must routinely invoke this skill during:
- **Code Generation:** If the component to be generated imports tools,
  libraries, or SDKs that you do not master 100% in their most current
  declared version.
- **API Error Troubleshooting:** When a pre-existing function breaks due
  to a TypeError or deprecation ("Module not found", "Property does not
  exist on type").
- **Explicit operator request:** When requested to review "how it's done
  in the latest version" of a utility.

---

## 2. Mandatory Operating Flow (MCP Usage)

To obtain the necessary information from context7, you must always
execute this strict 2-step sequence:

### Step 1: `resolve-library-id`
**Objective:** Obtain the official ID recognized by context7. NEVER
assume the ID of a library.
1. Make a call to the MCP tool `resolve-library-id`.
2. Provide:
   - `libraryName`: General name of the library (e.g., "Astro",
     "TailwindCSS", "Alpine.js").
   - `query`: What you are trying to do (e.g., "How to use
     ViewTransitions", "Theming configuration").
3. Receive the list of results. Evaluate the reputation score, snippet
   coverage, and select the most precise ID (in `/org/project` or
   `/org/project/version` format).

### Step 2: `query-docs`
**Objective:** Extract the technical specification.
1. Use the ID obtained in the previous step.
2. Make a call to `query-docs`.
3. Provide:
   - `libraryId`: The exact retrieved ID (`/vercel/next.js`).
   - `query`: Your highly specific question. Be concrete.
     - *BAD:* "auth"
     - *GOOD:* "How to implement JWT authentication and refresh
       tokens at the edge with middleware".
4. **Critical Restriction:** If you do not find the answer, you can
   call this tool up to a maximum of **3 times per question session**
   by rephrasing the query. After that, operate with the best
   available information.

---

## 3. Code Injection Protocol (Anti-Hallucinations)

Once the response from context7 is obtained:
1. **Incompatibility Audit:** Compare the pattern returned by context7
   against the AIRON‑Cast base stack (Astro + Tailwind + Alpine.js for
   Fase 1). If `query-docs` returns code for a different framework,
   logically transpile the architecture to the target environment. Do
   not copy and paste blindly.
2. **Implementation:** When injecting the code into your artifact or
   document, include a brief comment indicating that this pattern is
   based on dynamically obtained context7 specifications:
   `// Implementation validated via context7 (Latest version)`

---

## 4. Limitations and Warnings

- **Security:** NEVER send passwords, API keys, or private tokens
  within the `query` parameter to `context7`. It is an external network.
- **Redundancy:** Avoid resorting to context7 for standard Python
  native components (`os`, `json`, `datetime`) or basic HTML5 tags
  unless it's an edge case.
- **Operational Silence:** When using this skill during a Core Flow
  (e.g., Code Gen), it is not necessary to announce it in detail to
  the operator. Simply obtain the data and write the resulting code.

---

## 🔗 AIRON‑Cast Integration

This skill is consumed by all agents in the ecosystem:
- `requirements_architect` — to validate stack choices against current docs.
- `ux-ui_specialist` — to verify Tailwind/Alpine.js patterns.
- `frontend_worker` — to ensure Astro component APIs are up to date.
- `qa_auditor` — to cross-reference errors against official documentation.
- `meta_factory` — to research libraries when creating new skills.
- `orchestrator` — to inject context into agent prompts when external
  dependencies are detected.