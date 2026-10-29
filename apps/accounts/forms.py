from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

from .models import Usuario


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Usuario", widget=forms.TextInput(attrs={"autofocus": True}))
    password = forms.CharField(label="Contraseña", strip=False, widget=forms.PasswordInput)

    error_messages = {
        "invalid_login": "Usuario o contraseña incorrectos.",
        "inactive": "Esta cuenta está desactivada.",
    }


class _ValidaMembresiaMixin:
    def clean(self):
        datos = super().clean()
        if datos.get("rol") == Usuario.Rol.USUARIO and not datos.get("membresia"):
            raise ValidationError("Los usuarios finales deben tener un tipo de membresía.")
        if datos.get("rol") != Usuario.Rol.USUARIO:
            datos["membresia"] = None
        return datos


class UsuarioCrearForm(_ValidaMembresiaMixin, UserCreationForm):
    class Meta:
        model = Usuario
        fields = ("username", "first_name", "last_name", "email", "rol", "membresia")
        labels = {
            "username": "Nombre de usuario",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
            "rol": "Rol",
            "membresia": "Membresía",
        }


class UsuarioEditarForm(_ValidaMembresiaMixin, forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ("first_name", "last_name", "email", "rol", "membresia", "is_active")
        labels = {
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
            "rol": "Rol",
            "membresia": "Membresía",
            "is_active": "Cuenta activa",
        }
