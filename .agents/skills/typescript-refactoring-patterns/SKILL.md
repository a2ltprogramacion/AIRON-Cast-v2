---
name: typescript-refactoring-patterns
description: "Patrones de Refactorización en TypeScript Nivel 5. Eliminación de `any`, aserciones `as`, y primitivas obsesivas mediante Uniones Discriminadas, Type Guards, Branded Types y Const Assertions."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# TypeScript Refactoring Patterns (A2LT Standard)

Expert TypeScript refactoring patterns for cleaner, type-safe code. In the A2LT stack, these patterns are critical for Astro frontend logic, API client wrappers, and generic utility functions.

## 1. Core Principles

1. **Type Narrowing Over Type Assertions:** Use Type Guards and Discriminated Unions instead of `as` casts.
2. **Const Assertions for Literals:** Use `as const` for immutable literal types to prevent widening.
3. **Generic Constraints:** Prefer `extends` constraints over `any`.
4. **Branded Types:** Use branded types for domain-specific validation (e.g., distinguishing a UserID from a random string).

## 2. Refactoring Patterns

### Pattern 1: Extract Discriminated Union

When you see multiple boolean flags inside an interface, refactor it to a discriminated union. This explicitly prevents impossible states (e.g., being both an `admin` and a `guest` simultaneously).

**Bad (Ambiguous State):**

```typescript
interface User {
  isAdmin: boolean;
  isGuest: boolean;
  permissions?: string[];
}
```

**Good (Strict State Boundaries):**

```typescript
type User =
  | { role: "admin"; permissions: string[] }
  | { role: "guest" }
  | { role: "member"; permissions: string[] };

// TypeScript will now correctly force you to check `user.role` before accessing `user.permissions`
```

### Pattern 2: Replace Conditional with Polymorphism (Strategy)

When you see massive `switch` statements branching strictly on a type, use a Record Map (Strategy Pattern).

**Bad:**

```typescript
function process(item: Item) {
  switch (item.type) {
    case "a":
      return processA(item);
    case "b":
      return processB(item);
  }
}
```

**Good:**

```typescript
const processors: Record<ItemType, (item: Item) => Result> = {
  a: processA,
  b: processB,
};
const process = (item: Item) => processors[item.type](item);
```

### Pattern 3: Extract Type Guard

When filtering arrays or passing data boundaries, write explicit Type Guards instead of casting.

```typescript
function isNonNullable<T>(value: T): value is NonNullable<T> {
  return value !== null && value !== undefined;
}

// Automatically narrows the type from (string | null)[] to string[]
const validStrings = array.filter(isNonNullable);
```

### Pattern 4: Use Branded Types for Validation

Prevent "primitive obsession" where you accidentally pass a `ProductID` string into a function expecting a `UserID` string.

```typescript
// Define nominal types
type UserId = string & { readonly brand: unique symbol };
type Email = string & { readonly brand: unique symbol };

function createUserId(id: string): UserId {
  if (!id.match(/.../)) throw new Error('Invalid user ID');
  return id as UserId; // The ONLY place where 'as' is acceptable
}

// Now you cannot accidentally pass an Email into fetchUser()
function fetchUser(id: UserId) { ... }
```

## 3. Code Smell Detectors

Refactor immediately if you spot:

- `any` types: Replace with `unknown` and use Type Guards to parse them.
- Non-null assertions (`!`): e.g., `user.name!`. Rewrite to safely check `if (user && user.name)` or throw a deliberate runtime error.
- Type assertions (`as`): Except for Brand assertions, `as` hides errors from the compiler.
- Index signatures without validation: `Record<string, unknown>` requires a Zod/Valibot schema parser at the boundary.

## 4. Quick Wins

- Use `satisfies` to guarantee an object matches a type _without_ widening its deeper literal inferences.
- Prefer `readonly` arrays (`readonly string[]`) when data shouldn't be mutated.
