import os
import subprocess

import environ
import sentry_sdk
from django.utils.translation import gettext_lazy as _

checkout_dir = environ.Path(__file__) - 2
assert os.path.exists(checkout_dir("manage.py"))

parent_dir = checkout_dir.path("..")
if os.path.isdir(parent_dir("etc")):
    env_file = parent_dir("etc/env")
    default_var_root = environ.Path(parent_dir("var"))
else:
    env_file = checkout_dir(".env")
    default_var_root = environ.Path(checkout_dir("var"))

env = environ.Env(
    ALLOWED_HOSTS=(list, []),
    CACHE_URL=(str, "locmemcache://"),
    CORS_ORIGIN_ALLOW_ALL=(bool, False),
    CORS_ORIGIN_WHITELIST=(list, []),
    DATABASE_URL=(str, ""),
    DEBUG=(bool, False),
    DEFAULT_FROM_EMAIL=(str, "no-reply@hel.ninja"),
    HELUSERS_PASSWORD_LOGIN_DISABLED=(bool, False),
    ILMOITIN_QUEUE_NOTIFICATIONS=(bool, False),
    ILMOITIN_TRANSLATED_FROM_EMAIL=(dict, {}),
    MAIL_MAILGUN_API=(str, ""),
    MAIL_MAILGUN_DOMAIN=(str, ""),
    MAIL_MAILGUN_KEY=(str, ""),
    MAILER_EMAIL_BACKEND=(str, "django.core.mail.backends.console.EmailBackend"),
    MAILER_LOCK_PATH=(str, "/tmp/mailer_lockfile"),
    MEDIA_ROOT=(environ.Path(), environ.Path(checkout_dir("var"))("media")),
    MEDIA_URL=(str, "/media/"),
    QURIIRI_API_KEY=(str, ""),
    QURIIRI_API_URL=(str, "https://api.quriiri.fi/v1/"),
    QURIIRI_REPORT_URL=(str, ""),
    SECRET_KEY=(str, ""),
    SENTRY_DSN=(str, ""),
    SENTRY_ENABLE_TRACING=(bool, False),
    SENTRY_ENVIRONMENT=(str, ""),
    SENTRY_TRACES_SAMPLE_RATE=(float, 0.1),
    SOCIAL_AUTH_TUNNISTAMO_KEY=(str, "KEY_UNSET"),
    SOCIAL_AUTH_TUNNISTAMO_OIDC_ENDPOINT=(str, "OIDC_ENDPOINT_UNSET"),
    SOCIAL_AUTH_TUNNISTAMO_SECRET=(str, "SECRET_UNSET"),
    STATIC_ROOT=(environ.Path(), default_var_root("static")),
    STATIC_URL=(str, "/static/"),
    TOKEN_AUTH_ACCEPTED_AUDIENCE=(str, "https://api.hel.fi/auth/notification_service"),
    TOKEN_AUTH_ACCEPTED_SCOPE_PREFIX=(str, "notification_service"),
    TOKEN_AUTH_AUTHSERVER_URL=(str, ""),
    TOKEN_AUTH_REQUIRE_SCOPE_PREFIX=(bool, True),
    USE_X_FORWARDED_HOST=(bool, False),
)

if os.path.exists(env_file):
    env.read_env(env_file)
BASE_DIR = str(checkout_dir)

DEBUG = env.bool("DEBUG")
SECRET_KEY = env.str("SECRET_KEY")
if DEBUG and not SECRET_KEY:
    raise EnvironmentError("The environmental variable SECRET_KEY is not set.")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
USE_X_FORWARDED_HOST = env.bool("USE_X_FORWARDED_HOST")

DATABASES = {"default": env.db()}

CACHES = {"default": env.cache()}

if env.str("DEFAULT_FROM_EMAIL"):
    DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL")
if env("MAIL_MAILGUN_KEY"):
    ANYMAIL = {
        "MAILGUN_API_KEY": env("MAIL_MAILGUN_KEY"),
        "MAILGUN_SENDER_DOMAIN": env("MAIL_MAILGUN_DOMAIN"),
        "MAILGUN_API_URL": env("MAIL_MAILGUN_API"),
    }
EMAIL_BACKEND = "mailer.backend.DbBackend"
MAILER_EMAIL_BACKEND = env.str("MAILER_EMAIL_BACKEND")
if env("MAILER_LOCK_PATH"):
    MAILER_LOCK_PATH = env.str("MAILER_LOCK_PATH")
