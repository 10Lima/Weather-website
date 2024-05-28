from __future__ import absolute_import, unicode_literals

# Importa a aplicação Celery quando o Django é iniciado
from .celery import app as celery_app

# Define quais itens são exportados pelo módulo
__all__ = ('celery_app',)
