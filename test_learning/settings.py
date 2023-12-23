"""
Django settings for test_learning project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure--zj9!ham3_&ino22a$s=k7ek57o$z*kk!d%gcg(r@#ni_=1+nj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '159.223.47.176'
    #'139.59.99.129'
]


# Application definition

INSTALLED_APPS = [
    # 'admin_tools_stats',
    # 'django_nvd3',
    'jazzmin',
    #'admin_argon.apps.AdminArgonConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'learning',
    'rest_framework',
    "debug_toolbar",
    'djoser',
    'rest_framework_simplejwt',
    'django_filters',
    'nested_admin',
    'ckeditor',
    'storages',
    'django_rest_passwordreset',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware'
]

ROOT_URLCONF = 'test_learning.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR, 'templates/',],
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

WSGI_APPLICATION = 'test_learning.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
    	'OPTIONS': {
        	'read_default_file': '/etc/mysql/my.cnf',
    	},
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR,'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    #
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',

    ),
}

DJOSER = {
    'PASSWORD_RESET_CONFIRM_URL': 'learning/password_reset_confirm/{uid}/{token}',
    'USERNAME_RESET_CONFIRM_URL': '#/username/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': '#/activate/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': False,
    'SERIALIZERS':{
        'user_create': 'learning.serializers.UserCreateSerializer',
    },
}


SIMPLE_JWT = {
   'AUTH_HEADER_TYPES': ('JWT',),
   'ACCESS_TOKEN_LIFETIME': timedelta(days=5),
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "TIMEOUT": 5,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}


AWS_ACCESS_KEY_ID = 'DO00WGQZGGRM2MLDBUQU'
AWS_SECRET_ACCESS_KEY = 'NyvFsXju2WoeLmspMaVQyS7uEilB1EK+tFAK7PeRAUk'
AWS_STORAGE_BUCKET_NAME = 'api-media'
AWS_S3_ENDPOINT_URL = 'https://learn-ease.sgp1.digitaloceanspaces.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_PUBLIC_MEDIA_LOCATION = 'media/public'
DEFAULT_FILE_STORAGE = 'test_learning.storage_backends.PublicMediaStorage'
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static'),
# ]
#STATIC_URL = 'https://%s/%s/' % (AWS_S3_ENDPOINT_URL, AWS_LOCATION)
#STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
#DEFAULT_FILE_STORAGE = 'learning.storage_backends.PublicMediaStorage'

# Email Backend SMTP Server
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'truelife787799@gmail.com'
EMAIL_HOST_PASSWORD = 'rwsbdouaexkfdsqu'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
#EMAIL_PORT = 2525
#DEFAULT_FROM_EMAIL = 'learnease@gmail.com'
#JAZZMIN SETTINGS

JAZZMIN_SETTINGS = {
    "site_title": "LearnEase",
    "site_header": "LearnEase",
    "site_brand": "LearnEase",
     "welcome_sign": "Welcome to Admin Panel",
    "order_with_respect_to": ["auth", "learning.Category","learning.Course","learning.Section",
                              "learning.SubSection","learning.Video","learning.Pdf","learning.Blog",
                              "learning.Discount","learning.DiscountItem",
                              "learning.Student","learning.Enrollment","learning.EnrollStudents",
                              "learning.Review"],
    #"site_logo": "static/image/learnease-logo.png",
     "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "learning.Category": "fas fa-layer-group",
        "learning.Student": "fas fa-users",
        "learning.Course":"fas fa-book-open",
        "learning.BlogLink":"fas fa-link",
        "learning.Blog":"fas fa-clipboard",
        "learning.DiscountItem":"fas fa-tag",
        "learning.Discount":"fas fa-percent",
        "learning.EnrollStudents": "fas fa-graduation-cap",
        "learning.Enrollment":"fas fa-money-bill",
        "learning.Pdf":"fas fa-file-pdf",
        "learning.Review":"fas fa-comment-dots",
        "learning.Section":"fas fa-object-group",
         "learning.SubSection":"fas fa-object-ungroup",
         "learning.Video": "fas fa-film",
         "django_rest_passwordreset.resetpasswordtoken": "fas fa-lock",
    },
}
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-success",
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-success",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "journal",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    "actions_sticky_top": False
}
#JAZZMIN_SETTINGS["show_ui_builder"] = True


