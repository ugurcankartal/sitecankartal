import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / '.env')


def env_db_config(prefix: str) -> dict:
    """Build MySQL DATABASES config from dev_* or prod_* env variables."""
    return {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get(f'{prefix}_MYSQL_DATABASE', 'personal_portfolio'),
        'USER': os.environ.get(f'{prefix}_MYSQL_USER', 'root'),
        'PASSWORD': os.environ.get(f'{prefix}_MYSQL_PASSWORD', ''),
        'HOST': os.environ.get(f'{prefix}_MYSQL_HOST', '127.0.0.1'),
        'PORT': os.environ.get(f'{prefix}_MYSQL_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }


DEBUG = False

ALLOWED_HOSTS: list[str] = []

INSTALLED_APPS = [
    'portfolio.apps.PortfolioConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'portfolio.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'portfolio.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SESSION_COOKIE_NAME = os.environ.get('SESSION_COOKIE_NAME', 'admin_session')
SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
SESSION_COOKIE_AGE = int(timedelta(hours=24).total_seconds())

CORS_ORIGINS_STR = os.environ.get(
    'CORS_ORIGINS',
    'http://localhost:5173,http://localhost:5174,http://localhost:3000,'
    'http://127.0.0.1:5173,http://127.0.0.1:5174',
)
CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in CORS_ORIGINS_STR.split(',') if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'UNAUTHENTICATED_USER': None,
}

POSTS_PER_PAGE = int(os.environ.get('POSTS_PER_PAGE', 10))
PROJECTS_PER_PAGE = int(os.environ.get('PROJECTS_PER_PAGE', 12))

UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or str(BASE_DIR / 'static' / 'uploads')
MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 100 * 1024 * 1024))
DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_CONTENT_LENGTH
FILE_UPLOAD_MAX_MEMORY_SIZE = MAX_CONTENT_LENGTH
ALLOWED_EXTENSIONS = set(
    os.environ.get('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,gif,webp').split(',')
)

BIND_HOST = os.environ.get('BIND_HOST', '127.0.0.1')
DEV_PORT = int(os.environ.get('dev_port', 8000))
PROD_PORT = int(os.environ.get('prod_port', 8000))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
