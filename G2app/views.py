# views.py
from django.shortcuts import render, redirect
import requests
from django.contrib.auth import login, authenticate, logout as auth_logout
from .forms import SignUpForm
from .models import HistoricoPesquisa, AlertLocation
import json
from datetime import datetime, timedelta
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from django.conf import settings
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import math
import matplotlib.pyplot as plt
import io
import urllib, base64

# Função para criar gráficos
def create_chart(data, title, ylabel):
    plt.figure(figsize=(10, 5))
    plt.plot(data['dates'], data['values'], marker='o')
    plt.title(title)
    plt.xlabel('Data')
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.xticks(rotation=45)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    
    return uri

# Função principal de início
def inicio(request):
    if request.method == 'POST':
        # Verificar se o utilizador está autenticado
        if not request.user.is_authenticated:
            messages.error(request, 'Precisas entrar ou criar conta para realizar a pesquisa.')
            return redirect('login')

        search_type = request.POST['search_type']
        api_key = '941376db0bf38f9867c309281b11da60'
        location = None 
        coordinates = None
        
        # Definir URL da API com base no tipo de pesquisa
        if search_type == 'location':
            location = request.POST['location']
            api_url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&lang=pt&units=metric'
        
        elif search_type == 'coordinates':
            latitude = request.POST['latitude']
            longitude = request.POST['longitude']
            api_url = f'http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&lang=pt&units=metric'

        # Obter dados do tempo atual
        response = requests.get(api_url)
        if response.status_code == 200:
            weather_data = response.json()
            print("Current Weather Data:", weather_data)
        else:
            messages.error(request, 'Erro ao buscar dados de clima.')
            return render(request, 'G2app/inicio.html')
        
        latitude = weather_data.get('coord', {}).get('lat')
        longitude = weather_data.get('coord', {}).get('lon')

        # Obter dados de previsão do tempo
        forecast_api_url = f'http://api.openweathermap.org/data/2.5/forecast/daily?lat={latitude}&lon={longitude}&cnt=7&appid={api_key}&lang=pt&units=metric'
        forecast_response = requests.get(forecast_api_url)
        forecast_data = forecast_response.json().get('list', [])
        print("Forecast Data:", forecast_data)

        # Obter dados históricos dos últimos 5 dias
        historical_data = []
        for days_ago in range(1, 6):
            end = int((datetime.now() - timedelta(days=days_ago)).timestamp())
            start = end - 86400
            history_api_url = f'https://history.openweathermap.org/data/2.5/history/city?lat={latitude}&lon={longitude}&type=hour&start={start}&end={end}&appid={api_key}'
            print(f"Fetching historical data from: {history_api_url}")  # Adicionando esta linha para depuração
            history_response = requests.get(history_api_url)
            if history_response.status_code == 200:
                history_data = history_response.json()
                print(f"Historical Data Response for {days_ago} days ago:", history_data)
                if 'current' in history_data:
                    historical_item = history_data['current']
                else:
                    historical_item = history_data.get('list', [])
                historical_data.append(historical_item)
            else:
                print("Erro ao buscar dados históricos:", history_response.status_code, history_response.text)
                historical_data.append({})

        for day in forecast_data:
            day['dt'] = datetime.utcfromtimestamp(day['dt']).strftime('%d-%m-%y')
        
        alerts = analyze_weather_data(weather_data)

        # Gerar a URL do mapa com marcador vermelho
        google_maps_api_key = settings.GOOGLE_MAPS_API_KEY
        map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={latitude},{longitude}&zoom=12&size=600x400&markers=color:red%7C{latitude},{longitude}&key={google_maps_api_key}"
        print(map_url)

        # Dados para os gráficos
        dates = [day['dt'] for day in forecast_data]
        temps = [day['temp']['day'] for day in forecast_data]
        humidity = [day['humidity'] for day in forecast_data]
        pressure = [day['pressure'] for day in forecast_data]

        temp_chart = create_chart({'dates': dates, 'values': temps}, 'Previsão de Temperatura', 'Temperatura (°C)')
        humidity_chart = create_chart({'dates': dates, 'values': humidity}, 'Previsão de Humidade', 'Umidade (%)')
        pressure_chart = create_chart({'dates': dates, 'values': pressure}, 'Previsão de Pressão', 'Pressão (hPa)')

        context = {
            'forecast_data': forecast_data,
            'historical_data': historical_data,
            'location': weather_data.get('name', ''),
            'temperature': weather_data['main'].get('temp', ''),
            'temp_max': weather_data['main'].get('temp_max', ''),
            'temp_min': weather_data['main'].get('temp_min', ''),
            'pressure': weather_data['main'].get('pressure', ''),
            'humidity': weather_data['main'].get('humidity', ''),
            'rain': weather_data.get('rain', {}).get('1h', 'No rain'),
            'description': weather_data['weather'][0].get('description', ''),
            'icon': weather_data['weather'][0].get('icon', ''),
            'wind_speed': weather_data['wind'].get('speed', ''),
            'wind_deg': weather_data['wind'].get('deg', ''),
            'alerts': alerts,
            'map_url': map_url,
            'temp_chart': temp_chart,
            'humidity_chart': humidity_chart,
            'pressure_chart': pressure_chart,
        }
        
        # Enviar email se houver alertas
        if alerts:
            send_alert_email(request.user.email, weather_data, alerts)

        # Guardar histórico de pesquisa se o utilizador estiver autenticado
        if request.user.is_authenticated:
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
        else:
            messages.error(request, 'Precisa ter conta para salvar o histórico de pesquisa.')

        return render(request, 'G2app/inicio.html', context)
    else:
        return render(request, 'G2app/inicio.html')

