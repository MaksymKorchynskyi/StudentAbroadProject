import os
from pathlib import Path
from dotenv import load_dotenv

# Будуємо шляхи всередині проекту: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Завантажуємо змінні з файлу .env
# Шукаємо .env у папці backend, або в корені проекту (на рівень вище)
_env_path = BASE_DIR / '.env'
if not _env_path.exists():
    _env_path = BASE_DIR.parent / '.env'
load_dotenv(_env_path)


# ============================================================
# БЕЗПЕКА
# ============================================================
# SECRET_KEY — обов'язково задати у .env (без fallback на продакшні!)
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-only-change-in-production')

# DEBUG — за замовчуванням False (безпечний дефолт для продакшну)
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS — конкретні домени (ніколи не ['*'] на продакшні!)
ALLOWED_HOSTS = [
    h.strip() for h in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()
]

# ДОДАТКИ
INSTALLED_APPS = [
    # Django Unfold - MUST be before django.contrib.admin
    "unfold",
    "unfold.contrib.filters",
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',  # SEO: Sitemap generation
    
    # Сторонні бібліотеки
    'rest_framework',
    'corsheaders',
    'django_filters',
    'django_countries',
    
    # Твої додатки (Apps)
    'universities.apps.UniversitiesConfig',
    'programs.apps.ProgramsConfig',
    'faq.apps.FaqConfig',  # Окремий додаток FAQ
]

# ============================================================
# DJANGO UNFOLD CONFIGURATION
# ============================================================
from django.templatetags.static import static
from django.urls import reverse_lazy

UNFOLD = {
    "SITE_TITLE": "StudentAbroad Adminka",
    "SITE_HEADER": "StudentAbroad Adminka",
    "SITE_SYMBOL": "school",  # Material Symbol
    
    # Color theme - Academic Blue
    "COLORS": {
        "primary": {
            "50": "239 246 255",
            "100": "219 234 254",
            "200": "191 219 254",
            "300": "147 197 253",
            "400": "96 165 250",
            "500": "59 130 246",
            "600": "37 99 235",
            "700": "29 78 216",
            "800": "30 64 175",  # Primary Academic Blue #1E40AF
            "900": "30 58 138",
            "950": "23 37 84",
        },
    },
    
    # Sidebar Navigation Groups
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Education Content",
                "separator": True,
                "items": [
                    {
                        "title": "Програми",
                        "icon": "menu_book",
                        "link": reverse_lazy("admin:programs_program_changelist"),
                    },
                    {
                        "title": "Університети",
                        "icon": "school",
                        "link": reverse_lazy("admin:universities_university_changelist"),
                    },
                ],
            },
            {
                "title": "Site Content",
                "separator": True,
                "items": [
                    {
                        "title": "FAQ",
                        "icon": "help_center",
                        "link": reverse_lazy("admin:faq_faqitem_changelist"),
                    },
                    {
                        "title": "FAQ Категорії",
                        "icon": "category",
                        "link": reverse_lazy("admin:faq_faqcategory_changelist"),
                    },
                ],
            },
            {
                "title": "Access Control",
                "separator": True,
                "items": [
                    {
                        "title": "Користувачі",
                        "icon": "people",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                    {
                        "title": "Групи",
                        "icon": "groups",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
        ],
    },
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise — роздача статики на продакшні
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    'corsheaders.middleware.CorsMiddleware', # CORS має бути високо
    'django.middleware.locale.LocaleMiddleware', # Мови
    
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Вказуємо, що головний файл URL лежить у папці config
ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # <-- Вказуємо папку templates у корені backend
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'config.context_processors.seo_defaults',  # SEO defaults
            ],
        },
    },
]

# Вказуємо, що WSGI лежить у папці config
WSGI_APPLICATION = 'config.wsgi.application'

# ============================================================
# БАЗА ДАНИХ (PostgreSQL)
# ============================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME', 'studentabroad_db'),
        'USER': os.getenv('DATABASE_USER', 'postgres'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', ''),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
        # Connection pooling — зберігати з'єднання 10 хвилин (замість нового на кожен запит)
        'CONN_MAX_AGE': 600,
        'CONN_HEALTH_CHECKS': True,
    }
}

# ВАЛІДАЦІЯ ПАРОЛІВ
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# МОВНІ НАЛАШТУВАННЯ
LANGUAGE_CODE = 'uk'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

