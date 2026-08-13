# Quickreply - Guia de Desarrollo

> Para developers que van a extender o mantener el sistema.

---

## Stack y Versiones

| Componente | Version | Notas |
|---|---|---|
| Python | 3.11+ | Recomendado 3.12 |
| Django | 5.1.4 | LTS hasta 2028 |
| Django REST Framework | 3.15.2 | |
| django-cors-headers | 4.6.0 | Solo para dev local |
| django-filter | 24.3 | Filtros en API |
| python-dotenv | 1.0.1 | Carga `.env` |
| Node.js | 18+ (testeado 24.16) | |
| Astro | 5.x | Modo server con Node adapter |
| Tailwind CSS | 4.x | CSS-first con `@theme` |
| Alpine.js | 3.x | Reactive sprinkles |
| TypeScript | 5.x | Strict en server-side, `// @ts-nocheck` en client inline |

---

## Setup Local

```bash
# Backend
cd workspace/quickreply/src/api
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # Opcional
python manage.py import_messages ../seed/mensajes_originales.txt
python manage.py runserver

# Frontend (en otra terminal)
cd workspace/quickreply/src/frontend
npm install
npm run dev
```

---

## Estructura del Backend

```
src/api/
├── manage.py
├── pytest.ini                  # Django settings + markers
├── requirements.txt
├── .env.example
├── quickreply/
│   ├── settings.py             # Lee de env vars
│   ├── urls.py                 # Incluye catalog.urls
│   ├── wsgi.py
│   └── asgi.py
└── catalog/
    ├── __init__.py
    ├── apps.py
    ├── admin.py                # Registra Category, Message, UsageLog
    ├── models.py               # 4 entidades
    ├── serializers.py          # 3 serializers DRF
    ├── views.py                # 3 ViewSets + 5 custom actions
    ├── urls.py                 # DefaultRouter
    ├── parser.py               # Parser del seed
    ├── migrations/
    │   ├── 0001_initial.py
    │   └── 0002_messages_fts5.py
    ├── management/commands/
    │   └── import_messages.py  # CLI para importar
    └── tests/                  # 93 tests
        ├── test_models.py
        ├── test_api.py
        ├── test_fts5.py
        ├── test_parser.py
        ├── test_special_endpoints.py
        └── test_e2e.py
```

### Modelos Clave

**`Message.save()` extrae variables automaticamente:**

```python
def save(self, *args, **kwargs):
    self.variables = list(set(re.findall(r"\{\{(\w+)\}\}", self.content)))
    super().save(*args, **kwargs)
```

**`Message.render(values)` sustituye variables:**

```python
def render(self, values: dict) -> str:
    text = self.content
    for name in self.variables:
        text = text.replace("{{" + name + "}}", str(values.get(name, "")))
    return text
```

**`Message.increment_usage()` denormaliza:**

```python
def increment_usage(self):
    self.usage_count = F("usage_count") + 1
    self.last_used_at = timezone.now()
    self.save(update_fields=["usage_count", "last_used_at"])
```

### Búsqueda FTS5

**Standalone (no auto-mantenido por triggers):** el seed se importa via comando, asi que los triggers se aplican solo a operaciones CRUD posteriores.

```python
# Trigger en migración 0002
CREATE TRIGGER messages_ai AFTER INSERT ON catalog_message
BEGIN
  INSERT INTO messages_fts (rowid, title, content, tags_clean)
  VALUES (NEW.id, NEW.title, NEW.content, ...);
END;
```

**Búsqueda con wildcard prefix:**

```python
# views.py get_queryset
tokens = query.split()
match_expr = " AND ".join(f"{token}*" for token in tokens)
# "precio bomba" -> "precio* AND bomba*"
```

### Endpoints Especiales

