import os

import dj_database_url
import pathlib
import secrets

HERE = pathlib.Path(__file__).parent

ALLOWED_HOSTS = ["*"]
DATABASES = {"default": dj_database_url.config(default="postgis:///pct")}
DEBUG = "DJANGO_DEBUG" in os.environ
LANGUAGE_CODE = "en-us"
MAPBOX_TOKEN = (
    "pk.eyJ1IjoiamFjb2JrYXBsYW5tb3NzIiwiYSI6ImNqYnNjbGRrcDB0MmIyd21rbXRzc3V0b3YifQ.4Kz9dKc86l528aaoiegTqA"
)
ROOT_URLCONF = "pct.urls"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", secrets.token_bytes())
SPATIALITE_LIBRARY_PATH = "mod_spatialite"
SPOT_FEED_ID = "0GXMGIjTLtOisB0eFv6qb1xOdMaOx2u5m"
STATIC_URL = "/static/"
STATIC_ROOT = HERE.parent / "staticfiles"
STATICFILES_DIRS = [HERE.parent / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True
WSGI_APPLICATION = "pct.wsgi.application"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "markdownx",
    "pct",
]
if DEBUG:
    INSTALLED_APPS.append("django_extensions")

MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

# If we're on Heroku, need to do some special stuff to get gis working
# This is based on the (slightly incorrect) advise from two places:
# - https://devcenter.heroku.com/articles/postgis
# - https://github.com/TrailStash/heroku-geo-buildpack
if "DYNO" in os.environ:
    DATABASES["default"]["ENGINE"] = "django.contrib.gis.db.backends.postgis"
    GDAL_LIBRARY_PATH = os.path.expandvars(os.getenv("GDAL_LIBRARY_PATH"))
    GEOS_LIBRARY_PATH = os.path.expandvars(os.getenv("GEOS_LIBRARY_PATH"))

    # django-heroku does a bunch of magic I'd prefer not to have, but the logging
    # config is super-convienient so keep that on
    import django_heroku
    django_heroku.settings(
        locals(),
        databases=False,
        test_runner=False,
        staticfiles=False,
        allowed_hosts=False,
        logging=True,
        secret_key=False,
    )

