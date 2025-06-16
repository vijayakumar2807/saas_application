from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('email',)  # Use 'email' instead of 'username'
    
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('client', 'role',)}),
    )
    list_display = ('email', 'name', 'client', 'is_staff')
