---
name: mcp-architecture
description: "Patrones de Diseño y Construcción para Servidores MCP (Model Context Protocol). Define la creación de APIs para LLMs usando Node/TypeScript o FastMCP (Python) con enfoque en la utilidad, paginación y validación de tipos Zod/Pydantic."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# MCP Server Architecture & Development (A2LT Standard)

This discrete skill is invoked when building or extending Model Context Protocol (MCP) servers. The core objective of an MCP server is to bridge the gap between LLMs and external data/services securely and efficiently.

---

## 1. Architectural Philosophy

- **Workflow Tools vs APIs:** Your primary goal isn't just to wrap an entire REST API 1:1, but to create "composed workflow tools" that minimize the LLM's cognitive load and token usage.
- **Stateless Transport:** Default to Streamable HTTP (stateless JSON) for production scale. Use `stdio` only for local, tightly-coupled sidecar dependencies.
- **Actionable Errors:** When a tool fails, the error message sent back to the LLM must contain self-correcting logic (e.g., "ID not found. Valid IDs: 1, 2. Please try again.").

---

## 2. Tool Definition & Schema Strictness

### Zod (TypeScript) / Pydantic (Python) Enforcements

Never define an MCP Tool with a loose or `any` payload. You must define strict input/output schemas. The quality of an MCP server is entirely dependent on the LLM's ability to intuitively understand the schema.

- **Descriptions are Prompts:** The description of a tool argument is literally read by the LLM as a prompt constraint. Make them exhaustive.
- **Example Constraint:**
  ```python
  # FastMCP / Python Concept
  @mcp.tool()
  def block_user(user_id: int, reason: str = Field(description="Must be 'spam', 'abuse', or 'bot'")):
      """Blocks a user and instantly revokes active sessions."""
  ```

---

## 3. High-Performance Pagination & Context

When exposing list/search endpoints to an LLM:

- **Never dump > 50 records:** The context window will overflow.
- **Enforce Limit/Offset:** All listing tools must accept pagination arguments.
- **Structured Content:** Return dense `structuredContent` (Markdown + JSON) so the LLM client engine natively parses tables or entity references.

---

## 4. MCP Evaluations (The QA Standard)

Before an MCP server is complete, you must generate an LLM-Evaluation matrix.

- Isolate 10 highly complex, read-only interrogations (e.g., "Find all users created yesterday without an active subscription and sort by LTV").
- The QA script must verify the LLM can cleanly chain the MCP tools necessary to derive the correct string answer without human intervention.
