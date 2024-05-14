# G2app/tasks.py

from celery import shared_task
from .models import HistoricoPesquisa
from .views import get_weather_data, analyze_weather_data, send_alert_email

@shared_task
def check_weather_alerts():
    historico = HistoricoPesquisa.objects.all()
    for item in historico:
        weather_data = get_weather_data(item.local_pesquisa)
        alerts = analyze_weather_data(weather_data)
        if alerts:
            user = item.usuario
            send_alert_email(user.email, weather_data, alerts)