ILMOITIN_TRANSLATED_FROM_EMAIL = env("ILMOITIN_TRANSLATED_FROM_EMAIL")
ILMOITIN_QUEUE_NOTIFICATIONS = env("ILMOITIN_QUEUE_NOTIFICATIONS")

try:
    REVISION = (
        subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
        .strip()
        .decode("utf-8")
    )
except Exception:
    REVISION = "n/a"

sentry = sentry_sdk.init(
    dsn=env.str("SENTRY_DSN"),
    release=REVISION,
    environment=env("SENTRY_ENVIRONMENT"),
    enable_tracing=env.bool("SENTRY_ENABLE_TRACING"),
    traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE"),
)

MEDIA_ROOT = env("MEDIA_ROOT")
STATIC_ROOT = env("STATIC_ROOT")
MEDIA_URL = env.str("MEDIA_URL")
STATIC_URL = env.str("STATIC_URL")

ROOT_URLCONF = "notification_service.urls"
WSGI_APPLICATION = "notification_service.wsgi.application"

LANGUAGE_CODE = "fi"
LANGUAGES = (("fi", _("Finnish")), ("en", _("English")), ("sv", _("Swedish")))
TIME_ZONE = "Europe/Helsinki"
USE_I18N = True
USE_TZ = True

INSTALLED_APPS = [
    "helusers.apps.HelusersConfig",
    "helusers.apps.HelusersAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "anymail",
    "mailer",
    "axes",
    # local apps under this line
    "api",
    "social_django",
    "users",
    "utils",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "helusers.context_processors.settings",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

CORS_ORIGIN_WHITELIST = env.list("CORS_ORIGIN_WHITELIST")
CORS_ORIGIN_ALLOW_ALL = env.bool("CORS_ORIGIN_ALLOW_ALL")

AUTHENTICATION_BACKENDS = [
    "helusers.tunnistamo_oidc.TunnistamoOIDCAuth",
    "axes.backends.AxesBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_USER_MODEL = "users.User"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Keycloak parameters. Reference to Tunnistamo is necessary, although
# the naming convention is primarily historical.
SOCIAL_AUTH_TUNNISTAMO_SECRET = env.str("SOCIAL_AUTH_TUNNISTAMO_SECRET")
SOCIAL_AUTH_TUNNISTAMO_KEY = env.str("SOCIAL_AUTH_TUNNISTAMO_KEY")
SOCIAL_AUTH_TUNNISTAMO_OIDC_ENDPOINT = env.str("SOCIAL_AUTH_TUNNISTAMO_OIDC_ENDPOINT")

# A boolean that disables/enables Django admin password login
HELUSERS_PASSWORD_LOGIN_DISABLED = env.bool("HELUSERS_PASSWORD_LOGIN_DISABLED")

SOCIAL_AUTH_END_SESSION_URL = "/helauth/logout/"
LOGIN_REDIRECT_URL = "/admin/"
LOGOUT_REDIRECT_URL = "/admin/"

OIDC_API_TOKEN_AUTH = {
    "AUDIENCE": env.str("TOKEN_AUTH_ACCEPTED_AUDIENCE"),
    "API_SCOPE_PREFIX": env.str("TOKEN_AUTH_ACCEPTED_SCOPE_PREFIX"),
    "ISSUER": env.str("TOKEN_AUTH_AUTHSERVER_URL"),
    "REQUIRE_API_SCOPE_FOR_AUTHENTICATION": env.bool("TOKEN_AUTH_REQUIRE_SCOPE_PREFIX"),
}

OIDC_AUTH = {"OIDC_LEEWAY": 60 * 60}


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ]
}

SITE_ID = 1

AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # hour after locked out, user will be able to attempt login

QURIIRI_API_KEY = env.str("QURIIRI_API_KEY")
QURIIRI_API_URL = env.str("QURIIRI_API_URL")
QURIIRI_REPORT_URL = env.str("QURIIRI_REPORT_URL")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"django": {"handlers": ["console"], "level": "ERROR"}},
}

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
local_settings_path = os.path.join(checkout_dir(), "local_settings.py")
if os.path.exists(local_settings_path):
    with open(local_settings_path) as fp:
        code = compile(fp.read(), local_settings_path, "exec")
    exec(code, globals(), locals())


# Helusers stores the access token expiration time as a datetime which is
# not serializable to JSON, # so Django needs to be configured to use the
# built-in PickleSerializer
SESSION_SERIALIZER = "django.contrib.sessions.serializers.PickleSerializer"
