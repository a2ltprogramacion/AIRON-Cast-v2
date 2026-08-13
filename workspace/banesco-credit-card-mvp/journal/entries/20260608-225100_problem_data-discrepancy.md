<!-- [JOURNAL] type:problem -->
# AUDIT-FAILURE: Discrepancia masiva entre saldos del sistema y saldos reales del usuario

**Fecha:** 2026-06-08T22:51:00-04:00
**Severidad:** critical
**Riesgo de recurrencia:** high
**Componentes afectados:** banesco_tracker.parser, banesco_tracker.models.Transaction, banesco_tracker.models.CreditCard

## Contexto
El usuario reportó que los saldos mostrados por el sistema no coincidían con los saldos reales de su banca online:
- MasterCard: Sistema = Bs 258,544.94, Real = Bs 200,512.17 (diferencia Bs 58,032)
- Visa: Sistema = Bs 38,077.90, Real = Bs 9,885.50 (diferencia Bs 28,192)
- Cuenta Corriente: Sistema = Bs 23,981.94, Real = Bs 8,563.69 (diferencia Bs 15,418)

## Causa raíz
1. El parser `parse_banesco_bank_statement()` importaba líneas "SALDO ANTERIOR" de los archivos de exportación como transacciones positivas (consumos), cuando en realidad representan la deuda arrastrada del período anterior.
2. Las transacciones de tarjetas de crédito no tenían validación de duplicados, permitiendo importar el mismo movimiento múltiples veces.
3. No había diferenciación entre "SALDO ANTERIOR" (deuda pre-existente) y "CONSOMO" (nueva compra).

## Solución aplicada
1. Limpieza completa de la base de datos (eliminación de transactions, BankAccountTransactions, ExchangeRateLogs)
2. Se configuró initial_balance de cuenta = Bs 4,551.94 (correcto según estado de cuenta)
3. Se importaron movimientos de cuenta desde archivos `estado de cuenta mayo 26.txt` + `estado de cuenta junio 26.txt` con deduplicación
4. Se importaron transacciones de Visa desde `Visa Junio 2026.txt`
5. Para MasterCard, al no haber movimientos de Junio (archivo vacío), se configuró el saldo manualmente como Bs 200,512.17
6. La tasa Binance se corrigió cambiando tradeType de "SELL" a "BUY" (antes: 858.67 VES, después: 761.20 VES)

## Mitigación para prevenir recurrencia
1. Modificar parser para ignorar líneas que contengan "SALDO ANTERIOR" - no son consumos, son deuda previa
2. Agregar constraint UNIQUE en BankAccountTransaction(reference) - ya existe en el modelo (unique=True)
3. Para CreditCard, configurar previous_balance manualmente cuando no hay movimientos del período
4. Validar que el saldo final calculado coincida con el saldo real reportado por el usuario después de importar

---
*Generado por journal-writer v3.0 — AIRON‑Cast*