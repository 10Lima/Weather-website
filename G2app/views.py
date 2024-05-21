# views.py
from django.shortcuts import render, redirect
import requests
from django.contrib.auth import login, authenticate
from .forms import SignUpForm
from .models import HistoricoPesquisa
import json
from datetime import datetime, timedelta
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from django.conf import settings

def inicio(request):
    if request.method == 'POST':
        search_type = request.POST['search_type']
        api_key = '941376db0bf38f9867c309281b11da60'
        location = None 
        coordinates = None
        
        if search_type == 'location':
            location = request.POST['location']
            api_url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&lang=pt&units=metric'
        
        elif search_type == 'coordinates':
            latitude = request.POST['latitude']
            longitude = request.POST['longitude']
            api_url = f'http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&lang=pt&units=metric'


        response = requests.get(api_url)
        if response.status_code == 200:
            weather_data = response.json()
        else:
            messages.error(request, 'Erro ao buscar dados de clima.')
            return render(request, 'G2app/inicio.html')
        
        weather_data = response.json()

        latitude = weather_data.get('coord', {}).get('lat')
        longitude = weather_data.get('coord', {}).get('lon')

        forecast_api_url = f'http://api.openweathermap.org/data/2.5/forecast/daily?lat={latitude}&lon={longitude}&cnt=7&appid={api_key}&lang=pt&units=metric'

        forecast_response = requests.get(forecast_api_url)
        forecast_data = forecast_response.json().get('list', [])


        # Dados históricos dos últimos 5 dias 
        historical_data = []
        for days_ago in range(1, 6):
            end = int((datetime.now() - timedelta(days=days_ago)).timestamp())
            start = end - 86400
            history_api_url = f'https://history.openweathermap.org/data/2.5/history/city?lat={latitude}&lon={longitude}&type=hour&start={start}&end={end}&appid={api_key}'
            history_response = requests.get(history_api_url)
            if history_response.status_code == 200:
                historical_data.append(history_response.json().get('current', {}))
            else:
                print("Erro ao buscar dados históricos:", history_response.status_code, history_response.text)
           
        for day in forecast_data:
            day['dt'] = datetime.utcfromtimestamp(day['dt']).strftime('%d-%m-%y')
        
        alerts = analyze_weather_data(weather_data)

         # Gerar a URL do mapa
        google_maps_api_key = settings.GOOGLE_MAPS_API_KEY
        map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={latitude},{longitude}&zoom=12&size=600x400&markers=color:red%7C{latitude},{longitude}&key={google_maps_api_key}"
        print(map_url)


        context = {
            'forecast_data': forecast_data,
            'historical_data': historical_data,
            'location': weather_data.get('name', ''),
            'temperature': weather_data['main'].get('temp', ''),
            'temp_max': weather_data['main'].get('temp_max', ''),
            'temp_min': weather_data['main'].get('temp_min', ''),
            'pressure': weather_data['main'].get('pressure', ''),
            'rain': weather_data.get('rain', {}).get('1h', 'No rain'),
            'description': weather_data['weather'][0].get('description', ''),
            'icon': weather_data['weather'][0].get('icon', ''),
            'alerts': alerts,
            'map_url': map_url,
        }
        if alerts:
            send_alert_email(request.user.email, weather_data, alerts)

        if search_type == 'location':
            location = request.POST['location']
            local_pesquisa = location
        elif search_type == 'coordinates':
            latitude = request.POST['latitude']
            longitude = request.POST['longitude']
            local_pesquisa = f"Latitude: {latitude}, Longitude: {longitude}"
        if response.status_code == 200:
            HistoricoPesquisa.objects.create(
                usuario=request.user,
                local_pesquisa=local_pesquisa,
                resultado_pesquisa=response.text  
            )
        return render(request, 'G2app/inicio.html', context)
    else:
        return render(request, 'G2app/inicio.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('perfil')
    else:
        form = SignUpForm()
    return render(request, 'G2app/signup.html', {'form': form})


def perfil_usuario(request):
    if not request.user.is_authenticated:
        return redirect('login')
    historico = HistoricoPesquisa.objects.filter(usuario=request.user).order_by('-data_pesquisa')
    historico_formatado = []
    
    for item in historico:
        dados = json.loads(item.resultado_pesquisa)
        historico_formatado.append({
            'data': item.data_pesquisa,
            'local': item.local_pesquisa,
            'temperatura': dados['main']['temp'],
        })
    return render(request, 'G2app/perfil.html', {'historico': historico_formatado})


def is_superuser(user):
    return user.is_superuser


def admin_view(request):
    usuarios_historico = {}
    users = User.objects.all()
    
    for user in users:
        historico = HistoricoPesquisa.objects.filter(usuario=user).order_by('-data_pesquisa')
        usuarios_historico[user] = historico

    context = {
        'usuarios_historico': usuarios_historico
    }
    return render(request, 'G2app/admin_view.html', context)


def fetch_weather_data(location=None, latitude=None, longitude=None):
    api_key = '941376db0bf38f9867c309281b11da60'
    
    if location:
        api_url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&lang=pt&units=metric'
    elif latitude and longitude:
        api_url = f'http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&lang=pt&units=metric'
    else:
        return None

    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)

def analyze_weather_data(weather_data):
    alerts = []
    
    temp = weather_data['main']['temp']
    humidity = weather_data['main']['humidity']
    pressure = weather_data['main']['pressure']

    # Normalizar os valores
    temp_normalized = normalize(temp, -30, 50)  # Exemplo de faixa de temperatura em graus Celsius
    humidity_normalized = normalize(humidity, 0, 100)  # Umidade relativa em porcentagem
    pressure_normalized = normalize(pressure, 870, 1080)  # Faixa de pressão em hPa

    # Heurísticas para calcular probabilidades
    storm_probability = (temp_normalized * 0.4 + humidity_normalized * 0.4 + (1 - pressure_normalized) * 0.2) * 100
    drought_probability = ((1 - humidity_normalized) * 0.7 + (1 - temp_normalized) * 0.3) * 100
    hail_probability = (temp_normalized * 0.5 + (1 - humidity_normalized) * 0.3 + (1 - pressure_normalized) * 0.2) * 100

    # Adicionar alertas se a probabilidade ultrapassar certos limiares
    if storm_probability > 70:
        alerts.append(f'Probabilidade de tempestade severa: {storm_probability:.2f}%')
    
    if drought_probability > 70:
        alerts.append(f'Probabilidade de seca: {drought_probability:.2f}%')
    
    if hail_probability > 50:
        alerts.append(f'Probabilidade de queda de granizo: {hail_probability:.2f}%')

    return alerts

def send_alert_email(email, weather_data, alerts):
    subject = 'Weather Alert Notification'
    html_message = render_to_string('G2app/email_alert.html', {'weather_data': weather_data, 'alerts': alerts})
    plain_message = strip_tags(html_message)
    from_email = 'forecastnow49@gmail.com'
    to = email

    send_mail(subject, plain_message, from_email, [to], html_message=html_message)