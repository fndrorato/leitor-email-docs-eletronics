import email
import imaplib
import os
from datetime import datetime, timedelta
from documentos.util import processar_nfe_xml, save_xml_error_simple, parse_email_date
from email import policy
from emails.models import User


def ler_emails_com_anexos(max_emails=200):
    """
    Lê e-mails da caixa INBOX de todos os Users ativos, no intervalo dos últimos 5 dias
    (exclui hoje), processa anexos .xml e, em caso de erro no processamento de algum
    XML, salva o XML bruto em disco e registra no modelo EmailXmlError via helper
    save_xml_error_simple(...).
    """
    # Janela: últimos 5 dias, exclui hoje
    hoje = datetime.now()
    inicio = (hoje - timedelta(days=5)).strftime("%d-%b-%Y")  # SINCE
    antes  = hoje.strftime("%d-%b-%Y")                        # BEFORE (exclui hoje)
    amanha = (hoje + timedelta(days=1)).strftime("%d-%b-%Y")

    users = User.objects.filter(active=True)

    for user in users:
        host = user.host
        port = int(user.port or 993)  # seu port é CharField
        username = user.username
        password = user.password

        try:
            print(f"📥 Conectando com {username} em {host}:{port}")
            mail = imaplib.IMAP4_SSL(host, port)
            mail.login(username, password)
            mail.select("inbox")  # READ-WRITE

            # Busca todos os e-mails no período
            search_query = f'(SINCE "{inicio}" BEFORE "{amanha}")'
            status, data = mail.search(None, search_query)
            if status != "OK":
                print(f"⚠️  [{username}] Falha na busca: {status}")
                mail.logout()
                continue

            ids = data[0].split()
            print(f"🔍 [{username}] Encontrados {len(ids)} e-mails no período {inicio} .. {amanha} (inclui o hoje).")

            emails_processados = 0
            emails_apagados = 0

            for num in ids[:max_emails]:
                tudo_ok = True
                encontrou_xml = False

                try:
                    status, fetch_data = mail.fetch(num, "(RFC822)")
                    if status != "OK":
                        print(f"⚠️  Falha ao buscar e-mail id {num.decode()}: {status}")
                        tudo_ok = False
                        continue

                    raw_email = fetch_data[0][1]
                    msg = email.message_from_bytes(raw_email, policy=policy.default)

                    assunto = msg.get('subject', '(sem assunto)')
                    remetente = msg.get('from', '')
                    # tentar normalizar a data do header Date
                    date_hdr = msg.get('Date')
                    received_at = parse_email_date(date_hdr)

                    for part in msg.iter_attachments():
                        filename = part.get_filename()
                        if not filename:
                            continue

                        if filename.lower().endswith(".xml"):
                            encontrou_xml = True
                            mime_type = part.get_content_type()  # ex.: application/xml
                            payload_bytes = None
                            size_bytes = None

                            try:
                                payload_bytes = part.get_payload(decode=True) or b""
                                size_bytes = len(payload_bytes) if payload_bytes else 0

                                # Decodifica como UTF-8 com replace (não quebra por caracteres inválidos)
                                xml_content = payload_bytes.decode("utf-8", errors="replace")

                                # Validação mínima para DE
                                if "<DE Id=" in xml_content:
                                    # -> Chame seu parser/gravador aqui
                                    doc, created = processar_nfe_xml(xml_content)
                                    if created:
                                        print(f"✅ [{username}] {assunto} -> Documento {doc.cdc} criado com sucesso.")
                                    else:
                                        print(f"⚠️ [{username}] {assunto} -> Documento {doc.cdc} já existia.")
                                else:
                                    print(f"⏩ {filename} ignorado: não é um DE válido.")

                            except Exception as e:
                                tudo_ok = False
                                print(f"\n❌ Erro ao processar '{filename}' do e-mail: {assunto}")
                                print(f"➡️  Erro: {e}")

                                # 1) Salva o XML bruto em disco (bytes) para análise
                                try:
                                    os.makedirs("xmls_erros", exist_ok=True)
                                    with open(os.path.join("xmls_erros", filename), "wb") as f:
                                        if payload_bytes:
                                            f.write(payload_bytes)
                                    print(f"📝 XML com erro salvo: xmls_erros/{filename}")
                                except Exception as file_error:
                                    print(f"⚠️ Falha ao salvar XML com erro: {file_error}")

                                # 2) Registra no banco via helper simples
                                try:
                                    save_xml_error_simple(
                                        account=user,
                                        subject=assunto,
                                        received_from=remetente,
                                        received_at=received_at,
                                        filename=filename,
                                        mime_type=mime_type,
                                        payload_bytes=payload_bytes,
                                        xml_text=None,   # falhou decodificação/parse -> None
                                        err=e,
                                        size_bytes=size_bytes,
                                    )
                                except Exception as db_error:
                                    print(f"⚠️ Falha ao registrar erro no banco: {db_error}")

                    # Se não encontrou nenhum XML, não apaga — apenas informa e segue
                    if not encontrou_xml:
                        print(f"📎 [{username}] E-mail '{assunto}' sem anexos XML. Ignorado.")
                        tudo_ok = False  # não apagar

                    # Decisão de apagar: somente se tudo_ok e houve XML
                    if tudo_ok and encontrou_xml:
                        mail.store(num, '+FLAGS', '\\Deleted')
                        emails_apagados += 1

                    emails_processados += 1

                except Exception as e:
                    print(f"🚫 Erro inesperado ao processar e-mail id {num.decode()}: {e}")

            # Remove definitivamente os marcados
            if emails_apagados > 0:
                mail.expunge()

            mail.close()
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
