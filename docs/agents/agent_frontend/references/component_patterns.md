# component_patterns.md
# Agent: agent_frontend
# Purpose: Base markup patterns per component type
# Version: 1.0

---

## RULE
Always load this file before generating any .astro component.
Apply the base pattern for the declared component_type.
Do NOT deviate from heading hierarchy or ARIA patterns.

---

## PATTERN: header

```astro
---
interface Props {
  logo_text:  string
  logo_url?:  string
  nav_items:  { label: string; href: string }[]
  cta_label?: string
  cta_href?:  string
}
const { logo_text, logo_url = "/", nav_items, cta_label, cta_href } = Astro.props
---
<header class="sticky top-0 z-[var(--z-sticky)] bg-[var(--color-surface)]
               border-b border-[var(--color-border)]">
  <div class="max-w-7xl mx-auto px-4 md:px-8 h-16 flex items-center justify-between">
    <a href={logo_url}
       class="text-xl font-[var(--weight-bold)] text-[var(--color-text-primary)]
              hover:text-[var(--color-primary-600)] transition-colors">
      {logo_text}
    </a>
    <nav class="hidden md:flex items-center gap-8" aria-label="Navegacion principal">
      {nav_items.map(item => (
        <a href={item.href}
           class="text-sm text-[var(--color-text-secondary)]
                  hover:text-[var(--color-text-primary)] transition-colors">
          {item.label}
        </a>
      ))}
    </nav>
    {cta_label && (
      <a href={cta_href ?? "#"}
         class="hidden md:inline-flex items-center px-4 py-2 rounded-[var(--radius-lg)]
                bg-[var(--color-primary-500)] text-[var(--color-text-inverse)]
                text-sm font-[var(--weight-medium)]
                hover:bg-[var(--color-primary-600)]
                focus-visible:outline-none focus-visible:ring-2
                focus-visible:ring-[var(--color-border-focus)] transition-colors">
        {cta_label}
      </a>
    )}
    <button class="md:hidden p-2 rounded-[var(--radius-md)]
                   hover:bg-[var(--color-surface-alt)]
                   focus-visible:outline-none focus-visible:ring-2
                   focus-visible:ring-[var(--color-border-focus)]"
            aria-label="Abrir menu" aria-expanded="false">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16"/>
      </svg>
    </button>
  </div>
</header>
```

---

## PATTERN: hero

```astro
---
interface Props {
  headline:            string
  subheadline:         string
  cta_primary:         string
  cta_primary_href:    string
  cta_secondary?:      string
  cta_secondary_href?: string
}
const { headline, subheadline, cta_primary, cta_primary_href,
        cta_secondary, cta_secondary_href } = Astro.props
---
<section class="bg-[var(--color-background)] py-16 md:py-24">
  <div class="max-w-4xl mx-auto px-4 md:px-8 text-center">
    <h1 class="text-4xl md:text-5xl lg:text-6xl font-[var(--weight-bold)]
               leading-[var(--leading-tight)] text-[var(--color-text-primary)] mb-6">
      {headline}
    </h1>
    <p class="text-lg md:text-xl text-[var(--color-text-secondary)]
              leading-[var(--leading-relaxed)] mb-10 max-w-2xl mx-auto">
      {subheadline}
    </p>
    <div class="flex flex-col sm:flex-row gap-4 justify-center">
      <a href={cta_primary_href}
         class="inline-flex items-center justify-center px-8 py-3
                rounded-[var(--radius-lg)] bg-[var(--color-primary-500)]
                text-[var(--color-text-inverse)] font-[var(--weight-medium)]
                hover:bg-[var(--color-primary-600)]
                focus-visible:outline-none focus-visible:ring-2
                focus-visible:ring-[var(--color-border-focus)]
                transition-colors shadow-[var(--shadow-md)]">
        {cta_primary}
      </a>
      {cta_secondary && (
        <a href={cta_secondary_href ?? "#"}
           class="inline-flex items-center justify-center px-8 py-3
                  rounded-[var(--radius-lg)] border border-[var(--color-border)]
                  bg-[var(--color-surface)] text-[var(--color-text-primary)]
                  font-[var(--weight-medium)]
                  hover:bg-[var(--color-surface-alt)]
                  focus-visible:outline-none focus-visible:ring-2
                  focus-visible:ring-[var(--color-border-focus)] transition-colors">
          {cta_secondary}
        </a>
      )}
    </div>
  </div>
</section>
```

