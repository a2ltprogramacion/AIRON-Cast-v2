# Requirements Specification — Banesco Credit Card Tracker & Indexer MVP

## 1. Project Overview
The Banesco Credit Card Tracker is a local financial management solution developed in Python and Django. Its primary goal is to provide precise control over credit card expenses, indexed in US Dollars (USD), while simulating financing leverage and managing payment deadlines for Banesco (Venezuela) accounts.

## 2. Technical Stack
- **Backend:** Python 3.10+ / Django 5.x.
- **Database:** SQLite (Independent local instance: `src/db.sqlite3`).
- **Frontend:** Django Templates + Tailwind CSS.
- **External APIs:**
    - BCV Rates via `DolarAPI`.
    - Binance P2P Rates via secure scraping/request simulation.

## 3. Functional Requirements

### 3.1. Credit Card Leverage Simulation
- **Dynamic Calculation:** Calculate the number of interest-free days for a purchase made on a specific date.
- **Billing Cycle Logic:**
    - **Visa Gold:** Cut-off on the 12th | Payment on the 8th of the next month.
    - **Mastercard Platinum:** Cut-off on the 3rd | Payment on the 30th of the same month.
- **Visual Feedback:** Implement a "traffic light" system (Green > 35 days, Yellow 20-35, Red < 20) to indicate financing health.

### 3.2. Data Ingestion Engine (Paste Box)
- **Regex Parsing:** Extract transaction data from Banesco notification emails in bulk.
- **Supported Formats:**
    - Credit Card (TDC) notifications.
    - Debit Card (TDD) notifications.
    - Bank Transfers (TFR) and PDF receipts.
- **De-duplication:** Implement a 4-way unique constraint (Card, Date, Amount, Reference) to prevent duplicate entries.

### 3.3. Currency Indexing and Management
- **Real-time Rates:** Automatic fetch of BCV and Binance P2P rates.
- **Daily Cache:** Maintain a historical log of rates to index past transactions.
- **Manual Overrides:** Allow manual correction of rates in case of API failure.

### 3.4. Financial Reconciliation
- **FIFO Amortization:** Apply payments to the oldest outstanding debts first.
- **Bank Statement Matching:** Cross-reference bank statement (.txt) transactions with registered card consumptions using fuzzy matching on references.
- **Auto-creation:** Automatically create debit transactions if they appear in the bank statement but not in the system.

### 3.5. Interest Calculation
- **Ordinary Interest:** Calculate financing cost based on $t/360$ formula.
- **Mora Interest:** Apply late payment penalties for transactions that exceed their payment deadline.

## 4. Non-Functional Requirements
- **Data Isolation:** The project database must remain completely independent from the AIRON-Cast central intelligence database.
- **Performance:** Regex parsing and reconciliation should be near-instant for typical user volumes.
- **UI/UX:** Premium Dark Mode interface with responsive layouts.
