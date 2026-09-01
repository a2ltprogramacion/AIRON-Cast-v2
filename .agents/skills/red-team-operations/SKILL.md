---
name: red-team-operations
description: "Ingeniería de Red Team A2LT (Basado en MITRE ATT&CK). Define los límites éticos y estructurales para simular ataques, enumeración, evasión de defensas y movimiento lateral auditado."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Red Team Tactics & Auditing (A2LT Standard)

This isolated skill serves as a blueprint for conducting offensive security operations conceptually or mechanically in a safe, documented manner following the MITRE ATT&CK phases.

---

## 1. Objective and Ethical Standard

- **Zero Destruction:** Red Team simulates attackers to uncover blind spots. Never execute an exploit that inherently runs a Denial of Service (DoS) or drops production databases.
- **Reporting Over Execution:** The ultimate goal is the Audit Trail. Uncovering a vulnerability but failing to report _why the defense failed_ renders the operation useless.

## 2. Reconnaissance & Initial Access

- Differentiate heavily between Active (port scanning, touching the target) and Passive (OSINT, DNS records) reconnaissance.
- Identify the most lethal, yet common vectors: Phishing surfaces, Exposed public exploits, and Supply Chain leaks (`.env` commits).

## 3. Escalation and Evasion Framework

If executing an escalation audit:

- **Windows:** Check Unquoted Service Paths, weak service permissions, and stored local credentials.
- **Linux:** Enumerate SUID binaries, misconfigured `sudoers` (NOPASSWD), and writable scheduled `cron` jobs.
- **Evasion Mechanics:** Use LOLBins (Living Off The Land Binaries)—legitimate system tools like `certutil` or `powershell`—to execute code and blend in with normal network noise.

## 4. Immediate Termination Rule

If at any point a real threat or actively exploited vulnerability belonging to an external actor is uncovered, the simulation stops immediately and converts into an Incident Response escalation.
