import base64
import locale
import os
import pytz
import qrcode
import xml.etree.ElementTree as ET
from babel.numbers import format_currency
from common.models import Departamento, Cidade
from datetime import datetime
from documentos.models import TipoDocumento, Documento
from emissores.models import Emissor
from io import BytesIO
from num2words import num2words
from PIL import Image


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



def processar_nfe_xml(xml_str: str):
    ns = {'ns': 'http://ekuatia.set.gov.py/sifen/xsd'}
    root = ET.fromstring(xml_str)

    # 1. Dados principais
    de = root.find('ns:DE', ns)
    gTimb = de.find('ns:gTimb', ns)
    gDatGralOpe = de.find('ns:gDatGralOpe', ns)
    gEmis = gDatGralOpe.find('ns:gEmis', ns)

    # Campos de apoio
    cdc = de.attrib.get("Id")
    tipo_doc_code = int(gTimb.find('ns:iTiDE', ns).text)
    tipo_doc_name = gTimb.find('ns:dDesTiDE', ns).text
    est = gTimb.find('ns:dEst', ns).text
    pun_exp = gTimb.find('ns:dPunExp', ns).text
    num_doc = gTimb.find('ns:dNumDoc', ns).text
    data_emissao = gDatGralOpe.find('ns:dFeEmiDE', ns).text
    valor_total = root.find('ns:DE/ns:gTotSub/ns:dTotOpe', ns).text
    valor_total = float(valor_total)

    # 2. Departamento
    dep_code = gEmis.find('ns:cDepEmi', ns).text
    dep_name = gEmis.find('ns:dDesDepEmi', ns).text
    departamento, _ = Departamento.objects.get_or_create(code=dep_code, defaults={'name': dep_name})

    # 3. Cidade
    city_code = gEmis.find('ns:cCiuEmi', ns).text
    city_name = gEmis.find('ns:dDesCiuEmi', ns).text
    cidade, _ = Cidade.objects.get_or_create(code=city_code, defaults={'name': city_name, 'departamento': departamento})

    # 4. TipoDocumento
    tipo_doc, _ = TipoDocumento.objects.get_or_create(code=tipo_doc_code, defaults={'name': tipo_doc_name})

    # 5. Emissor
    ruc = gEmis.find('ns:dRucEm', ns).text
    nome = gEmis.find('ns:dNomEmi', ns).text
    nome_fantasia = gEmis.find('ns:dNomFanEmi', ns).text if gEmis.find('ns:dNomFanEmi', ns) is not None else None
    emissor, _ = Emissor.objects.get_or_create(code=ruc, defaults={
        'nome': nome,
        'nome_fantasia': nome_fantasia,
        'cidade': cidade
    })

    # 6. Documento
    documento, created = Documento.objects.get_or_create(
        cdc=cdc,
        defaults={
            'tipo_documento': tipo_doc,
            'est': est,
            'pun_exp': pun_exp,
            'num_doc': num_doc,
            'emissor': emissor,
            'fecha_emision': datetime.fromisoformat(data_emissao),
            'monto_total': valor_total,
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
