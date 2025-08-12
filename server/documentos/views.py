import os
import requests
import xmltodict
import xml.etree.ElementTree as ET
from decouple import config
from dotenv import load_dotenv
from datetime import datetime
from django.utils.dateparse import parse_datetime
from django.db.models import Q
from django.http import HttpResponse, Http404
from documentos.models import Documento, TipoDocumento
from documentos.serializers import DocumentoSerializer, TipoDocumentoSerializer
from documentos.generate_pdf import generate_factura_pdf, generate_nota_credito_pdf
from io import BytesIO
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from documentos.util import simplificar_dict


class DocumentoListView(ListAPIView):
    serializer_class = DocumentoSerializer
    filter_backends = [OrderingFilter]
    ordering = ['-fecha_emision']

    def get_queryset(self):
        queryset = Documento.objects.select_related(
            'tipo_documento', 'emissor__cidade__departamento'
        )

        # Filtros opcionais via query params
        emissor_id = self.request.GET.get('emissor')
        cdc = self.request.GET.get('cdc')
        num_doc = self.request.GET.get('num_doc')
        tipo_documento_id = self.request.GET.get('tipo_documento')
        fecha_inicio = self.request.GET.get('start_date')
        fecha_fim = self.request.GET.get('end_date')

        if emissor_id:
            queryset = queryset.filter(emissor__id=emissor_id)

        if cdc:
            queryset = queryset.filter(cdc=cdc)

        if num_doc:
            queryset = queryset.filter(num_doc__icontains=num_doc)

        if tipo_documento_id:
            queryset = queryset.filter(tipo_documento__code=tipo_documento_id)

        if fecha_inicio and fecha_fim:
            queryset = queryset.filter(
                fecha_emision__range=[fecha_inicio, fecha_fim]
            )

        return queryset.order_by('-fecha_emision')

class TipoDocumentoListView(ListAPIView):
    queryset = TipoDocumento.objects.all().order_by('name')
    serializer_class = TipoDocumentoSerializer

class DocumentoXMLDownloadView(APIView):
    # Sem autenticação
    def get(self, request, cdc):
        try:
            documento = Documento.objects.get(cdc=cdc)
        except Documento.DoesNotExist:
            raise Http404("Documento não encontrado")

        filename = f"{documento.cdc}.xml"
        response = HttpResponse(documento.documento_xml, content_type='application/xml')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

