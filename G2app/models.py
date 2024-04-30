#models.py
from django.db import models

# Create your models here.


from django.db import models
from django.contrib.auth.models import User

class HistoricoPesquisa(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data_pesquisa = models.DateTimeField(auto_now_add=True)
    local_pesquisa = models.CharField(max_length=200)
    resultado_pesquisa = models.TextField()

    def __str__(self):
        return f'{self.usuario} pesquisou {self.local_pesquisa} em {self.data_pesquisa}'
