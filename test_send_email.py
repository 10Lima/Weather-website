# test_send_email.py

import os
import django
from django.core.mail import send_mail

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meteorologia.settings')
django.setup()

def test_send_alert_email():
    subject = 'Teste de Notificação de Alerta Meteorológico'
    message = 'Este é um teste de envio de email.'
    from_email = 'forecastnow49@gmail.com'
    to_email = 'bruno.barros.alves2005@gmail.com'  # Altere para um email que você possa verificar

    send_mail(subject, message, from_email, [to_email])
    print('Email enviado com sucesso.')

if __name__ == '__main__':
    test_send_alert_email()
