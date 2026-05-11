---
name: web-design-guidelines
description: "Auditoría Vercel/A2LT de Interfaz Web. Revisa conformidad contra directrices de Accesibilidad y Mejores Prácticas Generales de UX web."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Web Interface Guidelines & Auditing (A2LT Standard)

This discrete skill serves as an auditor. It scans frontend web components to ensure compliance with official UI/UX interaction heuristics.

---

## 1. Interaction & Accessibility Checks

When evaluating `.astro`, `.tsx`, `.html`, or `.vue` components, run the following heuristics:

- **ARIA & Accessibility:** Are elements navigable purely via Keyboard (Tab indexing)? Do non-text elements possess accurate `aria-label` or `alt` tags?
- **Contrast Ratios:** Ensure text on backgrounds aligns with WCAG AA standard (Minimum 4.5:1 ratio for normal text).

## 2. Usage Mechanics

If a user requests you to "review my UI" or "audit design":

1. Review the structural layout of the JSX/HTML.
2. Determine if it breaks foundational design principles (padding inconsistency, inaccessible inputs).
3. Output findings exactly in a `file:line -> Actionable feedback` structure.

## 3. Design System Awareness (MASTER.md Integration)

If a file `design-system/<project>/MASTER.md` exists in the current workspace, it represents the project's Source of Truth for visual identity (colors, typography, spacing, shadows). When auditing:

1. Read `MASTER.md` BEFORE running generic heuristics.
2. Validate components against the MASTER's defined tokens (e.g., if MASTER defines `--color-primary: #2563EB`, flag any component using a different primary color).
3. For color contrast checks, use the specific hex values from MASTER rather than generic WCAG examples.
4. If a page override exists in `design-system/<project>/pages/<page>.md`, use its values for that specific page.

If no `MASTER.md` exists, fall back to the standard WCAG AA heuristics defined in Section 1.
