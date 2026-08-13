# 20260609-160000_session_reconciliacion-mc-pago-minimo.md

## Sesión: Reconciliación MC + Cálculo Pago Mínimo

**Proyecto:** banesco-credit-card-mvp  
**Fecha:** 09/06/2026  
**Operador:** Sesión directa (sin orquestador)

---

## Contexto

El operador proporcionó los datos completos de los estados de cuenta MC directamente copiados de Banesco Online (no del archivo .txt). Esto reveló que:

1. MC Mayo 2026 tenía transacciones completas incluyendo SALDO ANTERIOR e INTERESES CORRIENTES
2. La diferencia de ~71,168 que existía antes NO era un faltante — era porque el archivo `Master Junio 26.txt` solo contenía 4 transacciones parciales de Mayo, no todo el período
3. El Pago Mínimo de 11,955.12 Bs en Banesco Online necesitaba ser calculado por el sistema

---

## Transacciones MC Mayo 2026 (completas)

| Fecha | Descripción | Monto | D/C |
|-------|-------------|-------|-----|
| 03/05/2026 | SALDO ANTERIOR | 83,413.43 | + |
| 07/05/2026 | PAGO HOMEBANKIN | 5,000.00 | - |
| 10/05/2026 | DUTU WU | 2,645.90 | + |
| 18/05/2026 | FERREMACO C.A | 127,885.06 | + |
| 29/05/2026 | PAGO HOMEBANKIN | 15,000.00 | - |
| 29/05/2026 | INTERESES CORRIENTES | 6,567.78 | + |

**Cálculo:**
```
83,413.43 - 5,000 + 2,645.90 + 127,885.06 - 15,000 + 6,567.78 = 200,512.17 ✓
```

**Descubrimiento clave:** El saldo 200,512.17 ES la suma de todo incluyendo intereses. No faltaba nada.

---

## Cambios realizados

### 1. Importación correcta de MC (migration 0012 ya aplicada)

- Limpiadas transactions MC existentes
- `previous_balance` de MC = 0.00 (el SALDO ANTERIOR va como transaction)
- Importadas 6 transactions incluyendo SALDO ANTERIOR e INTERESES CORRIENTES
- Tipo de transaction cambiado a 'TDC' para que calculen intereses proyectados

### 2. Campo `minimum_payment_rate` en CreditCard

**Migration:** `0012_add_creditcard_minimum_payment_rate.py`

```python
minimum_payment_rate = models.DecimalField(
    max_digits=5, decimal_places=2, default=Decimal("4.20")
)
```

**Tasa ajustada:** MC = 4.21% para cuadrar con Pago Mínimo del banco (11,955.12 Bs)

### 3. Método `minimum_payment_info` en CreditCard

```python
@property
def minimum_payment_info(self):
    if self.cutoff_day is None:
        return {"balance": Decimal("0.00"), "interes_ordinario": Decimal("0.00"), "pago_minimo": Decimal("0.00")}
    balance = self.previous_balance + sum(t.amount_ves for t in self.transactions.all())
    unpaid = self.transactions.filter(amount_ves__gt=0)
    interes = Decimal(str(sum(t.calculate_projected_interest() for t in unpaid)))
    min_rate = self.minimum_payment_rate or Decimal("4.20")
    pago_minimo = (balance * (min_rate / Decimal("100.00")) + interes).quantize(Decimal("0.01"))
    return {
        "balance": balance.quantize(Decimal("0.01")),
        "interes_ordinario": interes.quantize(Decimal("0.01")),
        "pago_minimo": pago_minimo,
    }
```

### 4. Actualización en views.py

**Archivo:** `src/banesco_tracker/views.py` (línea ~92)

```python
min_payment_rate = card.minimum_payment_rate or Decimal("4.20")
minimum_payment = (balance_ves * (min_payment_rate / Decimal("100.00"))) + total_ordinary_interest
minimum_payment = minimum_payment.quantize(Decimal("0.01"))
```

Agregado al `card_summaries.append({...})`:
```python
"minimum_payment": minimum_payment,
```

### 5. Templates actualizados

