import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Load local environment variables
load_dotenv(BASE_DIR / ".env")


def get_boolean(name, default=False):
    """Read a Boolean value from an environment variable."""
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {
        "true",
        "1",
        "yes",
        "on",
    }


def get_list(name, default=""):
    """Convert a comma-separated environment variable into a list."""
    value = os.getenv(name, default)

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


# Security
DEBUG = get_boolean("DEBUG", True)

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-local-development-key",
)

if not DEBUG and SECRET_KEY == "django-insecure-local-development-key":
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY must be configured in production."
    )


ALLOWED_HOSTS = get_list(
    "ALLOWED_HOSTS",
    "127.0.0.1,localhost",
)

CSRF_TRUSTED_ORIGINS = get_list(
    "CSRF_TRUSTED_ORIGINS",
    "http://127.0.0.1:8000,http://localhost:8000",
)

SITE_URL = os.getenv(
    "SITE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


# Applications
INSTALLED_APPS = [
    # Local applications
    "accounts",
    "blog",

    # Third-party applications
    "cloudinary_storage",
    "cloudinary",

    # Django applications
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_ckeditor_5",
    "django.contrib.sitemaps",
    
]


# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# URL and application configuration
ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"

ASGI_APPLICATION = "config.asgi.application"


# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# Database
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=60,
            conn_health_checks=True,
            ssl_require=not DEBUG,
        )
    }
else:
    if not DEBUG:
        raise ImproperlyConfigured(
            "DATABASE_URL must be configured in production."
        )

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# Custom user model
AUTH_USER_MODEL = "accounts.CustomUser"


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# Authentication redirects
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "blog:home"
LOGOUT_REDIRECT_URL = "blog:home"


# Internationalization
LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Nairobi"

USE_I18N = True

USE_TZ = True


# Static files
STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]


# Local media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# Cloudinary configuration
CLOUDINARY_CLOUD_NAME = os.getenv(
    "CLOUDINARY_CLOUD_NAME",
    "",
).strip()

CLOUDINARY_API_KEY = os.getenv(
    "CLOUDINARY_API_KEY",
    "",
).strip()

CLOUDINARY_API_SECRET = os.getenv(
    "CLOUDINARY_API_SECRET",
    "",
).strip()

CLOUDINARY_IS_CONFIGURED = all(
    [
        CLOUDINARY_CLOUD_NAME,
        CLOUDINARY_API_KEY,
        CLOUDINARY_API_SECRET,
    ]
)

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": CLOUDINARY_CLOUD_NAME,
    "API_KEY": CLOUDINARY_API_KEY,
    "API_SECRET": CLOUDINARY_API_SECRET,
    "SECURE": True,
}


# File storage
if CLOUDINARY_IS_CONFIGURED:
    DEFAULT_STORAGE_BACKEND = (
        "cloudinary_storage.storage.MediaCloudinaryStorage"
    )
else:
    DEFAULT_STORAGE_BACKEND = (
        "django.core.files.storage.FileSystemStorage"
    )

STORAGES = {
    "default": {
        "BACKEND": DEFAULT_STORAGE_BACKEND,
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage."
            "CompressedManifestStaticFilesStorage"
        ),
    },
}


# Email configuration
EMAIL_HOST = os.getenv(
    "EMAIL_HOST",
    "smtp-relay.brevo.com",
)

EMAIL_PORT = int(
    os.getenv(
        "EMAIL_PORT",
        "587",
    )
)

EMAIL_USE_TLS = get_boolean(
    "EMAIL_USE_TLS",
    True,
)

EMAIL_HOST_USER = os.getenv(
    "EMAIL_HOST_USER",
    "",
)

EMAIL_HOST_PASSWORD = os.getenv(
    "EMAIL_HOST_PASSWORD",
    "",
)

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    "TechBlogKe <clintechke@gmail.com>",
)

if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
elif DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    raise ImproperlyConfigured(
        "Email credentials must be configured in production."
    )


# Messages
MESSAGE_STORAGE = (
    "django.contrib.messages.storage.session.SessionStorage"
)


# Production proxy and cookie security
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

X_FRAME_OPTIONS = "DENY"

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_REFERRER_POLICY = "same-origin"


# Primary key configuration
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "blockQuote",
            "codeBlock",
            "insertTable",
            "undo",
            "redo",
        ],
    }
}