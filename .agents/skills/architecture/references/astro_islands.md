# Astro Islands Architecture

A2LT Frontend applications use Astro to prioritize fast, static HTML delivery. JavaScript is expensive and should only be sent to the client when a component requires interactivity.

## The Island Concept

An "Island" is an interactive UI component (written in Vanilla JS, React, or Svelte) floating in a sea of static HTML (rendered by Astro).

## Directives for UI Architecture

### 1. Default to Static (`.astro`)

Always build components as `.astro` files first. If a component just displays data from an API, it does NOT need client-side JS.

```astro
---
// src/components/ProductCard.astro
// This runs on the server. Zero JS sent to client!
const { product } = Astro.props;
---
<div class="p-4 border shadow-sm">
    <h2>{product.name}</h2>
    <p>{product.price}</p>
</div>
```

### 2. Isolate Interactivity (The Island)

Only components with state (`useState`), browser events (`onClick`), or lifecycle effects (`useEffect`) should be built as UI Framework components (e.g., React `jsx` / Svelte).

### 3. Progressive Hydration

When you do use an interactive component, you MUST tell Astro how to load its JavaScript using a `client:*` directive. If you omit the directive, Astro will strip the JS and render it as static HTML.

- **`client:load`**: High priority. Loads JS immediately. Use for critical UI (Modals, Navbars).
- **`client:idle`**: Medium priority. Loads JS when the main thread is free. Use for non-critical tools.
- **`client:visible`**: Lazy load. Loads JS only when the component enters the viewport. Use for heavy widgets way down the page (Carousels, Video Players).

_Example of composing an Island:_

```astro
---
// src/pages/index.astro
import ProductCard from '../components/ProductCard.astro'; // Static
import AddToCartButton from '../components/AddToCartButton.jsx'; // Interactive
---

<main>
    <!-- Renders instantly as HTML -->
    <ProductCard product={data} />

    <!-- JS is only fetched and executed when this button scrolls into view -->
    <AddToCartButton productId={data.id} client:visible />
</main>
```
