from django.contrib.auth.models import AbstractUser
from django.db import models


class Membresia(models.Model):
    """Tipo de membresía: define cuántos días dura un préstamo y cuántos libros puede tener."""

    tipo = models.CharField(max_length=30, unique=True)
    dias_prestamo = models.PositiveIntegerField(default=7)
    max_prestamos = models.PositiveIntegerField(default=3)

    class Meta:
        verbose_name = "membresía"
        verbose_name_plural = "membresías"
        ordering = ["tipo"]

    def __str__(self):
        return self.tipo


class Usuario(AbstractUser):
    """Usuario del sistema. La contraseña se guarda con hash (PBKDF2) por Django."""

    class Rol(models.TextChoices):
        ADMINISTRADOR = "ADMINISTRADOR", "Administrador"
        BIBLIOTECARIO = "BIBLIOTECARIO", "Bibliotecario"
        USUARIO = "USUARIO", "Usuario"

    rol = models.CharField(max_length=15, choices=Rol.choices, default=Rol.USUARIO)
    membresia = models.ForeignKey(
        Membresia,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="usuarios",
        help_text="Solo aplica a los usuarios finales.",
    )

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        ordering = ["username"]

    @property
    def es_administrador(self):
        return self.rol == self.Rol.ADMINISTRADOR

    @property
    def es_bibliotecario(self):
        return self.rol == self.Rol.BIBLIOTECARIO

    def __str__(self):
        nombre = self.get_full_name() or self.username
        return f"{nombre} ({self.get_rol_display()})"