---

## PATTERN: form

```astro
---
interface Props {
  title:        string
  submit_label: string
  fields: { name: string; label: string; type: string;
            placeholder: string; required: boolean; options?: string[] }[]
}
const { title, submit_label, fields } = Astro.props
---
<section class="py-12 md:py-16">
  <div class="max-w-xl mx-auto px-4 md:px-8">
    <h2 class="text-2xl md:text-3xl font-[var(--weight-bold)]
               text-[var(--color-text-primary)] mb-8 text-center">{title}</h2>
    <form class="space-y-6" novalidate>
      {fields.map(field => (
        <div>
          <label for={field.name}
                 class="block text-sm font-[var(--weight-medium)]
                        text-[var(--color-text-primary)] mb-1.5">
            {field.label}
            {field.required && <span class="text-[var(--color-error)] ml-1" aria-hidden="true">*</span>}
          </label>
          {field.type === "textarea" ? (
            <textarea id={field.name} name={field.name} rows={4}
              placeholder={field.placeholder} required={field.required}
              class="w-full px-3 py-2 rounded-[var(--radius-md)] border
                     border-[var(--color-border)] bg-[var(--color-surface)]
                     text-[var(--color-text-primary)] text-sm
                     placeholder:text-[var(--color-text-muted)]
                     focus:outline-none focus:border-[var(--color-border-focus)]
                     focus:ring-1 focus:ring-[var(--color-border-focus)]
                     transition-colors resize-none" />
          ) : (
            <input id={field.name} name={field.name} type={field.type}
              placeholder={field.placeholder} required={field.required}
              class="w-full px-3 py-2 rounded-[var(--radius-md)] border
                     border-[var(--color-border)] bg-[var(--color-surface)]
                     text-[var(--color-text-primary)] text-sm
                     placeholder:text-[var(--color-text-muted)]
                     focus:outline-none focus:border-[var(--color-border-focus)]
                     focus:ring-1 focus:ring-[var(--color-border-focus)]
                     transition-colors" />
          )}
        </div>
      ))}
      <button type="submit"
              class="w-full px-6 py-3 rounded-[var(--radius-lg)]
                     bg-[var(--color-primary-500)] text-[var(--color-text-inverse)]
                     font-[var(--weight-medium)] text-sm
                     hover:bg-[var(--color-primary-600)]
                     focus-visible:outline-none focus-visible:ring-2
                     focus-visible:ring-[var(--color-border-focus)]
                     disabled:bg-[var(--color-neutral-200)]
                     disabled:text-[var(--color-text-muted)]
                     disabled:cursor-not-allowed transition-colors">
        {submit_label}
      </button>
    </form>
  </div>
</section>
```

---

## PATTERN: card

```astro
---
interface Props {
  title:       string
  description: string
  href?:       string
  image?:      string
  image_alt?:  string
  badge?:      string
}
const { title, description, href, image, image_alt = "", badge } = Astro.props
---
<article class="bg-[var(--color-surface)] border border-[var(--color-border)]
                rounded-[var(--radius-xl)] shadow-[var(--shadow-md)]
                hover:shadow-[var(--shadow-lg)] transition-shadow overflow-hidden">
  {image && <img src={image} alt={image_alt} class="w-full h-48 object-cover" loading="lazy" />}
  <div class="p-6">
    {badge && (
      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs
                   font-[var(--weight-medium)] bg-[var(--color-primary-100)]
                   text-[var(--color-primary-700)] mb-3">{badge}</span>
    )}
    <h3 class="text-lg font-[var(--weight-semibold)] text-[var(--color-text-primary)] mb-2">
      {title}
    </h3>
    <p class="text-sm text-[var(--color-text-secondary)] leading-[var(--leading-relaxed)]">
      {description}
    </p>
    {href && (
      <a href={href}
         class="inline-flex items-center mt-4 text-sm font-[var(--weight-medium)]
                text-[var(--color-text-link)] hover:text-[var(--color-text-link-hover)]
                focus-visible:outline-none focus-visible:underline transition-colors">
        Ver mas
        <svg class="ml-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
        </svg>
      </a>
    )}
  </div>
</article>
```