| Endpoint | Metodo | Vista |
|---|---|---|
| `/messages/{id}/copy/` | POST | `MessageViewSet.copy` |
| `/messages/recent/` | GET | `MessageViewSet.recent` |
| `/messages/most_used/` | GET | `MessageViewSet.most_used` |
| `/messages/import_seed/` | POST | `MessageViewSet.import_seed` |
| `/messages/export/` | GET | `MessageViewSet.export` |

---

## Estructura del Frontend

```
src/frontend/
├── package.json
├── astro.config.mjs            # Tailwind v4 via Vite plugin
├── tsconfig.json
├── .env.example
├── src/
│   ├── alpinejs.d.ts          # Tipos para window.Alpine
│   ├── styles/
│   │   └── global.css         # @theme + design tokens
│   ├── lib/
│   │   └── api.ts             # Cliente TS de la API
│   ├── layouts/
│   │   └── Layout.astro       # Header sticky + nav
│   ├── components/
│   │   ├── SearchBar.astro
│   │   ├── MessageList.astro
│   │   ├── MessageCard.astro
│   │   ├── CategoryFilter.astro
│   │   ├── MessageForm.astro  # Modal
│   │   ├── CategoryForm.astro # Modal
│   │   ├── VariablesModal.astro
│   │   └── Toast.astro
│   ├── pages/
│   │   ├── index.astro        # SSR + islands
│   │   └── categories.astro
│   └── scripts/
│       └── clipboard.ts       # Copy + shortcuts
└── tests/
    └── test_smoke.py          # 9 tests E2E via HTTP
```

### Patrones Clave del Frontend

**1. SSR para la carga inicial, CSR para interactividad:**

```astro
---
const initialMessages = await api.listMessages({});
---
<MessageList messages={initialMessages} />
```

**2. Click handlers globales delegados:**

```js
// En index.astro
document.addEventListener("click", async (e) => {
  const t = e.target;
  if (t.dataset.action === "edit") { ... }
  if (t.classList.contains("copy-btn")) { ... }
});
```

Cada componente solo define `data-action="..."` o `class="copy-btn"`, no su propio listener.

**3. Alpine.js inline en cada componente:**

```astro
<div x-data="{ open: false, count: 0 }">
  <button @click="open = true">Open</button>
</div>

<script is:inline>
  // Sin TypeScript
</script>
```

**4. TypeScript con `// @ts-nocheck` en handlers DOM:**

```ts
// @ts-nocheck
document.addEventListener("click", (e: Event) => {
  const t = e.target as HTMLElement;  // No funciona sin nocheck
  if (t.dataset.action === "edit") { ... }
});
```

Esto es necesario porque los types de Astro inline no extienden `HTMLElement` con `dataset` tipado.

**5. Tailwind v4 con `@theme` CSS-first:**

```css
/* src/styles/global.css */
@import "tailwindcss";

@theme {
  --color-bg: #ffffff;
  --color-accent: #3b82f6;
  /* ... */
}
```

Sin `tailwind.config.js`, todos los tokens se resuelven en build time.

---

## Agregar una Nueva Entidad

Ejemplo: agregar `Tag` como entidad de primera clase.

1. **Modelo** (`catalog/models.py`):

```python
class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
```

2. **Migracion**:

```bash
python manage.py makemigrations catalog
python manage.py migrate
```

3. **Serializer** (`catalog/serializers.py`):

```python
class TagSerializer(serializers.ModelSerializer):
    message_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Tag
        fields = ["id", "name", "message_count", "created_at"]
```

4. **ViewSet** (`catalog/views.py`):

```python
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
```

5. **URL** (`catalog/urls.py`):

```python
router.register("tags", TagViewSet, basename="tag")
```

6. **Tests** (`catalog/tests/test_api.py`):

```python
class TestTagAPI:
    def test_list_tags(self, client):
        Tag.objects.create(name="oferta")
        res = client.get("/api/tags/")
        assert res.json()["count"] == 1
```

7. **Frontend**: agregar en `src/lib/api.ts` y crear componente si es necesario.

---

## Agregar un Nuevo Componente Astro

