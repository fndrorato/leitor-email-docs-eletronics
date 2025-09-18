from django.contrib import admin
from emails.models import User, EmailXmlError


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Admin interface for managing users.
    """
    list_display = ('username', 'company__name', 'host', 'port')
    search_fields = ('username', 'company__name', 'host')
    ordering = ('username',)

@admin.register(EmailXmlError)
class EmailXmlErrorAdmin(admin.ModelAdmin):
    """
    Admin interface for managing email XML errors.
    """
    list_display = ('subject', 'received_from', 'received_at', 'filename', 'decoded_ok', 'created_at')
    search_fields = ('subject', 'received_from', 'filename')
    ordering = ('-created_at',)
