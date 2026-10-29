from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, ListView, UpdateView

from apps.catalog.models import Libro

from . import services
from .forms import LoginForm, UsuarioCrearForm, UsuarioEditarForm
from .models import Usuario
from .permissions import RolRequeridoMixin, rol_requerido


class IniciarSesionView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


@login_required
def home(request):
    contexto = {
        "total_libros": Libro.objects.count(),
        "disponibles": sum(1 for libro in Libro.objects.all() if libro.disponible),
    }
    if request.user.es_administrador:
        contexto["total_usuarios"] = Usuario.objects.count()
    return render(request, "home.html", contexto)


class UsuarioListView(RolRequeridoMixin, ListView):
    roles_permitidos = (Usuario.Rol.ADMINISTRADOR,)
    template_name = "accounts/usuario_list.html"
    context_object_name = "usuarios"
    paginate_by = 15

    def get_queryset(self):
        return services.buscar_usuarios(
            self.request.GET.get("q", "").strip(), self.request.GET.get("rol", "")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["rol_sel"] = self.request.GET.get("rol", "")
        ctx["roles"] = Usuario.Rol.choices
        return ctx


class UsuarioCreateView(RolRequeridoMixin, CreateView):
    roles_permitidos = (Usuario.Rol.ADMINISTRADOR,)
    model = Usuario
    form_class = UsuarioCrearForm
    template_name = "accounts/usuario_form.html"
    success_url = reverse_lazy("accounts:usuarios")
    extra_context = {"titulo": "Registrar usuario"}

    def form_valid(self, form):
        messages.success(self.request, "Usuario registrado correctamente.")
        return super().form_valid(form)


class UsuarioUpdateView(RolRequeridoMixin, UpdateView):
    roles_permitidos = (Usuario.Rol.ADMINISTRADOR,)
    model = Usuario
    form_class = UsuarioEditarForm
    template_name = "accounts/usuario_form.html"
    success_url = reverse_lazy("accounts:usuarios")
    extra_context = {"titulo": "Editar usuario"}

    def form_valid(self, form):
        messages.success(self.request, "Usuario actualizado correctamente.")
        return super().form_valid(form)


@require_POST
@rol_requerido(Usuario.Rol.ADMINISTRADOR)
def usuario_alternar_estado(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    try:
        usuario = services.alternar_estado(usuario, request.user)
    except ValidationError as error:
        messages.error(request, error.message)
    else:
        estado = "activada" if usuario.is_active else "desactivada"
        messages.success(request, f"Cuenta de {usuario.username} {estado}.")
    return redirect("accounts:usuarios")
