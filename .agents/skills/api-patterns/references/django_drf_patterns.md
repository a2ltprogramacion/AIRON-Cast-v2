# Django REST Framework (DRF) Patterns — AIRON‑Cast

Production-grade implementation patterns for APIs with Django REST Framework.
All code examples assume Django 4.2+ and DRF 3.14+.

## 1. Views Architecture

### 1.1 Function‑Based Views (`@api_view`)

Use only for simple endpoints (e.g., health checks).

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy'})
```

### 1.2 `APIView` — Custom Logic

For non‑CRUD operations or fine‑grained control.

```python
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
```

### 1.3 `ModelViewSet` — Standard CRUD

Preferred for standard CRUD operations.

```python
from rest_framework.viewsets import ModelViewSet
from .models import Article
from .serializers import ArticleSerializer

class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]
```

### 1.4 Routers

```python
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')
urlpatterns = router.urls
```

### 1.5 `@action` Decorator

Add custom actions to a ViewSet.

```python
from rest_framework.decorators import action

class ArticleViewSet(ModelViewSet):
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        article = self.get_object()
        article.publish()
        return Response({'status': 'published'})
```

## 2. Serializers

### 2.1 `ModelSerializer`

```python
from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']
```

### 2.2 Field‑Level Validation

```python
def validate_title(self, value):
    if 'badword' in value.lower():
        raise serializers.ValidationError("Title contains prohibited words")
    return value
```

### 2.3 Object‑Level Validation

```python
def validate(self, data):
    if data['start_date'] > data['end_date']:
        raise serializers.ValidationError("End date must be after start date")
    return data
```

### 2.4 Nested Serializers

```python
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'text']

class ArticleSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = Article
        fields = ['id', 'title', 'comments']
```

## 3. Authentication

### 3.1 JWT with `djangorestframework-simplejwt`

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}
```

### 3.2 Custom Authentication

```python
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

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

```python
from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
```

## 5. Throttling

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

## 6. Filtering, Searching, Ordering

```python
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter'
    ]
}

class ArticleViewSet(ModelViewSet):
    filterset_fields = ['author', 'published']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'title']
```

## 7. Pagination

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}
```

## 8. Exception Handling — Enforcing JSend

**core/exceptions.py:**

```python
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def a2lt_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return Response({
            'status': 'error',
            'message': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if response.status_code >= 500:
        data = {'message': str(exc), 'code': 'SERVER_ERROR'}
    elif response.status_code >= 400:
        data = {'message': 'Validation failed', 'data': response.data}
    else:
        data = {'data': response.data}

    response.data = {'status': 'fail' if response.status_code >= 400 else 'success', **data}
    return response
```

## 9. Testing

```python
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

class ArticleAPITestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test', password='pass')
        self.client.force_authenticate(user=self.user)

    def test_list_articles(self):
        response = self.client.get('/api/v1/articles/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
```

## 10. Performance

```python
class ArticleViewSet(ModelViewSet):
    def get_queryset(self):
        return Article.objects.select_related('author').prefetch_related('comments')
```

## 11. Complete CRUD Example

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