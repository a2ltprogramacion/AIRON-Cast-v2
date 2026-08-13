<!-- [JOURNAL] type:problem -->
# PROBLEM: UI mostraba valores incorrectos de balance en el dashboard

**Fecha:** 2026-06-09T01:00:00-04:00
**Severidad:** critical
**Riesgo de recurrencia:** medium
**Componentes afectados:** banesco_tracker.views, banesco_tracker.models

## Contexto
El usuario reportó que en la interfaz web:
- MasterCard: balance mostrado era 0, pero barra de uso decia 72.9%
- Visa: mostraba 118,837.23 pero barra decia 3.6%
- Control de Histórico de Tasas estaba en blanco

## Causa raíz
1. **En views.py**: `balance_ves` para tarjetas se calculaba como `sum(t.amount_ves for t in card.transactions.all())` SIN incluir `previous_balance`. Por eso MC (sin transacciones) mostraba 0.
2. **En views.py**: `total_tdc_debt` tampoco incluía `previous_balance`, causando que la deuda consolidada fuera incorrecta.
3. **En BankAccount**: `current_balance` se calculaba como `initial_balance + sum(movements)`, pero como solo teníamos transacciones de Junio (30), el cálculo era -4,443.11 en lugar del saldo real de 8,563.69.
4. **No había ExchangeRateLogs**: Por eso el control de tasas estaba en blanco.

## Solución aplicada
1. **views.py línea 69**: Cambiado a `balance_ves = card.previous_balance + sum(t.amount_ves for t in card.transactions.all())`
2. **views.py línea 72**: Similar fix para TDD
3. **views.py línea 155**: `total_tdc_debt` ahora suma `card.previous_balance + sum(transactions)` por tarjeta
4. **models.py BankAccount.current_balance**: Cambiado para retornar el `balance_ves` de la última transacción en lugar de recalcular desde initial_balance + movements
5. **models.py BankAccount.current_balance**: Añadido `-id` como tiebreaker para transacciones del mismo día (ya que todas tienen el mismo datetime)
6. **ensure_exchange_rate()**: Ejecutado para crear el primer ExchangeRateLog

## Mitigación para prevenir recurrencia
1. El campo `previous_balance` en CreditCard ahora se usa en todos los cálculos de deuda
2. El `current_balance` de cuenta usa el saldo oficial del banco (de la última transacción) en lugar de recalcular
3. Se debe ejecutar `ensure_exchange_rate()` periódicamente o en cada login para mantener las tasas actualizadas
4. Los archivos de estado de cuenta deben incluir transacciones completas (Mayo + Junio) para que el saldo se calcule correctamente

## Lección aprendida
- Para cuentas bancarias, el saldo final reportado por el banco (`balance_ves` de la última transacción) es más confiable que recalcular desde initial_balance + movements
- Para tarjetas de crédito, `previous_balance` es esencial cuando no se importan todas las transacciones históricas

---
*Generado por journal-writer v3.0 — AIRON‑Cast*