from django import forms

from .models import Categoria, Libro


class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ("titulo", "autor", "isbn", "categoria", "cantidad_total")
        labels = {"titulo": "Título", "autor": "Autor", "categoria": "Categoría",
                  "cantidad_total": "Cantidad de ejemplares"}

    def clean_cantidad_total(self):
        cantidad = self.cleaned_data["cantidad_total"]
        if cantidad < 1:
            raise forms.ValidationError("Debe haber al menos un ejemplar.")
        if self.instance.pk:
            prestados = self.instance.cantidad_total - self.instance.cantidad_disponible
            if cantidad < prestados:
                raise forms.ValidationError(
                    f"Hay {prestados} ejemplares prestados; el total no puede ser menor."
                )
        return cantidad


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ("nombre",)
        labels = {"nombre": "Nombre de la categoría"}
