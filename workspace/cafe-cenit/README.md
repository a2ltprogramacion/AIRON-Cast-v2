# Café Cenit — Landing Page

> Sitio web oficial de **Café Cenit**, café venezolano tostado a pedido.
> Construido con Astro 5 + Tailwind CSS v4 por **A2LT Soluciones**.

---

## ¿Qué es este proyecto?

Es una **landing page de una sola página** con el objetivo de captar clientes y
convertirlos en pedidos por **WhatsApp** (canal principal) o formulario de
contacto. El sitio es 100% estático, súper rápido y sin costos de hosting.

---

## Estructura del proyecto

```
cafe-cenit/
├── public/                  # Archivos servidos tal cual (robots.txt, humans.txt, imágenes)
├── src/
│   ├── components/         # Componentes Astro (.astro)
│   │   ├── atoms/          # Componentes pequeños reutilizables (SeoHead)
│   │   ├── Navbar.astro
│   │   ├── Hero.astro
│   │   ├── Process.astro
│   │   ├── Products.astro
│   │   ├── Testimonials.astro
│   │   ├── Contact.astro
│   │   ├── Footer.astro
│   │   ├── WhatsAppFloat.astro
│   │   └── CurrencySwitcher.astro
│   ├── content/            # ⭐ Aquí editas contenido (precios, textos, etc.)
│   │   ├── site.json       #   Datos de marca (WhatsApp, email, ciudad)
│   │   ├── products.json   #   Los 3 cafés
│   │   ├── process.json    #   Pasos del proceso
│   │   ├── testimonials.json
│   │   └── seo.json
│   ├── layouts/
│   │   └── Layout.astro    # Layout base
│   ├── pages/
│   │   └── index.astro     # Página principal
│   ├── scripts/
│   │   └── currency-switcher.ts  # Lógica del switcher USD/Bs.
│   └── styles/
│       ├── global.css      # ⭐ Design tokens (@theme) + estilos globales
│       ├── design-tokens.json
│       └── component-specs.md
├── adrs/                   # Decisiones de arquitectura
├── astro.config.mjs        # Configuración de Astro
├── netlify.toml            # Deploy y headers de seguridad
├── package.json
├── robots.txt              # (en public/)
├── humans.txt              # (en public/)
└── tsconfig.json
```

---

## Tareas comunes — ¿Cómo edito X?

### 1. Cambiar los precios de los cafés

Edita `src/content/products.json`. Cada producto tiene un campo `priceUSD`:

```json
{
  "id": "suave",
  "name": "Suave",
  "priceUSD": 8,        // ← Cambia este número
  ...
}
```

Después de guardar, reconstruye el sitio (`npm run build`).

### 2. Cambiar el número de WhatsApp

Edita `src/content/site.json`:

```json
{
  "whatsapp": "+584140000000",        // Formato internacional con +
  "whatsapp_display": "+58 414 000 0000"  // Como querés que se vea
}
```

### 3. Cambiar el email de contacto

Edita `src/content/site.json`:

```json
{
  "email": "hola@cafecenit.com.ve"
}
```

### 4. Cambiar la ciudad

Edita `src/content/site.json`:

```json
{
  "city": "Mérida"
}
```

### 5. Editar la descripción de un café (notas de cata, tueste, etc.)

Edita `src/content/products.json`. Cada producto tiene:

- `tagline` — frase corta (1 línea)
- `description` — párrafo de presentación
- `notes` — array de strings (notas de cata)
- `origin` — origen del grano
- `roast_level` — nivel de tueste
- `weight` — presentación (250g, 500g, 1kg)
- `best_for` — métodos de preparación recomendados

### 6. Agregar testimonios reales

Edita `src/content/testimonials.json`. Reemplaza los placeholders:

```json
{
  "id": "t1",
  "name": "María González",
  "city": "Caracas",
  "rating": 5,
  "text": "Pedí el Intenso y se nota que fue tostado hace poco..."
}
```

Recomendaciones para testimonios creíbles:
- Que mencionen un producto específico
- Que hablen del proceso (tostado a pedido) o la atención
- 3-5 líneas máximo por testimonio

### 7. Cambiar el logo (cuando lo tengas)

1. Coloca el archivo en `public/images/logo.svg` (preferentemente SVG vectorial)
2. Edita `src/components/Navbar.astro` — busca el `<span>` con "Café Cenit" y reemplázalo por:

```astro
<img src="/images/logo.svg" alt="Café Cenit" class="h-8 md:h-10 w-auto" />
```

3. Haz lo mismo en `src/components/Footer.astro` (la versión del footer es más grande).

### 8. Cambiar las imágenes provisionales (Unsplash)

Las imágenes provisionales están marcadas con el comentario:
```html
<!-- [Imagen provisional — reemplazar con foto real del proceso] -->
```

