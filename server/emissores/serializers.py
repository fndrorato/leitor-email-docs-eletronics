from emissores.models import Emissor
from rest_framework import serializers


class EmissorSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField()

    class Meta:
        model = Emissor
        fields = ['id', 'nome']

    def get_nome(self, obj):
        return f"{obj.nome} ({obj.code})"