# Função para criar uma nova conta de utilizador
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

# Função para mostrar o perfil do utilizador
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

# Função para verificar se o utilizador é superutilizador
def is_superuser(user):
    return user.is_superuser

# Função para a vista de administrador
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

# Função para fazer logout
def logout_view(request):
    auth_logout(request)
    return redirect('login')

# Função para obter dados meteorológicos
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

# Função para normalizar valores
def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)

# Função para analisar dados meteorológicos e gerar alertas
def analyze_weather_data(weather_data):
    alerts = []
    
    try:
        temp = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        pressure = weather_data['main']['pressure']
        wind_speed = weather_data['wind']['speed']
        wind_deg = weather_data['wind']['deg']
        visibility = weather_data.get('visibility', 10000)  # visibilidade em metros
        weather_conditions = weather_data['weather'][0]['id']  # código do tempo atual

        print(f"Dados recebidos - Temp: {temp}, Humidity: {humidity}, Pressure: {pressure}, Wind Speed: {wind_speed}, Wind Deg: {wind_deg}, Visibility: {visibility}, Conditions: {weather_conditions}")

        # Normalizar os valores
        temp_normalized = normalize(temp, -30, 50)  # Exemplo de faixa de temperatura em graus Celsius
        humidity_normalized = normalize(humidity, 0, 100)  # Umidade relativa em porcentagem
        pressure_normalized = normalize(pressure, 870, 1080)  # Faixa de pressão em hPa
        wind_speed_normalized = normalize(wind_speed, 0, 50)  # Velocidade do vento em m/s
        visibility_normalized = normalize(visibility, 0, 10000)  # Visibilidade em metros

        # Heurísticas para calcular probabilidades
        storm_probability = (temp_normalized * 0.3 + humidity_normalized * 0.3 + wind_speed_normalized * 0.2 + (1 - pressure_normalized) * 0.2) * 100
        drought_probability = ((1 - humidity_normalized) * 0.6 + (1 - temp_normalized) * 0.3 + (1 - visibility_normalized) * 0.1) * 100
        hail_probability = (temp_normalized * 0.4 + (1 - humidity_normalized) * 0.3 + (1 - pressure_normalized) * 0.2 + wind_speed_normalized * 0.1) * 100
        snow_probability = (temp_normalized * 0.2 + humidity_normalized * 0.3 + (1 - pressure_normalized) * 0.2 + (1 - visibility_normalized) * 0.3) * 100
        fog_probability = (humidity_normalized * 0.4 + (1 - visibility_normalized) * 0.6) * 100
        heat_wave_probability = (temp_normalized * 0.7 + (1 - humidity_normalized) * 0.3) * 100

        # Adicionar alertas se a probabilidade ultrapassar certos limiares
        if storm_probability > 70:
            alerts.append(f'Probabilidade de tempestade severa: {storm_probability:.2f}%')

        if drought_probability > 70:
            alerts.append(f'Probabilidade de seca: {drought_probability:.2f}%')

        if hail_probability > 70:
            alerts.append(f'Probabilidade de queda de granizo: {hail_probability:.2f}%')

        if snow_probability > 50 and temp < 0:
            alerts.append(f'Probabilidade de nevasca: {snow_probability:.2f}%')

        if fog_probability > 60:
            alerts.append(f'Probabilidade de neblina: {fog_probability:.2f}%')

        if heat_wave_probability > 75:
            alerts.append(f'Probabilidade de onda de calor: {heat_wave_probability:.2f}%')

    except KeyError as e:
        print(f"Erro ao acessar dados do JSON: {e}")

    return alerts

