---
name: deployment-procedures
description: "Procedimientos de Despliegue en Producción. Estrategias seguras, flujos de trabajo pre-despliegue, Rollbacks, y lineamientos de Zero-Downtime para entornos A2LT (Astro Frontend y Django Backend)."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Deployment Procedures (A2LT Standard)

This skill dictates the principles and decisions for safe production releases across the A2LT infrastructure (Astro Frontend, Django Backend). Every deployment is a risk; this skill teaches mitigation, not blind scripts.

## 1. Platform & Infrastructure Selection

A2LT enforces a decoupled deployment model.

- **Frontend (Astro JAMstack/SSR):** Vercel, Netlify, or Cloudflare Pages. Deployment is handled via Git Hooks (Auto-deploy on `main` merge).
- **Backend (Django REST Framework):** Managed VPS (DigitalOcean, Hetzner, AWS EC2). Use `gunicorn` (WSGI) or `uvicorn` (ASGI) managed by `systemd` or `supervisor`. Reverse proxy via Nginx.
- **Database:** Managed Postgres (Neon, RDS) or local Postgres on the VPS with regular automated backups.

## 2. Pre-Deployment Principles (The 4 Verification Categories)

Before typing `git push` or `ansible-playbook`, verify:

| Category         | What to Check & Why                                                                                                         |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------- |
| **Code Quality** | Linting passes (`ruff` for Python, `prettier` for Astro). No `print()` or `console.log()` left blocking production streams. |
| **Build Status** | `npm run build` succeeds locally. Django `makemigrations --check` shows no pending changes.                                 |
| **Environment**  | `.env` variables are synced in Vercel and the VPS. Secrets are rotated if compromised.                                      |
| **Safety**       | Database backup is triggered. Rollback commit hash is noted.                                                                |

## 3. Deployment Workflow Principles (The 5-Phase Process)

1. **PREPARE:** Never deploy untested code. Verify the Pre-Deployment checklist.
2. **BACKUP:** You cannot rollback if you don't save the current state. Backup the DB before running `python manage.py migrate`.
3. **DEPLOY:** Execute the push or deploy script. **Watch it happen, do not walk away.** Monitor the Vercel logging console and the VPS `journalctl -f`.
4. **VERIFY:** Trust but verify. Do not assume "Built successfully" means the app is working.
5. **CONFIRM or ROLLBACK:** Are the primary flows functional? Confirm. If there are critical errors, immediately Rollback.

## 4. Post-Deployment Verification

Once the deploy script finishes, manually or automatically check:

- **Health Endpoint:** Does `/api/health/` return 200 OK?
- **Error Logs:** Check Sentry or Nginx `error.log` for immediate tracebacks.
- **Key User Flows:** Can a user log in? Can a transaction be created?
- **Verification Window:**
  - _First 5 mins:_ Active monitoring.
  - _15 mins:_ Confirm stable.
  - _1 hour:_ Final check.

## 5. Rollback Principles (Speed over Perfection)

If the service goes down or degrades >50%, **Rollback immediately**. Do not attempt to debug live on production.

| Platform                   | Rollback Method                                                                                                                                                                             |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Vercel/Netlify (Astro)** | Use the Dashboard to "Promote" the previous successful build back to production.                                                                                                            |
| **VPS (Django)**           | `git revert HEAD` and push, or manually `git checkout <previous_commit_hash>` on the server, reload Gunicorn.                                                                               |
| **Database**               | _Warning:_ Rolling back code doesn't roll back the DB. If a migration broke production, you must run `python manage.py migrate app_name <previous_migration>` BEFORE rolling back the code. |

1. Speed over perfection.
2. Don't compound errors by making hotfixes on the fly.
3. Communicate the outage to the team.

## 6. Zero-Downtime Deployment Strategies

For high-traffic applications, dropping connections during a Gunicorn restart is unacceptable.

- **Blue-Green Deployment:** Spin up a new VPS (Green), deploy the new Django code, point the Nginx load balancer from Blue to Green. Fast rollback (switch back to Blue).
- **Rolling Restarts (Gunicorn):** Use `kill -HUP <gunicorn_master_pid>`. This gracefully spawns new workers with the updated code while old workers finish their requests.

## 7. Emergency Procedures (The Service is DOWN)

Priority order when an alert fires:

1. **Assess:** What is the symptom? (502 Bad Gateway vs 500 Server Error).
2. **Quick Fix:** Restart Gunicorn/Uvicorn if a memory leak killed the process.
3. **Rollback:** If restarting doesn't cure it, rollback the deployment.
4. **Investigate (Order):**
   - Logs (Django tracebacks)
   - Resources (`htop` for OOM kills, `df -h` for full disks preventing DB writes).
   - Network (Firewalls, Cloudflare Cache)
   - Dependencies (Is the Postgres server down?)

## 8. Anti-Patterns

- ❌ Deploying on Friday at 5:00 PM.
- ❌ Rushing a deployment "because it's just a text change".
- ❌ Skipping the Staging environment test.
- ❌ Walking away immediately after the Vercel build turns green.
- ❌ Applying 5 different infrastructure changes in one deployment.

## 9. Decision Checklist Before Release

- [ ] Is this the appropriate deployment procedure for the platform?
- [ ] Is the database backed up?
- [ ] Is the rollback plan documented and communicated?
- [ ] Do I have 15 free minutes right now to monitor the metrics post-deploy?

## 10. Best Practices

1. **Small, frequent deploys** are fundamentally safer than massive monthly releases.
2. Use **Feature Flags** (e.g., Django Waffle) to deploy risky code turned off, and turn it on without redeploying.
3. Automate repetitive SSH commands with Ansible or bash scripts (`setup.sh`).
4. Conduct blameless post-mortems after an outage to understand the _Why_.