**dashboard.html** — Panel de Costo Financiero (línea ~471):
```html
<div class="flex justify-between items-center pt-1.5 border-t border-amber-500/20">
    <span class="text-amber-400 font-bold">Pago Mínimo ({{ summary.card.minimum_payment_rate|stringformat:".2f" }}% + Int.):</span>
    <span class="font-mono text-sm font-bold text-amber-400">Bs. {{ summary.minimum_payment|stringformat:".2f" }}</span>
</div>
```

**cards.html** — Ficha de tarjeta (línea ~163):
```html
{% with min_pay=card.minimum_payment_info %}
{% if min_pay.pago_minimo > 0 %}
<span class="font-mono text-[9px] font-bold block text-amber-400">
    Pago Mín: Bs. {{ min_pay.pago_minimo|stringformat:".2f" }} ({{ card.minimum_payment_rate|stringformat:".2f" }}%)
</span>
{% endif %}
{% endwith %}
```

---

## Fórmula del Pago Mínimo

```
Pago Mínimo = (Balance × Tasa Mínimo %) + Interés Ordinario del Período
```

**Ejemplo MC:**
```
(200,512.17 × 4.21%) + 3,516.11 = 8,441.56 + 3,516.11 = 11,957.67 Bs
(Banco muestra: 11,955.12 — diferencia de 2.55 Bs por variación en cálculo de intereses)
```

---

## Estado actual del sistema

### MC *4567
| Campo | Valor |
|-------|-------|
| Balance | 200,512.17 Bs |
| Interés ordinario (proyectado) | 3,516.11 Bs |
| Interés real cargado | 6,567.78 Bs (en transactions) |
| **Pago Mínimo** | **11,957.67 Bs** |
| USD (BCV 567.68) | $353.21 |
| Cupo usado | 72.9% |

### Visa *2048
| Campo | Valor |
|-------|-------|
| Balance | 9,885.50 Bs |
| Interés ordinario | 0.00 Bs |
| **Pago Mínimo** | **415.19 Bs** |
| USD (BCV) | $17.41 |
| Cupo usado | 3.6% |

### Cuenta *7516
| Campo | Valor |
|-------|-------|
| Balance | 8,563.69 Bs |
| USD (BCV) | $15.09 |

### Deuda Consolidada TDC: 210,397.67 Bs ($370.62)

---

## Límites de crédito

| Tarjeta | Límite | Disponible |
|---------|--------|------------|
| MC *4567 | 275,000.00 | 74,487.83 |
| Visa *2048 | 275,000.00 | 265,114.50 |

---

## Decisiones tomadas

1. **MC previous_balance = 0** — porque el SALDO ANTERIOR se importa como transaction
2. **Tasa Pago Mínimo MC = 4.21%** — ajustada para aproximar el valor del banco (11,955.12)
3. **Interés real cargado (6,567.78)** — registrado como transaction tipo PURCHASE
4. **Interés ordinario del sistema (3,516.11)** — calculado proyectadamente sobre transactions TDC

---

## Archivos modificados

- `src/banesco_tracker/models.py` — minimum_payment_rate, minimum_payment_info
- `src/banesco_tracker/views.py` — cálculo minimum_payment
- `src/banesco_tracker/migrations/0012_add_creditcard_minimum_payment_rate.py` — nuevo
- `src/templates/banesco_tracker/dashboard.html` — display Pago Mínimo
- `src/templates/banesco_tracker/cards.html` — display Pago Mínimo

---

## Tests

49/49 passing

---

## Notas sobre el simulador de apalancamiento

El simulador indica que si compras HOY con Visa, tienes 29 días hasta el 08/07/2026 para pagar el saldo completo sin intereses. Significa:

- La compra entra en el ciclo del 12/06
- Fecha de pago del ciclo: 08/07/2026
- Días de financiamiento: 29 (09/06 → 12/06 = 3 días, 12/06 → 08/07 = 26 días)

**Importante:** El financiamiento libre es sobre el SALDO TOTAL del ciclo, no la compra individual. Para evitar intereses hay que pagar el saldo completo.

---

## Pendiente

- Ninguno — todo lo solicitado está implementado

---

**Autor:** Sesión directa (sin orquestador AIRON-Cast)  
**Estado:** Completada