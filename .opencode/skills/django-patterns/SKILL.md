---
name: django-patterns
version: 1.0.0
type: backend
subtype: skill
tier: all
description: |
  Patrones de arquitectura Django y DRF para producción. Cubre modelos,
  QuerySets, Managers, serializers, viewsets, capa de servicio y optimización.
  Activar cuando `backend_specialist` necesite referencia de patrones Django.
  Trigger phrases: "patrón Django", "cómo estructurar modelos", "DRF serializer",
  "QuerySet personalizado", "service layer Django".
  No activar para tareas de frontend o configuración de infraestructura.
triggers:
  primary: ["patrón Django", "django patterns", "DRF best practices"]
  secondary: ["QuerySet", "serializer", "service layer", "modelos Django"]
  context: ["backend development", "Django architecture"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - backend_specialist
last_used: 2026-06-05
scope: restricted
---

# Django Development Patterns — AIRON‑Cast

Production-grade Django architecture patterns for scalable applications.
This skill ensures consistency across all AIRON‑Cast backends.

---

## 1. Project Structure & Split Settings

Use a split settings pattern to isolate environments.

```
myproject/
├── config/
│   ├── settings/
│   │   ├── base.py          # Shared modules (INSTALLED_APPS, BASE_DIR)
│   │   ├── development.py   # sqlite3, debug_toolbar, CORS=*
│   │   └── production.py    # Postgres, SECURE_SSL_REDIRECT, Allowed_Hosts
│   ├── urls.py
│   └── wsgi.py
└── apps/
    └── users/
        ├── models.py
        ├── views.py
        ├── serializers.py
        ├── services.py      # Business logic goes here
        └── selectors.py     # Optional: Complex cross-model read queries
```

---

## 2. Model Design Patterns

Every critical Django app must begin with an `AbstractUser` extension for
future-proofing. Models must specify constraints at the database level.

```python
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

class User(AbstractUser):
    email = models.EmailField(unique=True)

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, db_index=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(
        'Category', on_delete=models.CASCADE, related_name='products'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        indexes = [
            models.Index(fields=['category', 'is_active']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name='price_non_negative'
            ),
        ]
```

---

## 3. QuerySet & Manager Best Practices

Move repetitive `.filter()` logic out of views and into Custom QuerySets.
Chain them for clean controllers.

```python
class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def with_category(self):
        return self.select_related('category')

class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

class Product(models.Model):
    objects = ProductManager()
```

---

## 4. DRF Serializer Patterns

Serializers are for translation and input validation only. Do not put complex
business logic in `create` or `update`.

```python
from rest_framework import serializers

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source='category.name', read_only=True
    )
    discount_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price',
            'discount_price', 'category_name'
        ]
        read_only_fields = ['id', 'slug']

    def get_discount_price(self, obj):
        return obj.price * 0.9 if obj.is_active else obj.price

    def validate(self, data):
        if data.get('price', 0) > 1000 and data.get('stock', 0) > 50:
            raise serializers.ValidationError(
                "Cannot hold large stock of luxury items."
            )
        return data
```

---

## 5. ViewSet & Custom Action Patterns

Views must remain thin. Delegate heavy lifting to `services.py`.

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .services import ProductService

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.active().with_category()
    serializer_class = ProductSerializer

    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        product = self.get_object()
        success, message = ProductService.process_purchase(
            user=request.user, product=product
        )
        if success:
            return Response(
                {'status': 'success', 'message': message},
                status=status.HTTP_200_OK
            )
        return Response(
            {'status': 'error', 'message': message},
            status=status.HTTP_400_BAD_REQUEST
        )
```

---

## 6. Service Layer Pattern (AIRON‑Cast Core)

The Service Layer encapsulates all database mutations and third-party API
calls. Views and Celery Tasks both call Services.

```python
from django.db import transaction

class ProductService:
    @staticmethod
    @transaction.atomic
    def process_purchase(user, product) -> tuple[bool, str]:
        if product.stock <= 0:
            return False, "Out of stock"

        product.stock -= 1
        product.save(update_fields=['stock'])

        PurchaseLog.objects.create(user=user, product=product)
        return True, "Purchase successful"
```

---

## 7. Signals (Use Sparingly)

Only use signals for decoupled side-effects like "Create an empty Profile when
a User registers." Do NOT use signals for critical business workflows.

```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
```

---

## 8. Performance Optimization (N+1 Prevention)

Never query inside a loop.

```python
# PREVENT N+1
# Bad:  Book.objects.all() -> loop -> book.author.name
# Good:
Book.objects.select_related('author').all()

# BULK OPERATIONS
new_logs = [SystemLog(message=f"Error {i}") for i in range(1000)]
SystemLog.objects.bulk_create(new_logs)

# BULK UPDATE
products = Product.objects.filter(category='old')
for p in products:
    p.is_active = False
Product.objects.bulk_update(products, ['is_active'])
```