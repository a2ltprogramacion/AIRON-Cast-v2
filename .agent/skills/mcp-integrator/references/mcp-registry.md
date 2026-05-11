# MCP Registry — Curated Production-Grade Packages

## Index

1. [API Integrations](#1-api-integrations)
2. [Databases](#2-databases)
3. [Developer Tools](#3-developer-tools)
4. [File & Data Sources](#4-file--data-sources)
5. [AI & LLM Utilities](#5-ai--llm-utilities)

Load only the section relevant to the operator's request. Do NOT load the entire file into context.

---

## 1. API Integrations

| Service     | npm Package                      | Auth Type             | Notes                                       |
| ----------- | -------------------------------- | --------------------- | ------------------------------------------- |
| GitHub      | `github-mcp`                     | Personal Access Token | Read issues, PRs, repos                     |
| Slack       | `slack-mcp`                      | Bot OAuth Token       | Read/write messages, channels               |
| Linear      | `linear-mcp`                     | API Key               | Issues, projects, cycles                    |
| Notion      | `notion-mcp`                     | Integration Token     | Pages, databases                            |
| Stripe      | `stripe-mcp`                     | Secret Key            | Payments, customers (READ-ONLY recommended) |
| Jira        | `jira-mcp`                       | API Token + Email     | Issues, sprints                             |
| GoHighLevel | _(custom — use `ghl-_` skills)\* | Private API Key       | See GHL skill catalog                       |

---

## 2. Databases

| Engine     | npm Package      | Auth Type            | Notes                     |
| ---------- | ---------------- | -------------------- | ------------------------- |
| PostgreSQL | `postgresql-mcp` | `DATABASE_URL`       | Full SQL query execution  |
| MySQL      | `mysql-mcp`      | `DATABASE_URL`       | Full SQL query execution  |
| SQLite     | `sqlite-mcp`     | File path            | Local dev only            |
| MongoDB    | `mongodb-mcp`    | `MONGODB_URI`        | Document queries          |
| Redis      | `redis-mcp`      | `REDIS_URL`          | Cache inspection          |
| Supabase   | `supabase-mcp`   | `SUPABASE_URL` + key | Postgres + Auth + Storage |

**Security rule:** All database MCPs → `ENABLE_WRITE: "false"` unless operator explicitly
authorizes mutations. Document the authorization reason in a comment.

---

## 3. Developer Tools

| Tool       | npm Package      | Notes                                    |
| ---------- | ---------------- | ---------------------------------------- |
| Git        | `git-mcp`        | Local repo operations, branch management |
| Docker     | `docker-mcp`     | Container management (use with caution)  |
| Kubernetes | `kubernetes-mcp` | Cluster inspection — prod READ-ONLY      |
| ESLint     | `eslint-mcp`     | Code linting feedback                    |
| Jest       | `jest-mcp`       | Test result parsing and insight          |

---

## 4. File & Data Sources

| Source           | npm Package      | Notes                                         |
| ---------------- | ---------------- | --------------------------------------------- |
| Local Filesystem | `filesystem-mcp` | Scope with `ALLOWED_PATHS` strictly           |
| Google Drive     | `gdrive-mcp`     | OAuth — scope to specific folders             |
| AWS S3           | `s3-mcp`         | `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` |
| Cloudflare R2    | `r2-mcp`         | Compatible with S3 MCP using custom endpoint  |
| PDF Reader       | `pdf-mcp`        | Extracts text from PDF files                  |

---

## 5. AI & LLM Utilities

| Utility             | npm / pypi Package                                 | Notes                                   |
| ------------------- | -------------------------------------------------- | --------------------------------------- |
| Sequential Thinking | `@modelcontextprotocol/server-sequential-thinking` | Extended reasoning for complex problems |
| Memory              | `@modelcontextprotocol/server-memory`              | Persistent context across sessions      |
| Puppeteer           | `@modelcontextprotocol/server-puppeteer`           | Browser automation                      |
| Fetch               | `@modelcontextprotocol/server-fetch`               | HTTP requests from LLM context          |
| Brave Search        | `@modelcontextprotocol/server-brave-search`        | Web search via Brave API                |

**High-value for Antigravity:**

- `sequential-thinking` + `memory` are the most impactful for complex agent pipelines.
- `fetch` enables agents to pull live data without a dedicated skill script.
