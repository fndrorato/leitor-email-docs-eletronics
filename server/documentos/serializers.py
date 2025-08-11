from babel.numbers import format_currency
from common.models import Cidade, Departamento
from documentos.models import Documento, TipoDocumento
from emissores.models import Emissor
from rest_framework import serializers

class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = ['code', 'name']

class CidadeSerializer(serializers.ModelSerializer):
    departamento = DepartamentoSerializer()

    class Meta:
        model = Cidade
        fields = ['code', 'name', 'departamento']

class EmissorSerializer(serializers.ModelSerializer):
    cidade = CidadeSerializer()

    class Meta:
        model = Emissor
        fields = ['code', 'nome', 'nome_fantasia', 'cidade']

class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = ['code', 'name']

class DocumentoSerializer(serializers.ModelSerializer):
    tipo_documento = TipoDocumentoSerializer()
    emissor = EmissorSerializer()
    monto_total_formatado = serializers.SerializerMethodField()

    class Meta:
        model = Documento
        fields = [
            'cdc', 'tipo_documento', 'est', 'pun_exp', 'num_doc',
            'emissor', 'fecha_emision', 'monto_total',
            'created_at', 'updated_at', 'monto_total_formatado'
        ]

    def get_monto_total_formatado(self, obj):
        if obj.monto_total is None:
            return ""
        return format_currency(obj.monto_total, 'PYG', locale='es_PY')        
