# Backlog — G3 Multistore

> Generado por `requirements_architect` · Slug: `g3-multistore`
> Estilo Visual: Comercial Limpio (Clean Commercial / Modern Retail)
> Estrategia de Inventario: Visibilidad total con badges de `❌ AGOTADO` para sentido de urgencia y neuromarketing.

## Resumen Round-Robin

| ID  | Tarea                                                                  | Agente                  | Prioridad | Dependencias   | Estado |
| --- | ---------------------------------------------------------------------- | ----------------------- | --------- | -------------- | ------ |
| T01 | Estructura JSON del catálogo completo (80+ productos en 27 categorías) | `requirements_architect`| 10        | —              | READY  |
| T02 | Identidad visual: tokens de diseño "Comercial Limpio" y component specs | `ux-ui_specialist`      | 9         | T01            | READY  |
| T03 | Copywriting de venta, Hero de alto impacto y templates de WhatsApp     | `writer`                | 8         | T01, T02       | READY  |
| T04 | Setup Astro 5 + Tailwind v4 + Layout + Navbar con Switcher Divisas/BCV  | `frontend_worker`       | 7         | T02, T03       | READY  |
| T05 | Implementar Mega Catálogo Filtrable, buscador y badges de Agotado      | `frontend_worker`       | 6         | T04            | READY  |
| T06 | Implementar sección Ubicación (San Diego), Métodos de Pago y FAQs      | `frontend_worker`       | 5         | T04, T05       | READY  |
| T07 | Smoke tests, verificación de enlaces WhatsApp y `astro build`          | `tester`                | 4         | T06            | READY  |
| T08 | Auditoría de calidad QA, Core Web Vitals y verificación de integridad   | `qa_auditor`            | 3         | T07            | READY  |
| T09 | Manual de administración de catálogo y actualización de inventario      | `docs`                  | 2         | T08            | READY  |

---

## T01: Estructura de Datos del Catálogo
**Agente:** `requirements_architect`  
**Prioridad:** 10  
**Dependencias:** —  
**Descripción:**
Extraer todos los productos, variantes, especificaciones técnicas, precios en Divisas y BCV y estado de inventario (disponible/agotado) desde `Y:\Proyectos\Precios G3 Multi\Mensjaes de Respuesta.md` hacia `src/data/products.json` y definir el esquema TypeScript `src/types/product.ts`.

---

## T02: Identidad Visual y Tokens de Diseño
**Agente:** `ux-ui_specialist`  
**Prioridad:** 9  
**Dependencias:** T01  
**Descripción:**
Definir tokens de diseño en `src/styles/design-tokens.json` con estética "Comercial Limpio" (fondos claros `#f8fafc`, acentos azul zafiro `#2563eb`, naranja comercial `#f97316`, badges rojos de urgencia `#ef4444` y tipografía moderna Inter / Plus Jakarta Sans). Diseñar especificaciones de tarjetas de producto con precios duales y micro-interacciones.

---

## T03: Copywriting de Venta y Plantillas WhatsApp
**Agente:** `writer`  
**Prioridad:** 8  
**Dependencias:** T01, T02  
**Descripción:**
Redactar titulares de alta conversión, garantías comerciales, propuesta de valor para San Diego / Valencia y generar el generador de enlaces de WhatsApp (`https://wa.me/584121869211?text=...`) con el mensaje prellenado por producto.

---

## T04: Setup Astro 5 + Tailwind v4 + Layout & Navbar
**Agente:** `frontend_worker`  
**Prioridad:** 7  
**Dependencias:** T02, T03  
**Descripción:**
Inicializar el proyecto base Astro 5 con Tailwind CSS v4, estructurar `Layout.astro`, `SeoHead.astro`, Navbar responsiva con selector interactivo de moneda (USD Divisas / USD BCV) y botón flotante de WhatsApp.

---

## T05: Mega Catálogo Filtrable y Buscador
**Agente:** `frontend_worker`  
**Prioridad:** 6  
**Dependencias:** T04  
**Descripción:**
Construir el componente `Catalog.astro` con selector de categorías por iconos (Solar, Bombas, Generadores, Herramientas, Gastronomía, Portones, etc.), buscador en tiempo real, badges de `❌ AGOTADO` destacados y cálculo dinámico de precios.

---

## T06: Ubicación, Confianza, FAQs y Footer
**Agente:** `frontend_worker`  
**Prioridad:** 5  
**Dependencias:** T04, T05  
**Descripción:**
Implementar sección de ubicación física en C.C. San Diego / Fin De Siglo Gran Bazar Local M9-5, métodos de pago aceptados, horarios de atención, política de envíos nacionales y preguntas frecuentes.

---

## T07: Verificación de Enlaces y Compilación
**Agente:** `tester`  
**Prioridad:** 4  
**Dependencias:** T06  
**Descripción:**
Ejecutar validación de sintaxis, test de enlaces dinámicos de WhatsApp, verificación de cálculo de precios y `astro build` libre de errores.

---

## T08: Auditoría de Calidad QA
**Agente:** `qa_auditor`  
**Prioridad:** 3  
**Dependencias:** T07  
**Descripción:**
Auditar accesibilidad, contraste de colores comercial limpio, responsive design en móviles y emitir veredicto formal.

---

## T09: Documentación y Guía de Actualización
**Agente:** `docs`  
**Prioridad:** 2  
**Dependencias:** T08  
**Descripción:**
Generar `README.md` con instrucciones claras para que el equipo de G3 Multistore pueda añadir o modificar productos en el JSON sin tocar el código frontend.