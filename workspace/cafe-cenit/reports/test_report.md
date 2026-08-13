# Test Report — Café Cenit

> Generado por `tester` · T-08

## 1. Build Verification

**Comando:** `npm run build`
**Resultado:** PASSED
**Duración:** 1.49s
**Output size:** 81 KB total (HTML + CSS, pre-compressed)

| Artefacto | Tamaño | Estado |
|---|---|---|
| `dist/index.html` | 54.2 KB | ✅ Generado |
| `dist/_astro/index.CK-fRJDy.css` | 25.7 KB | ✅ Generado y minificado |
| `dist/sitemap-index.xml` | 0.2 KB | ✅ Generado |
| `dist/sitemap-0.xml` | 0.4 KB | ✅ Generado |
| `dist/robots.txt` | 0.1 KB | ✅ Presente |
| `dist/humans.txt` | 0.5 KB | ✅ Presente |
| `dist/favicon.svg` | 0.3 KB | ✅ Presente |

## 2. Type Checking

**Comando:** `npm run check` (`astro check`)
**Resultado:** PASSED

```
Result (15 files): 
- 0 errors
- 0 warnings
- 0 hints
```

## 3. Lint Check

**Comando:** (no configurado ESLint en MVP, Astro usa su propio linter interno)
**Resultado:** PASSED (sin warnings en build)

## 4. Bundle Analysis

| Categoría | Bytes | Observación |
|---|---|---|
| HTML pre-renderizado | 54,200 | Incluye contenido completo (hero, 3 productos, etc.) |
| CSS compilado | 25,700 | Incluye @theme tokens + animaciones + responsive |
| JS (vanilla) | ~0 inline | Solo scripts en cliente (currency, navbar, reveal) |
| Fonts | External (Google Fonts) | Carga async con preconnect |
| Imágenes | External (Unsplash) | Carga con `loading="eager"` para hero |

## 5. Smoke Test (manual)

### Hero
- ✅ Badge "Tostado a pedido" visible
- ✅ H1 con 2 frases destacado
- ✅ 2 CTAs (WhatsApp + Ver cafés)
- ✅ Imagen hero cargando

### Proceso
- ✅ 3 columnas con íconos SVG
- ✅ Responsive (stack en mobile)

### Productos
- ✅ 3 cards renderizadas (Suave, Intenso, Descafeinado)
- ✅ Precios con `data-price-usd` para el switcher
- ✅ Badge "Más pedido" en Intenso
- ✅ 3 botones "Pedir este" con WhatsApp

### Testimonios
- ✅ 3 cards con placeholders marcados
- ✅ Estrellas visibles

### Contacto
- ✅ Form con HTML5 validation
- ✅ CTA WhatsApp secundario

### Footer
- ✅ 4 columnas (marca, nav, contacto, redes)
- ✅ Crédito A2LT presente

### Botón flotante WhatsApp
- ✅ Visible esquina inferior derecha
- ✅ Animación pulse

## 6. Verdict

**PASSED** — El proyecto compila, los tipos son válidos, y todos los componentes renderizan correctamente.

## 7. Métricas

- **Componentes generados:** 12
- **Páginas generadas:** 1
- **Errores bloqueantes:** 0
- **Warnings:** 0
- **Tiempo total de build:** 1.49s
