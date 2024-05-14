#views.py
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


#Mostrar os dados metereologicoa quadno se pesquisa o local
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


        #Dados historicos dos ultimos 5 dias 
        historical_data = []
        for days_ago in range(1, 6):
            end = int((datetime.now() - timedelta(days=days_ago)).timestamp())
            start = end - 86400
            history_api_url = f'https://history.openweathermap.org/data/2.5/history/city?lat={latitude}&lon={longitude}&type=hour&start={start}&end={end}&appid={api_key}'
            history_response = requests.get(history_api_url)
            #print("URL:", history_api_url) 
            if history_response.status_code == 200:
              historical_data.append(history_response.json().get('current', {}))
              
            else:
              print("Erro ao buscar dados históricos:", history_response.status_code, history_response.text)
           
          
        
        for day in forecast_data:
            day['dt'] = datetime.utcfromtimestamp(day['dt']).strftime('%d-%m-%y')
        
        alerts = analyze_weather_data(weather_data)

        context = {
            'forecast_data': forecast_data,
            'historical_data': historical_data,
            'location': weather_data.get('name', ''),
            'temperature': weather_data['main'].get('temp', ''),
            'temp_max': weather_data['main'].get('temp_max', ''),
            'temp_min': weather_data['main'].get('temp_min', ''),
            'pressure': weather_data['main'].get('pressure', ''),
            'rain': weather_data.get('rain', {}).get('1h', 'No rain'),  # '1h' é a chuva na última hora, se disponível
            'description': weather_data['weather'][0].get('description', ''),
            'icon': weather_data['weather'][0].get('icon', ''),
            'alerts': alerts,
        }
        if alerts:
          send_alert_email(request.user.email, weather_data, alerts)

        if search_type == 'location':
          location = request.POST['location']
          local_pesquisa = location  # Guarda o local diretamente
        elif search_type == 'coordinates':
          latitude = request.POST['latitude']
          longitude = request.POST['longitude']
          local_pesquisa = f"Latitude: {latitude}, Longitude: {longitude}"  # Cria uma string representando as coordenadas
        if response.status_code == 200:
            
            HistoricoPesquisa.objects.create(
                usuario=request.user,
                local_pesquisa=local_pesquisa,
                resultado_pesquisa=response.text  
        )
        return render(request, 'G2app/inicio.html', context)
    else:
        return render(request, 'G2app/inicio.html')

#enviar email
def send_alert_email(email, weather_data, alerts):
    subject = 'Notificação de alerta meteorológico'
    html_message = render_to_string('G2app/email_alert.html', {'weather_data': weather_data, 'alerts': alerts})
    plain_message = strip_tags(html_message)
    from_email = 'forecastnow49@gmail.com'
    to = email

    send_mail(subject, plain_message, from_email, [to], html_message=html_message)
    
def get_weather_data(location):
    api_key = '941376db0bf38f9867c309281b11da60'
    api_url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&lang=pt&units=metric'
    response = requests.get(api_url)
    return response.json()

   #criar conta--- 

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
        # Garanta que você importou o json na parte superior do arquivo
        dados = json.loads(item.resultado_pesquisa)
        historico_formatado.append({
            'data': item.data_pesquisa,
            'local': item.local_pesquisa,
            'temperatura': dados['main']['temp'],
            # Inclua mais campos conforme necessário
        })
    return render(request, 'G2app/perfil.html', {'historico': historico_formatado})

#Verificar posiveis desastres naturais
def analyze_weather_data(weather_data):
    alerts = []
    
    # Exemplo de condição para tempestade
    if weather_data.get('weather', [{}])[0].get('main', '').lower() in ['thunderstorm', 'tornado']:
        alerts.append('Aviso tempestade severa')

    # Exemplo de condição para vento forte
    if weather_data['wind'].get('speed', 0) > 20:  # Velocidade do vento em m/s
        alerts.append('Aviso de velocidade elevada do vento')

    # Exemplo de condição para ondas de calor
    if weather_data['main'].get('temp', 0) > 35:  # Temperatura em Celsius
        alerts.append('Aviso de onda de calor')

    # Exemplo de condição para chuvas intensas
    if weather_data.get('rain', {}).get('1h', 0) > 10:  # Precipitação em mm
        alerts.append('Aviso de chuvas fortes')

    return alerts
