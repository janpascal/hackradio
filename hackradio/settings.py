"""
Django settings for hackradio project.

Generated by 'django-admin startproject' using Django 1.10.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from ConfigParser import ConfigParser

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'j$6lcn^ua=%&f7ac5xrm65f+ba&23y+lw+rf^3byy-qdll$+yr'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'jukebox.apps.JukeboxConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ordered_model',
    'django_js_reverse',
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

ROOT_URLCONF = 'hackradio.urls'

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

WSGI_APPLICATION = 'hackradio.wsgi.application'

TWEET_BASEPATH = 'results'


config = ConfigParser()
config.read(os.path.join(BASE_DIR, 'hackradio', 'local.ini'))

#DATABASES = {
#    'default': {
#        'ENGINE': config.get('database', 'ENGINE'),
#        'NAME': config.get('database', 'NAME'),
#        'USER': config.get('database', 'USER'),
#        'PASSWORD': config.get('database', 'PASSWORD'),
#        'HOST': config.get('database', 'HOST'),
#        'OPTIONS': {'charset': 'utf8mb4'},
#    }
#}

JUKEBOX_SHOUT_HOST = config.get('shout', 'JUKEBOX_SHOUT_HOST')
JUKEBOX_SHOUT_PORT = config.getint('shout', 'JUKEBOX_SHOUT_PORT')
JUKEBOX_SHOUT_USER = config.get('shout', 'JUKEBOX_SHOUT_USER')
JUKEBOX_SHOUT_PASSWORD = config.get('shout', 'JUKEBOX_SHOUT_PASSWORD')
JUKEBOX_SHOUT_MOUNT = config.get('shout', 'JUKEBOX_SHOUT_MOUNT')
JUKEBOX_SHOUT_NAME = config.get('shout', 'JUKEBOX_SHOUT_NAME')
JUKEBOX_SHOUT_GENRE = config.get('shout', 'JUKEBOX_SHOUT_GENRE')
JUKEBOX_SHOUT_URL = config.get('shout', 'JUKEBOX_SHOUT_URL')
JUKEBOX_SHOUT_PUBLIC = config.getint('shout', 'JUKEBOX_SHOUT_PUBLIC')

JUKEBOX_ROOT_DIR = config.get('shout', 'JUKEBOX_ROOT_DIR')
JUKEBOX_STREAM_URL = config.get('shout', 'JUKEBOX_STREAM_URL')

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
