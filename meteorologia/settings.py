#settings.py
"""
Configurações do Django para o projeto 'meteorologia'.

Gerado por 'django-admin startproject' usando Django 5.0.4.

Para mais informações sobre este arquivo, veja
https://docs.djangoproject.com/en/5.0/topics/settings/

Para a lista completa de configurações e seus valores, veja
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
from celery.schedules import crontab
import logging

# Configuração básica do logging
logging.basicConfig(level=logging.DEBUG)

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Configurações rápidas de desenvolvimento - não são adequadas para produção
# Veja https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# Chave secreta - manter secreta em produção
SECRET_KEY = 'django-insecure-29lb=l1^8lcv^b0d9!w-gmrjq1ggh5#(un2$u5rest_zk1%$ui'

# Definir DEBUG como True para desenvolvimento
DEBUG = True

# Hosts permitidos
ALLOWED_HOSTS = []

# Definição das aplicações do projeto
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'G2app',
    'django_celery_beat',
    'django_celery_results',
]

# Definição dos middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuração da URL principal
ROOT_URLCONF = 'meteorologia.urls'

# Configuração dos templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'G2app/templates')],
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

# Configuração da aplicação WSGI
WSGI_APPLICATION = 'meteorologia.wsgi.application'

# Chave da API do Google Maps
GOOGLE_MAPS_API_KEY = 'AIzaSyANVnlD8qgnSzhL7UWTSmBPlaisCb37K-c'

# Configuração da base de dados
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Validação de senha
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
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

# Internacionalização
# https://docs.djangoproject.com/en/5.0/topics/i18n/
LANGUAGE_CODE = 'pt-pt'

TIME_ZONE = 'Europe/Lisbon'

USE_I18N = True

USE_TZ = True

# Arquivos estáticos (CSS, JavaScript, Imagens)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = 'static/'

# Tipo de campo de chave primária padrão
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuração do Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'

# Configurações adicionais do Celery
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Configuração do agendador do Celery Beat
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Importar a aplicação Celery
from .celery import app as celery_app
__all__ = ('celery_app',)

# Configurações de email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'forecastnow49@gmail.com'
EMAIL_HOST_PASSWORD = 'dpui wapq rmga zeyn'
DEFAULT_FROM_EMAIL = 'forecastnow49@gmail.com'
