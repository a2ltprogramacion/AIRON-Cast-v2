# Component Specs — Café Cenit

> Generado por `ux-ui_specialist` · Wireframes ASCII para implementación
> Referencia: `astro-landing-kit` y `ui-ux-pro-max` (arquetipo Modern Clinic + artesanal)

---

## 1. Navbar (Sticky)

```
┌─────────────────────────────────────────────────────────────┐
│ ☕ Café Cenit   Inicio · Proceso · Cafés · Testimonios ·   │
│                                          [USD⇄Bs] [Pedir]  │
└─────────────────────────────────────────────────────────────┘
```

- **Mobile:** Logo + hamburguesa (drawer fullscreen)
- **Desktop:** Logo + nav links + switcher + CTA "Pedir por WhatsApp"
- **Scroll:** fondo transparente → backdrop-blur al pasar 80px
- **Sticky:** `position: sticky; top: 0; z-index: 50`

---

## 2. Hero (Offset Overlap 60/40)

```
┌─────────────────────────────────────────────────────────────┐
│   [Badge: Tostado a pedido]                                │
│                                                             │
│   Café tostado cuando lo                                     │
│   pedís. Ni un día antes.         [Imagen granos]           │
│                                                             │
│   Origen único venezolano,                                  │
│   empacado al vacío el mismo día.                           │
│                                                             │
│   [Pedir por WhatsApp]  [Ver los cafés →]                  │
└─────────────────────────────────────────────────────────────┘
```

- Layout: split 60% texto / 40% imagen en desktop
- Imagen: provisional Unsplash (café beans, coffee roasting)
- Background: `--color-bg-cream` con textura sutil opcional

---

## 3. Proceso (3 columnas)

```
┌─────────────────────────────────────────────────────────────┐
│              De la finca a tu taza                          │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ [ícono]  │  │ [ícono]  │  │ [ícono]  │                  │
│  │ ①        │  │ ②        │  │ ③        │                  │
│  │Seleccion.│  │ Tostado  │  │  Envío   │                  │
│  │ del grano│  │ artesanal│  │inmediato │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

- Background: `--color-bg-paper` (zebra)
- Grid: 1 col mobile, 3 col desktop
- Íconos: SVG inline con stroke `--color-ember-500`

---

## 4. Productos (3 cards premium)

```
┌─────────────────────────────────────────────────────────────┐
│              Tres perfiles, un mismo cuidado                 │
│                                                             │
│ ┌─────────┐  ┌─────────┐  ┌─────────┐                       │
│ │  ☕     │  │  🔥     │  │  🌙     │                       │
│ │ Suave   │  │ Intenso │  │ Descaf. │                       │
│ │ $8 USD  │  │ $10 USD │  │ $11 USD │                       │
│ │         │  │         │  │         │                       │
│ │ • Choc  │  │ • Cacao │  │ • Cacao │                       │
│ │ • Caram.│  │ • Panela│  │ • Nuez  │                       │
│ │ • Almend│  │ • Espec.│  │ • Gall. │                       │
│ │         │  │         │  │         │                       │
│ │[Pedir]  │  │[Pedir]  │  │[Pedir]  │                       │
│ └─────────┘  └─────────┘  └─────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

- Card: `background: white`, `border-radius: 1.5rem`, sombra al hover
- Precio: `text-3xl font-heading font-bold text-roast-900`
- Botón "Pedir": `--color-ember-500` → hover `--color-ember-600`
- Cada botón abre WhatsApp con mensaje pre-cargado: "Hola Café Cenit, quiero pedir el [Suave/Intenso/Descafeinado]"

---

## 5. Testimonios (3 placeholders)

```
┌─────────────────────────────────────────────────────────────┐
│              Lo que dicen nuestros clientes                 │
│                                                             │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│ │  ⭐⭐⭐⭐⭐ │  │  ⭐⭐⭐⭐⭐ │  │  ⭐⭐⭐⭐⭐ │                   │
│ │  "[...]" │  │  "[...]" │  │  "[...]" │                   │
│ │  — Nom 1 │  │  — Nom 2 │  │  — Nom 3 │                   │
│ │  Ciudad  │  │  Ciudad  │  │  Ciudad  │                   │
│ └──────────┘  └──────────┘  └──────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

- Background: `--color-bg-cream`
- Cards con borde sutil
- Textos marcados como PLACEHOLDER para Carlos

---

## 6. Contacto (Form + nota WhatsApp)

```
┌─────────────────────────────────────────────────────────────┐
│              Pedinos o preguntanos                          │
│                                                             │
│ ┌─────────────────────────┐  ┌──────────────────────────┐  │
│ │ Nombre:    [_________]  │  │  ¿Preferís WhatsApp?     │  │
│ │ Email:     [_________]  │  │                          │  │
│ │ Mensaje:   [_________]  │  │  [Abrir WhatsApp →]      │  │
│ │            [_________]  │  │                          │  │
│ │            [Enviar →]   │  │  Respondemos en menos    │  │
│ │                         │  │  de 24h.                 │  │
│ └─────────────────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

- Form: HTML5 con validación nativa
- Action: `mailto:hola@cafecenit.com.ve` (placeholder) — Carlos puede cambiar a Formspree/Resend después
- Layout: 2 col desktop, 1 col mobile

---

## 7. Footer (4 columnas)

```
┌─────────────────────────────────────────────────────────────┐
│ ☕ Café Cenit    Enlaces       Contacto     Seguinos        │
│ Tostado a       · Inicio      · WhatsApp    [IG] [WA]      │
│ pedido,         · Proceso     · Email       [FB] [TT]      │
│ siempre.        · Cafés                     [YT]            │
│                 · Testimonios                                │
│                 · Contacto                                   │
│                                                             │
│ ─────────────────────────────────────────────────────────  │
│ © 2026 Café Cenit · Designed by A2LT Soluciones             │
└─────────────────────────────────────────────────────────────┘
```

- Background: `--color-roast-900` (oscuro pero cálido) con texto crema
- Crédito A2LT siempre presente

---

## 8. Botón Flotante WhatsApp

```
                                          ┌─────┐
                                          │  📱 │  ← siempre fixed bottom-right
                                          │     │
                                          └─────┘
```

- `position: fixed; bottom: 1.5rem; right: 1.5rem; z-index: 100`
- Background: `--color-brand-whatsapp`
- Animación `pulse-subtle` cada 2.4s
- aria-label: "Abrir conversación de WhatsApp"
