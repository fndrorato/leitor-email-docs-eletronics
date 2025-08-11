import xml.etree.ElementTree as ET
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm # Import mm for easier conversion
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from datetime import datetime
import pytz # pip install pytz
from num2words import num2words # pip install num2words
from babel.numbers import format_currency # pip install Babel
from PIL import Image # pip install Pillow
import base64
import qrcode # pip install qrcode
import re # For regex operations like cdcprinc.match(/.{1,4}/g)
from functools import partial # Importar partial para passar argumentos adicionais

# Django Rest Framework imports
from rest_framework.views import APIView
from django.http import Http404, HttpResponse

# Assume these are available or define them if not
# from .models import Documento, Item # Assuming Documento has 'documento_xml' and 'cdc'
# from .utils import numero_por_extenso, formatar_valor, carregar_logo_base64, gerar_qrcode_base64, formatar_data

# --- Auxiliary Functions (provided by the user, ensure they are imported or defined) ---
def numero_por_extenso(valor, moeda='guarani'):
    """
    Converte um número para sua representação por extenso em espanhol.
    """
    try:
        valor_float = float(valor)
        extenso = num2words(valor_float, lang='es').upper()
        if moeda.lower() == 'guarani':
            return f'GUARANI {extenso}'
        elif moeda.lower() == 'usd':
            return f'DÓLAR US {extenso}'
        return extenso
    except Exception as e:
        # print(f"Error converting number to words: {e}") # Descomente para depuração
        return str(valor)

def formatar_valor(valor, moeda='PYG', decimal_places=0):
    """
    Formata um valor monetário para a localidade espanhol do Paraguai.
    """
    try:
        valor_float = float(valor)
        # Use a specific locale for Paraguay, and control decimal places
        # For PYG, usually 0 decimal places. For USD, 2.
        return format_currency(valor_float, currency=moeda, locale='es_PY', currency_digits=False, decimal_places=decimal_places)
    except Exception as e:
        # print(f"Error formatting currency: {e}") # Descomente para depuração
        return str(valor)

