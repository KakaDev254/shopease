"""
Django settings for ShopEase project.

Local dev:  SQLite + local media
Production: Railway (PostgreSQL) + Cloudinary media + WhiteNoise static

Environment variables are read from .env via python-decouple.
"""

from pathlib import Path
from decouple import config, Csv
import dj_database_url
import cloudinary
import cloudinary.uploader
import cloudinary.api


# ------------------------------------------------------------------
# BASE
# ------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')

# DEBUG=True locally (set in .env), False in production
DEBUG = config('DEBUG', default=False, cast=bool)

# ALLOWED_HOSTS — comma-separated in .env
#   dev  → localhost,127.0.0.1
#   prod → shopease.up.railway.app,.railway.app,shopease.co.ke
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1',
    cast=Csv()
)

# CSRF trusted origins (required for HTTPS on Railway)
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:8000,http://127.0.0.1:8000',
    cast=Csv()
)


# ------------------------------------------------------------------
# APPLICATIONS
# ------------------------------------------------------------------
INSTALLED_APPS = [
    # Cloudinary must come BEFORE staticfiles
    'cloudinary_storage',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'cloudinary',

    # Project apps
    'core',
    'products',
    'accounts',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # static files on Railway
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'shopease_project.urls'


# ------------------------------------------------------------------
# TEMPLATES (root-level templates/ folder)
# ------------------------------------------------------------------
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
                'core.context_processors.global_context',   # navbar: categories, cart & wishlist counts
            ],
        },
    },
]

WSGI_APPLICATION = 'shopease_project.wsgi.application'


# ------------------------------------------------------------------
# DATABASE
# Local:  SQLite fallback if DATABASE_URL is not set
# Railway: DATABASE_URL injected automatically by Postgres plugin
# ------------------------------------------------------------------
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
        conn_max_age=600,
        ssl_require=not DEBUG,   # SSL only in production
    )
}


# ------------------------------------------------------------------
# PASSWORD VALIDATION
# ------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ------------------------------------------------------------------
# I18N
# ------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True


# ------------------------------------------------------------------
# STATIC FILES (root-level static/ folder)
# ------------------------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise compressed manifest (best for Railway)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ------------------------------------------------------------------
# MEDIA (Cloudinary handles all uploads)
# ------------------------------------------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': config('CLOUDINARY_API_KEY'),
    'API_SECRET': config('CLOUDINARY_API_SECRET'),
}

# Explicitly configure the Cloudinary SDK.
# This prevents "Must supply api_key" errors in the admin upload view.
cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
    secure=True
)

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'


# ------------------------------------------------------------------
# DEFAULT AUTO FIELD
# ------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ------------------------------------------------------------------
# EMAIL (console in dev → swap to SMTP in prod)
# ------------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'sales@shopease.co.ke'


# ------------------------------------------------------------------
# SESSION (guest cart & wishlist)
# ------------------------------------------------------------------
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30   # 30 days
CART_SESSION_ID = 'cart'
WISHLIST_SESSION_ID = 'wishlist'


# ------------------------------------------------------------------
# AUTH REDIRECTS
# ------------------------------------------------------------------
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


# ------------------------------------------------------------------
# PRODUCTION SECURITY HARDENING (only when DEBUG=False)
# ------------------------------------------------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True