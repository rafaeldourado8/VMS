import os
from pathlib import Path
from datetime import timedelta
import logging.config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-insecure-@c6%21k63w@e1#*gq!8s0m@z&h(c$l5a@#c(g*q!w_x9j$7"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = str(os.environ.get("DEBUG", "1")) == "1"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Application definition

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
    "django_celery_results", # --- ADICIONADO (Para resultados de tasks)
    "django_celery_beat",   # --- ADICIONADO (Para tarefas agendadas)
    # Apps
    "apps.usuarios",
    "apps.cameras",
    "apps.deteccoes",
    "apps.analytics",
    "apps.configuracoes",
    "apps.dashboard",
    "apps.suporte",
    "streaming_integration",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware", # Adicionado para servir estáticos
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
        "DIRS": [os.path.join(BASE_DIR, 'templates')], # Para o frontend estático
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

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Configuração Padrão (SQLite - para dev local se não usar Docker)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Configuração do PostgreSQL (para Docker, lendo do .env)
DB_NAME = os.environ.get("POSTGRES_DB")
DB_USER = os.environ.get("POSTGRES_USER")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")

if all([DB_NAME, DB_USER, DB_PASSWORD]):
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
        "OPTIONS": {
            'client_encoding': 'UTF8',
        },
    }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I1N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Pasta onde o 'collectstatic' vai procurar
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"), # Pasta estática principal do projeto
    os.path.join(BASE_DIR, "frontend_build"), # Pasta do build do Vite
]

# Configuração do WhiteNoise
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files (Uploads)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom User Model
AUTH_USER_MODEL = "usuarios.Usuario"

# REST FRAMEWORK
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
}


# JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# CORS
CORS_ALLOW_ALL_ORIGINS = True  # Para desenvolvimento
# Em produção, use:
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
# ]

# OpenAPI (Spectacular)
SPECTACULAR_SETTINGS = {
    "TITLE": "VMS API",
    "DESCRIPTION": "API para o Sistema de Gerenciamento de Vídeo (VMS)",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# REDIS
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
REDIS_DB = os.environ.get("REDIS_DB", "0")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# --- CONFIGURAÇÃO DO CELERY E RABBITMQ ---
# -----------------------------------------------------------------

# Broker (RabbitMQ)
# URL lida do environment (definido no docker-compose.yml)
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672//')

# Backend de Resultados (Usando o DB do Django via django-celery-results)
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache' # Usar o cache do Django (Redis)

# Configurações de Serialização
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE # Reutiliza o TIME_ZONE do Django
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60 # Timeout de 30 min por task

# Mapeamento da Fila (importante!)
# Mapeia a fila 'detection_ingest' para ser usada
CELERY_TASK_QUEUES = {
    'detection_ingest': {
        'exchange': 'detection_ingest',
        'binding_key': 'detection_ingest',
    },
    'default': {
        'exchange': 'default',
        'binding_key': 'default',
    }
}
# Define a fila padrão para tasks que não especificarem uma
CELERY_TASK_DEFAULT_QUEUE = 'default'

# Roteamento de tasks (conecta a task 'process_detection_message' à sua fila)
CELERY_TASK_ROUTES = {
    'process_detection_message': {'queue': 'detection_ingest'},
}

# Celery Beat (Scheduler - para tarefas agendadas)
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
# -----------------------------------------------------------------


# LOGGING
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} [{name}:{lineno}] {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/django_app.log"),
            "maxBytes": 1024 * 1024 * 5,  # 5MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "celery": { # Logger específico para o Celery
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "apps": { # Logger para todos os 'apps'
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "streaming_integration": { # Logger para a integração
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        }
    },
}

# --- ATUALIZAÇÃO DA ARQUITETURA (MediaMTX) ---

# URLS DOS SERVIÇOS (NGINX E INTERNOS)
# -----------------------------------------------------------------

MEDIAMTX_API_URL = os.getenv("MEDIAMTX_API_URL", "http://mediamtx:8888")

# NOVAS URLs (MediaMTX e IA)
NGINX_WEBRTC_URL_BASE = "/webrtc"  # Rota do Nginx para o MediaMTX WHEP/WHIP
NGINX_AI_URL_BASE = "/ai"        # Rota do Nginx para o serviço de IA

# URL interna para o serviço de IA (usada pelo backend/Django)
AI_SERVICE_URL = os.environ.get("AI_SERVICE_URL", "http://localhost:8002")

# Chave de API para o serviço de IA ingerir dados (deve ser a mesma no .env)
INGEST_API_KEY = os.environ.get("INGEST_API_KEY", "default_insecure_key_12345")