# Django Backend Setup

Follow these specific instructions to bootstrap a secure, API-ready Django backend adhering to A2LT patterns.

## 1. Environment & Initialization

Always assume the user is managing dependencies via `requirements.txt` and `venv`, or globally if in a dedicated container.

```bash
# Create the backend folder and enter it
mkdir backend
cd backend

# Initialize Python Virtual Environment (Windows standard)
python -m venv venv
.\venv\Scripts\activate

# Install the critical A2LT stack
pip install django djangorestframework django-cors-headers

# Start the Django project (name it 'core' to keep meaning clear)
django-admin startproject core .
```

## 2. Immediate Configuration (settings.py)

Before asking the user to code any models, modify `core/settings.py` to enforce the REST API context.

### Add Installed Apps

```python
INSTALLED_APPS = [
    # ... django defaults ...
    'corsheaders',
    'rest_framework',
]
```

### Configure CORS

The frontend (Astro) usually runs on `http://localhost:4321`. We must allow it.
Add `corsheaders.middleware.CorsMiddleware` to the TOP of the `MIDDLEWARE` list.

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4321",
    "http://127.0.0.1:4321",
]
```

### Configure DRF Default Permissions

Lock down the API globally by default to prevent accidental data leaks.

```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication', # Useful for browsable API
    ]
}
```

## 3. Database Migration & Run

```bash
python manage.py migrate
python manage.py runserver 8000
```
