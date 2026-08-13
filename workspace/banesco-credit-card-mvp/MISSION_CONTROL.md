# Mission Control — Banesco Credit Card Tracker MVP

**Proyecto:** banesco-credit-card-mvp
**Operador:** Argenis @ A2LT Soluciones
**Estado:** ACTIVE
**Ultima Actualizacion:** 2026-06-09

---

## Historial de Ejecucion AIRON-Cast

| Tarea | Agente | Estado | Artefactos |
|---|---|---|---|
| T31: Generar REQUIREMENTS.md y BACKLOG.md | `requirements_architect` | COMPLETED | `REQUIREMENTS.md`, `BACKLOG.md` |
| T32: Definir design tokens y especificaciones visuales | `ux-ui_specialist` | COMPLETED | `src/styles/design-tokens.json`, `src/styles/component-specs.md` |
| T33: Optimizar Dashboard y vistas de Django con Tailwind CSS | `frontend_worker` | COMPLETED | `src/templates/base.html` (mobile navbar + Alpine.js) |
| T34: Ejecutar suite de pruebas y emitir reporte de auditoria QA | `qa_auditor` | COMPLETED | `reports/test_report.md` (38/38 tests OK) |
| T36: Refactorizar motor Binance P2P con cadena de fallback resiliente | `backend_specialist` | COMPLETED | `services.py` refactorizado, 11 tests nuevos (49 total OK) |
| T38: Reconciliacion completa MC + Pago Minimo | `backend_specialist` | COMPLETED | journal/entries/20260609-160000_session_reconciliacion-mc-pago-minimo.md |

---

## Arquitectura del Sistema

### Stack Tecnico
- **Backend:** Python 3.10+ / Django 5.x
- **Database:** SQLite (`src/db.sqlite3`) - Independiente de AIRON-Cast
- **Frontend:** Django Templates + Tailwind CSS + Alpine.js
- **APIs Externas:** DolarAPI (BCV), Binance P2P (scraping)

### Modelos de Datos
- `CreditCard` - Tarjetas de credito/debito con parametros financieros
- `BankAccount` - Cuentas bancarias con saldo contable y proyectado
- `Transaction` - Transacciones de tarjeta (TDC/TDD) con restriccion de unicidad 4-vias
- `BankAccountTransaction` - Movimientos de cuenta bancaria
- `ExchangeRateLog` - Tasas diarias BCV + Binance P2P
- `TransactionReconciliation` - Tabla pivot Muchos-a-Muchos

### Modulos Clave
- `parser.py` - Motor de extraccion regex (emails, TXT, PDFs)
- `reconciliation.py` - Conciliador inteligente con heuristicas difusas
- `services.py` - Integracion API con cadena de fallback resiliente (curl_cffi -> httpx -> requests -> urllib) + ProxyPool
- `models.py` - Logica de negocio (FIFO, intereses, ciclos)

---

## Decisiones Arquitectonicas (ADRs)

### ADR-001: Aislamiento de Base de Datos
- **Decision:** Mantener `src/db.sqlite3` completamente separada de `central_intelligence.db`
- **Razon:** Cumplimiento de directriz del operador para aislamiento total de datos de usuario

### ADR-002: Motor de Parseo Regex
- **Decision:** Usar regex nombrada con grupos para extraccion de transacciones
- **Razon:** Eficiencia O(n) vs O(n^2) de parsing tradicional, soporte multi-formato

### ADR-003: Conciliacion FIFO
- **Decision:** Amortizar pagos usando algoritmo FIFO cronologico
- **Razon:** Alineado con normativa bancaria venezolana para cancelacion de deudas

### ADR-004: Indexacion Dual USD
- **Decision:** Mantener tasas BCV y Binance P2P por separado
- **Razon:** El usuario necesita comparar ambos mercados para tomar decisiones informadas

### ADR-005: Resilient Binance P2P Fetching (T36)
- **Decision:** Implementar cadena de fallback en 4 niveles para scraping de Binance P2P
- **Niveles:** curl_cffi (TLS fingerprint) -> httpx -> requests -> urllib stdlib
- **ProxyPool:** Health-aware proxy rotation con failover parcial (3 fallos = exclusion temporal)
- **Razon:** El scraping directo de Binance P2P es frecuentemente bloqueado por anti-bots y Cloudflare

### ADR-006: Calculo de Pago Minimo (T38)
- **Decision:** Pago Minimo = (Balance × Tasa Min%) + Interes Ordinario del periodo
- **Tasa MC:** 4.21% (ajustada para aproximar valor real del banco: 11,955.12 Bs)
- **Tasa Visa:** 4.20% (default)
- **Razon:** El banco calcula el pago minimo como un porcentaje del saldo mas los intereses del periodo
- **Campo nuevo:** `CreditCard.minimum_payment_rate` (migration 0012)
- **Metodo nuevo:** `CreditCard.minimum_payment_info` para templates

---

## Proximo Ciclo de Mejoras (Backlog Futuro)

| ID | Tarea | Agente | Prioridad |
|---|---|---|---|
| T35 | Implementar exportacion de reportes en PDF/Excel | `backend_specialist` | 5 |
| T37 | Implementar sistema de alertas por correo | `backend_specialist` | 7 |

---

## Metricas del Ciclo

- **Duracion Total:** ~3 minutos (T31-T36 ejecutados)
- **Tests Ejecutados:** 49 (100% OK - incluyendo 11 tests nuevos para T36)
- **Archivos Modificados:** 4 (`services.py`, `base.html`, `tests.py`, `requirements.txt`)
- **Archivos Creados:** 7 (`REQUIREMENTS.md`, `BACKLOG.md`, `MISSION_CONTROL.md`, `design-tokens.json`, `component-specs.md`, `test_report.md`, `reports/`)
- **Estado del Proyecto:** Saludable, listo para siguientes iteraciones

### Sesion 2026-06-09 (T38)
- **Duracion:** ~45 minutos
- **Tests:** 49/49 passing
- **Archivos Modificados:** `models.py`, `views.py`, `dashboard.html`, `cards.html`
- **Migrations Creadas:** 0012 (`minimum_payment_rate`)
- **Artefactos:** Journal entry `20260609-160000_session_reconciliacion-mc-pago-minimo.md`

---

## Numeros Clave (al 09/06/2026)

| Concepto | Valor |
|----------|-------|
| MC Balance | 200,512.17 Bs ($353.21 USD) |
| MC Pago Minimo | 11,957.67 Bs |
| MC Interes Proyectado | 3,516.11 Bs |
| MC Interes Real Cargado | 6,567.78 Bs |
| Visa Balance | 9,885.50 Bs ($17.41 USD) |
| Visa Pago Minimo | 415.19 Bs |
| Cuenta Corriente | 8,563.69 Bs ($15.09 USD) |
| **Deuda TDC Total** | **210,397.67 Bs ($370.62 USD)** |
| Tasa BCV | 567.68 |
| Tasa Binance P2P | 761.73 |

---

> *"No automatices el caos. Orquesta con memoria."*
> — AIRON-Cast Manifesto, v1.0.0
