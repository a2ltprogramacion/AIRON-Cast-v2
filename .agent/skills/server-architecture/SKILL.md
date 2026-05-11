---
name: server-architecture
description: "Ingeniería de Operaciones de Servidores A2LT. Establece la política estricta de reinicio cero-downtime (PM2 / Systemd), y la evaluación del uso de RAM o CPU antes del particionado horizontal."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Server Architecture Operations (A2LT Standard)

This discrete skill directs the agent on how to diagnose, monitor, and scale production environments securely without blindly restarting services and dropping live connections.

---

## 1. Process Management Doctrine

- **Node.js Ecosystem:** Use `PM2` for clustering. Never execute raw `node index.js`. Require zero-downtime reloads (`pm2 reload app`).
- **Python / Django / System Services:** Use `systemd` alongside `gunicorn`.
- **Health Checks:** A server is not healthy just because the process is running. Verification requires checking Database connectivity and Resource (RAM) availability.

## 2. Telemetry and Log Analysis

- **Blind Restarts are Forbidden:** Before restarting a failing service, the agent MUST inspect the error logs (`tail -n 100`) and the memory spikes (`htop` / `top`).
- **Structured Logging:** Enforce JSON structured logs for production. Never allow sensitive PII / JWT tokens to be written into access logs.

## 3. Scaling Heuristics

If asked to solve a performance drop:

- Measure CPU/RAM usage.
- If CPU hits 100%, consider adding instances (Horizontal Scaling).
- If responses are slow but resources are low, **DO NOT SCALE**. The bottleneck is the Database (missing indexes or locks). Profile the DB first.
