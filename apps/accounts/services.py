"""Capa de servicios: reglas de negocio del módulo de usuarios."""

from django.core.exceptions import ValidationError
from django.db.models import Q

from .models import Usuario


def buscar_usuarios(texto="", rol=""):
    qs = Usuario.objects.select_related("membresia")
    if texto:
        qs = qs.filter(
            Q(username__icontains=texto)
            | Q(first_name__icontains=texto)
            | Q(last_name__icontains=texto)
            | Q(email__icontains=texto)
        )
    if rol:
        qs = qs.filter(rol=rol)
    return qs


def alternar_estado(usuario, solicitante):
    """Activa o desactiva una cuenta (RF-11). Un administrador no puede desactivarse a sí mismo."""
    if usuario.pk == solicitante.pk:
        raise ValidationError("No puedes desactivar tu propia cuenta.")
    usuario.is_active = not usuario.is_active
    usuario.save(update_fields=["is_active"])
    return usuario
