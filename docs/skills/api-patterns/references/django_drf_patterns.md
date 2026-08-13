# Django REST Framework (DRF) Patterns

This reference provides deep, actionable patterns for implementing APIs with Django REST Framework (DRF) in the A2LT ecosystem. All code examples assume Django 4.2+ and DRF 3.14+.

## 1. Views Architecture

### 1.1 Function‑Based Views (`@api_view`)

Use sparingly – only for extremely simple endpoints (e.g., health checks). Always wrap with `@api_view` and return `Response`.

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy'})
```

### 1.2 `APIView` – Base Class for Custom Logic

Ideal for non‑CRUD operations or when you need fine‑grained control.

```python
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import UserProfileSerializer

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
```

### 1.3 `GenericAPIView` + Mixins

Use for CRUD when you want to leverage DRF’s built‑in mixins (`ListModelMixin`, `CreateModelMixin`, etc.).

```python
from rest_framework import mixins, generics
from .models import Article
from .serializers import ArticleSerializer

class ArticleList(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
```

### 1.4 `ViewSet` and `ModelViewSet`

Preferred for standard CRUD operations. Reduces boilerplate significantly.

```python
from rest_framework.viewsets import ModelViewSet
from .models import Article
from .serializers import ArticleSerializer

class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]
```

### 1.5 Routers

Automatically generate URL patterns for ViewSets.

```python
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')

urlpatterns = router.urls
```

### 1.6 `@action` Decorator for Additional Endpoints

Add custom actions to a ViewSet.

```python
from rest_framework.decorators import action
from rest_framework.response import Response

class ArticleViewSet(ModelViewSet):
    # ... base configuration ...

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def publish(self, request, pk=None):
        article = self.get_object()
        article.publish()  # custom model method
        return Response({'status': 'published'})
```

## 2. Serializers – The Core of Validation

### 2.1 `ModelSerializer`

Use for resources tightly coupled to Django models.

```python
from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']
```

### 2.2 `Serializer` for Non‑Model Data

For custom payloads (e.g., contact forms, analytics events).

```python
class ContactSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    message = serializers.CharField()

    def create(self, validated_data):
        # Process the data (send email, etc.)
        return validated_data
```

### 2.3 Field‑Level Validation

Define `validate_<field_name>` methods.

```python
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

    def validate_title(self, value):
        if 'badword' in value.lower():
            raise serializers.ValidationError("Title contains prohibited words")
        return value
```

### 2.4 Object‑Level Validation

Override `validate()` for cross‑field checks.

```python
def validate(self, data):
    if data['start_date'] > data['end_date']:
        raise serializers.ValidationError("End date must be after start date")
    return data
```

### 2.5 Nested Serializers

**Read‑only nested representation:**

```python
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'text', 'author']

class ArticleSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = Article
        fields = ['id', 'title', 'comments']
```

**Writable nested serializers** (override `create` / `update`):

```python
class ArticleSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'comments']

    def create(self, validated_data):
        comments_data = validated_data.pop('comments')
        article = Article.objects.create(**validated_data)
        for comment_data in comments_data:
            Comment.objects.create(article=article, **comment_data)
        return article
```

### 2.6 Custom Serializer Fields

Create reusable fields for special formats.

```python
class LowercaseCharField(serializers.CharField):
    def to_representation(self, value):
        return value.lower()
    def to_internal_value(self, data):
        return data.lower()
```

## 3. Authentication

### 3.1 JWT with `djangorestframework-simplejwt`

Install: `pip install djangorestframework-simplejwt`

**Settings:**

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}
```

**Obtain and refresh tokens:**

```python
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

**Include user data in token** (via custom serializer).

### 3.2 Session Authentication

Use for first‑party web apps that share the same domain.

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    )
}
```

### 3.3 Token Authentication (Legacy)

Built‑in `TokenAuthentication` is less secure than JWT; avoid for new projects.

### 3.4 Custom Authentication

Implement `rest_framework.authentication.BaseAuthentication`.

```python
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import APIKey

class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return None
        try:
            key = APIKey.objects.get(key=api_key)
        except APIKey.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')
        return (key.user, None)
```

## 4. Permissions

### 4.1 Built‑in Permissions

- `AllowAny`
- `IsAuthenticated`
- `IsAdminUser`
- `IsAuthenticatedOrReadOnly`

### 4.2 Custom Permissions

```python
from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
```

Apply in ViewSet:

```python
class ArticleViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwner]
```

### 4.3 Object‑Level Permissions

DRF checks object permissions only if the view has a `get_object()` method. Use `has_object_permission` as above.

## 5. Throttling

### 5.1 Built‑in Throttles

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}
```

### 5.2 Custom Throttle

```python
from rest_framework.throttling import SimpleRateThrottle

class BurstRateThrottle(SimpleRateThrottle):
    scope = 'burst'

    def get_cache_key(self, request, view):
        return self.get_ident(request)  # throttle by IP
```

## 6. Filtering, Searching, Ordering

### 6.1 `DjangoFilterBackend`

Install `django-filter`, then add to `DEFAULT_FILTER_BACKENDS`.

```python
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
}

