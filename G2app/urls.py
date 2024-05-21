from django.urls import path, re_path
from . import views
from .views import signup, perfil_usuario
from django.contrib.auth.views import LoginView
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views
from .views import logout_view

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('signup/', signup, name='signup'),
    path('login/', LoginView.as_view(template_name='G2app/login.html'), name='login'),
    path('perfil/', perfil_usuario, name='perfil'),
    path('admin-view/', views.admin_view, name='admin_view'),
    path('logout/', logout_view, name='logout'),
    re_path(r'^accounts/profile/$', RedirectView.as_view(pattern_name='perfil', permanent=False)),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='G2app/password/password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='G2app/password/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='G2app/password/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='G2app/password/password_reset_complete.html'), name='password_reset_complete'),
]
