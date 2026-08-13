# Astro Frontend Setup

Follow these exact CLI instructions to scaffold the A2LT standard frontend. **Do not use interactive prompts** if you can pass flags to bypass them.

## 1. Initialization

1. Navigate to the root of the project.
2. Run the Astro creation script.

```bash
# Create the frontend directory automatically
npx create-astro@latest frontend --template minimal --install --no-git --yes

# Install Type-Checking Tool (MANDATORY for CI/CD)
cd frontend
npm install @astrojs/check typescript --save-dev
```

### Decap CMS Configuration (Local Backend)

When configuring Decap CMS (`public/admin/config.yml`), you MUST always include the `local_backend: true` flag during development to allow the local server proxy to work.

## 2. Tailwind Configuration

Tailwind CSS is the absolute standard for styling in A2LT projects. You MUST install it globally for the Astro project immediately after initialization.

```bash
cd frontend
# FORCED DOWNGRADE: @astrojs/tailwind currently demands Tailwind ^3.0.24.
# Avoid Tailwind v4 until the official integration is fully compatible.
npm install tailwindcss@^3.4.0 @astrojs/tailwind postcss autoprefixer
npx astro add tailwind --yes
```

This automates the installation of `tailwindcss`, `@astrojs/tailwind`, and creates the base configuration files. Ensure tailwind is locked to version 3.x.

## 3. Basic Refinements

1. **Delete Boilerplate:** Remove the default placeholder text in `frontend/src/pages/index.astro`.
2. **Global Base:** Ensure that the Tailwind directives are properly injected into a base layout, usually by creating `src/layouts/Layout.astro` and importing global CSS if necessary.
3. **PWA Preparedness:** Remind the user if they want to install `@vite-pwa/astro` for progressive web app features, as A2LT focuses on web-native mobile solutions.

## 4. Astro 5 Natively Directives (CRITICAL)

- **Content Collections (Windows Safe):** ALWAYS use the new Astro 5 Content Layer API with `loader: glob()`. NEVER use `type: 'content'` as it causes silent `InvalidContentEntryDataError` validation failures in Windows environments.
- **JSX Parser Fragility in `.astro` Files:** Avoid using generics like `CollectionEntry<'services'>` directly inside `.astro` template expressions (like `.sort()` callbacks or inline maps), because the Astro parser confuses `< >` with JSX Fragments. Either cast to `any` (e.g., `(a: any, b: any)`) or define the typed function in the frontmatter script boundary `---` before passing it to the HTML template.

## 5. Running the Dev Server

The command to start the frontend server locally is:

```bash
npm run dev
```
