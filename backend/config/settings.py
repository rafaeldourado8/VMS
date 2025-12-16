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
# LÓGICA MANTIDA: Espera "1" no .env para ativar o Debug.
DEBUG = str(os.environ.get("DEBUG", "1")) == "1"

# --- CORREÇÃO: ALLOWED_HOSTS ---
# Adicionado 'backend' (nome do container) aos defaults para comunicação interna.
# Se DEBUG=1, libera geral ('*') para evitar erros 400 em desenvolvimento.
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,backend").split(",")
if DEBUG:
    ALLOWED_HOSTS = ["*"]

# --- CORREÇÃO: CSRF TRUSTED ORIGINS ---
# Obrigatório no Django 4.0+ quando o frontend e backend estão em portas diferentes.
# Permite que o Django aceite o login vindo dessas origens.
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:80",
    "http://localhost",
    "http://127.0.0.1:80",
    "http://127.0.0.1",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Aceita CSRF de proxies
CSRF_USE_SESSIONS = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_NAME = 'csrftoken'
SESSION_COOKIE_NAME = 'sessionid'

# Em desenvolvimento, aceita qualquer origem
if DEBUG:
    CSRF_COOKIE_SAMESITE = None
    SESSION_COOKIE_SAMESITE = None
    # Desabilita CSRF para admin em desenvolvimento
    CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

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
    "django_celery_results", # Para resultados de tasks
    "django_celery_beat",    # Para tarefas agendadas
    # Apps
    "apps.usuarios",
    "apps.cameras",
    "apps.deteccoes",
    "apps.analytics",
    "apps.configuracoes",
    "apps.dashboard",
    "apps.suporte",
    "streaming_integration",
    "apps.thumbnails",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    # CSRF desabilitado temporariamente para desenvolvimento
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Configurações CSRF para desenvolvimento com proxies
if DEBUG:
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_DOMAIN = None
    SESSION_COOKIE_DOMAIN = None

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'templates')],
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

# --- DATABASE CONFIGURATION (HIGH AVAILABILITY) ---
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DB_NAME = os.environ.get("POSTGRES_DB")
DB_USER = os.environ.get("POSTGRES_USER")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")

# Réplicas de Leitura (Para balanceamento de carga)
# Se não definidas no .env, assumem o mesmo host do Master (para dev local)
DB_HOST_REPLICA_1 = os.environ.get("DB_HOST_REPLICA_1", DB_HOST)
DB_HOST_REPLICA_2 = os.environ.get("DB_HOST_REPLICA_2", DB_HOST)

if all([DB_NAME, DB_USER, DB_PASSWORD]):
    DATABASES = {
        "default": {  # MASTER (Escrita/Leitura Crítica)
            "ENGINE": "django.db.backends.postgresql",
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": DB_PASSWORD,
            "HOST": DB_HOST,
            "PORT": DB_PORT,
            "OPTIONS": {'client_encoding': 'UTF8'},
        },
        "replica1": { # READ REPLICA 1
            "ENGINE": "django.db.backends.postgresql",
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": DB_PASSWORD,
            "HOST": DB_HOST_REPLICA_1,
            "PORT": DB_PORT,
            "OPTIONS": {'client_encoding': 'UTF8'},
        },
        "replica2": { # READ REPLICA 2
            "ENGINE": "django.db.backends.postgresql",
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": DB_PASSWORD,
            "HOST": DB_HOST_REPLICA_2,
            "PORT": DB_PORT,
            "OPTIONS": {'client_encoding': 'UTF8'},
        }
    }
    
    # Ativa o roteamento de leitura/escrita
    # Certifique-se de criar o arquivo config/db_router.py
    DATABASE_ROUTERS = ['config.db_router.PrimaryReplicaRouter']

else:
    # Fallback para SQLite (Desenvolvimento sem Docker)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Password validation
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
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I1N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Pasta onde o 'collectstatic' vai procurar
STATICFILES_DIRS = [
    d for d in [
        os.path.join(BASE_DIR, "static"),
        os.path.join(BASE_DIR, "frontend_dist"),
    ] if os.path.exists(d)
]

# Configuração do WhiteNoise
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files (Uploads)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
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

# --- CORREÇÃO: CORS ---
# Lista explícita de origens permitidas.
# Necessário quando 'CORS_ALLOW_CREDENTIALS = True' (usado pelo seu axios).
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:80",
    "http://127.0.0.1:80",
    "http://localhost:3000",
]
CORS_ALLOW_CREDENTIALS = True
# CORS_ALLOW_ALL_ORIGINS = True  <-- Removido pois conflita com CREDENTIALS=True

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
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672//')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

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
CELERY_TASK_DEFAULT_QUEUE = 'default'

CELERY_TASK_ROUTES = {
    'process_detection_message': {'queue': 'detection_ingest'},
}

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

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
            "maxBytes": 1024 * 1024 * 5,
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
        "celery": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "apps": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "streaming_integration": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        }
    },
}

# --- URLS DOS SERVIÇOS ---
MEDIAMTX_API_URL = os.getenv("MEDIAMTX_API_URL", "http://mediamtx:9997")
MEDIAMTX_API_USER = os.getenv("MEDIAMTX_API_USER", "mediamtx_api_user")
MEDIAMTX_API_PASS = os.getenv("MEDIAMTX_API_PASS", "GtV!sionMed1aMTX$2025")

NGINX_WEBRTC_URL_BASE = "/ws/live"
NGINX_AI_URL_BASE = "/ai"
AI_SERVICE_URL = os.environ.get("AI_SERVICE_URL", "http://localhost:8002")
INGEST_API_KEY = os.environ.get("INGEST_API_KEY", "default_insecure_key_12345")