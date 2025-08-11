from django.db import models

class Departamento(models.Model):
    """
    Modelo que contem os dados dos departamentos/estados
    """
    code = models.CharField(max_length=5, unique=True) #cDepEmi
    name = models.CharField(max_length=100) #dDesDepEmi
    created_at = models.DateTimeField(auto_now_add=True) #
    updated_at = models.DateTimeField(auto_now=True)

class Cidade(models.Model):
    """
    Modelo que contem os dados das cidades
    """
    code = models.CharField(max_length=10, unique=True) #cCiuEmi
    name = models.CharField(max_length=100) #dDesCiuEmi
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='cidades')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"
