import email
import imaplib
import os
from datetime import datetime, timedelta
from documentos.util import processar_nfe_xml
from email import policy
from emails.models import User


def ler_emails_com_anexos(max_emails=100):
    # Janela de datas: últimos 5 dias (inclui ontem), exclui hoje
    hoje = datetime.now()
    inicio = (hoje - timedelta(days=5)).strftime("%d-%b-%Y")   # SINCE
    antes = hoje.strftime("%d-%b-%Y")                          # BEFORE (exclui hoje)

    users = User.objects.filter(active=True)

    for user in users:
        host = user.host
        port = int(user.port or 993)
        username = user.username
        password = user.password

        try:
            print(f"📥 Conectando com {username} em {host}:{port}")
            mail = imaplib.IMAP4_SSL(host, port)
            mail.login(username, password)
            mail.select("inbox")  # padrão: READ-WRITE

            # Todos os e-mails no intervalo (sem filtrar por SEEN/UNSEEN)
            # Ex.: (SINCE "07-Aug-2025" BEFORE "12-Aug-2025")
            search_query = f'(SINCE "{inicio}" BEFORE "{antes}")'
            status, data = mail.search(None, search_query)
            if status != "OK":
                print(f"⚠️  [{username}] Falha na busca: {status}")
                mail.logout()
                continue

            ids = data[0].split()
            print(f"🔍 [{username}] Encontrados {len(ids)} e-mails no período {inicio} .. {antes} (exclui hoje).")

            emails_processados = 0
            emails_apagados = 0

            for idx, num in enumerate(ids[:max_emails]):
                # Para cada e-mail, vamos processar TODOS os XMLs anexos
                # Só apagamos se TUDO der certo
                tudo_ok = True
                encontrou_xml = False

                try:
                    status, data = mail.fetch(num, "(RFC822)")
                    if status != "OK":
                        print(f"⚠️  Falha ao buscar e-mail id {num.decode()}: {status}")
                        tudo_ok = False
                        continue

                    raw_email = data[0][1]
                    msg = email.message_from_bytes(raw_email, policy=policy.default)
                    assunto = msg.get('subject', '(sem assunto)')

                    for part in msg.iter_attachments():
                        filename = part.get_filename()
                        if not filename:
                            continue

                        if filename.lower().endswith(".xml"):
                            encontrou_xml = True
                            try:
                                payload = part.get_payload(decode=True)
                                xml_content = payload.decode("utf-8", errors="replace")

                                if "<DE Id=" in xml_content:
                                    doc, created = processar_nfe_xml(xml_content)
                                    if created:
                                        print(f"✅ [{username}] {assunto} -> Documento {doc.cdc} criado com sucesso.")
                                    else:
                                        print(f"⚠️ [{username}] {assunto} -> Documento {doc.cdc} já existia.")
                                else:
                                    print(f"⏩ {filename} ignorado: não é um DE válido.")
                                    # opcionalmente, isso poderia NÃO invalidar o e-mail inteiro.
                                    # aqui consideramos como 'processado' porém sem erro.
                            except Exception as e:
                                tudo_ok = False
                                print(f"\n❌ Erro ao processar '{filename}' do e-mail: {assunto}")
                                print(f"➡️  Erro: {e}")

                                os.makedirs("xmls_erros", exist_ok=True)
                                try:
                                    with open(f"xmls_erros/{filename}", "w", encoding="utf-8") as f:
                                        # se xml_content não existir por falha de decode:
                                        try:
                                            f.write(xml_content)
                                        except Exception:
                                            f.write("(Falha ao obter conteúdo do XML para salvar)")
                                    print(f"📝 XML com erro salvo: xmls_erros/{filename}")
                                except Exception as file_error:
                                    print(f"⚠️ Falha ao salvar XML com erro: {file_error}")

                    # Se não encontrou nenhum XML, não apaga — apenas informa e segue
                    if not encontrou_xml:
                        print(f"📎 [{username}] E-mail '{assunto}' sem anexos XML. Ignorado.")
                        tudo_ok = False  # não vamos apagar

                    # Decisão de apagar: somente se tudo_ok e houve XML
                    if tudo_ok and encontrou_xml:
                        # Se quiser apagar quando ao menos UM XML deu certo,
                        # troque a condição por: if encontrou_xml:
                        mail.store(num, '+FLAGS', '\\Deleted')
                        emails_apagados += 1

                    emails_processados += 1

                except Exception as e:
                    print(f"🚫 Erro inesperado ao processar e-mail id {num.decode()}: {e}")

            # Remove definitivamente os marcados
            if emails_apagados > 0:
                mail.expunge()

            mail.close()  # fecha a caixa
            mail.logout()
            print(f"📊 [{username}] Processados {emails_processados} e-mails; apagados {emails_apagados}.")

        except Exception as e:
            print(f"🚫 Erro ao conectar ou processar e-mails de {username}: {e}")

# def ler_emails_com_anexos(max_emails=100):
#     ontem = (datetime.now() - timedelta(days=4)).strftime("%d-%b-%Y")
#     users = User.objects.filter(active=True)

#     for user in users:
#         host = user.host
#         port = int(user.port or 993)  # fallback para porta segura comum
#         username = user.username
#         password = user.password

#         try:
#             print(f"📥 Conectando com {username} em {host}:{port}")
#             mail = imaplib.IMAP4_SSL(host, port)
#             mail.login(username, password)
#             mail.select("inbox")

#             status, data = mail.search(None, f'(ON "{ontem}" SEEN)')
#             ids = data[0].split()
#             print(f"🔍 [{username}] Encontrados {len(ids)} e-mails lidos de ontem.")

#             for idx, num in enumerate(ids[:max_emails]):
#                 status, data = mail.fetch(num, "(RFC822)")
#                 raw_email = data[0][1]
#                 msg = email.message_from_bytes(raw_email, policy=policy.default)

#                 for part in msg.iter_attachments():
#                     filename = part.get_filename()
#                     if filename and filename.lower().endswith(".xml"):
#                         try:
#                             payload = part.get_payload(decode=True)
#                             xml_content = payload.decode("utf-8", errors="replace")

#                             if "<DE Id=" in xml_content:
#                                 doc, created = processar_nfe_xml(xml_content)
#                                 if created:
#                                     print(f"✅ Documento {doc.cdc} criado com sucesso.")
#                                 else:
#                                     print(f"⚠️ Documento {doc.cdc} já existia.")
#                             else:
#                                 print(f"⏩ {filename} ignorado: não é um DE válido.")
#                         except Exception as e:
#                             print(f"\n❌ Erro ao processar '{filename}' do e-mail: {msg['subject']}")
#                             print(f"➡️  Erro: {e}")
#                             print(f"📄 Conteúdo parcial do XML:\n{xml_content[:300]}")

#                             os.makedirs("xmls_erros", exist_ok=True)
#                             try:
#                                 with open(f"xmls_erros/{filename}", "w", encoding="utf-8") as f:
#                                     f.write(xml_content)
#                                 print(f"📝 XML com erro salvo: xmls_erros/{filename}")
#                             except Exception as file_error:
#                                 print(f"⚠️ Falha ao salvar XML com erro: {file_error}")

#             mail.logout()
#         except Exception as e:
#             print(f"🚫 Erro ao conectar ou processar e-mails de {username}: {e}")
