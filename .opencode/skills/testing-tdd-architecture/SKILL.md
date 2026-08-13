---
name: testing-tdd-architecture
version: 1.0.0
type: utility
subtype: skill
tier: all
description: |
  Testing and TDD architecture for AIRON‑Cast. Enforces strict testing
  mandates (Pytest for Python, Vitest/Playwright for Astro), >80% coverage,
  and code review audits across functionality, security, performance, and
  test coverage.
  Trigger phrases: "TDD", "pytest", "playwright", "vitest", "cobertura",
  "test coverage", "integration test", "unit test".
  Do NOT activate for manual code review without automated testing context.
triggers:
  primary: ["TDD", "pytest", "playwright", "cobertura"]
  secondary: ["vitest", "integration test", "unit test"]
  context: ["testing", "quality assurance", "CI/CD"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - qa_auditor
  - tester
last_used: 2026-06-05
scope: restricted
---

# Testing Architecture & TDD Workflow (AIRON‑Cast Standard)

This skill defines how automated testing and Test-Driven Development (TDD)
are executed across AIRON‑Cast projects. It consolidates Python Backend
(Pytest), Frontend/E2E (Vitest/Playwright), and Code Review audits into
a single quality gate.

---

## PART 1: Core TDD Principles

Before writing any production logic, the testing cycle must dictate the design:

1. **Write the Failing Test:** Define the exact User Journey or API Contract.
2. **Execute:** Watch it fail.
3. **Write Minimum Code:** Write only enough code to make the test pass.
4. **Refactor:** Clean the code without altering behavior.

**Mandate:** Minimum **80% coverage** across Unit, Integration, and E2E
boundaries.

---

## PART 2: Python Backend Testing (Pytest)

Django Services and utilities must be exhaustively tested using the `AAA`
Pattern (Arrange, Act, Assert) without polluting the actual database.

### 2.1 Fixtures (State Management)

Never pollute the global state. Inject strictly scoped fixtures.

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

### 2.2 Mocking & Time Freezing

External APIs and Time constraints must always be mocked using `unittest.mock`
and `freezegun`. Never hit real external APIs during tests.

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

## PART 3: Frontend Unit & Integration (Vitest)

For Astro components, test the **User-Visible Behavior**, never the
internal state.

- **❌ WRONG:** `expect(component.state.count).toBe(5)`
- **✅ CORRECT:** `expect(screen.getByText('Count: 5')).toBeInTheDocument()`

### 3.1 Semantic Selectors Only

Never use brittle CSS classes to find elements in tests.

```typescript
// Resilient to Tailwind changes
await fireEvent.click(screen.getByRole("button", { name: /Submit/i }));
```

---

## PART 4: End-to-End Testing (Playwright)

E2E tests simulate actual browser behavior. Follow the
**Reconnaissance-Then-Action** Pattern.

### 4.1 The Network Idle Rule (Critical)

For dynamic applications (SPAs/Astro Islands), inspecting the DOM before
JS executes guarantees flaky tests.

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

## PART 5: Testing Anti-Patterns (Immediate Rejection)

- **Dependency between tests:** `test_2()` failing because `test_1()` didn't
  run. Every test must set up its own data.
- **Testing Implementation Details:** Failing a test because a variable was
  renamed internally, even if the output remained identical.
- **Ignoring Error Paths:** Only writing tests for the "Happy Path". You
  MUST explicitly write tests triggering HTTP 400, 404, and 500 scenarios.

---

## PART 6: Code Review & QA Audit

This skill activates as the final gatekeeper before code is considered
"complete". It mandates a rigorous inspection across multiple layers.

### 6.1 Functional Verification

- Does the code resolve the precise objective without introducing
  out-of-scope logic?
- Are edge cases (empty states, zero values, massive payloads) handled
  gracefully?

### 6.2 Security & Data Protection

- **Injection:** Are SQL queries parameterized? Are XSS strings sanitized?
- **Authentication/Authorization:** Is the endpoint actively validating
  session/JWT tokens? Does it verify the user owns the resource?
- **Hardcoded Secrets:** Scrape the payload for leaked API keys, `.env`
  fallbacks, or raw database credentials. Halt immediately if found.

### 6.3 Performance & Structural Integrity

- **N+1 Queries:** Does a loop execute a database hit per iteration?
- **DRY / Modularity:** Have duplicate blocks of logic been hoisted into
  a shared utility or base class?

### 6.4 Test Coverage Validation (The 80% Rule)

- All new business logic MUST be accompanied by a Unit/Integration test.
- If a PR fixes a bug but includes zero tests to prevent future
  regressions, the PR is **Rejected**.

---

### 6.5 Actionable Feedback Mode

When utilizing this skill, output feedback linearly:

- `[CRITICAL]` For security / crash risks.
- `[ARCH]` For structural improvements (Clean Code violations).
- `[TESTS]` For missing coverage.

---

## 🔗 AIRON‑Cast Integration

This skill is consumed by:
- `qa_auditor` — to execute tests, validate coverage, and perform code
  reviews before approving any task.

Test files go to `workspace/<slug>/tests/`.