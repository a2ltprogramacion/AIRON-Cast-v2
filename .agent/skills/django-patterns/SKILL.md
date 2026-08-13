---
name: django-patterns
description: "Patrones de Arquitectura Django y DRF. Mejores prácticas de producción: Custom QuerySets, Managers, Serializers con validación compleja, ViewSets con JSend, Service Layer explícito y Optimización (N+1)."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Django Development Patterns (A2LT Standard)

Production-grade Django architecture patterns for scalable applications. This skill ensures consistency across all A2LT backends.

## 1. Project Structure & Split Settings

We use a split settings pattern to isolate environments.

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
        ├── services.py      # Core A2LT Rule: Business logic goes here
        └── selectors.py     # Optional: Complex cross-model read queries
```

## 2. Model Design Patterns

Every critical Django app must begin with an `AbstractUser` extension for future-proofing. Models must specify constraints at the database level.

```python
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

class User(AbstractUser):
    email = models.EmailField(unique=True)
    # ... required fields

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products')

    class Meta:
        db_table = 'products'
        indexes = [models.Index(fields=['category', 'is_active'])]
        constraints = [models.CheckConstraint(check=models.Q(price__gte=0), name='price_non_negative')]
```

## 3. QuerySet & Manager Best Practices

Move repetitive `.filter()` logic out of views and into Custom QuerySets. Chain them for clean controllers.

```python
class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)
    def with_category(self):
        return self.select_related('category') # Prevent N+1

class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

class Product(models.Model):
    # ... fields ...
    objects = ProductManager()

# Usage in View: Product.objects.active().with_category()
```

## 4. DRF Serializer Patterns

Serializers are for Translation and Input Validation _only_. Do not put complex business logic in `create` or `update`.

```python
from rest_framework import serializers

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    discount_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'discount_price', 'category_name']
        read_only_fields = ['id', 'slug']

    def get_discount_price(self, obj):
        return obj.price * 0.9 if obj.is_active else obj.price

    def validate(self, data):
        # Multi-field cross validation occurs here before passing to Services
        if data.get('price', 0) > 1000 and data.get('stock', 0) > 50:
            raise serializers.ValidationError("Cannot hold large stock of luxury items.")
        return data
```

## 5. ViewSet & Custom Action Patterns

Views must remain thin. Delegate heavy lifting to `services.py`. All responses must adhere to the A2LT JSend envelope.

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
        # DELEGATE TO SERVICE LAYER
        success, message = ProductService.process_purchase(user=request.user, product=product)

        if success:
            return Response({'status': 'success', 'message': message}, status=status.HTTP_200_OK)
        return Response({'status': 'error', 'message': message}, status=status.HTTP_400_BAD_REQUEST)
```

## 6. Service Layer Pattern (A2LT Core)

The Service Layer encapsulates all database mutations and third-party API calls. Views and Celery Tasks both call Services.

```python
from django.db import transaction

class ProductService:
    @staticmethod
    @transaction.atomic
    def process_purchase(user, product) -> tuple[bool, str]:
        if product.stock <= 0:
            return False, "Out of stock"

        # Deduct stock safely inside transaction
        product.stock -= 1
        product.save(update_fields=['stock'])

        # Create ledger entry
        PurchaseLog.objects.create(user=user, product=product)
        return True, "Purchase successful"
```

## 7. Caching Strategies

Use caching aggressively for read-heavy resources to protect the database.

**Low-Level Caching API:**

```python
from django.core.cache import cache

def get_popular_categories():
    cache_key = 'popular_categories'
    categories = cache.get(cache_key)

    if categories is None:
        categories = list(Category.objects.filter(is_popular=True))
        cache.set(cache_key, categories, timeout=60 * 60) # 1 hour

    return categories
```

**View-Level Caching (DRF):**
Use `@method_decorator(cache_page(60 * 15))` above readonly ViewSet methods.

## 8. Signals (Use Sparingly)

Signals (`post_save`) obscure control flow. Only use them for decoupled side-effects like "Create an empty Profile when a User registers." Do NOT use signals for critical business workflow like "Charge credit card when order is saved."

```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
```

## 9. Middleware Patterns

Custom middleware is ideal for request mutation (tracking execution time, user active status).

```python
import time
from django.utils.deprecation import MiddlewareMixin

class RequestTimingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            response['X-Execute-Time'] = str(duration)
        return response
```

## 10. Performance Optimization (Bulk & N+1)

Never query inside a loop.

```python
# PREVENT N+1
# Bad: Book.objects.all() -> loop -> book.author.name
# Good:
Book.objects.select_related('author').all()

# BULK OPERATIONS (Prevents N queries on INSERT/UPDATE)
new_logs = [SystemLog(message=f"Error {i}") for i in range(1000)]
SystemLog.objects.bulk_create(new_logs)

# BULK UPDATE
products = Product.objects.filter(category='old')
for p in products:
    p.is_active = False
Product.objects.bulk_update(products, ['is_active'])
```
