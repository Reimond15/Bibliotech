from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Membresia, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("BiblioTech", {"fields": ("rol", "membresia")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("BiblioTech", {"fields": ("rol", "membresia")}),)
    list_display = ("username", "first_name", "last_name", "rol", "is_active")
    list_filter = ("rol", "is_active")


admin.site.register(Membresia)
