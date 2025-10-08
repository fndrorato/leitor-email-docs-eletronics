from django.core.management.base import BaseCommand, CommandError
from emails.models import User
import imaplib
import email
from email import policy


class Command(BaseCommand):
    help = "Conecta na caixa de e-mail de um usuário e mostra um resumo (sem apagar ou processar)."

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Username da conta de e-mail cadastrada no sistema")
        parser.add_argument("--max", type=int, default=20, help="Máximo de e-mails a inspecionar (padrão 20)")

    def handle(self, *args, **options):
        username = options["username"]
        max_emails = options["max"]

        try:
            user = User.objects.get(username=username, active=True)
        except User.DoesNotExist:
            raise CommandError(f"Usuário {username} não encontrado ou inativo.")

        host = user.host
        port = int(user.port or 993)
        password = user.password

        self.stdout.write(self.style.NOTICE(f"📥 Conectando com {username} em {host}:{port}"))
        try:
            mail = imaplib.IMAP4_SSL(host, port)
            mail.login(username, password)
            mail.select("inbox", readonly=True)  # <-- READONLY, não marca como lido nem permite deletar

            # Busca todos os e-mails
            status, data = mail.search(None, "ALL")
            if status != "OK":
                raise CommandError("Não foi possível buscar os e-mails.")

            ids = data[0].split()
            total_emails = len(ids)
            self.stdout.write(self.style.NOTICE(f"📊 Total de e-mails na INBOX: {total_emails}"))

            nf_count = 0
            for num in ids[-max_emails:]:  # pega os mais recentes
                status, fetch_data = mail.fetch(num, "(RFC822)")
                if status != "OK":
                    continue

                raw_email = fetch_data[0][1]
                msg = email.message_from_bytes(raw_email, policy=policy.default)

                assunto = msg.get("subject", "(sem assunto)")
                remetente = msg.get("from", "")

                encontrou_xml = False
                for part in msg.iter_attachments():
                    filename = part.get_filename()
                    if filename and filename.lower().endswith(".xml"):
                        encontrou_xml = True
                        break

                if encontrou_xml:
                    nf_count += 1
                    self.stdout.write(self.style.SUCCESS(f"📧 [NF] {assunto} | {remetente}"))
                else:
                    self.stdout.write(f"📎 [OUTRO] {assunto} | {remetente}")

            self.stdout.write(self.style.SUCCESS(f"\n✅ Resumo: {nf_count} e-mails com anexos XML encontrados."))

            mail.logout()

        except Exception as e:
            raise CommandError(f"Erro: {e}")
