import os
import sys
from pathlib import Path

import dj_database_url

# import prometheus_client
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# os.environ["PROMETHEUS_MULTIPROC_DIR"] = os.environ.get(
#     "PROMETHEUS_MULTIPROC_DIR", str(BASE_DIR / "prometheus_metrics")
# )

# prometheus_client.values.ValueClass = prometheus_client.values.MultiProcessValue(
#     process_identifier=lambda: os.environ.get("APP_WORKER_ID", "1")
# )

ENV_FILE_PATH = BASE_DIR / ".env"

if os.path.exists(ENV_FILE_PATH):
    load_dotenv(ENV_FILE_PATH)

sys.path.append(str(BASE_DIR))

SECRET_KEY = os.environ.get("SECRET_KEY", "dk&%(9#899k2s_p_b4+vjyt(mb9916&i&4i+%$%*3y9+sr$m3tt")

DEBUG = int(os.environ.get("DEBUG", False))

ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "salaries",
    "rest_framework",
    "corsheaders",
    # "django_prometheus",
]

MIDDLEWARE = [
    # "salaries.middlewares.simple_middleware",
    # "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "salaries.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "salaries.wsgi.application"

DATABASES = {"default": dj_database_url.config(default="sqlite:///" + str(BASE_DIR / "db.sqlite3"))}

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

LANGUAGE_CODE = "ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_ROOT = BASE_DIR / "static"
STATIC_URL = "/static/"
LOGIN_URL = "/auth/login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

REST_FRAMEWORK = {"DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"]}

CORS_ORIGIN_ALLOW_ALL = True

AMOCRM_ENTITIES_ENDPOINT_AUTH_KEY = os.environ.get("AMOCRM_ENTITIES_ENDPOINT_AUTH_KEY")
SALARIES_DASHBOARD_AUTH_KEY = os.environ.get("SALARIES_DASHBOARD_AUTH_KEY")
