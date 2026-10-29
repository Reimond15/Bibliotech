from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.accounts.models import Usuario
from apps.accounts.permissions import RolRequeridoMixin

from . import services
from .forms import CategoriaForm, LibroForm
from .models import Categoria, Libro


class LibroListView(LoginRequiredMixin, ListView):
    """Buscador del catálogo: lo pueden usar los tres roles (RF-05)."""

    template_name = "catalog/libro_list.html"
    context_object_name = "libros"
    paginate_by = 12

    def get_queryset(self):
        return services.buscar_libros(
            self.request.GET.get("q", "").strip(),
            self.request.GET.get("categoria") or None,
            self.request.GET.get("disponibilidad", ""),
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["categoria_sel"] = self.request.GET.get("categoria", "")
        ctx["disp_sel"] = self.request.GET.get("disponibilidad", "")
        ctx["categorias"] = Categoria.objects.all()
        return ctx


class _SoloAdminMixin(RolRequeridoMixin):
    roles_permitidos = (Usuario.Rol.ADMINISTRADOR,)


class LibroCreateView(_SoloAdminMixin, CreateView):
    model = Libro
    form_class = LibroForm
    template_name = "catalog/libro_form.html"
    success_url = reverse_lazy("catalog:libros")
    extra_context = {"titulo": "Registrar libro"}

    def form_valid(self, form):
        form.instance.cantidad_disponible = form.cleaned_data["cantidad_total"]
        messages.success(self.request, "Libro registrado en el catálogo.")
        return super().form_valid(form)


class LibroUpdateView(_SoloAdminMixin, UpdateView):
    model = Libro
    form_class = LibroForm
    template_name = "catalog/libro_form.html"
    success_url = reverse_lazy("catalog:libros")
    extra_context = {"titulo": "Editar libro"}

    def form_valid(self, form):
        total_anterior = Libro.objects.get(pk=self.object.pk).cantidad_total
        respuesta = super().form_valid(form)
        services.ajustar_inventario_al_editar(self.object, total_anterior)
        messages.success(self.request, "Libro actualizado.")
        return respuesta


class LibroDeleteView(_SoloAdminMixin, DeleteView):
    model = Libro
    template_name = "catalog/libro_confirm_delete.html"
    success_url = reverse_lazy("catalog:libros")

    def form_valid(self, form):
        messages.success(self.request, "Libro eliminado del catálogo.")
        return super().form_valid(form)


class CategoriaListView(_SoloAdminMixin, ListView):
    model = Categoria
    template_name = "catalog/categoria_list.html"
    context_object_name = "categorias"


class CategoriaCreateView(_SoloAdminMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "catalog/categoria_form.html"
    success_url = reverse_lazy("catalog:categorias")

    def form_valid(self, form):
        messages.success(self.request, "Categoría creada.")
        return super().form_valid(form)


class CategoriaDeleteView(_SoloAdminMixin, DeleteView):
    model = Categoria
    template_name = "catalog/categoria_confirm_delete.html"
    success_url = reverse_lazy("catalog:categorias")

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, "No se puede eliminar: hay libros en esta categoría.")
            return redirect("catalog:categorias")
