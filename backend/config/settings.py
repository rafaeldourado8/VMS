import os
from pathlib import Path
from datetime import timedelta
import logging.config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SEGURANÇA BÁSICA ---
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-@c6%21k63w@e1#*gq!8s0m@z&h(c$l5a@#c(g*q!w_x9j$7")
DEBUG = str(os.environ.get("DEBUG", "1")) == "1"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,backend").split(",")
if DEBUG:
    ALLOWED_HOSTS = ["*"]

# --- INTEGRAÇÃO FRONTEND (CORS/CSRF) ---
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173", "http://127.0.0.1:5173",
    "http://localhost:80", "http://localhost",
    "http://localhost:3000", "http://localhost:8000"
]
CORS_ALLOWED_ORIGINS = CSRF_TRUSTED_ORIGINS
CORS_ALLOW_CREDENTIALS = True

# --- APPLICAÇÕES ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd Party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_spectacular",
    "django_filters",
    "django_celery_results",
    "django_celery_beat",
    # Módulos Internos
    "apps.usuarios",
    "apps.cameras",
    "apps.deteccoes",
    "apps.analytics",
    "apps.configuracoes",
    "apps.dashboard",
    "apps.suporte",
    "apps.thumbnails",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- BASE DE DADOS (Alta Disponibilidade) ---
DB_NAME = os.environ.get("POSTGRES_DB")
if DB_NAME:
    DATABASES = {
        "default": { # MASTER (Escrita)
            "ENGINE": "django.db.backends.postgresql",
            "NAME": DB_NAME,
            "USER": os.environ.get("POSTGRES_USER"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
        },
        "replica1": { # LEITURA 1
            "ENGINE": "django.db.backends.postgresql",
            "NAME": DB_NAME,
            "USER": os.environ.get("POSTGRES_USER"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
            "HOST": os.environ.get("DB_HOST_REPLICA_1", "localhost"),
            "PORT": "5432",
        }
    }
    DATABASE_ROUTERS = ['config.db_router.PrimaryReplicaRouter']
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3", 
            "NAME": BASE_DIR / "db.sqlite3"
        }
    }

# --- AUTENTICAÇÃO E REST FRAMEWORK ---
AUTH_USER_MODEL = "usuarios.Usuario"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
}

# --- INTERNACIONALIZAÇÃO ---
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# --- ARQUIVOS ESTÁTICOS E MEDIA ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --- CELERY / REDIS ---
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', f'redis://{REDIS_HOST}:6379/0')
CELERY_RESULT_BACKEND = 'django-db'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:6379/0",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

# --- INTEGRAÇÃO IA E STREAMING ---
MEDIAMTX_API_URL = os.getenv("MEDIAMTX_API_URL", "http://mediamtx:9997")
INGEST_API_KEY = os.environ.get("INGEST_API_KEY", "default_insecure_key_12345")

# --- LOGGING ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} [{name}:{lineno}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/django_app.log"),
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {"handlers": ["console", "file"], "level": "INFO"},
        "apps": {"handlers": ["console", "file"], "level": "DEBUG"},
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
STREAMING_SERVICE_URL = os.environ.get("STREAMING_SERVICE_URL", "http://streaming:8001")