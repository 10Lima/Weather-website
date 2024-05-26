from django.test import TestCase

# Create your tests here.
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def test_send_alert_email():
    subject = 'Teste de Notificação de Alerta Meteorológico'
    weather_data = {
        'name': 'Lisboa',
        'main': {
            'temp': 25
        },
        'weather': [{
            'description': 'céu limpo'
        }]
    }
    alerts = ['Probabilidade de neblina: 26.40%']
    html_message = render_to_string('G2app/email_alert.html', {'weather_data': weather_data, 'alerts': alerts})
    plain_message = strip_tags(html_message)
    from_email = 'seu_email@gmail.com'
    to = 'email_de_teste@gmail.com'

    send_mail(subject, plain_message, from_email, [to], html_message=html_message)

test_send_alert_email()