# Café Cenit — Requerimientos

> Documento generado por `requirements_architect` · Proyecto: `cafe-cenit`
> Versión: 1.0.0 · 2026-06-06

## 1. Visión General

**Café Cenit** es un negocio venezolano de café artesanal de origen único, **tostado a pedido**. La landing page debe transmitir la calidez de un café recién hecho, la seriedad de un producto de especialidad, y la cercanía de un negocio atendido por su dueño. El objetivo comercial es convertir visitas en pedidos por WhatsApp (canal principal) o formulario de contacto.

**Audiencia:** personas en Venezuela (y LATAM) que ya consumen café de especialidad, entienden de tueste, origen y notas de cata, y están dispuestas a pagar un precio premium por calidad.

**Lo que NO es:** no es una tienda con carrito de compras ni un marketplace. Es una página de presentación + canal de pedido directo con el dueño.

## 2. Stack Tecnológico

| Capa | Tecnología | Justificación |
|---|---|---|
| Framework | **Astro 5** (SSG) | Performance brutal, SEO nativo, ideal para landing estática |
| Estilos | **Tailwind CSS v4** (CSS-First, `@theme`) | Design tokens estrictos, sin HEX sueltos |
| Interactividad | **Vanilla TypeScript** | Formulario, switcher de moneda, scroll reveals (sin frameworks pesados) |
| Tipografías | **Fraunces** + **Inter** (Google Fonts) | Serif cálida moderna + sans limpia |
| Deploy | **Netlify** | CI/CD, headers de seguridad, dominio `.com.ve` o `.netlify.app` |
| SEO | Sitemap + 12 meta tags OG/Twitter | Siguiendo `astro-landing-kit` |
| Seguridad | Headers HTTP en `netlify.toml` | X-Frame, CSP, HSTS, etc. |
| Moneda dual | **API pública BCV** (`dolarapi.com`) | Tasa referencial con fallback |

## 3. Estructura de Páginas

Landing de **una sola página** (`/`) con secciones ancladas:

| # | Sección | Anchor | Tipo |
|---|---|---|---|
| 1 | Navbar | (fija arriba) | Sticky con blur |
| 2 | Hero | `#inicio` | Offset Overlap 60/40 + badge |
| 3 | Proceso | `#proceso` | 3 columnas con íconos |
| 4 | Productos | `#cafes` | 3 cards premium |
| 5 | Testimonios | `#testimonios` | Carrusel cálido (3 placeholders) |
| 6 | Contacto | `#contacto` | Formulario + nota WhatsApp |
| 7 | Footer | — | 4 columnas: marca, enlaces, contacto, redes |
| — | Botón WhatsApp | (flotante) | Siempre visible |

## 4. Componentes

| Componente | Archivo | Props clave |
|---|---|---|
| `Layout.astro` | `src/layouts/` | `title`, `description`, `ogImage` |
| `SeoHead.astro` | `src/components/atoms/` | 12 meta tags (OG + Twitter + canonical) |
| `Navbar.astro` | `src/components/` | — |
| `CurrencySwitcher.astro` + `.ts` | `src/components/` + `src/scripts/` | USD ⇄ Bs. |
| `Hero.astro` | `src/components/` | `badge`, `title`, `subtitle`, CTAs |
| `Process.astro` | `src/components/` | `steps[]` desde `process.json` |
| `Products.astro` | `src/components/` | `products[]` desde `products.json` |
| `Testimonials.astro` | `src/components/` | `testimonials[]` desde `testimonials.json` |
| `Contact.astro` | `src/components/` | Form con validación HTML5 |
| `Footer.astro` | `src/components/` | Datos de `site.json` |
| `WhatsAppFloat.astro` | `src/components/` | `phone`, `message` |

## 5. Paleta de Diseño (design tokens)

Definidos formalmente en `src/styles/design-tokens.json` y consumidos vía `@theme` en `global.css`.

| Token | HEX | Uso |
|---|---|---|
| `--color-bg-cream` | `#F5EFE6` | Fondo principal (crema cálida) |
| `--color-bg-paper` | `#FBF7F1` | Fondo alterno (zebra) |
| `--color-roast-900` | `#3B2417` | Texto principal (marrón profundo) |
| `--color-roast-700` | `#5C3A24` | Texto secundario |
| `--color-roast-500` | `#8B5A3C` | Acento marrón tostado |
| `--color-ember-500` | `#D97742` | Naranja suave (CTA, highlights) |
| `--color-ember-600` | `#B85F30` | Hover/activo |
| `--color-cream-soft` | `#EDE3D3` | Hover sutil en superficies |
| `--color-whatsapp` | `#25D366` | Verde WhatsApp oficial |

## 6. Tipografía

- **Headings:** Fraunces, weight 500–700, optical sizing. Tono: editorial moderno, artesanal.
- **Body:** Inter, weight 400–600. Tono: limpio, legible.
- **Escala:** Mobile `text-base` (16px) → Desktop `text-lg` (18px) en cuerpo. Headings desde `text-3xl` mobile hasta `text-6xl` desktop.