# In ViewSet
class ArticleViewSet(ModelViewSet):
    filterset_fields = ['author', 'published']
```

### 6.2 `SearchFilter`

Adds simple text search.

```python
class ArticleViewSet(ModelViewSet):
    search_fields = ['title', 'content']
```

### 6.3 `OrderingFilter`

```python
class ArticleViewSet(ModelViewSet):
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']  # default
```

### 6.4 Custom Filter Backend

```python
from rest_framework.filters import BaseFilterBackend

class RecentArticlesFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.query_params.get('recent'):
            return queryset.filter(created_at__gte=timezone.now() - timedelta(days=7))
        return queryset
```

## 7. Pagination

### 7.1 `PageNumberPagination` (Default)

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}
```

### 7.2 Custom Pagination

```python
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
```

Apply per view:

```python
class ArticleViewSet(ModelViewSet):
    pagination_class = StandardResultsSetPagination
```

## 8. Versioning

### 8.1 URLPathVersioning (A2LT Standard)

```python
REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning'
}
```

URLs: `/api/v1/articles/`, `/api/v2/articles/`

### 8.2 AcceptHeaderVersioning

Version via `Accept: application/json; version=1.0`.

## 9. Exception Handling – Enforcing JSend

Create a custom exception handler to wrap all errors in the A2LT envelope.

**core/exceptions.py:**

```python
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def a2lt_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        # Unhandled exception – log and return 500
        return Response({
            'status': 'error',
            'message': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if response.status_code >= 500:
        status_label = 'error'
        data = {'message': str(exc), 'code': 'SERVER_ERROR'}
    elif response.status_code >= 400:
        status_label = 'fail'
        data = {'message': 'Validation failed', 'data': response.data}
    else:
        status_label = 'success'  # unlikely for exceptions
        data = {'data': response.data}

    response.data = {'status': status_label, **data}
    return response
```

**Settings:**

```python
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'core.exceptions.a2lt_exception_handler'
}
```

## 10. Response Envelope – Optional Mixin

For success responses, you can also use a mixin to automatically wrap data.

```python
class A2LTResponseMixin:
    def finalize_response(self, request, response, *args, **kwargs):
        if response.exception is True:
            return super().finalize_response(request, response, *args, **kwargs)
        if response.status_code < 400:
            response.data = {
                'status': 'success',
                'data': response.data
            }
        return super().finalize_response(request, response, *args, **kwargs)
```

Apply to views (or use a custom renderer as an alternative).

## 11. Testing

### 11.1 `APITestCase` and `APIClient`

```python
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model

class ArticleAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='test', password='pass')
        self.client.force_authenticate(user=self.user)

    def test_list_articles(self):
        response = self.client.get('/api/v1/articles/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
```

### 11.2 Testing Permissions

```python
def test_unauthenticated_cannot_create(self):
    self.client.logout()
    response = self.client.post('/api/v1/articles/', {'title': 'Hack'})
    self.assertEqual(response.status_code, 401)
    self.assertEqual(response.data['status'], 'fail')
```

### 11.3 Factory Boy for Test Data

```python
import factory
from .models import Article

class ArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Article
    title = factory.Faker('sentence')
    content = factory.Faker('paragraph')
```

## 12. Performance

### 12.1 `select_related` and `prefetch_related`

Override `get_queryset` in views:

```python
class ArticleViewSet(ModelViewSet):
    def get_queryset(self):
        return Article.objects.select_related('author').prefetch_related('comments')
```

### 12.2 Caching with Django Cache

Use `@method_decorator(cache_page)` for expensive endpoints, or cache querysets with `cache.set`.

## 13. Security Considerations

- **CORS:** Use `django-cors-headers` and configure `CORS_ALLOWED_ORIGINS`.
- **HTTPS:** Enforce via `SECURE_SSL_REDIRECT` and `SESSION_COOKIE_SECURE`.
- **Sensitive Data:** Never return password fields; use `write_only=True` in serializers.
- **Rate Limiting:** Always apply throttling to prevent abuse.
- **Input Sanitization:** DRF serializers handle this automatically.

## 14. Example: Complete CRUD for a Blog Post

**models.py**

```python
from django.db import models
from django.contrib.auth.models import User

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=False)
```

**serializers.py**

```python
from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'author_username', 'created_at', 'published']
        read_only_fields = ['id', 'created_at']
```

**views.py**

```python
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Article
from .serializers import ArticleSerializer
from .permissions import IsOwner

class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
```

**urls.py**

```python
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet

router = DefaultRouter()
router.register(r'articles', ArticleViewSet)
urlpatterns = router.urls
```

**tests.py**

```python
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Article

class ArticleTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='test')
        self.client.force_authenticate(user=self.user)

    def test_create_article(self):
        data = {'title': 'New Post', 'content': 'Hello world'}
        response = self.client.post('/articles/', data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Article.objects.count(), 1)
        self.assertEqual(Article.objects.first().author, self.user)
```

---

_This reference covers the core DRF patterns for A2LT. Always refer back to the checklist in `SKILL.md` before implementing._
