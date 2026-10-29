from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.LibroListView.as_view(), name="libros"),
    path("libros/nuevo/", views.LibroCreateView.as_view(), name="libro_crear"),
    path("libros/<int:pk>/editar/", views.LibroUpdateView.as_view(), name="libro_editar"),
    path("libros/<int:pk>/eliminar/", views.LibroDeleteView.as_view(), name="libro_eliminar"),
    path("categorias/", views.CategoriaListView.as_view(), name="categorias"),
    path("categorias/nueva/", views.CategoriaCreateView.as_view(), name="categoria_crear"),
    path("categorias/<int:pk>/eliminar/", views.CategoriaDeleteView.as_view(), name="categoria_eliminar"),
]