Para reemplazarlas:
1. Coloca tu imagen real en `public/images/`
2. Cambia el `src=` de la etiqueta `<img>` apuntando a `/images/tu-foto.jpg`

Imágenes a reemplazar:
- **Hero:** imagen de granos de café
- **Futuras secciones:** fotos del proceso, productos, Carlos tostando, etc.

---

## Comandos principales

```bash
# Instalar dependencias (primera vez)
npm install

# Iniciar servidor de desarrollo (verás cambios en vivo)
npm run dev
# → Abre http://localhost:4321

# Compilar el sitio para producción
npm run build
# → Genera la carpeta dist/ con todo listo para subir

# Previsualizar el build
npm run preview

# Verificar tipos TypeScript
npm run check
```

---

## Deploy a Netlify (paso a paso)

### Opción A — Deploy desde GitHub (recomendado)

1. Sube este proyecto a un repositorio de GitHub
2. Ve a [netlify.com](https://netlify.com) y conecta tu cuenta
3. Click en "Add new site" → "Import an existing project"
4. Selecciona tu repositorio
5. Netlify detecta automáticamente que es Astro:
   - Build command: `npm run build`
   - Publish directory: `dist`
6. Click "Deploy"
7. Tu sitio estará en `https://cafecenit.netlify.app`

### Opción B — Deploy manual (sin Git)

1. En tu computadora, ejecuta `npm run build`
2. Esto crea una carpeta `dist/`
3. En Netlify, click "Add new site" → "Deploy manually"
4. Arrastra la carpeta `dist/` al área de upload
5. Listo

### Configurar un dominio personalizado (ej. cafecenit.com.ve)

1. Compra el dominio donde prefieras (Namecheap, GoDaddy, etc.)
2. En Netlify: Site settings → Domain management → Add custom domain
3. Sigue las instrucciones para apuntar los DNS
4. Netlify configura HTTPS automático (incluido en el plan gratuito)

### Cambiar la URL del sitio en el código

Una vez tengas tu dominio, edita estos archivos:

**`astro.config.mjs`:**
```js
site: 'https://cafecenit.com.ve',  // ← tu dominio real
```

**`public/robots.txt`:**
```
Sitemap: https://cafecenit.com.ve/sitemap-index.xml
```

---

## El switcher de moneda (USD ⇄ Bs.)

El sitio muestra precios en **USD por defecto**. El switcher en la esquina
superior derecha convierte a **bolívares usando la tasa oficial del BCV**.

### ¿Cómo funciona?

- Al cargar la página, un pequeño script consulta la API pública
  [dolarapi.com](https://ve.dolarapi.com/v1/dolares/oficial)
- Si la API responde, los precios se actualizan al instante
- Si la API **cae**, usa una API de respaldo
- Si **ambas caen**, usa una tasa manual de `site.json`
- Si todo falla, los precios en USD siguen visibles y el switcher muestra
  "No disponible"

### Cambiar la tasa manual de respaldo

Edita `src/content/site.json`:

```json
"fallback_rate_ves_per_usd": 36.5
```

---

## Solución de problemas

### La build falla

```bash
rm -rf node_modules dist
npm install
npm run build
```

### El switcher no muestra la tasa

- Abre la consola del navegador (F12 → Console)
- Verás logs del `currency-switcher.ts`
- La API puede estar caída; revisá [status.dolarapi.com](https://status.dolarapi.com) o similar

### Cambios no se ven

- Hacé un rebuild: `npm run build`
- Si usás `npm run dev`, los cambios son automáticos
- Limpia caché del navegador (Ctrl+Shift+R)

### El formulario no envía

El formulario actual usa `mailto:` (abre el cliente de email del usuario).
Si querés un envío directo sin abrir el email, recomendamos:

- **Formspree** (gratis hasta 50 envíos/mes) — https://formspree.io
- **Netlify Forms** (gratis hasta 100 envíos/mes) — nativo en Netlify
- **Resend** (gratis hasta 100 emails/día) — https://resend.com

---

## Próximos pasos sugeridos

- [ ] Reemplazar placeholders de testimonios
- [ ] Agregar fotos reales del proceso
- [ ] Cambiar el logo cuando esté listo
- [ ] Configurar dominio personalizado
- [ ] Configurar analytics simples (Plausible o Umami, ambos respetuosos de privacidad)
- [ ] Crear página de política de privacidad (requerida para analytics)
- [ ] (Opcional) Agregar Instagram feed embebido

---

## Créditos

- **Diseño y desarrollo:** [A2LT Soluciones](https://a2lt.netlify.app)
- **Cliente:** Café Cenit
- **Stack:** Astro 5 · Tailwind CSS v4 · TypeScript
- **Hosting:** Netlify
- **Tipografías:** Fraunces + Inter (Google Fonts)

---

> "¿Dudas? Escribinos a **contacto@a2lt.com**"
