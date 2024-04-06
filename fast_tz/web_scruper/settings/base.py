import datetime
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4e&6aw+(5&cg^_!05r(&7_#dghg_pdgopq(yk)xa^bog7j)^*j'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
DNS_NAME = os.environ.get("DNS_NAME", 'localhost')
HOST_IP = os.environ.get("HOST_IP", "127.0.0.1")

PROTOCOL = 'http' if DNS_NAME == 'localhost' else 'https'
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = 6379
REDIS_LOGS_DB = 3
REDIS_RESULT_DB = 1
REDIS_BROKER_DB = 0
REDIS_SCHEDULER_DB = 2
REDIS_CACHE_DB = 4
REDIS_COMMON_DB = 5
CELERY_TIMEOUT = 4 * 60 * 60
CELERY_HARD_TIMEOUT = 16 * 60 * 60

CELERY_BROKER_URL = f"rediss://{REDIS_HOST}:{REDIS_PORT}/{REDIS_BROKER_DB}?ssl_cert_reqs=none"
CELERY_BROKER_POOL_LIMIT = 50
CELERY_RESULT_BACKEND = f"rediss://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULT_DB}?ssl_cert_reqs=none"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_EXPIRES = datetime.timedelta(days=60)

LOG_LINK = f"{PROTOCOL}://{DNS_NAME}/logs/%(task_name)/%(task_id).txt"

CELERY_TIMEOUTS_BY_TASK = {
    "fb_scrupper": 1 * 60 * 60,
}

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

DJANGO_LOG_LEVEL = os.environ.get("DJANGO_LOG_LEVEL", "INFO")
CELERY_LOG_LEVEL = os.environ.get("CELERY_LOG_LEVEL", "INFO")

BASE_LOG_DIR = "/var/log/scruppy"
TASK_LOG_DIR = f"{BASE_LOG_DIR}/logs/%(task_name)"
TASK_LOG_FILE_PATH = f"{TASK_LOG_DIR}/%(task_id).txt"

DEBUG_LOG_FILE_HANDLER_NAME = 'debug_log_file_handler'
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(levelname)s %(asctime)s [%(processName)s/%(threadName)s] "
                      "%(name)s.%(funcName)s:%(lineno)s - %(message)s"
        },
    },
    "handlers": {
        DEBUG_LOG_FILE_HANDLER_NAME: {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": f"{BASE_LOG_DIR}/debug.log",
            "maxBytes": 1024 * 1024 * 50,  # 50 MB
            "backupCount": 5,
        },
        "celery_log_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": f"{BASE_LOG_DIR}/celery.log",
            "maxBytes": 1024 * 1024 * 50,  # 50 MB
            "backupCount": 5,
        },
        "console_handler": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "handlers": [DEBUG_LOG_FILE_HANDLER_NAME, "console_handler"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": [DEBUG_LOG_FILE_HANDLER_NAME, "console_handler"],
            "level": DJANGO_LOG_LEVEL,
            "propagate": False,
        },
        "celery": {
            "handlers": ["celery_log_file_handler", "console_handler"],
            "level": CELERY_LOG_LEVEL,
            "propagate": False,
        },
    },
}

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
LOCAL_MODE_ENABLED = os.environ.get("LOCAL_MODE_ENABLED", False)
