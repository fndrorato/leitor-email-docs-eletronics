from django.core.management.base import BaseCommand
from documentos.util import processar_nfe_xml

class Command(BaseCommand):
    help = 'Processa um arquivo XML de nota fiscal paraguaia'

    def add_arguments(self, parser):
        parser.add_argument('xml_path', type=str, help='Caminho do arquivo XML')

    def handle(self, *args, **kwargs):
        xml_path = kwargs['xml_path']
        try:
            with open(xml_path, 'r', encoding='utf-8') as f:
                xml = f.read()
                doc, created = processar_nfe_xml(xml)
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Documento {doc.cdc} criado com sucesso!"))
                else:
                    self.stdout.write(self.style.WARNING(f"Documento {doc.cdc} já existia."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Erro ao processar XML: {e}"))
