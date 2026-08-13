<!-- [JOURNAL] type:task -->
# TASK: Reinicialización completa y corrección de ecosistema banesco-credit-card-mvp

**Fecha:** 2026-06-09T01:30:00-04:00
**Agente:** Orchestrator / Backend Specialist
**Skills utilizadas:** django-patterns, database-architecture, journal-writer
**Duración estimada:** 180 minutos
**Estado:** COMPLETADA

## Descripción de la tarea
El usuario reportó que los saldos en el dashboard no coincidían con su banca online. El sistema presentaba múltiples problemas de cálculo y visualización.

## Problemas identificados inicialmente
- MC: Sistema mostraba Bs 258,544.94 vs Real Bs 200,512.17
- Visa: Sistema mostraba Bs 38,077.90 vs Real Bs 9,885.50
- Cuenta: Sistema mostraba Bs 23,981.94 vs Real Bs 8,563.69
- Tasa Binance mostraba 858.67 (incorrecta) en lugar de ~761
- UI mostraba "balance pendiente cero" para MC pero barra de 72.9%

## Acciones realizadas

### 1. Limpieza y reinicialización de base de datos
- Eliminación de transacciones de tarjetas y cuenta
- Configuración de initial_balance de cuenta = Bs 4,551.94

### 2. Corrección de bugs en views.py
- `balance_ves` no incluía `previous_balance` → MC mostraba 0
- `total_tdc_debt` no incluía `previous_balance` de tarjetas
- Fix: `balance_ves = card.previous_balance + sum(transactions)`

### 3. Corrección de current_balance en BankAccount
- El modelo calculaba mal: `initial_balance + sum(movements)`
- Corregido para usar `balance_ves` de última transacción
- Añadido tiebreaker `-id` para transacciones del mismo día

### 4. Campo previous_balance en CreditCard
- Nueva migración `0011_add_previous_balance`
- Actualizado método `available_limit()` para incluir previous_balance

### 5. Importación de transacciones
- Cuenta: 121 transacciones (Mayo + Junio hasta 09/06)
- Visa: 11 transacciones desde `Visa Junio 2026.txt`
- MC: Sin transactions (archivo vacío), solo previous_balance

### 6. Creación de reconciliaciones
- 3 pagos de Visa vinculados a transacciones de cuenta:
  - 14/05: Bs 30,000
  - 19/05: Bs 50,000
  - 29/05: Bs 126,155.26

### 7. Tasas de cambio
- BCV: 567.68
- Binance: 761.73

## Configuración final de saldos

| Tarjeta | previous_balance | transactions | Balance Total |
|---------|------------------|--------------|---------------|
| MC (*4567) | 200,512.17 | 0 | 200,512.17 |
| Visa (*2048) | 128,722.73 | -118,837.23 | 9,885.50 |

## Validaciones
- 49 tests ejecutados → 49 PASSED
- MC saldo: 200,512.17 ✓
- Visa saldo: 9,885.50 ✓
- Cuenta saldo: 8,563.69 ✓

## Limitaciones conocidas
- MC no tiene transactions detalladas (archivo de Junio vacío)
- Pagos de MC a cuenta (07/05 y 29/05) no están reconciliados
- Sin desglose de intereses para MC

---
*Generado por journal-writer v3.0 — AIRON‑Cast*