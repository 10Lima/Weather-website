# G2app/tasks.py
from celery import shared_task
from .models import HistoricoPesquisa, AlertLocation
from django.contrib.auth.models import User
from .views import analyze_weather_data, send_alert_email, fetch_weather_data

@shared_task
def check_weather_alerts():
    users = User.objects.all()
    for user in users:
        alert_locations = AlertLocation.objects.filter(usuario=user)
        
        for location in alert_locations:
            weather_data = fetch_weather_data(location=location.local_pesquisa)
            if weather_data:
                alerts = analyze_weather_data(weather_data)
                if alerts:
                    send_alert_email(user.email, weather_data, alerts)