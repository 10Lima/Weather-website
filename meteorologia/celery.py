# celery.py
# celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meteorologia.settings')

app = Celery('meteorologia')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-weather-alerts-every-hour': {
        'task': 'G2app.tasks.check_weather_alerts',
        'schedule': crontab(minute=0, hour='*'),  # A cada hora
    },
}

