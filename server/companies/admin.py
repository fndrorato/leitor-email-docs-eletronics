from django.contrib import admin
from companies.models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'created_at', 'updated_at')
    search_fields = ('name', 'active')
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)
