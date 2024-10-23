import os
from pathlib import Path
import environ

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False)
)

# Set the project base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Read the .env file
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# Allowed hosts configuration
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["dtrack.zprime.ai"])

# Site URL
SSITE_URL = os.getenv('SITE_URL', 'http://localhost:8000')

# Application definition
INSTALLED_APPS = [
    # Django default apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Custom Apps
    "accounts",
    "certificates",
    "food_safety",
    "notifications",
    "qr_generator",
    "file_management",
    "dashboard",
    "supplier_management",
    "reports",
    "audit_logs",
    "custom_auth",
    "user_management",
    "compliance",
    "analytics",
    "system_settings",
    "payments",
    "support",
    "inventory",
    "task_scheduler",
    "approval",
    "profiles",
    "notification_templates",
    "twilio_app",
    # Third-party apps (if any)
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Place WhiteNoiseMiddleware here
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # For multi-language support
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "dtrack.urls"

# Template configuration
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",  # Remove in production if DEBUG=False
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "dtrack.wsgi.application"

# Database configuration
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT", default="5432"),
        "CONN_MAX_AGE": 600,  # Keep connections open for performance
        "OPTIONS": {
            "sslmode": "require",  # Ensure SSL is enabled
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 12,  # Increase minimum length for better security
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization and localization settings
LANGUAGE_CODE = "en-us"

LANGUAGES = [
    ("en", "English"),
    ("ar", "Arabic"),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",  # Path to store language translations
]

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files configuration
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files configuration
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Static files storage
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom user model
AUTH_USER_MODEL = "accounts.CustomUser"

# Email configuration
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)

EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="webmaster@dtrack.zprime.ai")

# Twilio configuration
TWILIO_ACCOUNT_SID = env("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = env("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = env("TWILIO_PHONE_NUMBER")

# Ensure Twilio credentials are set
if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
    raise ValueError("Twilio credentials are not all set in environment variables.")

# Authentication backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# Security settings
# SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=3600)
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Content Security Policy (CSP)
# You might need to install django-csp or similar middleware
# CSP_DEFAULT_SRC = ("'self'",)
# CSP_STYLE_SRC = ("'self'", "https://fonts.googleapis.com")
# CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Additional settings
# Add any other settings specific to your project or third-party apps
