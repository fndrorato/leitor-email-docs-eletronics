from celery import shared_task
from .email_reader import ler_emails_com_anexos

@shared_task
def tarefa_processar_emails():
    ler_emails_com_anexos(max_emails=100)
