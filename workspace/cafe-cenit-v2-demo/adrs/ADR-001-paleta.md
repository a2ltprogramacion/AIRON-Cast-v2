# ADR-001 · Paleta Cálida (cafe-cenit-v2-demo)

**Fecha:** 2026-06-06
**Estado:** Activo
**Decisor:** ux-ui_specialist (Round-Robin Turno 1)

## Contexto

El proyecto `cafe-cenit-v2-demo` (proyecto de validación del ecosistema
multi-agente) requiere una paleta cálida, artesanal y moderna.

## Decisión

7 colores + 2 tipografías (Fraunces headings, Inter body). Ver
`src/styles/design-tokens.json`.

## Consecuencias

- Cero HEX sueltos en HTML: todo via tokens.
- Contraste WCAG AA: roast-900 sobre bg-cream ≈ 12:1.
- Prohibido: negro puro, azul corporativo, rojo saturado.
