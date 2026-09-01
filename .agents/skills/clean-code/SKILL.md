---
name: clean-code
description: "Estándares de Código Limpio (Clean Code). Aplicación profunda de los principios de Robert C. Martin (Uncle Bob) para todo el stack A2LT: Python/Django, Astro, Vanilla JS/TS y HTML semántico."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Clean Code Skill (A2LT Standard)

This skill embodies the principles of "Clean Code" by Robert C. Martin (Uncle Bob), adapted for the **entire** A2LT technology stack: Python (Django), Astro, JavaScript/TypeScript, and HTML. Use it to transform "code that works" into robust, enterprise-grade code across both the Backend and Frontend.

## 🧠 Core Philosophy

> "Code is clean if it can be read, and enhanced by a developer other than its original author." — Grady Booch

## 1. Meaningful Names

- **Intention-Revealing:** Variables must answer why they exist. Use `days_since_creation`, not `d`.
- **Avoid Disinformation:** Don't use `user_list` if it's actually a dictionary or Map. Use `user_map`.
- **Pronounceable/Searchable:** Avoid acronyms like `genymdhms`. Use `generation_timestamp`.
- **Classes/Components:** Use nouns (`Customer`, `PaymentGateway`, `ProductCard.astro`). Avoid `Manager` or `Processor` if possible.
- **Method/Function Names:** Use verbs indicating the action (`calculate_total()`, `fetchUserData()`, `renderHeroSection()`).
- **Booleans:** Prefix with questions (`is_active`, `hasPermission`, `canEdit`).

## 2. Functions & UI Components

- **Extreme Brevity:** The ideal function or Astro component logic block is smaller than 20 lines.
- **Single Responsibility (SRP):** A function or component must do ONE thing.
  - _Backend:_ If `extract_and_save_data()` exists, split it.
  - _Frontend:_ An Astro component should not fetch data, format dates, and render 5 nested layouts. Split it into smaller `.astro` files.
- **One Level of Abstraction:** Don't mix high-level business logic with low-level details (like manual regex parsing or direct DOM manipulation in JS). Delegate.
- **Argument/Props Minimization:** 0-2 arguments is ideal. For Astro components, if you pass more than 3 props, group them into an interface or Type (e.g., `interface ProductProps`).
- **No Side Effects:** A function named `validate_password` must ONLY return a boolean; it must not secretly reset the session or mutate the `window` object in JS.

## 3. Comments (The "No Comment" Rule)

- **Self-Documenting Code:** Don't comment bad code—rewrite it. If you feel the need to explain _what_ a block does, extract it into a well-named function or a smaller Astro component.
  _Bad (Python):_ `# Check if employee is eligible` -> `if employee.flags & HOURLY and employee.age > 65:`
  _Good (Python):_ `if employee.is_eligible_for_benefits():`
  _Bad (HTML):_ `<!-- Wrapper div for the user profile header --> <div>...</div>`
  _Good (HTML):_ `<header class="user-profile-header">...</header>`
- **Good Comments:** Only explain _WHY_ an unusual technical decision was made (e.g., `// Using bitwise OR to match the third-party legacy API`). Legal notices and TODOs are also acceptable.
- **Docstrings / JSDoc:** Required for public API logic in Python and exported utilities in TS. DO NOT mumble or restate the function name.

## 4. Formatting & Structure

- **The Newspaper Metaphor:** High-level concepts at the top of the file, deep implementation details at the bottom.
- **Vertical Density:** Related lines (e.g., configuring an object) should be grouped together without blank lines in between.
- **Distance:** Variables should be declared as close to their usage as possible.
- **Indentation:** Adhere strictly to PEP 8 for Python and Prettier for JS/TS/Astro. HTML must be perfectly nested.

## 5. Objects and Data Structures

- **Data Abstraction:** Hide implementation details behind methods (encapsulation).
- **The Law of Demeter:** A module should not know about the innards of the objects it manipulates. Avoid deep chaining: `a.get_b().get_c().do_something()` or `document.getElementById('a').parentNode.childNodes[0]`.
- **Data Transfer Objects (DTO):** Use standard Python `dataclasses` or TypeScript `Interfaces`/`Types` when passing complex data between layers.

## 6. Error Handling

- **Use Exceptions, Not Codes:** Never return `-1`, `False`, or `null` to indicate systemic failure. Raise semantic exceptions (e.g., `ValueError`, `throw new Error('Invalid input')`).
- **Fail Fast:** Check preconditions at the very top of the function and abort immediately.
- **Don't Pass Null:** Avoid passing `None` or `null` as an argument if it causes complex branching deep in the code. Use default objects or early returns.

## 7. HTML and Astro Specific Patterns

- **Semantic HTML:** Use `<article>`, `<section>`, `<nav>`, `<aside>` instead of infinite `<div>` soup.
- **CSS Utility Classes:** Tailwind classes should be ordered logically (Base layout -> spacing -> typography -> colors). Extract extremely long strings of classes into structural CSS or Astro `<style>` if they ruin template readability.
- **Framework Agnostic:** Do not write React/Vue hooks in plain JS scripts or Astro frontmatter. Keep framework lifecycles out unless explicitly inside an Island.

## 8. Classes

- **Small!:** Classes should have a single responsibility.
- **Cohesion:** A class has high cohesion if its methods use the majority of its instance variables.

## 9. Code Smells to Eradicate

- **Rigidity:** The system is hard to change because every change forces many others.
- **Fragility:** Changes cause the system to break in conceptually unrelated places.
- **Immobility:** It's hard to detangle the system into components that can be reused.
- **Viscosity:** Doing things right is harder than doing things wrong (hacks).

## 🛠️ Validation Checklist

Before finalizing a code edit, verify:

- [ ] Is this function/component smaller than 20-30 lines?
- [ ] Does this function do exactly one thing without side-effects?
- [ ] Are all variable, function, and Astro Prop names intention-revealing?
- [ ] Have I avoided comments by making the code structure (and HTML tags) clearer?
- [ ] Have I used exact HTML semantics instead of nested divs?
- [ ] Have I used exceptions instead of returning custom error codes?
