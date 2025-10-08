import base64
import email
import imaplib
import os
import requests
from datetime import datetime, timedelta
from documentos.util import processar_nfe_xml, save_xml_error_simple, parse_email_date, get_graph_token
from email import policy
from emails.models import User


def ler_emails_com_anexos(max_emails=200):
    """
    Lê e-mails da caixa INBOX de todos os Users ativos, no intervalo dos últimos 5 dias
    (exclui hoje), processa anexos .xml e, em caso de erro no processamento de algum
    XML, salva o XML bruto em disco e registra no modelo EmailXmlError via helper
    save_xml_error_simple(...).
    """
    users = User.objects.filter(active=True)

    for user in users:
        host = user.host
        port = int(user.port or 993)  # seu port é CharField
        username = user.username

        try:
            print(f"📥 Conectando com {username} em {host}:{port}")
            if user.office365:
                leitor_email_graph(user, max_emails=max_emails)
            else:
                leitor_email_box(user, max_emails=max_emails)

        except Exception as e:
            print(f"🚫 Erro ao conectar ou processar e-mails de {username}: {e}")

def leitor_email_box(user, max_emails=200):
    """
    Função placeholder para evitar erro de importação circular.
    """
    host = user.host
    port = int(user.port or 993)  # seu port é CharField
    username = user.username
    password = user.password
        
    hoje = datetime.now()
    inicio = (hoje - timedelta(days=5)).strftime("%d-%b-%Y")  # SINCE
    antes  = hoje.strftime("%d-%b-%Y")                        # BEFORE (exclui hoje)
    amanha = (hoje + timedelta(days=1)).strftime("%d-%b-%Y")

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
                                doc, created = processar_nfe_xml(xml_content, user)
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

def leitor_email_graph(user, max_emails=200):
    """
    Versão Microsoft Graph da função leitor_email_box.
    Busca e-mails dos últimos 5 dias, processa anexos .xml e apaga os processados.
    """
    hoje = datetime.utcnow()
    inicio = (hoje - timedelta(days=5)).isoformat() + "Z"
    amanha = (hoje + timedelta(days=1)).isoformat() + "Z"

    token = get_graph_token(user.office365_tenant_id, user.office365_client_id, user.office365_client_secret)
    headers = {"Authorization": f"Bearer {token}"}

    print(f"📥 Lendo e-mails de {user.username} via Microsoft Graph...")

    # Busca e-mails recentes da Inbox
    url = (
        f"https://graph.microsoft.com/v1.0/users/{user.username}/mailFolders/inbox/messages"
        f"?$filter=receivedDateTime ge {inicio} and receivedDateTime lt {amanha}"
        f"&$top={max_emails}&$select=id,subject,from,receivedDateTime,hasAttachments"
    )

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"⚠️ Erro ao buscar mensagens: {response.text}")
        return

    emails = response.json().get("value", [])
    print(f"🔍 [{user.username}] Encontrados {len(emails)} e-mails no período.")

    emails_processados = 0
    emails_apagados = 0

    for msg in emails:
        try:
            assunto = msg.get("subject", "(sem assunto)")
            remetente = msg.get("from", {}).get("emailAddress", {}).get("address", "")
            received_at = msg.get("receivedDateTime")
            encontrou_xml = False
            tudo_ok = True

            if not msg.get("hasAttachments"):
                print(f"📎 [{user.username}] '{assunto}' sem anexos XML. Ignorado.")
                continue

            msg_id = msg["id"]
            attach_url = f"https://graph.microsoft.com/v1.0/users/{user.username}/messages/{msg_id}/attachments"
            attach_resp = requests.get(attach_url, headers=headers)

            if attach_resp.status_code != 200:
                print(f"⚠️ Erro ao buscar anexos: {attach_resp.text}")
                continue

            attachments = attach_resp.json().get("value", [])
            for att in attachments:
                filename = att.get("name")
                if not filename or not filename.lower().endswith(".xml"):
                    continue

                encontrou_xml = True
                mime_type = att.get("contentType", "application/xml")
                payload_bytes = base64.b64decode(att.get("contentBytes", ""))
                size_bytes = len(payload_bytes)
                xml_content = payload_bytes.decode("utf-8", errors="replace")

                try:
                    if "<DE Id=" in xml_content:
                        doc, created = processar_nfe_xml(xml_content, user)
                        if created:
                            print(f"✅ [{user.username}] {assunto} -> Documento {doc.cdc} criado com sucesso.")
                        else:
                            print(f"⚠️ [{user.username}] {assunto} -> Documento {doc.cdc} já existia.")
                    else:
                        print(f"⏩ {filename} ignorado: não é um DE válido.")
                        tudo_ok = False

                except Exception as e:
                    tudo_ok = False
                    print(f"❌ Erro ao processar {filename}: {e}")
                    try:
                        os.makedirs("xmls_erros", exist_ok=True)
                        with open(os.path.join("xmls_erros", filename), "wb") as f:
                            f.write(payload_bytes)
                        print(f"📝 XML com erro salvo: xmls_erros/{filename}")
                    except Exception as fe:
                        print(f"⚠️ Falha ao salvar XML com erro: {fe}")

                    try:
                        save_xml_error_simple(
                            account=user,
                            subject=assunto,
                            received_from=remetente,
                            received_at=received_at,
                            filename=filename,
                            mime_type=mime_type,
                            payload_bytes=payload_bytes,
                            xml_text=None,
                            err=e,
                            size_bytes=size_bytes,
                        )
                    except Exception as dbe:
                        print(f"⚠️ Falha ao registrar erro no banco: {dbe}")

            # Move para “Itens Excluídos” se processou com sucesso
            if tudo_ok and encontrou_xml:
                move_url = f"https://graph.microsoft.com/v1.0/users/{user.username}/messages/{msg_id}/move"
                move_data = {"destinationId": "deleteditems"}
                move_resp = requests.post(move_url, headers=headers, json=move_data)
                if move_resp.status_code == 201:
                    emails_apagados += 1
                else:
                    print(f"⚠️ Falha ao mover para lixeira: {move_resp.text}")

            emails_processados += 1

        except Exception as e:
            print(f"🚫 Erro inesperado ao processar e-mail: {e}")

    print(f"📊 [{user.username}] Processados {emails_processados}; apagados {emails_apagados}.")
