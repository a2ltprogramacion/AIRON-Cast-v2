---
name: testing-tdd-architecture
description: "Macro-Skill de Arquitectura Testing y TDD Nivel 5. Fusiona estrategias de Pytest (Fixtures/Mocking/Freezegun) para Django, con Vitest/Playwright para componentes Astro. Impone >80% de cobertura y aislamiento estricto."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Testing Architecture & TDD Workflow (A2LT Standard)

This macro-skill dictates how automated testing and Test-Driven Development (TDD) are executed across the entire A2LT Full-Stack environment. It consolidates Python Backend (Pytest) and Frontend/E2E (Vitest/Playwright).

---

## 1. Core TDD Principles (The "Tests BEFORE Code" Mandate)

Before writing any production logic, the testing cycle must dictate the design:

1. **Write the Failing Test:** Define the exact User Journey or API Contract.
2. **Execute:** Watch it fail (`npm test` or `pytest`).
3. **Write Minimum Code:** Write only enough code to make the test turn green.
4. **Refactor:** Clean the code without altering behavior.
   **Mandate:** Minimum **80% coverage** across Unit, Integration, and E2E boundaries.

---

## 2. Python Backend Testing (Pytest)

Django Services and utilities must be exhaustively tested using the `AAA` Pattern (Arrange, Act, Assert) without polluting the actual database.

### Fixtures (State Management)

Never pollute the global state. Inject strictly scoped fixtures (function, module, session).

```python
import pytest

@pytest.fixture
def fake_payment_payload():
    return {"amount": 1000, "currency": "usd"}

def test_payment_service_rejects_negative(fake_payment_payload):
    fake_payment_payload["amount"] = -50
    with pytest.raises(ValueError, match="Amount must be positive"):
        PaymentService.process(fake_payment_payload)
```

### Mocking & Time Freezing

External APIs and Time constraints must always be mocked using `unittest.mock` and `freezegun`. Never hit real external APIs (e.g., Stripe, OpenAI) during tests.

```python
from freezegun import freeze_time
from unittest.mock import patch

@freeze_time("2026-01-01 12:00:00")
@patch("apps.payments.services.stripe.PaymentIntent.create")
def test_subscription_creation(mock_stripe):
    mock_stripe.return_value = {"id": "pi_123", "status": "succeeded"}
    result = SubscriptionService.create_user_sub(user_id=1)

    assert result.is_active is True
    assert result.expires_at.year == 2026
    mock_stripe.assert_called_once()
```

---

## 3. Frontend Unit & Integration (Vitest / React Testing Lib)

For Astro/React components, test the **User-Visible Behavior**, never the internal state.

- **❌ WRONG:** `expect(component.state.count).toBe(5)`
- **✅ CORRECT:** `expect(screen.getByText('Count: 5')).toBeInTheDocument()`

### Semantic Selectors Only

Never use brittle CSS classes to find elements in tests.

```typescript
// Resilient to Tailwind changes
await fireEvent.click(screen.getByRole("button", { name: /Submit/i }));
```

---

## 4. End-to-End Testing (Playwright)

E2E tests simulate actual browser behavior. When testing workflows, follow the **Reconnaissance-Then-Action** Pattern.

### Server Lifecycle

Never write a script assuming the server is flawlessly running. In A2LT, we use isolated setups triggering backend (`python manage.py runserver`) and frontend (`npm run dev`) before executing the suite.

### The Network Idle Rule (Critical)

For dynamic applications (SPAs/Astro Islands), inspecting the DOM before JS executes guarantees flaky tests.

```python
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('http://localhost:5173')

    # CRITICAL: Wait for hydration and dynamic fetches
    page.wait_for_load_state('networkidle')

    # Now it is safe to act
    page.click('button:has-text("Login")')
```

---

## 5. Testing Anti-Patterns (Immediate Rejection)

- **Dependency between tests:** `test_2()` failing because `test_1()` didn't run. Every test must set up its own data.
- **Testing Implementation Details:** Failing a test because a variable was renamed internally, even if the output remained identical.
- **Ignoring Error Paths:** Only writing tests for the "Happy Path". You MUST explicitly write tests triggering HTTP 400, 404, and 500 scenarios to ensure they fail gracefully.
