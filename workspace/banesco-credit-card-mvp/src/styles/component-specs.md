# Component Specifications — Banesco Credit Card Tracker

## 1. Card Widget (Dynamic Leverage)
- **Visuals:** Uses the gradient defined in `design-tokens.json` based on the card theme.
- **Effects:** `backdrop-blur-md`, `shadow-xl`, and `rounded-2xl`.
- **Dynamic Badges:** 
    - **Green:** Maximum financing (> 35 days).
    - **Yellow:** Medium financing (20-35 days).
    - **Red:** Critical/Corte proximity (< 20 days).
- **Content:** Card name, last 4 digits, days of interest-free financing, and projected payment date.

## 2. Paste Box (Bulk Ingestion)
- **Layout:** Large textarea with a premium glassmorphism effect (`bg-slate-800/50 backdrop-blur-lg`).
- **Interaction:** Single-click processing with a loading state indicator.
- **Feedback:** Toast messages in the top-right corner with smooth transitions (Emerald for success, Rose for errors).

## 3. Financial Dashboard
- **Metric Cards:** Display consolidated debt (VES/USD) using a high-contrast typography.
- **Transactions Table:** 
    - Zebra striping using `bg-slate-900/50` and `bg-slate-800/50`.
    - Amount indicators: Green for income/payments, Rose for consumptions.
- **Tabs:** Active tab highlighted with a bottom border in the card's primary color.

## 4. Rate Control Interface
- **Input Style:** Minimalist inline editing for BCV and Binance rates.
- **Visual Cues:** Pulse animation for rates that were updated within the last hour.
