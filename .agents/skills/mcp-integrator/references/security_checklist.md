# MCP Security Checklist

Run through this checklist before declaring any MCP integration complete.

## Pre-Integration

- [ ] Package exists on npm/PyPI and was published within the last 6 months
- [ ] Package has >100 weekly downloads (or is from a trusted org like `@modelcontextprotocol/`)
- [ ] LICENSE is compatible (MIT, Apache 2.0, or similar permissive)

## Configuration Security

- [ ] ZERO secrets hardcoded in `"args"` array
- [ ] ALL secrets loaded from `"env"` block (which maps to `.env` — never committed)
- [ ] API keys are scoped to minimum permissions required (read-only if possible)
- [ ] `ALLOWED_PATHS` is restricted to specific project directories (file system MCPs)
- [ ] `ENABLE_WRITE` is `"false"` unless write access is explicitly justified

## Network & Rate Limiting

- [ ] `TIMEOUT` defined (recommended: 30000ms for most APIs)
- [ ] `RETRY_ATTEMPTS` defined (recommended: 3 max)
- [ ] Rate limit params configured if the service enforces them

## Post-Integration Validation

- [ ] MCP server starts without errors (manual test with `npx -y package-name --help`)
- [ ] Operator confirmed credentials are valid
- [ ] `.mcp.json` added to `.gitignore` if it contains env references
- [ ] `.env.template` updated with the new required variables documented
