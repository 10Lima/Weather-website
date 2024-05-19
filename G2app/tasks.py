# G2app/tasks.py

# tasks.py
# tasks.py
from celery import shared_task
from .models import HistoricoPesquisa
from django.contrib.auth.models import User
from .views import analyze_weather_data, send_alert_email, fetch_weather_data
from datetime import datetime, timedelta

@shared_task
def check_weather_alerts():
    # Verificar as localizações recentes de cada usuário
    users = User.objects.all()
    for user in users:
        # Obter as 4 localizações mais recentes
        recent_searches = HistoricoPesquisa.objects.filter(usuario=user).order_by('-data_pesquisa')[:4]
        
        for search in recent_searches:
            if search.local_pesquisa:
                # Pegar os dados de clima da localização
                weather_data = fetch_weather_data(location=search.local_pesquisa)
                if weather_data:
                    # Analisar os dados de clima
                    alerts = analyze_weather_data(weather_data)
                    if alerts:
                        # Enviar e-mail de alerta
                        send_alert_email(user.email, weather_data, alerts)
