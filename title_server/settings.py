import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-title-server")
DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() in {"1", "true", "yes", "on"}
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if host.strip()
]
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "rest_framework",
    "titles.apps.TitlesConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "title_server.urls"
TEMPLATES = []
WSGI_APPLICATION = "title_server.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "UNAUTHENTICATED_USER": None,
}

TITLE_MODEL_ID = os.getenv("TITLE_MODEL_ID", "Qwen/Qwen3.5-9B")
TITLE_MODEL_ENABLED = os.getenv(
    "TITLE_MODEL_ENABLED",
    "true",
).lower() in {"1", "true", "yes", "on"}
TITLE_MODEL_DEVICE = os.getenv("TITLE_MODEL_DEVICE", "auto")
TITLE_MODEL_DTYPE = os.getenv("TITLE_MODEL_DTYPE", "auto")
TITLE_MODEL_MAX_NEW_TOKENS = int(os.getenv("TITLE_MODEL_MAX_NEW_TOKENS", "24"))
TITLE_MODEL_TEMPERATURE = float(os.getenv("TITLE_MODEL_TEMPERATURE", "0.1"))
TITLE_MODEL_TIMEOUT_SECONDS = float(os.getenv("TITLE_MODEL_TIMEOUT_SECONDS", "20"))
TITLE_MAX_LENGTH = int(os.getenv("TITLE_MAX_LENGTH", "40"))
TITLE_MODEL_EAGER_LOAD = os.getenv(
    "TITLE_MODEL_EAGER_LOAD",
    "true",
).lower() in {"1", "true", "yes", "on"}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = os.getenv(
    "DJANGO_SECURE_SSL_REDIRECT",
    "false",
).lower() in {"1", "true", "yes", "on"}
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT
SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_HSTS_PRELOAD = False
