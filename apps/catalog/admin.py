from django.contrib import admin

from .models import Categoria, Libro


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ("titulo", "autor", "isbn", "categoria", "cantidad_disponible", "cantidad_total")
    list_filter = ("categoria",)
    search_fields = ("titulo", "autor", "isbn")


admin.site.register(Categoria)