from django.utils.translation import gettext_lazy as _
LANGUAGES = [
    ('uk', _('Ukrainian')),
    ('en', _('English')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# ============================================================
# СТАТИКА І МЕДІА
# ============================================================
STATIC_URL = '/static/'
# Ми беремо статику з папки static у корені backend
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / 'staticfiles' # Для collectstatic

# WhiteNoise — стиснення та кешування статичних файлів
STORAGES = {
    "staticfiles": {
        "BACKEND": "config.storage.NonStrictWhiteNoiseStorage",
    },
}

# ============================================================
# CLOUDFLARE R2 (MEDIA STORAGE)
# ============================================================
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
AWS_S3_REGION_NAME = 'auto'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN')

if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    # Cloudflare не підтримує S3 ACLs, тому вимикаємо їх
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    
    # Якщо є публічний домен (r2.dev або свій), вимикаємо генерацію довгих тимчасових посилань
    if AWS_S3_CUSTOM_DOMAIN:
        AWS_QUERYSTRING_AUTH = False
    
    # Використовувати R2 для MEDIA
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    }

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# НАЛАШТУВАННЯ ID (Потрібно для деяких моделей)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# CORS — Cross-Origin Resource Sharing
# ============================================================
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Тільки для розробки (DEBUG=True)
CORS_ALLOW_CREDENTIALS = True

# На продакшні CORS_ALLOW_ALL_ORIGINS=False, і використовуються тільки ці origins:
_cors_origins_env = os.getenv('CORS_ORIGINS', '')
CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in _cors_origins_env.split(',') if origin.strip()
] if _cors_origins_env else [
    # Fallback для локальної розробки
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5500",
]

# ============================================================
# CSRF — Cross-Site Request Forgery Protection
# ============================================================
# Django 4.0+ вимагає CSRF_TRUSTED_ORIGINS для роботи за Nginx reverse proxy
_csrf_origins_env = os.getenv('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in _csrf_origins_env.split(',') if origin.strip()
] if _csrf_origins_env else [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# ============================================================
# REST FRAMEWORK
# ============================================================
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        # 'rest_framework.renderers.BrowsableAPIRenderer', # Розкоментуй для зручності в браузері
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.QueryParameterVersioning',
    
    # Rate Limiting — захист від спаму та DDoS
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    
    # Пагінація — не віддавати всі записи одним запитом
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}

# ============================================================
# SECURITY HEADERS (Production)
# ============================================================
# Захист від XSS, clickjacking, content type sniffing
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# HTTPS-only settings (активується через .env на продакшні)
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False') == 'True'
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000  # 1 рік
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ============================================================
# CACHING
# ============================================================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': BASE_DIR / 'cache',
        'TIMEOUT': 3600,  # 1 година
    }
}

# ============================================================
# LOGGING
# ============================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} [{levelname}] {name}: {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 5 * 1024 * 1024,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'] + (['file'] if not DEBUG else []),
        'level': 'INFO' if DEBUG else 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'] + (['file'] if not DEBUG else []),
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'] + (['file'] if not DEBUG else []),
            'level': 'ERROR',
            'propagate': False,
        },
        # Логер для кастомних додатків
        'programs': {
            'handlers': ['console'] + (['file'] if not DEBUG else []),
            'level': 'INFO' if DEBUG else 'WARNING',
            'propagate': False,
        },
        'universities': {
            'handlers': ['console'] + (['file'] if not DEBUG else []),
            'level': 'INFO' if DEBUG else 'WARNING',
            'propagate': False,
        },
        'faq': {
            'handlers': ['console'] + (['file'] if not DEBUG else []),
            'level': 'INFO' if DEBUG else 'WARNING',
            'propagate': False,
        },
    },
}

# ============================================================
# CLOUDFLARE TURNSTILE (Anti-bot CAPTCHA)
# ============================================================
# Ключі отримати: https://dash.cloudflare.com/?to=/:account/turnstile
# Якщо ключі не задані — Turnstile вимкнений (для локальної розробки)
TURNSTILE_SITE_KEY = os.getenv('TURNSTILE_SITE_KEY', '')
TURNSTILE_SECRET_KEY = os.getenv('TURNSTILE_SECRET_KEY', '')