class FacturaPDFView(APIView):
    
    def get(self, request, cdc):
        try:
            documento = Documento.objects.get(cdc=cdc)
        except Documento.DoesNotExist:
            raise Http404("Documento não encontrado.")

        try:
            # Converte o XML bruto em dict
            xml = documento.documento_xml  # XML bruto
            data_dict = xmltodict.parse(xml)
            data_simplificado = simplificar_dict(data_dict)
        except Exception as e:
            return HttpResponse(f"Erro ao processar XML: {e}", status=400)


        # xml_content = documento.documento_xml
        # # Parâmetros adicionais que podem vir da requisição ou de configurações
        # cod_empresa = request.query_params.get('cod_empresa', 'default')
        # desc_empresa = request.query_params.get('desc_empresa', 'Empresa Desconocida')
        # # Em um ambiente real, 'ruta_logo' deve ser um caminho de arquivo acessível
        # ruta_logo = request.query_params.get('ruta_logo', '/media/logoFactura.png') # Substitua pelo seu caminho real

        # pdf_buffer = None
        # if documento.tipo_documento and documento.tipo_documento.code == 1: # Assumindo 1 para Factura
        #     pdf_buffer = generate_factura_pdf(xml_content, cod_empresa, desc_empresa, ruta_logo)
        # elif documento.tipo_documento and documento.tipo_documento.code == 5: # Assumindo 5 para Nota de Crédito
        #     pdf_buffer = generate_nota_credito_pdf(xml_content, cod_empresa, desc_empresa, ruta_logo)
        # else:
        #     return HttpResponse("Tipo de documento no soportado para generación de PDF.", status=400)

        # response = HttpResponse(pdf_buffer, content_type='application/pdf')
        # response['Content-Disposition'] = f'attachment; filename="{documento.cdc}.pdf"'
        # return response
        print('Gerando PDF para o documento:', cdc, ' com tipo de documento:', documento.tipo_documento.code)
        if (documento.tipo_documento.code == 1):
            rota_api = 'factura'
        elif (documento.tipo_documento.code == 5):
            rota_api = 'notacredito'
        elif (documento.tipo_documento.code == 6):
            rota_api = 'notacredito' # porém é notadebito
        
        rota_gerador_pdf = config('ROUTE_PDF_GENERATOR', default='http://localhost:3001/api/pdf/')
        result = requests.post(f'{rota_gerador_pdf}/api/pdf/{rota_api}', json={
            "xml": xml,
            "cod_empresa": 4,
            "nome_empresa": documento.emissor.nome,
        })

        if result.status_code == 200:
            response = HttpResponse(result.content, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename={rota_api}_{cdc}.pdf'
            return response
        else:
            return HttpResponse(f"Erro ao gerar PDF: {result.text}", status=result.status_code)


class DocumentoPDFView(APIView):
    """
    APIView para gerar um PDF de uma Fatura Eletrônica do Paraguai
    a partir de um XML armazenado no modelo Documento.
    """
    def get(self, request, cdc):
        """
        Método GET para buscar um documento pelo CDC e gerar seu PDF.
        """
        try:
            # Busca o objeto Documento no banco de dados usando o CDC.
            # O modelo Documento deve ter um campo 'documento_xml' (texto)
            # e um campo 'cdc' (string) para o Código de Documento de Controle.
            documento = Documento.objects.get(cdc=cdc)
        except Documento.DoesNotExist:
            # Retorna 404 se o documento não for encontrado.
            raise Http404("Documento no encontrado")

        # Chama o método privado para gerar o PDF.
        return self._generate_pdf_response(documento)

    def _generate_pdf_response(self, documento):
        """
        Método auxiliar para processar o XML e gerar o PDF.
        """
        try:
            # Define o namespace padrão para o XML SIFEN do Paraguai.
            # É crucial para que as buscas XPath funcionem corretamente.
            NS = {'sifen': 'http://ekuatia.set.gov.py/sifen/xsd'}
            xml_root = ET.fromstring(documento.documento_xml)
        except ET.ParseError:
            # Retorna um erro se o XML for inválido.
            return HttpResponse("Error al leer el XML: Formato inválido.", status=400)

        # Cria um buffer de memória para armazenar o PDF.
        buffer = BytesIO()
        # Inicializa o SimpleDocTemplate com o tamanho A4 e margens.
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                leftMargin=30, rightMargin=30,
                                topMargin=50, bottomMargin=50)
        Story = [] # Esta lista conterá todos os elementos (Flowables) do PDF.

        # Define os estilos de parágrafo para diferentes elementos de texto.
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['h1'],
            fontSize=16,
            leading=18,
            alignment=TA_CENTER,
            spaceAfter=10
        )
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Normal'],
            fontSize=12,
            leading=14,
            alignment=TA_CENTER,
            spaceAfter=10
        )
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['h2'],
            fontSize=12,
            leading=14,
            alignment=TA_LEFT,
            spaceAfter=5
        )
        normal_text_style = ParagraphStyle(
            'NormalTextStyle',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
            alignment=TA_LEFT,
            spaceAfter=3
        )
        table_header_style = ParagraphStyle(
            'TableHeaderStyle',
            parent=styles['Normal'],
            fontSize=8,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            leading=9
        )
        table_cell_style = ParagraphStyle(
            'TableCellStyle',
            parent=styles['Normal'],
            fontSize=8,
            leading=9,
            alignment=TA_LEFT
        )
        right_aligned_text_style = ParagraphStyle(
            'RightAlignedStyle',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
            alignment=TA_RIGHT,
            spaceAfter=3
        )
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=9,
            leading=10,
            alignment=TA_CENTER,
            spaceBefore=10
        )

        # --- Título do Documento e Número ---
        doc_type_node = xml_root.find("sifen:DE/sifen:gTimb/sifen:dDesTiDE", NS)
        doc_type_text = doc_type_node.text.replace("&#xF3;", "ó") if doc_type_node is not None else "Documento Electrónico"

        doc_num_est_node = xml_root.find("sifen:DE/sifen:gTimb/sifen:dEst", NS)
        doc_num_punexp_node = xml_root.find("sifen:DE/sifen:gTimb/sifen:dPunExp", NS)
        doc_num_doc_node = xml_root.find("sifen:DE/sifen:gTimb/sifen:dNumDoc", NS)
        timbrado_num_node = xml_root.find("sifen:DE/sifen:gTimb/sifen:dNumTim", NS)

        full_doc_number = ""
        if all(node is not None for node in [doc_num_est_node, doc_num_punexp_node, doc_num_doc_node]):
            full_doc_number = f"{doc_num_est_node.text}-{doc_num_punexp_node.text}-{doc_num_doc_node.text}"

        Story.append(Paragraph(doc_type_text, title_style))
        Story.append(Paragraph(f"N°: {full_doc_number}", subtitle_style))
        Story.append(Spacer(1, 0.5*cm))

        # --- Informações do Emissor (Datos del Emisor) ---
        Story.append(Paragraph("Datos del Emisor:", header_style))
        emitter_name = xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gEmis/sifen:dNomEmi", NS)
        emitter_ruc = xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gEmis/sifen:dRucEm", NS)
        emitter_dv = xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gEmis/sifen:dDVEmi", NS)
        emitter_address = xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gEmis/sifen:dDirEmi", NS)
        emitter_num_cas = xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gEmis/sifen:dNumCas", NS)
        emitter_city = xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gEmis/sifen:dDesCiuEmi", NS)
        emitter_phone = xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gEmis/sifen:dTelEmi", NS)
        emitter_email = xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gEmis/sifen:dEmailE", NS)
        emitter_activity = xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gEmis/sifen:gActEco/sifen:dDesActEco", NS)

        if emitter_name is not None: Story.append(Paragraph(f"Nombre/Razón Social: {emitter_name.text}", normal_text_style))
        if emitter_ruc is not None and emitter_dv is not None: Story.append(Paragraph(f"RUC: {emitter_ruc.text}-{emitter_dv.text}", normal_text_style))
        if emitter_address is not None:
            addr_text = emitter_address.text
            if emitter_num_cas is not None and emitter_num_cas.text.strip():
                addr_text += f" N° {emitter_num_cas.text}"
            Story.append(Paragraph(f"Dirección: {addr_text}", normal_text_style))
        if emitter_city is not None: Story.append(Paragraph(f"Ciudad: {emitter_city.text}", normal_text_style))
        if emitter_phone is not None: Story.append(Paragraph(f"Teléfono: {emitter_phone.text}", normal_text_style))
        if emitter_email is not None: Story.append(Paragraph(f"Email: {emitter_email.text}", normal_text_style))
        if emitter_activity is not None: Story.append(Paragraph(f"Actividad Económica: {emitter_activity.text}", normal_text_style))
        if timbrado_num_node is not None: Story.append(Paragraph(f"Timbrado N°: {timbrado_num_node.text}", normal_text_style))
        Story.append(Spacer(1, 0.5*cm))

        # --- Detalhes Gerais da Operação ---
        emission_date_time_node = xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:dFeEmiDE", NS)
        condition_sale_node = xml_root.find("sifen:DE/sifen:gDtipDE/sifen:gCamCond/sifen:dDCondOpe", NS)
        currency_node = xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gOpeCom/sifen:dDesMoneOpe", NS)

        if emission_date_time_node is not None:
            formatted_date = ""
            try:
                dt_obj = datetime.strptime(emission_date_time_node.text, "%Y-%m-%dT%H:%M:%S")
                formatted_date = dt_obj.strftime("%d/%m/%Y %H:%M:%S")
            except ValueError:
                formatted_date = emission_date_time_node.text
            Story.append(Paragraph(f"Fecha y Hora de Emisión: {formatted_date}", normal_text_style))

        if condition_sale_node is not None: Story.append(Paragraph(f"Condición de Venta: {condition_sale_node.text}", normal_text_style))
        if currency_node is not None: Story.append(Paragraph(f"Moneda: {currency_node.text}", normal_text_style))
        Story.append(Spacer(1, 0.5*cm))

        # --- Informações do Receptor (Datos del Receptor) ---
        Story.append(Paragraph("Datos del Receptor:", header_style))
        receiver_name = xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gDatRec/sifen:dNomRec", NS)
        receiver_id_type = xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gDatRec/sifen:dDTipIDRec", NS)
        receiver_id_num = xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gDatRec/sifen:dNumIDRec", NS)
        receiver_ruc = xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gDatRec/sifen:dRucRec", NS)
        receiver_dv = xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gDatRec/sifen:dDVRec", NS)
        receiver_address = xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gDatRec/sifen:dDirRec", NS)
        receiver_num_cas = xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gDatRec/sifen:dNumCasRec", NS)
        receiver_city = xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gDatRec/sifen:dDesCiuRec", NS)
        receiver_phone = xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gDatRec/sifen:dTelRec", NS)
        receiver_cell = xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gDatRec/sifen:dCelRec", NS)
        receiver_email = xml_root.find("sifen:DE/sifen:gDatGralOpe/sifen:gDatRec/sifen:dEmailRec", NS)

        if receiver_name is not None: Story.append(Paragraph(f"Nombre/Razón Social: {receiver_name.text}", normal_text_style))
        if receiver_ruc is not None and receiver_dv is not None:
            Story.append(Paragraph(f"RUC: {receiver_ruc.text}-{receiver_dv.text}", normal_text_style))
        elif receiver_id_type is not None and receiver_id_num is not None:
            Story.append(Paragraph(f"{receiver_id_type.text}: {receiver_id_num.text}", normal_text_style))

        if receiver_address is not None:
            addr_text = receiver_address.text
            if receiver_num_cas is not None and receiver_num_cas.text.strip():
                addr_text += f" N° {receiver_num_cas.text}"
            Story.append(Paragraph(f"Dirección: {addr_text}", normal_text_style))
        if receiver_city is not None: Story.append(Paragraph(f"Ciudad: {receiver_city.text}", normal_text_style))
        if receiver_phone is not None: Story.append(Paragraph(f"Teléfono: {receiver_phone.text}", normal_text_style))
        elif receiver_cell is not None: Story.append(Paragraph(f"Teléfono: {receiver_cell.text}", normal_text_style))
        if receiver_email is not None: Story.append(Paragraph(f"Email: {receiver_email.text}", normal_text_style))
        Story.append(Spacer(1, 0.5*cm))

        # --- Tabela de Produtos ---
        Story.append(Paragraph("Productos:", header_style))

        # Cabeçalhos da tabela de produtos.
        processed_table_data = [
            [Paragraph(h, table_header_style) for h in ["Cod", "Descripción", "Unid.", "Cant.", "P. Unitario", "Desc.", "Exentas", "Ventas 5%", "Ventas 10%"]]
        ]
        items = xml_root.findall("sifen:DE/sifen:gDtipDE/sifen:gCamItem", NS)

        # Estilo para parágrafos dentro da tabela (para quebra de linha)
        description_style = ParagraphStyle(
            'DescriptionStyle',
            parent=styles['Normal'],
            fontSize=8,
            leading=9,
            alignment=TA_LEFT
        )
        # Estilo para o código do produto (também pode quebrar linha)
        code_style = ParagraphStyle(
            'CodeStyle',
            parent=styles['Normal'],
            fontSize=8,
            leading=9,
            alignment=TA_CENTER
        )
        # Estilo para valores numéricos na tabela (alinhado à direita)
        table_numeric_style = ParagraphStyle(
            'TableNumericStyle',
            parent=styles['Normal'],
            fontSize=8,
            leading=9,
            alignment=TA_RIGHT
        )

        def get_float_value(node):
            try:
                return float(node.text) if node is not None and node.text else 0.0
            except (ValueError, TypeError):
                return 0.0

        for item in items:
            cod = item.find("sifen:dCodInt", NS)
            desc = item.find("sifen:dDesProSer", NS)
            unit = item.find("sifen:dDesUniMed", NS)
            qty = item.find("sifen:dCantProSer", NS)
            price = item.find("sifen:gValorItem/sifen:dPUniProSer", NS)
            discount = item.find("sifen:gValorItem/sifen:gValorRestaItem/sifen:dDescItem", NS)
            iva_rate = item.find("sifen:gCamIVA/sifen:dTasaIVA", NS)
            total_item_value = item.find("sifen:gValorItem/sifen:dTotBruOpeItem", NS)

            qty_val = get_float_value(qty)
            price_val = get_float_value(price)
            discount_val = get_float_value(discount)
            total_item_val = get_float_value(total_item_value)

            exentas = "0"
            valor_5 = "0"
            valor_10 = "0"

            if iva_rate is not None:
                if iva_rate.text == "10":
                    valor_10 = f"{total_item_val:,.0f}".replace(",", ".")
                elif iva_rate.text == "5":
                    valor_5 = f"{total_item_val:,.0f}".replace(",", ".")
                else:
                    exentas = f"{total_item_val:,.0f}".replace(",", ".")
            else:
                exentas = f"{total_item_val:,.0f}".replace(",", ".")

            description_text = (desc.text.replace("&#xD;", "").replace("&#xA;", " ").strip() if desc is not None else "")

            processed_table_data.append([
                Paragraph(cod.text if cod is not None else "", code_style), # Cod agora usa Paragraph
                Paragraph(description_text, description_style),
                Paragraph(unit.text if unit is not None else "", table_cell_style),
                Paragraph(f"{qty_val:,.0f}".replace(",", ".") if qty_val != 0 else "0", table_numeric_style),
                Paragraph(f"{price_val:,.0f}".replace(",", ".") if price_val != 0 else "0", table_numeric_style),
                Paragraph(f"{discount_val:,.0f}".replace(",", ".") if discount_val != 0 else "0", table_numeric_style),
                Paragraph(exentas, table_numeric_style),
                Paragraph(valor_5, table_numeric_style),
                Paragraph(valor_10, table_numeric_style)
            ])

        # Define as larguras das colunas da tabela.
        # A largura total disponível é (A4[0] - leftMargin - rightMargin)
        # = 595.27 - 30 - 30 = 535.27 pontos.
        # 1 cm = 28.3465 pontos
        # Distribuindo o espaço:
        # Cod: 1.5cm (42.5 pts)
        # Unid: 1.0cm (28.3 pts)
        # Cant: 1.0cm (28.3 pts)
        # P. Unitario: 1.8cm (51.0 pts)
        # Desc: 1.0cm (28.3 pts)
        # Exentas: 1.5cm (42.5 pts)
        # Ventas 5%: 1.5cm (42.5 pts)
        # Ventas 10%: 1.5cm (42.5 pts)
        # Soma das larguras fixas: 1.5 + 1.0 + 1.0 + 1.8 + 1.0 + 1.5 + 1.5 + 1.5 = 10.8 cm
        # Espaço restante para "Descripción": (535.27 / 28.3465) - 10.8 = 18.88 - 10.8 = 8.08 cm
        # Ajustei as larguras para que a soma seja um pouco menor que o total disponível,
        # permitindo que 'None' na descrição preencha o restante.
        col_widths = [1.5*cm, None, 1.0*cm, 1.0*cm, 1.8*cm, 1.0*cm, 1.5*cm, 1.5*cm, 1.5*cm]
        table = Table(processed_table_data, colWidths=col_widths)

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E0E0E0")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Os alinhamentos específicos para as colunas são definidos nos ParagraphStyles agora.
            # No entanto, para garantir, podemos manter alguns aqui para o TableStyle.
            ('ALIGN', (0, 1), (0, -1), 'CENTER'), # Cod
            ('ALIGN', (1, 1), (1, -1), 'LEFT'), # Descripción
            ('ALIGN', (2, 1), (3, -1), 'CENTER'), # Unid. e Cant.
            ('ALIGN', (4, 1), (-1, -1), 'RIGHT'), # P. Unitario, Desc., Exentas, Ventas 5%, Ventas 10%
        ]))
        Story.append(table)
        Story.append(Spacer(1, 0.5*cm))

        # --- Totais ---
        Story.append(Paragraph("Resumen de la Operación:", header_style))
        total_operation_node = xml_root.find("sifen:DE/sifen:gTotSub/sifen:dTotOpe", NS)
        total_guaranies_node = xml_root.find("sifen:DE/sifen:gTotSub/sifen:dTotGralOpe", NS)
        total_discount_node = xml_root.find("sifen:DE/sifen:gTotSub/sifen:dTotDesc", NS)
        total_iva_node = xml_root.find("sifen:DE/sifen:gTotSub/sifen:dTotIVA", NS)
        iva_5_node = xml_root.find("sifen:DE/sifen:gTotSub/sifen:dIVA5", NS)
        iva_10_node = xml_root.find("sifen:DE/sifen:gTotSub/sifen:dIVA10", NS)
        
        def format_currency_value(value_node):
            try:
                return f"{float(value_node.text):,.0f}".replace(",", ".") if value_node is not None and value_node.text else "0"
            except (ValueError, TypeError):
                return "0"

        Story.append(Paragraph(f"SUBTOTAL: {format_currency_value(total_operation_node)}", right_aligned_text_style))
        Story.append(Paragraph(f"DESCUENTO: {format_currency_value(total_discount_node)}", right_aligned_text_style))
        Story.append(Paragraph(f"TOTAL DE LA OPERACIÓN: {format_currency_value(total_operation_node)}", right_aligned_text_style))
        Story.append(Paragraph(f"TOTAL EN GUARANIES: {format_currency_value(total_guaranies_node)}", right_aligned_text_style))
        Story.append(Spacer(1, 0.5*cm))

        # --- Liquidação de IVA ---
        Story.append(Paragraph("LIQUIDACIÓN IVA:", header_style))
        # Usando uma mini-tabela para alinhar os valores de IVA.
        iva_table_data = [
            [Paragraph(f"(5%): {format_currency_value(iva_5_node)}", normal_text_style),
             Paragraph(f"(10%): {format_currency_value(iva_10_node)}", normal_text_style)],
            [Paragraph("TOTAL IVA:", normal_text_style),
             Paragraph(format_currency_value(total_iva_node), right_aligned_text_style)]
        ]
        # A largura total disponível para esta tabela é a largura da página menos as margens laterais.
        page_width_points = A4[0]
        usable_width_points = page_width_points - (doc.leftMargin + doc.rightMargin)
        iva_table = Table(iva_table_data, colWidths=[usable_width_points/2, usable_width_points/2])
        iva_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (0,-1), 'LEFT'),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,0), 0),
            ('TOPPADDING', (0,0), (-1,0), 0),
        ]))
        Story.append(iva_table)
        Story.append(Spacer(1, 0.5*cm))

        # --- Total em Guaranies por Extenso (Atualmente numérico) ---
        Story.append(Paragraph(f"TOTAL EN GUARANIES: {format_currency_value(total_guaranies_node)}", header_style))
        Story.append(Spacer(1, 0.5*cm))

        # --- CDC e Link do QR Code ---
        cdc_value = documento.cdc
        qr_code_link_node = xml_root.find("sifen:DE/sifen:gCamFuFD/sifen:dCarQR", NS)
        qr_code_link_text = qr_code_link_node.text if qr_code_link_node is not None else "Enlace del Código QR no disponible."

        Story.append(Paragraph("Consulte la validez de esta Factura Electrónica con el número CDC impreso abajo en:", normal_text_style))
        Story.append(Paragraph(qr_code_link_text, normal_text_style))
        Story.append(Paragraph(f"CDC: {cdc_value}", header_style))
        Story.append(Spacer(1, 0.5*cm))

        # --- Aviso Legal ---
        Story.append(Paragraph("ESTE DOCUMENTO ES UNA REPRESENTACIÓN GRÁFICA DE UN DOCUMENTO ELECTRÓNICO (XML)", footer_style))
        Story.append(Paragraph("Si su documento electrónico presenta algún error, podrá solicitar la modificación dentro de las 72 horas siguientes de la emisión de este comprobante.", footer_style))

        # Constrói o PDF a partir da lista de Flowables.
        doc.build(Story)

        # Retorna o PDF como uma resposta HTTP.
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{documento.cdc}.pdf"'
        return response