Ejemplo: agregar un componente `Stats` que muestra "X mensajes copiados hoy".

1. Crear `src/components/Stats.astro`:

```astro
---
import { api } from "../lib/api";
const stats = await api.stats();
---
<div class="rounded-lg border border-border bg-surface p-4">
  <h3 class="text-sm font-semibold m-0">Estadisticas</h3>
  <p class="text-2xl font-bold m-0 mt-1">{stats.today_count}</p>
  <p class="text-xs text-text-tertiary m-0">copiados hoy</p>
</div>
```

2. Usar en una pagina:

```astro
---
import Stats from "../components/Stats.astro";
---
<Stats />
```

3. Si requiere interactividad, agregar `x-data` y `<script is:inline>`.

---

## Convenciones de Codigo

### Python (Backend)

- PEP 8 (maximo 100 chars por linea)
- Docstrings en cada modulo y clase
- Type hints en funciones publicas
- Snake_case para variables/funciones
- PascalCase para clases
- Tests con `pytest`, no `unittest`

### TypeScript (Frontend)

- Strict mode en `tsconfig.json` para `src/`, no en scripts inline
- `// @ts-nocheck` solo en handlers de DOM en scripts inline
- Interfaces para tipos de API (`Message`, `Category`)
- Funciones exportadas nombradas, no default
- Archivos `<Name>.astro` con `export interface Props`

### CSS

- Solo Tailwind v4 utility classes + tokens del `@theme`
- Sin `<style>` global en componentes (usar `class` con utilities)
- Custom CSS solo en `src/styles/global.css` (resets, scrollbar, etc)

### Commits

Sin convencion formal (no usamos git en MVP). Si se agrega VCS:
- `feat: descripcion corta`
- `fix: descripcion corta`
- `test: agregar tests para X`
- `docs: actualizar README`

---

## Debug

### Backend

```bash
# Ver queries SQL
python manage.py runserver --traceback

# Shell interactivo
python manage.py shell

# Tests especificos
python -m pytest catalog/tests/test_e2e.py::TestE2EFlow::test_full_flow -v

# Debug con pdb
import pdb; pdb.set_trace()
```

### Frontend

```bash
# Dev con hot reload
npm run dev

# Build + preview
npm run build
npm run preview

# Logs del servidor
# (en consola del navegador, F12)
```

---

## Despliegue (TODO - No implementado en MVP)

Para produccion, los pasos serian:

1. **Backend:**
   - `gunicorn quickreply.wsgi:application -b 0.0.0.0:8000`
   - Detras de nginx con HTTPS
   - `DEBUG=False`, `SECRET_KEY` aleatorio, `ALLOWED_HOSTS` con dominio

2. **Frontend:**
   - `npm run build` → genera `dist/`
   - `npm start` → sirve con Node adapter
   - Detras del mismo nginx con `/api-proxy/` → `proxy_pass http://localhost:8000`

3. **Proxy reverso (nginx):**
   ```nginx
   location / {
     proxy_pass http://localhost:4321;
   }
   location /api-proxy/ {
     rewrite ^/api-proxy/(.*)$ /api/$1 break;
     proxy_pass http://localhost:8000;
   }
   ```

---

## Performance

**Backend:**
- Búsqueda FTS5 sub-50ms incluso con miles de mensajes
- Paginación obligatoria (>20 resultados)
- `select_related("category")` en querysets

**Frontend:**
- Bundle gzip < 20KB
- SSR solo en la carga inicial, el resto es CSR
- Sin frameworks pesados (React/Vue)
- Tailwind v4 con purge automatico

---

## Limites Conocidos

- **Single-user:** sin autenticacion, no usar en hosting publico
- **Sin sincronizacion en la nube:** los datos viven en SQLite local
- **Sin internacionalizacion de la UI:** solo español
- **Sin metricas de uso agregadas:** solo por mensaje

---

> Si tenes preguntas no cubiertas aci, abre un issue o contacta al equipo.
