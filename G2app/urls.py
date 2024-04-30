#urls.py
from django.urls import path,re_path
from .import views 
from .views import signup, perfil_usuario
from django.contrib.auth.views import LoginView
from django.views.generic.base import RedirectView

urlpatterns = [
  path('', views.inicio, name='inicio'),
  path('signup/', signup, name='signup'),
  path('login/', LoginView.as_view(template_name='G2app/login.html'), name='login'),
  path('perfil/', perfil_usuario, name='perfil'),
  
   re_path(r'^accounts/profile/$', RedirectView.as_view(pattern_name='perfil', permanent=False)),
]

