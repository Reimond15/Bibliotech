from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("iniciar-sesion/", views.IniciarSesionView.as_view(), name="login"),
    path("cerrar-sesion/", LogoutView.as_view(), name="logout"),
    path("usuarios/", views.UsuarioListView.as_view(), name="usuarios"),
    path("usuarios/nuevo/", views.UsuarioCreateView.as_view(), name="usuario_crear"),
    path("usuarios/<int:pk>/editar/", views.UsuarioUpdateView.as_view(), name="usuario_editar"),
    path("usuarios/<int:pk>/estado/", views.usuario_alternar_estado, name="usuario_estado"),
]
