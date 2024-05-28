from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Definir a variável de ambiente para as configurações do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meteorologia.settings')

# Inicializar a aplicação Celery com o nome 'meteorologia'
app = Celery('meteorologia')

# Configurar a aplicação Celery usando as configurações do Django, com namespace 'CELERY'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-descobrir tarefas definidas nos arquivos 'tasks.py' das aplicações Django
app.autodiscover_tasks()

# Definir a agenda do Celery Beat para tarefas periódicas
app.conf.beat_schedule = {
    # Tarefa para verificar alertas meteorológicos de manhã
    'check-weather-alerts-morning': {
        'task': 'G2app.tasks.check_weather_alerts',  # Caminho para a tarefa
        'schedule': crontab(hour=9, minute=0),  # Horário para executar a tarefa
    },
    # Tarefa para verificar alertas meteorológicos ao meio-dia
    'check-weather-alerts-noon': {
        'task': 'G2app.tasks.check_weather_alerts',  # Caminho para a tarefa
        'schedule': crontab(hour=12, minute=0),  # Horário para executar a tarefa
    },
    # Tarefa para verificar alertas meteorológicos à noite
    'check-weather-alerts-evening': {
        'task': 'G2app.tasks.check_weather_alerts',  # Caminho para a tarefa
        'schedule': crontab(hour=19, minute=55),  # Horário para executar a tarefa
    },
}
