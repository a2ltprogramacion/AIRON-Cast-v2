---
name: async-python-patterns
description: "Patrones Asíncronos Avanzados en Python. Dominio de `asyncio`, concurrencia, semáforos, pools de conexiones y offloading a hilos para aplicaciones ASGI (Django/FastAPI) y workers de alto rendimiento."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Async Python Patterns (A2LT Standard)

Comprehensive guidance for implementing asynchronous Python applications. In the A2LT stack, async is used for heavily I/O-bound workloads (web scrapers, concurrent API consumption) or within Django ASGI (views using `async def`).

## 1. Sync vs Async Decision Guide

**Key Rule:** Stay fully sync or fully async within a call path. Mixing creates hidden blocking and catastrophic event loop starvation.

| Use Case                         | A2LT Recommendation                         |
| -------------------------------- | ------------------------------------------- |
| Many concurrent network/DB calls | `asyncio` (`aiohttp`, FastAPI/Django ASGI)  |
| CPU-bound computation            | `multiprocessing` or ThreadPool             |
| Simple scripts, few connections  | Sync (Requests, standard Django WSGI)       |
| Mixed I/O + CPU                  | Offload CPU work with `asyncio.to_thread()` |

## 2. Fundamental Patterns

### Concurrent Execution (`asyncio.gather`)

Fire off multiple tasks simultaneously and wait for all to finish.

```python
async def fetch_all_users(user_ids: list[int]) -> list[dict]:
    # Creates an array of coroutines (un-awaited)
    tasks = [fetch_user(uid) for uid in user_ids]
    # Executes them concurrently on the event loop
    results = await asyncio.gather(*tasks)
    return results
```

### Error Handling with Gather

If one task in `gather` fails, the exception propagates and kills the gather. To prevent this:

```python
# Pass return_exceptions=True
results = await asyncio.gather(*tasks, return_exceptions=True)

successful = [r for r in results if not isinstance(r, Exception)]
failed = [r for r in results if isinstance(r, Exception)]
```

### Timeout Handling (`asyncio.wait_for`)

Never let network calls hang infinitely.

```python
try:
    result = await asyncio.wait_for(slow_operation(), timeout=5.0)
except asyncio.TimeoutError:
    logger.error("Operation timed out")
```

## 3. Advanced Synchronization

### Semaphores (Rate Limiting)

When scraping or hitting external APIs, unbounded `gather()` will get your IP banned or crash the target server.

```python
async def api_call(url: str, semaphore: asyncio.Semaphore) -> dict:
    async with semaphore:
        return await fetch(url)

async def rate_limited_requests(urls: list[str], max_concurrent: int = 5):
    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = [api_call(url, semaphore) for url in urls]
    return await asyncio.gather(*tasks)
```

### Async Iterators (`async for`)

Useful for reading large sets of paginated data asynchronously.

```python
async def fetch_pages(url: str, max_pages: int):
    for page in range(1, max_pages + 1):
        await asyncio.sleep(0.2) # Simulate API
        yield {"page": page, "data": []}

async for page_data in fetch_pages("https://api.example.com/items", 3):
    print(page_data)
```

## 4. Anti-Patterns & Blocking the Event Loop (CRITICAL)

**Never use `time.sleep()`, `requests.get()`, or synchronous Django ORM calls directly inside an `async def` function.** It freezes the entire Node/Worker.

_Bad:_

```python
async def fetch_data():
    time.sleep(1) # FATAL: Entire server freezes for 1 second.
```

_Good (Offload sync code to a thread):_

```python
async def fetch_data():
    # Runs the blocking synchronous function in a separate thread pool
    result = await asyncio.to_thread(requests.get, "https://example.com")
```

## 5. Async Database Operations (Django)

Django 4.1+ supports async ORM via `a`-prefixed methods.

- Use `await User.objects.aget(id=1)` instead of `.get()`.
- Use `async for user in User.objects.all():` instead of `for`.
- For bulk operations, wrap them in `sync_to_async`:

```python
from asgiref.sync import sync_to_async

@sync_to_async
def complex_sync_db_query():
    return list(Product.objects.select_related('category').all())
```