def carregar_logo_base64(caminho_logo):
    """
    Carrega uma imagem de logo de um caminho de arquivo e a converte para base64.
    """
    try:
        # Esta função assume que `caminho_logo` é um caminho de arquivo acessível pelo servidor.
        # Em uma configuração Django real, isso pode envolver MEDIA_ROOT ou static files.
        # Para este exemplo, assumimos que é um caminho direto.
        with Image.open(caminho_logo) as img:
            buffer = BytesIO()
            # Tenta salvar como JPEG se o caminho original era JPEG, senão PNG
            if caminho_logo.lower().endswith(('.jpg', '.jpeg')):
                img.save(buffer, format='JPEG')
            else:
                img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return f"data:image/png;base64,{img_str}" # Retorna como PNG para consistência
    except Exception as e:
        # print(f"Erro ao carregar logo: {e}") # Descomente para depuração
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
    """
    try:
        tz = pytz.timezone('America/Asuncion')
        data = datetime.strptime(data_str, formato_entrada)
        data = tz.localize(data)
        return data.strftime(formato_saida)
    except Exception:
        return data_str  # Retorna original se der erro

# --- End Auxiliary Functions ---

# Helper to safely get text from XML node
def get_xml_text(node, default=''):
    """Retorna o texto de um nó XML, ou um valor padrão se o nó for None."""
    return node.text if node is not None else default

# Helper to safely get attribute from XML node
def get_xml_attr(node, attr_name, default=''):
    """Retorna o valor de um atributo de um nó XML, ou um valor padrão se o nó ou atributo for None."""
    return node.get(attr_name, default) if node is not None else default

# Helper to safely get float value from XML node
def get_float_value(node, default=0.0):
    """Retorna o valor float de um nó XML, ou um valor padrão se o nó for None ou o texto não for numérico."""
    if node is not None and node.text:
        try:
            return float(node.text)
        except ValueError:
            pass # Fall through to default
    return default

# --- PDF Generation Functions ---

def _draw_factura_fixed_elements(canvas, doc, data_extracted, cod_empresa, desc_empresa, ruta_logo):
    """
    Desenha elementos fixos (caixas de cabeçalho, logo, texto estático) em cada página para a Fatura.
    Esta função é passada para onFirstPage e onLaterPages do SimpleDocTemplate.
    """
    canvas.saveState()
    canvas.setStrokeColorRGB(0, 0, 0)
    canvas.setLineWidth(0.2 * mm) # Convertendo 0.2mm para pontos

    # --- Primer Cuadro (Informações da Empresa) ---
    # Coordenadas e tamanhos em mm, convertidos para pontos para o canvas
    # doc.internal.pageSize.getWidth() em jsPDF é 210mm
    # doc.width é a largura da área de conteúdo do ReportLab (A4[0] - leftMargin - rightMargin)
    # doc.height é a altura da área de conteúdo do ReportLab (A4[1] - topMargin - bottomMargin)

    # Retângulo principal do cabeçalho da empresa
    # x: 7mm, y: 7mm (do topo da página)
    # width: (210 - 75)mm = 135mm
    # height: 30mm
    canvas.roundRect(
        7 * mm,
        A4[1] - 7 * mm - 30 * mm, # Y do canto inferior esquerdo
        135 * mm,
        30 * mm,
        1 * mm,
        stroke=1
    )

    # Logo
    if ruta_logo:
        logo_data = carregar_logo_base64(ruta_logo)
        if logo_data:
            # Posição e tamanho do logo baseados em cod_empresa, como no JS
            if cod_empresa == '4':
                canvas.drawImage(logo_data, 10 * mm, A4[1] - 8 * mm - 35 * mm / (35/15), width=35 * mm, height=15 * mm, mask='auto')
            elif cod_empresa in ['5', '6']:
                canvas.drawImage(logo_data, 10 * mm, A4[1] - 12 * mm - 37 * mm / (37/15), width=37 * mm, height=15 * mm, mask='auto')
            elif cod_empresa == '7':
                canvas.drawImage(logo_data, 10 * mm, A4[1] - 8 * mm - 30 * mm / (30/15), width=30 * mm, height=15 * mm, mask='auto')

    # Textos da empresa
    canvas.setFont("Helvetica-Bold", 6)
    canvas.drawCentredString(93 * mm, A4[1] - 18 * mm, data_extracted['dDesActEco'])
    canvas.setFont("Helvetica", 6)
    if cod_empresa == '4':
        canvas.drawCentredString(93 * mm, A4[1] - 24 * mm, 'Matriz: ' + data_extracted['dDirEmi'].upper())
        canvas.drawCentredString(93 * mm, A4[1] - 27 * mm, f"{data_extracted['dDesDisEmi']} - {data_extracted['dDesDepEmi']}")
        canvas.drawCentredString(93 * mm, A4[1] - 30 * mm, 'Suc: ' + 'ESTANCIA SAN NICANOR - BAHIA NEGRA')
        canvas.drawCentredString(93 * mm, A4[1] - 33 * mm, f"{data_extracted['dDesDisEmi']} - {data_extracted['dDesDepEmi']}")
        canvas.drawCentredString(93 * mm, A4[1] - 36 * mm, f"Teléfono: {data_extracted['dTelEmi']}")
    else:
        canvas.drawCentredString(93 * mm, A4[1] - 24 * mm, data_extracted['dDirEmi'].upper())
        canvas.drawCentredString(93 * mm, A4[1] - 27 * mm, f"{data_extracted['dDesDisEmi']} - {data_extracted['dDesDepEmi']}")
        canvas.drawCentredString(93 * mm, A4[1] - 30 * mm, f"Teléfono: {data_extracted['dTelEmi']}")

    # --- Segundo Cuadro (Informações do Timbrado) ---
    # x: 143mm, y: 7mm (do topo da página)
    # width: 60mm, height: 20mm
    canvas.roundRect(
        143 * mm,
        A4[1] - 7 * mm - 20 * mm, # Y do canto inferior esquerdo
        60 * mm,
        20 * mm,
        1 * mm,
        stroke=1
    )
    canvas.setFont("Helvetica", 5)
    canvas.drawCentredString(172 * mm, A4[1] - 10 * mm, f"TIMBRADO Nº {data_extracted['dNumTim']}")
    canvas.setFont("Helvetica", 4)
    canvas.drawCentredString(172 * mm, A4[1] - 12 * mm, f"FECHA INICIO VIGENCIA {formatar_data(data_extracted['dFeIniT'], formato_saida='%d/%m/%Y')}")
    canvas.setFont("Helvetica", 7)
    canvas.drawCentredString(172 * mm, A4[1] - 16 * mm, f"RUC: {data_extracted['dRucEm']}-{data_extracted['dDVEmi']}")
    canvas.setFont("Helvetica", 10)
    canvas.drawCentredString(172 * mm, A4[1] - 21 * mm, data_extracted['dDesTiDE'])
    canvas.drawCentredString(172 * mm, A4[1] - 25 * mm, f"{data_extracted['dEst']}-{data_extracted['dPunExp']}-{data_extracted['dNumDoc']}")

    # --- Tercer Cuadro (Condição de Venda) ---
    # x: 143mm, y: 28mm (do topo da página)
    # width: 60mm, height: 9mm
    canvas.roundRect(
        143 * mm,
        A4[1] - 28 * mm - 9 * mm, # Y do canto inferior esquerdo
        60 * mm,
        9 * mm,
        1 * mm,
        stroke=1
    )
    canvas.setFont("Helvetica", 5)
    canvas.drawString(145 * mm, A4[1] - 33 * mm, 'COND. DE VENTA: ')
    canvas.drawRightString(180 * mm, A4[1] - 33 * mm, 'CONTADO')
    canvas.drawRightString(198 * mm, A4[1] - 33 * mm, 'CREDITO')
    canvas.rect(166 * mm, A4[1] - 30 * mm - 4 * mm, 4 * mm, 4 * mm, stroke=1) # Checkbox Contado
    canvas.rect(185 * mm, A4[1] - 30 * mm - 4 * mm, 4 * mm, 4 * mm, stroke=1) # Checkbox Credito
    canvas.drawCentredString(168 * mm, A4[1] - 33 * mm, data_extracted['Contado'])
    canvas.drawCentredString(187 * mm, A4[1] - 33 * mm, data_extracted['Credito'])

    # --- Cuarto Cuadro (Informações do Cliente) ---
    # x: 7mm, y: 38mm (do topo da página)
    # width: (210 - 14)mm = 196mm
    # height: 14mm
    canvas.roundRect(
        7 * mm,
        A4[1] - 38 * mm - 14 * mm, # Y do canto inferior esquerdo
        (A4[0] / mm - 14) * mm, # Usar a largura total da página menos margens
        14 * mm,
        1 * mm,
        stroke=1
    )
    canvas.setFont("Helvetica", 5)
    canvas.drawString(8 * mm, A4[1] - 41 * mm, 'FECHA DE EMISION: ')
    canvas.drawString(35 * mm, A4[1] - 41 * mm, data_extracted['dFeEmiDE'])
    canvas.drawString(8 * mm, A4[1] - 44 * mm, 'NOMBRE O RAZON SOCIAL: ')
    canvas.drawString(35 * mm, A4[1] - 44 * mm, data_extracted['dNomRec'])
    canvas.drawString(8 * mm, A4[1] - 47 * mm, 'DIRECCION: ')
    canvas.drawString(35 * mm, A4[1] - 47 * mm, data_extracted['dDirRec'][:100])

    canvas.drawString(140 * mm, A4[1] - 41 * mm, 'TELEFONO: ')
    canvas.drawString(155 * mm, A4[1] - 41 * mm, data_extracted['dTelRec'])
    canvas.drawString(140 * mm, A4[1] - 47 * mm, 'PLAZO: ')
    canvas.drawString(155 * mm, A4[1] - 47 * mm, data_extracted['plazo'])
    canvas.drawString(140 * mm, A4[1] - 44 * mm, 'RUC: ')
    canvas.drawString(155 * mm, A4[1] - 44 * mm, data_extracted['numero_documento'])

    # Número da Página
    canvas.setFont("Helvetica", 5)
    canvas.setFillColorRGB(40/255, 40/255, 40/255) # Cor similar ao T=40 do jsPDF
    page_num = canvas.getPageNumber()
    total_pages_placeholder = "{total_pages_count_string}" # Placeholder para o total de páginas
    text = f"Página {page_num} de {total_pages_placeholder}"
    canvas.drawRightString(A4[0] - 12 * mm, A4[1] - 50 * mm, text)

    # --- Quinto Cuadro (Cabeçalhos da Tabela de Produtos) ---
    # Estes são os cabeçalhos fixos da tabela que aparecem em cada página.
    canvas.setStrokeColorRGB(0,0,0)
    canvas.setFillColorRGB(1,1,1)
    canvas.rect(6 * mm, A4[1] - 51 * mm - 10 * mm, (A4[0] / mm - 12) * mm, 10 * mm, fill=1, stroke=1) # Retângulo externo

    # Colunas individuais
    canvas.rect(7 * mm, A4[1] - 51 * mm - 10 * mm, 15 * mm, 10 * mm, stroke=1)
    canvas.drawCentredString(11 * mm, A4[1] - 57 * mm, 'CANT.')

    canvas.rect(22 * mm, A4[1] - 51 * mm - 10 * mm, 116 * mm, 10 * mm, stroke=1)
    canvas.drawCentredString(75 * mm, A4[1] - 57 * mm, 'DESCRIPCION')

    canvas.rect(138 * mm, A4[1] - 51 * mm - 10 * mm, 20 * mm, 10 * mm, stroke=1)
    canvas.drawCentredString(148 * mm, A4[1] - 56 * mm, 'PRECIO')
    canvas.drawCentredString(148 * mm, A4[1] - 59 * mm, 'UNITARIO')

    canvas.rect(158 * mm, A4[1] - 51 * mm - 10 * mm, 45 * mm, 10 * mm, stroke=1)
    canvas.drawCentredString(180 * mm, A4[1] - 54 * mm, 'VALOR DE VENTA')

    canvas.rect(158 * mm, A4[1] - 56 * mm - 5 * mm, 15 * mm, 5 * mm, stroke=1)
    canvas.drawCentredString(165 * mm, A4[1] - 59 * mm, 'EXENTA')

    canvas.rect(173 * mm, A4[1] - 56 * mm - 5 * mm, 15 * mm, 5 * mm, stroke=1)
    canvas.drawCentredString(180 * mm, A4[1] - 59 * mm, '5%')

    canvas.rect(188 * mm, A4[1] - 56 * mm - 5 * mm, 15 * mm, 5 * mm, stroke=1)
    canvas.drawCentredString(196 * mm, A4[1] - 59 * mm, '10%')

    canvas.restoreState()


def generate_factura_pdf(xml_content, cod_empresa, desc_empresa, ruta_logo):
    """
    Gera o PDF para um documento de Fatura Eletrônica.
    """
    NS = {'sifen': 'http://ekuatia.set.gov.py/sifen/xsd'}
    xml_root = ET.fromstring(xml_content)

    buffer = BytesIO()
    # Definindo as margens para dar espaço aos elementos fixos do cabeçalho
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=7 * mm, rightMargin=7 * mm,
                            topMargin=61 * mm, bottomMargin=60 * mm) # Ajustado para acomodar cabeçalhos/rodapés fixos

    Story = [] # Esta lista conterá todos os elementos (Flowables) do PDF.
    styles = getSampleStyleSheet()

    # Define paragraph styles (já definidos na versão anterior)
    # ... (mantidos os estilos de parágrafo da versão anterior para concisão)
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['h1'],
        fontSize=16, leading=18, alignment=TA_CENTER, spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=12, leading=14, alignment=TA_CENTER, spaceAfter=10
    )
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['h2'],
        fontSize=12, leading=14, alignment=TA_LEFT, spaceAfter=5
    )
    normal_text_style = ParagraphStyle(
        'NormalTextStyle',
        parent=styles['Normal'],
        fontSize=10, leading=12, alignment=TA_LEFT, spaceAfter=3
    )
    table_header_style = ParagraphStyle(
        'TableHeaderStyle',
        parent=styles['Normal'],
        fontSize=8, fontName='Helvetica-Bold', alignment=TA_CENTER, leading=9
    )
    table_cell_style = ParagraphStyle(
        'TableCellStyle',
        parent=styles['Normal'],
        fontSize=8, leading=9, alignment=TA_LEFT
    )
    table_numeric_style = ParagraphStyle(
        'TableNumericStyle',
        parent=styles['Normal'],
        fontSize=8, leading=9, alignment=TA_RIGHT
    )
    right_aligned_text_style = ParagraphStyle(
        'RightAlignedStyle',
        parent=styles['Normal'],
        fontSize=10, leading=12, alignment=TA_RIGHT, spaceAfter=3
    )
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=9, leading=10, alignment=TA_CENTER, spaceBefore=10
    )
    small_text_style = ParagraphStyle(
        'SmallTextStyle',
        parent=styles['Normal'],
        fontSize=5, leading=6, alignment=TA_LEFT
    )
    small_centered_text_style = ParagraphStyle(
        'SmallCenteredTextStyle',
        parent=styles['Normal'],
        fontSize=5, leading=6, alignment=TA_CENTER
    )
    small_right_text_style = ParagraphStyle(
        'SmallRightTextStyle',
        parent=styles['Normal'],
        fontSize=5, leading=6, alignment=TA_RIGHT
    )


    # --- Extração de Dados do XML (Mapeamento da estrutura JS para Python) ---
    data_extracted = {}

    # Emisor
    data_extracted['dDesActEco'] = get_xml_text(xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gEmis/sifen:gActEco/sifen:dDesActEco", NS))
    data_extracted['dEmailE'] = get_xml_text(xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gEmis/sifen:dEmailE", NS))
    data_extracted['dTelEmi'] = get_xml_text(xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gEmis/sifen:dTelEmi", NS))
    data_extracted['dDirEmi'] = get_xml_text(xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gEmis/sifen:dDirEmi", NS))
    data_extracted['dDesDepEmi'] = get_xml_text(xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gEmis/sifen:dDesDepEmi", NS))
    data_extracted['dDesDisEmi'] = get_xml_text(xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gEmis/sifen:dDesDisEmi", NS))

    # Segundo Cuadro (Timbrado)
    data_extracted['dNumTim'] = get_xml_text(xml_root.find("sifen:DE/sifen:gTimb/sifen:dNumTim", NS))
    data_extracted['dFeIniT'] = get_xml_text(xml_root.find("sifen:DE/sifen:gTimb/sifen:dFeIniT", NS))
    data_extracted['dRucEm'] = get_xml_text(xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gEmis/sifen:dRucEm", NS))
    data_extracted['dDVEmi'] = get_xml_text(xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gEmis/sifen:dDVEmi", NS))
    data_extracted['dFeEmiDE'] = formatar_data(get_xml_text(xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:dFeEmiDE", NS)))
    data_extracted['dDesTiDE'] = get_xml_text(xml_root.find("sifen:DE/sifen:gTimb/sifen:dDesTiDE", NS)).replace("&#xF3;", "ó")
    data_extracted['dEst'] = get_xml_text(xml_root.find("sifen:DE/sifen:gTimb/sifen:dEst", NS))
    data_extracted['dPunExp'] = get_xml_text(xml_root.find("sifen:DE/sifen:gTimb/sifen:dPunExp", NS))
    data_extracted['dNumDoc'] = get_xml_text(xml_root.find("sifen:DE/sifen:gTimb/sifen:dNumDoc", NS))

    # Tercer Cuadro (Receptor)
    iNatRec = get_xml_text(xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gDatRec/sifen:iNatRec", NS))
    data_extracted['dNomRec'] = get_xml_text(xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gDatRec/sifen:dNomRec", NS))
    data_extracted['dNomFanRec'] = get_xml_text(xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gDatRec/sifen:dNomFanRec", NS))
    data_extracted['dCodCliente'] = get_xml_text(xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gDatRec/sifen:dCodCliente", NS))
    data_extracted['dDirRec'] = get_xml_text(xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gDatRec/sifen:dDirRec", NS))
    dRucRec = get_xml_text(xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gDatRec/sifen:dRucRec", NS))
    dDVRec = get_xml_text(xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gDatRec/sifen:dDVRec", NS))
    dNumIDRec = get_xml_text(xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gDatRec/sifen:dNumIDRec", NS))
    data_extracted['dTelRec'] = get_xml_text(xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gDatRec/sifen:dTelRec", NS))
    data_extracted['dDesCiuRec'] = get_xml_text(xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gDatRec/sifen:dDesCiuRec", NS))
    data_extracted['dDesTipTra'] = get_xml_text(xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gOpeCom/sifen:dDesTipTra", NS))

    data_extracted['numero_documento'] = f"{dRucRec}-{dDVRec}" if dRucRec and dDVRec else dNumIDRec

    # Condição de Venda
    iCondOpe = get_xml_text(xml_root.find("sifen:DE/sifen:gDtipDE/sifen:gCamCond/sifen:iCondOpe", NS))
    data_extracted['Contado'] = 'X' if iCondOpe == "1" else ''
    data_extracted['Credito'] = 'X' if iCondOpe != "1" else ''
    
    plazo_node = xml_root.find("sifen:gCamFuFD/sifen:dInfAdic", NS)
    plazo_text = get_xml_text(plazo_node)
    data_extracted['plazo'] = plazo_text.split('|')[3] if plazo_text and len(plazo_text.split('|')) > 3 else ''
    if iCondOpe == "2": # Credito
        plazo_cred_node = xml_root.find("sifen:DE/sifen:gDtipDE/sifen:gCamCond/sifen:gPagCred/sifen:dPlazoCre", NS)
        data_extracted['plazo'] = get_xml_text(plazo_cred_node)

    # Moeda
    codigo_moneda = get_xml_text(xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gOpeCom/sifen:cMoneOpe", NS))
    data_extracted['Simbolo'] = 'Gs'
    data_extracted['CantidadDeDecimales'] = 0
    data_extracted['DescripcionMoneda'] = 'GUARANI '
    if codigo_moneda == 'USD':
        data_extracted['Simbolo'] = '$'
        data_extracted['CantidadDeDecimales'] = 2
        data_extracted['DescripcionMoneda'] = 'DOLAR US'

    # CDC e QR Code
    cdc_princ = get_xml_attr(xml_root.find("sifen:DE", NS), 'Id')
    data_extracted['cdc'] = " ".join(re.findall(r'.{1,4}', cdc_princ)) if cdc_princ else ''
    dCarQR = get_xml_text(xml_root.find("sifen:gCamFuFD/sifen:dCarQR", NS))
    data_extracted['qr_code_base64'] = gerar_qrcode_base64(dCarQR) if dCarQR else None

    # Informações Adicionais (Zona, Vendedor, OC)
    dInfAdic = get_xml_text(xml_root.find("sifen:gCamFuFD/sifen:dInfAdic", NS))
    data_extracted['zona'] = dInfAdic.split('|')[0] if dInfAdic and len(dInfAdic.split('|')) > 0 else ''
    data_extracted['vendedor'] = dInfAdic.split('|')[1] if dInfAdic and len(dInfAdic.split('|')) > 1 else ''
    data_extracted['oc'] = dInfAdic.split('|')[2] if dInfAdic and len(dInfAdic.split('|')) > 2 else ''

    # --- Tabela de Produtos ---
    # Adiciona um espaçador para garantir que o conteúdo da tabela comece abaixo dos elementos fixos
    Story.append(Spacer(1, 10 * mm)) # Ajuste este valor conforme necessário para o espaçamento

    # Cabeçalhos da tabela
    table_headers = [
        Paragraph("Cod", table_header_style),
        Paragraph("Descripción", table_header_style),
        Paragraph("Unid.", table_header_style),
        Paragraph("Cant.", table_header_style),
        Paragraph("P. Unitario", table_header_style),
        Paragraph("Desc.", table_header_style),
        Paragraph("Exentas", table_header_style),
        Paragraph("Ventas 5%", table_header_style),
        Paragraph("Ventas 10%", table_header_style)
    ]
    table_data = [table_headers]

    items = xml_root.findall("sifen:DE/sifen:gDtipDE/sifen:gCamItem", NS)

    for item in items:
        cod_node = item.find("sifen:dCodInt", NS)
        desc_node = item.find("sifen:dDesProSer", NS)
        unit_node = item.find("sifen:dDesUniMed", NS)
        qty_node = item.find("sifen:dCantProSer", NS)
        price_node = item.find("sifen:gValorItem/sifen:dPUniProSer", NS)
        discount_node = item.find("sifen:gValorItem/sifen:gValorRestaItem/sifen:dDescItem", NS)
        iva_rate_node = item.find("sifen:gCamIVA/sifen:dTasaIVA", NS)
        total_item_value_node = item.find("sifen:gValorItem/sifen:dTotBruOpeItem", NS)

        cod = get_xml_text(cod_node)
        desc = get_xml_text(desc_node)
        unit = get_xml_text(unit_node)

        qty_val = get_float_value(qty_node) # Pass the node
        price_val = get_float_value(price_node) # Pass the node
        discount_val = get_float_value(discount_node) # Pass the node
        iva_rate = get_xml_text(iva_rate_node) # This remains text
        total_item_val = get_float_value(total_item_value_node) # Pass the node

        exentas = "0"
        valor_5 = "0"
        valor_10 = "0"

        if iva_rate == "10":
            # A JS code adds dBasGravIVA + dLiqIVAItem. Let's replicate this if available.
            dBasGravIVA = get_float_value(item.find("sifen:gCamIVA/sifen:dBasGravIVA", NS))
            dLiqIVAItem = get_float_value(item.find("sifen:gCamIVA/sifen:dLiqIVAItem", NS))
            valor_10 = formatar_valor(dBasGravIVA + dLiqIVAItem, moeda=codigo_moneda, decimal_places=data_extracted['CantidadDeDecimales'])
        elif iva_rate == "5":
            dBasGravIVA = get_float_value(item.find("sifen:gCamIVA/sifen:dBasGravIVA", NS))
            dLiqIVAItem = get_float_value(item.find("sifen:gCamIVA/sifen:dLiqIVAItem", NS))
            valor_5 = formatar_valor(dBasGravIVA + dLiqIVAItem, moeda=codigo_moneda, decimal_places=data_extracted['CantidadDeDecimales'])
        else: # PropIVA = 0 for Exenta, or no IVA rate
            exentas = formatar_valor(total_item_val, moeda=codigo_moneda, decimal_places=data_extracted['CantidadDeDecimales'])

        description_text = desc.replace("&#xD;", "").replace("&#xA;", " ").strip()

        table_data.append([
            Paragraph(cod, table_cell_style),
            Paragraph(description_text, table_cell_style),
            Paragraph(unit, table_cell_style),
            Paragraph(formatar_valor(qty_val, moeda=codigo_moneda, decimal_places=3), table_numeric_style), # Cantidad has 3 decimals in JS
            Paragraph(formatar_valor(price_val, moeda=codigo_moneda, decimal_places=4), table_numeric_style), # Price has 4 decimals in JS
            Paragraph(formatar_valor(discount_val * qty_val, moeda=codigo_moneda, decimal_places=data_extracted['CantidadDeDecimales']), table_numeric_style), # Discount * quantity
            Paragraph(exentas, table_numeric_style),
            Paragraph(valor_5, table_numeric_style),
            Paragraph(valor_10, table_numeric_style)
        ])

    # Larguras das colunas em cm. 'None' para a descrição permite que ela ocupe o espaço restante.
    col_widths = [1.5*cm, None, 1.0*cm, 1.0*cm, 1.8*cm, 1.0*cm, 1.5*cm, 1.5*cm, 1.5*cm]
    table = Table(table_data, colWidths=col_widths)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E0E0E0")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Alinhamentos específicos para células já são tratados pelos ParagraphStyles
    ]))
    Story.append(table)
    Story.append(Spacer(1, 0.5*cm))

    # --- Totais ---
    # O código JS desenha retângulos para os totais. Usaremos uma Tabela para melhor alinhamento.
    total_subexe_node = xml_root.find("sifen:DE/sifen:gTotSub/sifen:dSubExe", NS)
    total_sub5_node = xml_root.find("sifen:DE/sifen:gTotSub/sifen:dSub5", NS)
    total_sub10_node = xml_root.find("sifen:DE/sifen:gTotSub/sifen:dSub10", NS)

    total_operation_node = xml_root.find("sifen:DE/sifen:gTotSub/sifen:dTotOpe", NS)
    total_guaranies_node = xml_root.find("sifen:DE/sifen:gTotSub/sifen:dTotGralOpe", NS)
    total_discount_node = xml_root.find("sifen:DE/sifen:gTotSub/sifen:dTotDesc", NS)
    total_iva_node = xml_root.find("sifen:DE/sifen:gTotSub/sifen:dTotIVA", NS)
    iva_5_node = xml_root.find("sifen:DE/sifen:gTotSub/sifen:dIVA5", NS)
    iva_10_node = xml_root.find("sifen:DE/sifen:gTotSub/sifen:dIVA10", NS)

    # Subtotal
    subtotal_data = [
        [
            Paragraph("SUBTOTAL:", small_text_style),
            Paragraph(formatar_valor(get_xml_text(total_subexe_node), moeda=codigo_moneda, decimal_places=data_extracted['CantidadDeDecimales']), small_right_text_style),
            Paragraph(formatar_valor(get_xml_text(total_sub5_node), moeda=codigo_moneda, decimal_places=data_extracted['CantidadDeDecimales']), small_right_text_style),
            Paragraph(formatar_valor(get_xml_text(total_sub10_node), moeda=codigo_moneda, decimal_places=data_extracted['CantidadDeDecimales']), small_right_text_style)
        ]
    ]
    subtotal_table = Table(subtotal_data, colWidths=[138*mm, 15*mm, 15*mm, 15*mm]) # Fixed widths based on JS layout
    subtotal_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 2*mm),
        ('RIGHTPADDING', (0,0), (-1,-1), 2*mm),
        ('TOPPADDING', (0,0), (-1,-1), 1*mm),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1*mm),
    ]))
    Story.append(subtotal_table)
    Story.append(Spacer(1, 0.2*cm))

    # Liquidacion IVA
    Story.append(Paragraph("LIQUIDACIÓN DEL IVA:", small_text_style))
    iva_data = [
        [
            Paragraph("5 %:", small_text_style),
            Paragraph(formatar_valor(get_xml_text(iva_5_node), moeda=codigo_moneda, decimal_places=data_extracted['CantidadDeDecimales']), small_text_style),
            Paragraph("10 %:", small_text_style),
            Paragraph(formatar_valor(get_xml_text(iva_10_node), moeda=codigo_moneda, decimal_places=data_extracted['CantidadDeDecimales']), small_text_style),
            Paragraph("TOTAL:", small_text_style),
            Paragraph(formatar_valor(get_xml_text(total_iva_node), moeda=codigo_moneda, decimal_places=data_extracted['CantidadDeDecimales']), small_text_style)
        ]
    ]
    iva_table = Table(iva_data, colWidths=[10*mm, 20*mm, 10*mm, 20*mm, 10*mm, 20*mm]) # Ajustar larguras conforme necessário
    iva_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    Story.append(iva_table)
    Story.append(Spacer(1, 0.2*cm))

    # Total a Pagar (en letras)
    total_en_letras = data_extracted['DescripcionMoneda'] + ' ' + numero_por_extenso(get_xml_text(total_guaranies_node), moeda=codigo_moneda) + ' ====='
    total_pagar_data = [
        [
            Paragraph("TOTAL A PAGAR (en letras):", small_text_style),
            Paragraph(total_en_letras, small_text_style),
            Paragraph(formatar_valor(get_xml_text(total_guaranies_node), moeda=codigo_moneda, decimal_places=data_extracted['CantidadDeDecimales']), small_right_text_style)
        ]
    ]
    total_pagar_table = Table(total_pagar_data, colWidths=[50*mm, None, 30*mm])
    total_pagar_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 2*mm),
        ('RIGHTPADDING', (0,0), (-1,-1), 2*mm),
        ('TOPPADDING', (0,0), (-1,-1), 1*mm),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1*mm),
    ]))
    Story.append(total_pagar_table)
    Story.append(Spacer(1, 0.5*cm))

    # CDC and QR Code
    if data_extracted['qr_code_base64']:
        from reportlab.platypus import Image as RLImage
        # Largura e altura do QR Code em mm, como no JS (0, 25)
        qr_image = RLImage(BytesIO(base64.b64decode(data_extracted['qr_code_base64'].split(',')[1])), width=25*mm, height=25*mm)
        # Para alinhar o QR e o texto ao lado, podemos usar uma mini-tabela
        qr_info_data = [
            [
                qr_image,
                Paragraph("Consulte la validez de esta Factura Electrónica con el número de CDC impreso abajo:<br/>https://ekuatia.set.gov.py/consultas/", small_text_style),
            ]
        ]
        qr_info_table = Table(qr_info_data, colWidths=[25*mm, None])
        qr_info_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (0,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        Story.append(qr_info_table)

    Story.append(Paragraph(f"<b>CDC: {data_extracted['cdc']}</b>", normal_text_style))
    Story.append(Spacer(1, 0.2*cm))

    # Legal Disclaimer
    Story.append(Paragraph("ESTE DOCUMENTO ES UNA REPRESENTACIÓN GRÁFICA DE UN DOCUMENTO ELECTRÓNICO (XML)", small_text_style))
    Story.append(Paragraph("Información de Interés del facturador eletrónico emisor", small_text_style))
    Story.append(Paragraph("Si su documento electrónico presenta algún error, podrá solicitar la modificación dentro de las 72 horas siguientes de la emisión de este comprobante.", small_text_style))


    # Build the PDF with the fixed elements drawing function on each page
    # Usando functools.partial para passar os argumentos adicionais
    on_page_callback = partial(_draw_factura_fixed_elements,
                               data_extracted=data_extracted,
                               cod_empresa=cod_empresa,
                               desc_empresa=desc_empresa,
                               ruta_logo=ruta_logo)
    doc.build(Story, onFirstPage=on_page_callback, onLaterPages=on_page_callback)

    buffer.seek(0)
    return buffer

def generate_nota_credito_pdf(xml_content, cod_empresa, desc_empresa, ruta_logo):
    """
    Gera o PDF para um documento de Nota de Crédito Eletrônica.
    Esta é uma função placeholder e precisa ser implementada.
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.drawString(100, 750, "PDF de Nota de Crédito - En Construcción")
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer