from common.models import Cidade
from django.db import models


class Emissor(models.Model):
    """
    Modelo que representa un emisor de documentos.
    """
    code = models.CharField(max_length=20, unique=True) #dRucEm
    nome = models.CharField(max_length=200)  #dNomEmi
    nome_fantasia = models.CharField(max_length=200, blank=True, null=True) #dNomFanEmi
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE, related_name='cidades')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} ({self.code})"
