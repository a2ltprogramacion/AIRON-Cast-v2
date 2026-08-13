# ADR-001 · Stack Tecnológico

**Fecha:** 2026-06-06
**Estado:** Aprobado
**Decisor:** requirements_architect + Operador

## Contexto

Landing page para "Café Cenit" (negocio venezolano de café de especialidad). Necesita ser rápida, fácil de mantener, escalable, y con costo operativo cero.

## Decisión

- **Framework:** Astro 5 en modo SSG (Static Site Generation)
- **Estilos:** Tailwind CSS v4 con metodología CSS-First (`@theme`)
- **Interactividad:** TypeScript vanilla (sin React/Vue/Svelte)
- **Tipografías:** Fraunces (headings) + Inter (body) desde Google Fonts
- **Deploy:** Netlify con headers de seguridad
- **SEO:** 12 meta tags OG/Twitter + sitemap

## Consecuencias

### Positivas

- Performance: HTML estático pre-renderizado, ~0KB JS por defecto
- Costo: hosting gratuito en Netlify, dominio opcional
- Mantenibilidad: archivo de contenido JSON editable sin tocar componentes
- SEO: meta tags completos, sitemap automático
- Diseño: tokens estrictos sin HEX sueltos

### Negativas

- Cambios de contenido requieren rebuild (mitigado: JSON en `src/content/`)
- Tasa BCV requiere API externa (mitigado: fallback elegante)
- Sin CMS visual (Carlos edita JSON, no Decap CMS en esta fase)

## Alternativas consideradas

| Opción | Por qué se descartó |
|---|---|
| Next.js | Más complejo, requiere SSR para nuestros casos |
| WordPress | Costoso, vulnerable, overkill |
| HTML puro sin framework | Pierde organización de componentes y SEO automático |
| Hugo | Comunidad más chica, menos skills disponibles |
