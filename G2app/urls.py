from django.urls import path
from .import views 
from .views import signup
from django.contrib.auth.views import LoginView

urlpatterns = [
  path('', views.index, name='index'),
  path('signup/', signup, name='signup'),
  path('login/', LoginView.as_view(template_name='G2app/login.html'), name='login'),
]