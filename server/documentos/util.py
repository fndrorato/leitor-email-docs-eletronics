import base64
import locale
import os
import pytz
import qrcode
import traceback
import xml.etree.ElementTree as ET
import requests
import os
from babel.numbers import format_currency
from common.models import Departamento, Cidade
from datetime import datetime, timedelta
from decimal import Decimal
from email import policy
from documentos.models import TipoDocumento, Documento
from emails.models import EmailXmlError, User as EmailAccount
from emissores.models import Emissor
from io import BytesIO
from num2words import num2words
from PIL import Image
from typing import Optional

def get_graph_token(ms_tenant_id=None, ms_client_id=None, ms_client_secret=None):
    """Obtém token de acesso do Microsoft Graph via client credentials."""
    tenant_id = ms_tenant_id
    client_id = ms_client_id
    client_secret = ms_client_secret

    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "client_id": client_id,
        "scope": "https://graph.microsoft.com/.default",
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

# locale.setlocale(locale.LC_ALL, 'es_PY.UTF-8')
def simplificar_dict(d):
    if isinstance(d, dict):
        # Se o dict tem só "_text", retorna o valor
        if set(d.keys()) == {"_text"}:
            return d["_text"]
        # Caso contrário, recursivamente processa os valores
        return {k: simplificar_dict(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [simplificar_dict(item) for item in d]
    return d

def processar_nfe_xml(xml_str: str, user):
    print('Iniciando o processar NFE XML')
    NS = {'ns': 'http://ekuatia.set.gov.py/sifen/xsd'}
    root = ET.fromstring(xml_str)

    # helper pra extrair texto com erro amigável
    def get_text(node, path, required=True, default=None):
        el = node.find(path, NS)
        if el is None or el.text is None:
            if required:
                raise ValueError(f"Campo obrigatório não encontrado: {path}")
            return default
        return el.text.strip()

    # 1) Aponta para o nó DE em qualquer lugar (por causa do rLoteDE/rDE)
    de = root.find('.//ns:DE', NS)
    if de is None:
        raise ValueError("Nó <DE> não encontrado (verifique namespace/caminho).")

    # 2) Blocos principais (sempre RELATIVOS a 'de')
    gTimb = de.find('ns:gTimb', NS)
    if gTimb is None:
        raise ValueError("Bloco <gTimb> não encontrado em <DE>.")

    gDatGralOpe = de.find('ns:gDatGralOpe', NS)
    if gDatGralOpe is None:
        raise ValueError("Bloco <gDatGralOpe> não encontrado em <DE>.")

    gEmis = gDatGralOpe.find('ns:gEmis', NS)
    if gEmis is None:
        raise ValueError("Bloco <gEmis> não encontrado em <gDatGralOpe>.")

    # 3) Campos principais
    cdc = de.attrib.get("Id")
    if not cdc:
        raise ValueError("Atributo Id não encontrado em <DE>.")

    tipo_doc_code = int(get_text(gTimb, 'ns:iTiDE'))
    tipo_doc_name = get_text(gTimb, 'ns:dDesTiDE')
    est = get_text(gTimb, 'ns:dEst')
    pun_exp = get_text(gTimb, 'ns:dPunExp')
    num_doc = get_text(gTimb, 'ns:dNumDoc')

    data_emissao_str = get_text(gDatGralOpe, 'ns:dFeEmiDE')
    fecha_emision = datetime.fromisoformat(data_emissao_str)

    # Totais (dentro de DE)
    dTotOpe_txt = get_text(de, 'ns:gTotSub/ns:dTotOpe')
    monto_total = Decimal(dTotOpe_txt)

    # 4) Departamento e cidade do emissor
    dep_code = get_text(gEmis, 'ns:cDepEmi')
    dep_name = get_text(gEmis, 'ns:dDesDepEmi')
    departamento, _ = Departamento.objects.get_or_create(
        code=dep_code, defaults={'name': dep_name}
    )

    city_code = get_text(gEmis, 'ns:cCiuEmi')
    city_name = get_text(gEmis, 'ns:dDesCiuEmi')
    cidade, _ = Cidade.objects.get_or_create(
        code=city_code, defaults={'name': city_name, 'departamento': departamento}
    )

    # 5) TipoDocumento
    tipo_doc, _ = TipoDocumento.objects.get_or_create(
        code=tipo_doc_code, defaults={'name': tipo_doc_name}
    )

    # 6) Emissor
    ruc = get_text(gEmis, 'ns:dRucEm')
    nome = get_text(gEmis, 'ns:dNomEmi')
    nome_fantasia = get_text(gEmis, 'ns:dNomFanEmi', required=False, default=None)

    emissor, _ = Emissor.objects.get_or_create(
        code=ruc,
        defaults={'nome': nome, 'nome_fantasia': nome_fantasia, 'cidade': cidade}
    )

    # 7) Documento
    print("➡️ Processando documento:", cdc)
    documento, created = Documento.objects.get_or_create(
        cdc=cdc,
        defaults={
            'company': user.company,
            'tipo_documento': tipo_doc,
            'est': est,
            'pun_exp': pun_exp,
            'num_doc': num_doc,
            'emissor': emissor,
            'fecha_emision': fecha_emision,
            'monto_total': monto_total,
            'documento_xml': xml_str,
        }
    )
    return documento, created

def numero_por_extenso(valor, moeda='guarani'):
    try:
        valor_float = float(valor)
        extenso = num2words(valor_float, lang='es').upper()
        if moeda.lower() == 'guarani':
            return f'GUARANI {extenso}'
        elif moeda.lower() == 'usd':
            return f'DÓLAR US {extenso}'
        return extenso
    except Exception as e:
        return str(valor)

def formatar_valor(valor, moeda='PYG'):
    try:
        valor_float = float(valor)
        return format_currency(valor_float, currency=moeda, locale='es_PY')
    except Exception:
        return str(valor)

def carregar_logo_base64(caminho_logo):
    try:
        with Image.open(caminho_logo) as img:
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return f"data:image/png;base64,{img_str}"
    except Exception as e:
        print(f"Erro ao carregar logo: {e}")
        return None

def gerar_qrcode_base64(texto: str) -> str:
    """
    Gera um QRCode em base64 a partir de um texto.
    Retorna a string base64 (ex: 'data:image/png;base64,...').
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=10,
        border=1,
    )
    qr.add_data(texto)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    base64_img = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return f"data:image/png;base64,{base64_img}"

def formatar_data(data_str: str, formato_entrada='%Y-%m-%dT%H:%M:%S', formato_saida='%d/%m/%Y %H:%M:%S') -> str:
    """
    Converte uma string de data no formato ISO ou similar para o formato desejado.
    Ajusta o fuso horário para o Paraguai (America/Asuncion).

    :param data_str: String de data (ex: '2024-08-01T15:30:00')
    :param formato_entrada: Formato da string de entrada
    :param formato_saida: Formato desejado da data de saída
    :return: Data formatada como string
    """
    try:
        tz = pytz.timezone('America/Asuncion')
        data = datetime.strptime(data_str, formato_entrada)
        data = tz.localize(data)
        return data.strftime(formato_saida)
    except Exception:
        return data_str  # Retorna original se der erro

def save_xml_error_simple(
    *,
    account: Optional[EmailAccount],
    subject: str,
    received_from: str,
    received_at: Optional[datetime],
    filename: str,
    mime_type: Optional[str],
    payload_bytes: Optional[bytes],
    xml_text: Optional[str],
    err: Exception,
    size_bytes: Optional[int] = None,
) -> None:
    decoded_ok = xml_text is not None
    xml_b64 = None
    if payload_bytes and not decoded_ok:
        try:
            xml_b64 = base64.b64encode(payload_bytes).decode("ascii")
        except Exception:
            xml_b64 = None

    EmailXmlError.objects.create(
        account=account,
        subject=subject,
        received_from=received_from,
        received_at=received_at,
        filename=filename or "",
        mime_type=mime_type or "",
        size_bytes=size_bytes,
        decoded_ok=decoded_ok,
        xml_text=xml_text if decoded_ok else None,
        xml_base64=xml_b64,
        error_message=str(err),
        stacktrace=traceback.format_exc(),
    )

def parse_email_date(date_str):
    """
    Tenta converter a string de data do e-mail em datetime.
    Retorna None se não conseguir.
    """
    if not date_str:
        return None
    try:
        # formato comum em e-mails: 'Mon, 12 Aug 2025 14:23:45 -0300'
        return datetime.strptime(date_str[:31], "%a, %d %b %Y %H:%M:%S %z")
    except Exception:
        try:
            # formato sem dia da semana: '12 Aug 2025 14:23:45 -0300'
            return datetime.strptime(date_str[:30], "%d %b %Y %H:%M:%S %z")
        except Exception:
            return None
