# stack_versions.md
# Agent: agent_architect
# Purpose: Pinned versions for A2LT standard stack
# Version: 1.0
# Last verified: 2026-03-17

---

## RULE
Always use versions from this file.
Never pin to "latest" — exact versions only.
Update this file when a stack upgrade is confirmed and tested.

---

## PYTHON ECOSYSTEM

### Runtime
```
Python: 3.12.3
```

### Django Stack (web_app / api)
```
Django:                         5.0.6
djangorestframework:            3.15.2
djangorestframework-simplejwt:  5.3.1
django-cors-headers:            4.3.1
drf-spectacular:                0.27.2
psycopg2-binary:                2.9.9
gunicorn:                       22.0.0
python-dotenv:                  1.0.1
Pillow:                         10.3.0
```

### Automation Stack (GHL)
```
httpx:         0.27.0
python-dotenv: 1.0.1
```

### La Forja Core
```
chromadb:             0.5.3
sentence-transformers:2.7.0
torch:                2.3.0   (CPU build — no CUDA for inference)
transformers:         4.41.1
sqlparse:             0.5.0
```

### Testing & Quality
```
pytest:        8.2.0
pytest-django: 4.8.0
factory-boy:   3.3.0
coverage:      7.5.1
flake8:        7.0.0
pylint:        3.2.2
bandit:        1.7.8
```

---

## NODE / FRONTEND ECOSYSTEM

### Runtime
```
Node.js: 20.14.0 LTS
npm:     10.7.0
```

### Astro Stack
```
astro:                4.10.2
@astrojs/tailwind:    5.1.0
tailwindcss:          3.4.4
```

### Decap CMS
```
decap-cms-app: 3.1.6
```

### Tooling
```
stylelint:                 16.6.1
stylelint-config-standard: 36.0.0
```

---

## DATABASE
```
PostgreSQL: 16.3
```

---

## KNOWN INCOMPATIBILITIES

| Package A             | Package B          | Issue                                   |
|-----------------------|--------------------|-----------------------------------------|
| Django 5.x            | psycopg2 < 2.9     | Async support requires psycopg2 2.9+    |
| drf-spectacular 0.27+ | DRF < 3.14         | Schema generation breaks                |
| sentence-transformers | torch CUDA on 3GB  | OOM — use CPU build for inference       |
| Astro 4.x             | Node.js < 18       | ESM requirements not met                |
| chromadb 0.5+         | Python < 3.10      | Type hints require 3.10+                |

---

## REQUIREMENTS SKELETONS

### web_app — requirements.txt
```
Django==5.0.6
djangorestframework==3.15.2
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
drf-spectacular==0.27.2
psycopg2-binary==2.9.9
gunicorn==22.0.0
python-dotenv==1.0.1
Pillow==10.3.0
```

### web_app — requirements-dev.txt
```
pytest==8.2.0
pytest-django==4.8.0
factory-boy==3.3.0
coverage==7.5.1
flake8==7.0.0
pylint==3.2.2
bandit==1.7.8
```

### api — requirements.txt
```
Django==5.0.6
djangorestframework==3.15.2
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
drf-spectacular==0.27.2
psycopg2-binary==2.9.9
gunicorn==22.0.0
python-dotenv==1.0.1
```

### automation — requirements.txt
```
httpx==0.27.0
python-dotenv==1.0.1
```
