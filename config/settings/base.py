"""
Django settings for hello project.

Generated by 'django-admin startproject' using Django 2.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# BASE_DIR = os.path.dirname(
#     os.path.dirname(
#         os.path.abspath(__file__)))

BASE_DIR = Path(os.path.abspath(__file__)).parents[2]


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# configure your proxy to set a custom HTTP header that tells Django whether the request came
# in via HTTPS, and set SECURE_PROXY_SSL_HEADER so that Django knows what header to look for.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

DEBUG = False
ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'presqt',
    'rest_framework',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
    'UNAUTHENTICATED_USER': None,
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/staticfiles/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/mediafiles/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# If we don't do this, NGINX will not be able to serve large files that are uploaded to the server
# since the default permissions set for large files deny it access.
FILE_UPLOAD_PERMISSIONS = 0o644

# Test user tokens. Used for unit tests.
# DON'T EVER USE THESE TOKENS TO STORE NON-PUBLIC DATA AS THEY ARE NOT SECURE
OSF_TEST_USER_TOKEN = os.environ['OSF_TEST_USER_TOKEN']
OSF_PRIVATE_USER_TOKEN = os.environ['OSF_PRIVATE_USER_TOKEN']
OSF_UPLOAD_TEST_USER_TOKEN = os.environ['OSF_UPLOAD_TEST_USER_TOKEN']
OSF_PRESQT_FORK_TOKEN = os.environ['OSF_PRESQT_FORK_TOKEN']
ZENODO_TEST_USER_TOKEN = os.environ['ZENODO_TEST_USER_TOKEN']
CURATE_ND_TEST_TOKEN = os.environ['CURATE_ND_TEST_TOKEN']
GITHUB_TEST_USER_TOKEN = os.environ['GITHUB_TEST_USER_TOKEN']
GITLAB_TEST_USER_TOKEN = os.environ['GITLAB_TEST_USER_TOKEN']
