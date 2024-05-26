# models.py
from django.db import models
from django.contrib.auth.models import User

class HistoricoPesquisa(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    local_pesquisa = models.CharField(max_length=255)
    resultado_pesquisa = models.TextField()
    data_pesquisa = models.DateTimeField(auto_now_add=True)

class AlertLocation(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    local_pesquisa = models.CharField(max_length=255)
