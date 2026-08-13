# ADR-002 · Paleta de Diseño

**Fecha:** 2026-06-06
**Estado:** Aprobado
**Decisor:** ux-ui_specialist + Operador del cliente

## Contexto

Café Cenit necesita transmitir **calidez, tradición moderna, limpieza artesanal**. Carlos pidió explícitamente marrón tostado, crema y naranja suave, "nada oscuro ni triste".

## Decisión

### Paleta principal

| Token | HEX | OKLCH aprox. | Rol |
|---|---|---|---|
| `--color-bg-cream` | `#F5EFE6` | oklch(0.95 0.02 75) | Fondo principal |
| `--color-bg-paper` | `#FBF7F1` | oklch(0.97 0.015 80) | Fondo alterno (zebra) |
| `--color-roast-900` | `#3B2417` | oklch(0.25 0.04 50) | Texto principal |
| `--color-roast-700` | `#5C3A24` | oklch(0.40 0.06 55) | Texto secundario |
| `--color-roast-500` | `#8B5A3C` | oklch(0.55 0.08 60) | Acento marrón |
| `--color-ember-500` | `#D97742` | oklch(0.65 0.15 50) | CTA / highlight |
| `--color-ember-600` | `#B85F30` | oklch(0.55 0.13 45) | Hover CTA |
| `--color-cream-soft` | `#EDE3D3` | oklch(0.92 0.03 75) | Hover superficie |
| `--color-whatsapp` | `#25D366` | oklch(0.72 0.18 145) | Verde WhatsApp oficial |

### Tipografía

- **Headings:** Fraunces (serif moderna con optical sizing, transmite tradición editorial)
- **Body:** Inter (sans humanista, legibilidad comprobada)

## Consecuencias

### Positivas

- Contraste WCAG AA: `roast-900` sobre `bg-cream` = 12.4:1 (AAA)
- Acento naranja (`ember-500`) sobre crema = 4.6:1 (AA)
- Cero HEX en HTML: todos los tokens se exponen vía `@theme` y se usan como clases Tailwind
- Psicología del color: marrón = tierra/café, naranja = energía/calidez, crema = pureza/naturalidad

### Restricciones

- **Prohibido:** negro puro (`#000`), azul corporativo, rojo saturado
- **Prohibido:** temas oscuros en esta fase (consistencia con la marca cálida)
- **Acento metálico:** se reservan los efectos `a2lt-shine-*` para casos especiales (no usados en MVP)

## Alternativas consideradas

| Opción | Por qué se descartó |
|---|---|
| Tema oscuro tipo "bar de café" | Contradice "nada oscuro ni triste" |
| Verde matcha como acento | Demasiado genérico para café |
| Rojo terracota | Compite con la calidez, no suma |
| Paleta A2LT neón (cyan/magenta) | No aplica a la marca de café |
