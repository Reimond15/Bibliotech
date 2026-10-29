from django.core.exceptions import ValidationError
from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=60, unique=True)

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=120)
    isbn = models.CharField("ISBN", max_length=20, unique=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="libros")
    cantidad_total = models.PositiveIntegerField("ejemplares totales", default=1)
    cantidad_disponible = models.PositiveIntegerField("ejemplares disponibles", default=1)

    class Meta:
        ordering = ["titulo"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(cantidad_disponible__lte=models.F("cantidad_total")),
                name="disponible_no_mayor_que_total",
            )
        ]

    @property
    def disponible(self):
        return self.cantidad_disponible > 0

    def clean(self):
        if self.cantidad_disponible > self.cantidad_total:
            raise ValidationError(
                "Los ejemplares disponibles no pueden superar los ejemplares totales."
            )

    def __str__(self):
        return f"{self.titulo} — {self.autor}"
