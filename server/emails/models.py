from django.db import models
from django.utils import timezone
from companies.models import Company


class User(models.Model):
    """
    Model representing a user in the system.
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    host = models.CharField(max_length=128, blank=True)
    port = models.CharField(max_length=128, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.username

class EmailXmlError(models.Model):
    # Relacione com seu modelo atual de contas de e-mail:
    account = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True)

    # Metadados do e-mail
    subject = models.TextField(blank=True)
    received_from = models.TextField(blank=True)                   # de quem veio o e-mail (From)
    received_at = models.DateTimeField(null=True, blank=True)      # data do e-mail (Date/Received)

    # Metadados do anexo
    filename = models.CharField(max_length=255, blank=True)
    mime_type = models.CharField(max_length=100, blank=True)
    size_bytes = models.IntegerField(null=True, blank=True)

    # Conteúdo do XML
    decoded_ok = models.BooleanField(default=False)
    xml_text = models.TextField(null=True, blank=True)                # XML em texto (UTF-8) quando decodou
    xml_base64 = models.TextField(null=True, blank=True)              # fallback: bytes em base64 se falhar decode

    # Erro
    error_message = models.TextField(blank=True)
    stacktrace = models.TextField(blank=True)

    # Auditoria
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"[{self.subject or '(sem assunto)'}] {self.filename or '(sem arquivo)'}"