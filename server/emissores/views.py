from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from emissores.models import Emissor
from emissores.serializers import EmissorSerializer


class EmissorListView(ListAPIView):
    queryset = Emissor.objects.all().order_by('nome')
    serializer_class = EmissorSerializer
    filter_backends = [SearchFilter]
    search_fields = ['nome', 'code'] 
