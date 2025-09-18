from django.contrib import admin
from users.models import UserCompany


@admin.register(UserCompany)
class UserCompanyAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'created_at', 'updated_at')
    search_fields = ('user__first_name', 'company__name')
    list_filter = ('created_at', 'updated_at')
    ordering = ('user__first_name', 'company__name')
