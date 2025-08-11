import email
import imaplib
import os
from datetime import datetime, timedelta
from documentos.util import processar_nfe_xml
from email import policy
from emails.models import User


def ler_emails_com_anexos(max_emails=100):
    ontem = (datetime.now() - timedelta(days=4)).strftime("%d-%b-%Y")
    users = User.objects.filter(active=True)

    for user in users:
        host = user.host
        port = int(user.port or 993)  # fallback para porta segura comum
        username = user.username
        password = user.password

        try:
            print(f"📥 Conectando com {username} em {host}:{port}")
            mail = imaplib.IMAP4_SSL(host, port)
            mail.login(username, password)
            mail.select("inbox")

            status, data = mail.search(None, f'(ON "{ontem}" SEEN)')
            ids = data[0].split()
            print(f"🔍 [{username}] Encontrados {len(ids)} e-mails lidos de ontem.")

            for idx, num in enumerate(ids[:max_emails]):
                status, data = mail.fetch(num, "(RFC822)")
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email, policy=policy.default)

                for part in msg.iter_attachments():
                    filename = part.get_filename()
                    if filename and filename.lower().endswith(".xml"):
                        try:
                            payload = part.get_payload(decode=True)
                            xml_content = payload.decode("utf-8", errors="replace")

                            if "<DE Id=" in xml_content:
                                doc, created = processar_nfe_xml(xml_content)
                                if created:
                                    print(f"✅ Documento {doc.cdc} criado com sucesso.")
                                else:
                                    print(f"⚠️ Documento {doc.cdc} já existia.")
                            else:
                                print(f"⏩ {filename} ignorado: não é um DE válido.")
                        except Exception as e:
                            print(f"\n❌ Erro ao processar '{filename}' do e-mail: {msg['subject']}")
                            print(f"➡️  Erro: {e}")
                            print(f"📄 Conteúdo parcial do XML:\n{xml_content[:300]}")

                            os.makedirs("xmls_erros", exist_ok=True)
                            try:
                                with open(f"xmls_erros/{filename}", "w", encoding="utf-8") as f:
                                    f.write(xml_content)
                                print(f"📝 XML com erro salvo: xmls_erros/{filename}")
                            except Exception as file_error:
                                print(f"⚠️ Falha ao salvar XML com erro: {file_error}")

            mail.logout()
        except Exception as e:
            print(f"🚫 Erro ao conectar ou processar e-mails de {username}: {e}")
