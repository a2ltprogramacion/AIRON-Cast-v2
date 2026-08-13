# Report Structure Reference — AIRON‑Cast Journal

## Sections in a Pattern Report

1. **Header** — batch number, generation date, entry count, date range  
2. **Tareas del Batch** — agent activity count, list of completed tasks  
3. **Análisis de Problemas** — count by severity and recurrence risk, flagged high‑recurrence items  
4. **Decisiones Arquitectónicas (ADRs)** — all ADRs with status (accepted/superseded/deprecated)  
5. **Patrones Detectados** — new patterns registered in this batch  
6. **Field Feedback** — average operator rating, list with individual ratings  
7. **Recomendaciones para el Ecosistema** — auto‑generated from data: high‑recurrence problems, low‑rated field deployments, patterns that could become skills  

## Report Naming Convention

`[YYYYMMDD]_pattern-report_batch-[N].md`  
N = `total_tasks` value at time of generation.

## When Reports Are Generated

Automatically when `total_tasks - last_report_at >= report_threshold`.  
Default threshold: 10 tasks. Configurable in `.task-counter.json`.

## Reading a Report

The Recommendations section is the most actionable part.  
Cross‑reference flagged components against `manifest.json` to prioritize improvements.