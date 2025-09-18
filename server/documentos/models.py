from django.db import models
from companies.models import Company
from emissores.models import Emissor

class TipoDocumento(models.Model):
    """
    Modelo que representa un tipo de documento.
    """
    code = models.IntegerField(unique=True)
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f"{self.name} ({self.code})"

class Documento(models.Model):
    """
    Modelo que representa un documento.
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    cdc = models.CharField(max_length=48, unique=True) # <DE Id="01800628535055001003334022025072617152780206">
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE) #iTiDE
    est = models.CharField(max_length=10, null=True, blank=True) #dEst
    pun_exp = models.CharField(max_length=10, null=True, blank=True) #dPunExp
    num_doc = models.CharField(max_length=20) #dNumDoc
    emissor = models.ForeignKey(Emissor, on_delete=models.CASCADE)
    fecha_emision = models.DateTimeField() #dFeEmiDE
    monto_total = models.DecimalField(max_digits=15, decimal_places=2) #dTotOpe
    documento_xml = models.TextField() # Todo o arquivo XML
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tipo_documento.name} - {self.est}-{self.pun_exp}-{self.num_doc}"
