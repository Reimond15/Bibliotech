"""Capa de servicios: reglas de negocio del catálogo."""

from django.db.models import F, Q

from .models import Libro


def buscar_libros(texto="", categoria=None, disponibilidad=""):
    """RF-05: busca por título, autor o ISBN, y filtra por categoría y disponibilidad."""
    qs = Libro.objects.select_related("categoria")
    if texto:
        qs = qs.filter(
            Q(titulo__icontains=texto) | Q(autor__icontains=texto) | Q(isbn__icontains=texto)
        )
    if categoria:
        qs = qs.filter(categoria_id=categoria)
    if disponibilidad == "disponible":
        qs = qs.filter(cantidad_disponible__gt=0)
    elif disponibilidad == "prestado":
        qs = qs.filter(cantidad_disponible=0)
    return qs


def ajustar_inventario_al_editar(libro, total_anterior):
    """Si cambia el total de ejemplares, el disponible se ajusta en la misma proporción.

    Ejemplo: había 5 totales y 2 prestados (3 disponibles). Si el total pasa a 8,
    quedan 6 disponibles; los 2 prestados siguen fuera.
    """
    diferencia = libro.cantidad_total - total_anterior
    libro.cantidad_disponible = max(0, min(libro.cantidad_total, libro.cantidad_disponible + diferencia))
    libro.save(update_fields=["cantidad_disponible"])
    return libro
