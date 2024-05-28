from django.urls import path, re_path
from . import views
from .views import signup, perfil_usuario, delete_location, check_weather_events_now
from django.contrib.auth.views import LoginView
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views
from .views import logout_view

# Definição das URLs da aplicação
urlpatterns = [
    # URL para a página inicial
    path('', views.inicio, name='inicio'),

    # URL para a página de registo de novo utilizador
    path('signup/', signup, name='signup'),

    # URL para a página de login
    path('login/', LoginView.as_view(template_name='G2app/login.html'), name='login'),

    # URL para a página de perfil do utilizador
    path('perfil/', perfil_usuario, name='perfil'),

    # URL para a página de vista de administrador
    path('admin-view/', views.admin_view, name='admin_view'),

    # URL para a função de logout
    path('logout/', logout_view, name='logout'),

    # URL para atualizar as localidades de alerta
    path('update_alert_locations/', views.update_alert_locations, name='update_alert_locations'),

    # URL para apagar uma localidade de alerta, baseada no ID da localidade
    path('delete_location/<int:location_id>/', delete_location, name='delete_location'),

    # URL para verificar eventos meteorológicos agora
    path('check_weather_events_now/', check_weather_events_now, name='check_weather_events_now'),

    # Redirecionamento do perfil do utilizador
    re_path(r'^accounts/profile/$', RedirectView.as_view(pattern_name='perfil', permanent=False)),

    # URLs para reset de senha
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='G2app/password/password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='G2app/password/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='G2app/password/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='G2app/password/password_reset_complete.html'), name='password_reset_complete'),
]