---

## PATTERN: footer

```astro
---
interface Props {
  business_name:   string
  columns:         { title: string; links: { label: string; href: string }[] }[]
  copyright_year?: number
}
const { business_name, columns, copyright_year = new Date().getFullYear() } = Astro.props
---
<footer class="bg-[var(--color-neutral-900)] text-[var(--color-neutral-300)] py-12 md:py-16">
  <div class="max-w-7xl mx-auto px-4 md:px-8">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
      {columns.map(col => (
        <div>
          <h4 class="text-sm font-[var(--weight-semibold)] text-[var(--color-neutral-50)]
                     mb-4 uppercase tracking-wide">{col.title}</h4>
          <ul class="space-y-3">
            {col.links.map(link => (
              <li>
                <a href={link.href}
                   class="text-sm hover:text-[var(--color-neutral-50)]
                          focus-visible:outline-none focus-visible:underline transition-colors">
                  {link.label}
                </a>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
    <div class="border-t border-[var(--color-neutral-700)] pt-8
                flex flex-col md:flex-row items-center justify-between gap-4">
      <p class="text-sm">© {copyright_year} {business_name}. Todos los derechos reservados.</p>
    </div>
  </div>
</footer>
```

---

## PATTERN: modal

```astro
---
interface Props {
  id:           string
  title:        string
  description?: string
}
const { id, title, description } = Astro.props
---
<div id={id} role="dialog" aria-modal="true" aria-labelledby={`${id}-title`}
     class="hidden fixed inset-0 z-[var(--z-modal)]">
  <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" aria-hidden="true"/>
  <div class="relative z-10 flex items-center justify-center min-h-full p-4">
    <div class="w-full max-w-md bg-[var(--color-surface)]
                rounded-[var(--radius-2xl)] shadow-[var(--shadow-2xl)] p-6">
      <div class="flex items-start justify-between mb-4">
        <h2 id={`${id}-title`}
            class="text-xl font-[var(--weight-semibold)] text-[var(--color-text-primary)]">
          {title}
        </h2>
        <button aria-label="Cerrar"
                class="ml-4 p-1 rounded-[var(--radius-md)]
                       hover:bg-[var(--color-surface-alt)]
                       focus-visible:outline-none focus-visible:ring-2
                       focus-visible:ring-[var(--color-border-focus)] transition-colors">
          <svg class="w-5 h-5 text-[var(--color-text-muted)]"
               fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
      {description && (
        <p class="text-sm text-[var(--color-text-secondary)]
                  leading-[var(--leading-relaxed)] mb-6">{description}</p>
      )}
      <slot />
    </div>
  </div>
</div>
```

---

## ACCESSIBILITY CHECKLIST

```
[] All interactive elements have focus-visible styles
[] Images have descriptive alt attributes
[] Form inputs have associated label via for/id pair
[] Heading hierarchy respected: h1 -> h2 -> h3 (no skipping)
[] Color contrast: text on background >= 4.5:1 (WCAG AA)
[] Modal has role="dialog" + aria-modal="true" + aria-labelledby
[] Buttons have aria-label when icon-only
[] Nav has aria-label to distinguish multiple nav elements
[] No tabindex > 0 anywhere
[] No outline: none without focus-visible alternative
```
