# Project Backlog — Banesco Credit Card Tracker MVP

| ID | Task Description | Assigned Agent | Priority | Dependencies | Status |
|---|---|---|---|---|---|
| T31 | Generar REQUIREMENTS.md y BACKLOG.md | `requirements_architect` | 1 | None | COMPLETED |
| T32 | Definir design tokens y especificaciones visuales (Dark Mode Premium) | `ux-ui_specialist` | 2 | T31 | COMPLETED |
| T33 | Optimizar Dashboard y vistas de Django con Tailwind CSS | `frontend_worker` | 3 | T32 | COMPLETED |
| T34 | Ejecutar suite de pruebas y emitir reporte de auditoría QA | `qa_auditor` | 4 | T31 | COMPLETED |
| T35 | Implementar exportación de reportes financieros en PDF/Excel | `backend_specialist` | 5 | T31 | PENDING |
| T36 | Refactorizar motor de scraping de Binance P2P para mejorar resiliencia | `backend_specialist` | 6 | T31 | COMPLETED |
| T37 | Implementar sistema de alertas por correo/notificación para fechas de corte | `backend_specialist` | 7 | T31 | PENDING |

## Notas de Implementacion T36

- Nueva clase `BinanceP2PService` con cadena de fallback en 4 niveles: curl_cffi -> httpx -> requests -> urllib
- Nueva clase `ProxyPool` con health checking y failover parcial
- Dependencias agregadas: `curl_cffi>=0.6.0`, `httpx>=0.27.0`, `requests>=2.32.0`
- 11 tests nuevos para la cadena de fallback y ProxyPool
