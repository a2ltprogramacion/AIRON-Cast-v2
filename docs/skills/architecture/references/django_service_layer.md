# Django Service Layer Pattern

In A2LT, we avoid strict Clean Architecture because Django's ORM is too powerful to hide behind abstract Repository interfaces. Instead, we use the **Service Layer** pattern to keep Views thin and testable.

## The Rule of "Thin Views"

A Django View (or DRF ViewSet) should do exactly three things:

1. **Unpack:** Extract data from the HTTP Request (Params, Headers, JSON).
2. **Delegate:** Hand the data to a Service or Model method.
3. **Pack:** Format the result from the Service into an HTTP Response (JSON/Template).

If your view has nested `if/else` business rules or complex Database `filter` chains, it is too fat.

## Implementing the Service Layer

Create a `services.py` file inside your Django app (e.g., `users/services.py`).

### Anti-Pattern: Fat View

```python
# users/views.py (BAD)
class RegisterUserView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email taken"}, status=400)

        user = User.objects.create(email=email)
        user.set_password(request.data.get('password'))
        user.save()

        # Third-party integration inside view!
        send_welcome_email(user.email)

        return Response({"status": "success"})
```

### A2LT Standard: Service Layer Orchestration

```python
# users/services.py (GOOD)
def register_new_user(*, email: str, password: str) -> User:
    """Handles the business logic of registering a user."""
    if User.objects.filter(email=email).exists():
        raise ValidationError("Email is already taken.")

    user = User.objects.create_user(email=email, password=password)
    send_welcome_email(user.email)
    return user

# users/views.py (GOOD)
class RegisterUserView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # The view delegates the complex work to the Service Layer
        user = register_new_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )

        return Response({"status": "success", "user_id": user.id})
```

## When to use Models vs Services

- **Model Methods:** Use for logic that only requires the current instance's data (e.g., `user.get_full_name()`).
- **Services:** Use for operations that span multiple models or involve external APIs (e.g., `process_checkout(cart, user)`).
