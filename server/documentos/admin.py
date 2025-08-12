from django.contrib import admin
from documentos.models import Documento, TipoDocumento


@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('code',)
    list_filter = ('created_at', 'updated_at')

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('cdc', 'tipo_documento', 'est', 'pun_exp', 'num_doc', 'emissor', 'fecha_emision', 'monto_total', 'created_at', 'updated_at')
    search_fields = ('cdc', 'num_doc', 'emissor__nombre')
    ordering = ('-fecha_emision',)
    list_filter = ('tipo_documento', 'fecha_emision', 'emissor')