## 7. Requerimientos Funcionales

### 7.1 Hero
- Badge: "Tostado a pedido"
- H1: 2 frases (≤ 12 palabras en total) que expliquen el producto
- Subtítulo: 1 línea de valor
- CTA principal: "Pedir por WhatsApp" → `https://wa.me/<PHONE>?text=...`
- CTA secundario: "Ver los cafés" → `#cafes`
- Imagen: granos de café cayendo o similares (Unsplash provisional)

### 7.2 Proceso
- 3 pasos en columnas: ① Selección del grano · ② Tostado artesanal · ③ Envío inmediato
- Cada paso con ícono SVG inline, título y descripción (2-3 líneas)

### 7.3 Productos
- 3 cards: **Suave**, **Intenso**, **Descafeinado**
- Cada card muestra: nombre, descripción (1 línea), notas de cata (3-4 bullet points), precio en USD, switcher a Bs.
- Botón "Pedir este" → WhatsApp con mensaje pre-cargado

### 7.4 Testimonios
- 3 placeholders con texto `[TESTIMONIO REAL DE CLIENTE — Carlos, completar]`
- Cada testimonio: nombre, ciudad, texto (3-5 líneas), ⭐⭐⭐⭐⭐

### 7.5 Contacto
- Formulario: nombre, email, mensaje
- Botón "Enviar mensaje" (POST a `mailto:` o endpoint a definir)
- Texto: "O escribinos directo a WhatsApp — respondemos en menos de 24h"

### 7.6 Botón WhatsApp flotante
- Siempre visible (esquina inferior derecha)
- Color verde WhatsApp
- Animación de pulse sutil
- Abre chat con mensaje pre-cargado: "Hola Café Cenit, quiero hacer un pedido"

## 8. Requerimientos No Funcionales

| Requerimiento | Criterio |
|---|---|
| Responsive | Mobile-first, breakpoints sm/md/lg, perfecto en 375px |
| Performance | Lighthouse Performance > 90 |
| Accesibilidad | WCAG 2.1 AA, contraste mínimo 4.5:1, navegación por teclado |
| SEO | 12 meta tags, sitemap, robots.txt, OpenGraph completo |
| Seguridad | Headers HTTP (CSP, X-Frame, HSTS) en `netlify.toml` |
| TypeScript | Estricto, sin `any` |
| Internacionalización | Español (es_VE) por defecto |
| Privacidad | Cero cookies de rastreo, cero analytics invasivos |

## 9. Placeholders Operacionales

Estos campos los completa **Carlos** (Operador del cliente) en cualquier momento:

| Campo | Ubicación | Dato actual |
|---|---|---|
| Nombre comercial exacto | `src/content/site.json` → `name` | `Café Cenit` (verificar tilde) |
| Número WhatsApp | `src/content/site.json` → `whatsapp` | `+584140000000` (REEMPLAZAR) |
| Email de contacto | `src/content/site.json` → `email` | `hola@cafecenit.com.ve` (REEMPLAZAR) |
| Ciudad base | `src/content/site.json` → `city` | `Venezuela` (REEMPLIZAR con ciudad) |
| Precios USD | `src/content/products.json` → `priceUSD` | `8`, `10`, `11` (REEMPLAZAR) |
| Notas de cata | `src/content/products.json` → `notes` | Borrador, REEMPLAZAR |
| Presentación | `src/content/products.json` → `weight` | `250g` (verificar) |
| Testimonios | `src/content/testimonials.json` | PLACEHOLDERS marcados |

## 10. Criterios de Aceptación Generales

- [ ] Página se ve perfecta en iPhone SE (375px), iPhone 14, iPad, desktop 1920px
- [ ] Lighthouse: Performance > 90, Accessibility > 95, SEO = 100, Best Practices > 90
- [ ] Sin errores en consola del navegador
- [ ] Sin warnings en `astro build`
- [ ] Sitemap se genera correctamente
- [ ] Switcher de moneda funciona con fallback a "no disponible"
- [ ] Botón WhatsApp abre conversación con mensaje pre-cargado
- [ ] Formulario valida campos requeridos
- [ ] Todos los textos están en español (es_VE)
- [ ] Crédito "Designed by A2LT Soluciones" presente en `humans.txt`
- [ ] Logo placeholder (word-mark Fraunces) se reemplaza fácilmente en Fase 2+

## 11. Riesgos Identificados

| Riesgo | Mitigación |
|---|---|
| API BCV caída | Fallback elegante + precios USD siempre visibles |
| Imágenes provisionales | Marcadas con `data-provisional="true"` y comentario para reemplazo |
| Cambio de tasa BCV | Texto "última actualización DD/MM/AAAA" debajo de los precios en Bs. |
| Carlos no tiene dominio | Deploy inicial en `cafecenit.netlify.app`; migración documentada en README |

---

> *"Una especificación clara es la mitad del código escrito."*
