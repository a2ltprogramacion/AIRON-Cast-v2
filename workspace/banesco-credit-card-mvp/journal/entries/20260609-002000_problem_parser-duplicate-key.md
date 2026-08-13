<!-- [JOURNAL] type:problem -->
# PROBLEM: Parser de tarjetas no diferenciaba transacciones con misma descripción y monto diferente

**Fecha:** 2026-06-09T00:20:00-04:00
**Severidad:** medium
**Riesgo de recurrencia:** medium
**Componentes afectados:** banesco_tracker.parser, CreditCard transactions import

## Contexto
Al importar transacciones de Visa, dos compras a "EL MARACUCHO 88, C.A." en la misma fecha (23/05/2026) fueron tratadas como duplicadas:
- +530,50 Bs
- +526,87 Bs

Ambas tienen descripción similar y la referencia generada era idéntica (solo usaba fecha + descripción truncada).

## Causa raíz
El parser usaba `date + last_four + desc[:10]` como referencia. Cuando dos transacciones tienen la misma descripción (aunque distinto monto), la referencia colisiona.

## Solución aplicada
Modificar el parser para incluir el monto en la referencia:
```python
ref = date + '_' + last_four + '_' + desc[:8] + '_' + amount_str_cleaned
```

## Mitigación para prevenir recurrencia
1. Siempre incluir monto en la referencia para transacciones de tarjetas
2. O usar timestamp completo + monto como clave única
3. Agregar validación adicional: si dos transacciones tienen misma referencia pero diferente monto, crear referencia alternativa

## Lección aprendida
Para transacciones financieras, usar descripción pura como clave de deduplicación es insuficiente. Incluir siempre identificadores únicos adicionales (monto, timestamp, o ambos).

---
*Generado por journal-writer v3.0 — AIRON‑Cast*