# Função para enviar email de alerta
def send_alert_email(email, weather_data, alerts):
    subject = 'Weather Alert Notification'
    html_message = render_to_string('G2app/email_alert.html', {'weather_data': weather_data, 'alerts': alerts})
    plain_message = strip_tags(html_message)
    from_email = 'forecastnow49@gmail.com'
    to = email

    send_mail(subject, plain_message, from_email, [to], html_message=html_message)

# Função para mostrar o perfil do utilizador
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

    alert_locations = AlertLocation.objects.filter(usuario=request.user)

    return render(request, 'G2app/perfil.html', {
        'historico': historico_formatado,
        'alert_locations': alert_locations,
    })

# Função para atualizar as localidades de alerta
def update_alert_locations(request):
    if request.method == 'POST':
        selected_locations = request.POST.getlist('alert_locations')
        valid_locations = []
        for location in selected_locations:
            if validate_location(location):
                valid_locations.append(location)
            else:
                messages.error(request, f'Localidade inválida: {location}', extra_tags='error')
        
        if valid_locations:
            for location in valid_locations:
                if not AlertLocation.objects.filter(usuario=request.user, local_pesquisa=location).exists():
                    AlertLocation.objects.create(usuario=request.user, local_pesquisa=location)
            messages.success(request, 'Localidades de alerta atualizadas com sucesso.', extra_tags='success')
        else:
            messages.error(request, 'Nenhuma localidade válida foi fornecida.', extra_tags='error')

    return redirect('perfil')

# Função para validar a localidade
def validate_location(location):
    api_key = '941376db0bf38f9867c309281b11da60'
    api_url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&lang=pt&units=metric'
    response = requests.get(api_url)
    return response.status_code == 200

# Função para apagar localidade
@require_POST
def delete_location(request, location_id):
    location = get_object_or_404(AlertLocation, id=location_id)
    location.delete()
    return JsonResponse({'success': True})

# Função para verificar eventos meteorológicos agora
@csrf_exempt
def check_weather_events_now(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Usuário não autenticado.'})
        
        alert_locations = AlertLocation.objects.filter(usuario=request.user)
        if not alert_locations.exists():
            return JsonResponse({'success': False, 'message': 'Nenhuma localidade salva para alertas.'})
        
        events_found = False
        for location in alert_locations:
            weather_data = fetch_weather_data(location=location.local_pesquisa)
            if weather_data:
                print(f"Dados meteorológicos para {location.local_pesquisa}: {weather_data}")
                alerts = analyze_weather_data(weather_data)
                if alerts:
                    print(f"Alertas encontrados: {alerts}")
                    send_alert_email(request.user.email, weather_data, alerts)
                    events_found = True
        
        if events_found:
            return JsonResponse({'success': True, 'message': 'Eventos meteorológicos encontrados e emails enviados.'})
        else:
            return JsonResponse({'success': True, 'message': 'Nenhum evento meteorológico encontrado.'})

    return JsonResponse({'success': False, 'message': 'Método inválido.'})
