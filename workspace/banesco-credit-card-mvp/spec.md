# Especificación Técnica (Blueprint) — Banesco Credit Card Tracker

## Descripción General
MVP local robusto y modular desarrollado en Python 3.10+ y Django 5.x para el control de gastos indexados en dólares (utilizando tasas oficiales del BCV y promedios de Binance P2P) y tracking del apalancamiento y fechas de pago de tarjetas de crédito Banesco (Venezuela).

## Tarjetas y Reglas de Negocio
1. **Visa Dorada:** Corte el 12 de cada mes | Pago el 08 del mes siguiente.
2. **Mastercard Platinum:** Corte el 03 de cada mes | Pago el 30 del mismo mes.
3. **Tarjeta de Débito Banesco (Opcional):** Sin días de corte ni de pago. Se registra para asociar consumos diarios.

### Lógica de Ciclo de Facturación
- Si la fecha del consumo es `<= cutoff_day` de ese mes, pertenece al ciclo del mes actual.
- Si la fecha del consumo es `> cutoff_day`, pertenece al ciclo del mes siguiente.
- Para Mastercard Platinum en febrero: la fecha límite de pago se desplaza dinámicamente al último día del mes en curso (28 o 29 de febrero).

### Estado de Transacción
- `PENDIENTE`: Pendiente por Cortar.
- `CORTADO_NO_PAGADO`: Cortado No Pagado.
- `PAGADO`: Pagado.

## Modelos de Datos
- **CreditCard**: Contiene el nombre, últimos 4 dígitos, día de corte y día de pago.
- **ExchangeRateLog**: Registro diario único de tasas de cambio del dólar (BCV y Binance P2P).
- **Transaction**: Consumo individual con tipo (TDC/DEBIT), fecha, descripción, monto en bolívares, referencia única y asociación a una tasa y tarjeta.

## APIs de Tasas de Cambio
1. **DolarAPI (BCV):** `https://ve.dolarapi.com/v1/dolares/oficial`
2. **Binance P2P:** `https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search`

## Motor de Parseo Regex
Soporta procesamiento por lote de correos Banesco de Débito y Crédito.
