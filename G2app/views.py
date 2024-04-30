#views.py
from django.shortcuts import render, redirect
import requests
from django.contrib.auth import login, authenticate
from .forms import SignUpForm
from .models import HistoricoPesquisa
import json
from datetime import datetime, timedelta



#Mostrar os dados metereologicoa quadno se pesquisa o local
def inicio(request):
    if request.method == 'POST':
        location = request.POST['location']
        api_key = '941376db0bf38f9867c309281b11da60'
        api_url = api_url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&lang=pt&units=metric'
        response = requests.get(api_url)
        weather_data = response.json()

        lat =  weather_data.get('coord', {}).get('lat')
        lon =  weather_data.get('coord', {}).get('lon')

        #Dados de prvisão para os proximos 7 dias
        forecast_api_url = f'http://api.openweathermap.org/data/2.5/forecast/daily?q={location}&cnt=7&appid={api_key}&lang=pt&units=metric'
        forecast_response = requests.get(forecast_api_url)
        forecast_data = forecast_response.json().get('list', [])

        #Dados historicos dos ultimos 5 dias 
        historical_data = []
        for days_ago in range(1, 6):
            dt = int((datetime.now() - timedelta(days=days_ago)).timestamp())
            history_api_url = f'http://api.openweathermap.org/data/2.5/onecall/timemachine?lat={weather_data["coord"]["lat"]}&lon={weather_data["coord"]["lon"]}&dt={dt}&appid={api_key}&lang=pt&units=metric'
            history_response = requests.get(history_api_url)
            historical_data.append(history_response.json().get('current', {}))
        
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
        }
        if response.status_code == 200:
            
            HistoricoPesquisa.objects.create(
                usuario=request.user,
                local_pesquisa=location,
                resultado_pesquisa=response.text  
        )
        return render(request, 'G2app/inicio.html', context)
    else:
        return render(request, 'G2app/inicio.html')

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

