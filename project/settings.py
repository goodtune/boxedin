"""
Django settings for project project.

Settings are managed with django-configurations: each logical deployment is a
class below, chosen with the DJANGO_CONFIGURATION environment variable
(Development by default). Values that vary per deployment are read from the
environment using the DJANGO_ prefix, e.g. DJANGO_SECRET_KEY.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/
https://django-configurations.readthedocs.io/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path

from configurations import Configuration, values

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


class Base(Configuration):
    """Settings shared by every deployment."""

    DEBUG = False

    ALLOWED_HOSTS = values.ListValue([])

    CSRF_TRUSTED_ORIGINS = values.ListValue([])

    # Application definition

    INSTALLED_APPS = [
        # Third-party apps
        "markdownfield",
        # Standard Django apps
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        # Our apps
        "designs",
    ]

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

    ROOT_URLCONF = "project.urls"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
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

    WSGI_APPLICATION = "project.wsgi.application"

    # Database
    # https://docs.djangoproject.com/en/5.2/ref/settings/#databases
    # Read from DATABASE_URL (no prefix), falling back to a local SQLite file.

    DATABASES = values.DatabaseURLValue(
        f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )

    # Password validation
    # https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
    # https://docs.djangoproject.com/en/5.2/topics/i18n/

    LANGUAGE_CODE = "en-us"

    TIME_ZONE = "UTC"

    USE_I18N = True

    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/5.2/howto/static-files/

    STATIC_URL = "static/"
    STATIC_ROOT = BASE_DIR / "staticfiles"

    # Default primary key field type
    # https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

    DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


class Development(Base):
    """Local development and the test suite."""

    DEBUG = True

    # SECURITY WARNING: this key is public; never use it outside development.
    SECRET_KEY = values.Value(
        "django-insecure-g1rdj64cgg+6pm96j#izsxmd&o5=7+54k(%uv+5cp#e9f9p07a"
    )

    ALLOWED_HOSTS = values.ListValue(["localhost", "127.0.0.1", "[::1]"])


class Production(Base):
    """Deployed behind DigitalOcean App Platform (see .do/app.yaml)."""

    SECRET_KEY = values.SecretValue()

    ALLOWED_HOSTS = values.ListValue(environ_required=True)

    CSRF_TRUSTED_ORIGINS = values.ListValue(environ_required=True)

    DATABASES = values.DatabaseURLValue(
        environ_required=True,
        conn_max_age=600,
        conn_health_checks=True,
    )

    # App Platform terminates TLS at its load balancer and redirects HTTP to
    # HTTPS.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
