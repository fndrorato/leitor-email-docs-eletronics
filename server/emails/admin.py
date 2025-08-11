from django.contrib import admin
from emails.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Admin interface for managing users.
    """
    list_display = ('username', 'host', 'port')
    search_fields = ('username', 'host')
    ordering = ('username',)

