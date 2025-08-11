from django.urls import path
from documentos.views import (
    DocumentoListView, 
    TipoDocumentoListView,
    DocumentoXMLDownloadView,
    DocumentoPDFView,
    FacturaPDFView
)


urlpatterns = [
    path('documentos/download-xml/<str:cdc>/', DocumentoXMLDownloadView.as_view(), name='documento-download-xml'),    
    path("documentos/download-pdf/<str:cdc>/", FacturaPDFView.as_view(), name="documento-download-pdf"),
    path('documentos/', DocumentoListView.as_view(), name='documento-list'),
    path('tipos-documento/', TipoDocumentoListView.as_view(), name='tipo-documento-list'),
    
]
