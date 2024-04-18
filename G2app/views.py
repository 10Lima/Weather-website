from django.shortcuts import render, HttpResponse
import requests

# Create your views here.

def index(request):
    if request.method == 'POST':
        location = request.POST['location']
        api_key = '941376db0bf38f9867c309281b11da60'
        api_url = api_url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&lang=pt&units=metric'
        response = requests.get(api_url)
        weather_data = response.json()
        
        context = {
                     'location': weather_data.get('name', ''),
            'temperature': weather_data['main'].get('temp', ''),
            'temp_max': weather_data['main'].get('temp_max', ''),
            'temp_min': weather_data['main'].get('temp_min', ''),
            'pressure': weather_data['main'].get('pressure', ''),
            'rain': weather_data.get('rain', {}).get('1h', 'No rain'),  # '1h' é a chuva na última hora, se disponível
            'description': weather_data['weather'][0].get('description', ''),
            'icon': weather_data['weather'][0].get('icon', ''),
        }
        return render(request, 'G2app/index.html', context)
    else:
        return render(request, 'G2app/index.html')
    
