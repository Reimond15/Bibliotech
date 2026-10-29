"""Control de acceso por roles (requisito de seguridad RNF)."""

from functools import wraps

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from .models import Usuario


class RolRequeridoMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restringe una vista basada en clase a los roles indicados en `roles_permitidos`."""

    roles_permitidos = (Usuario.Rol.ADMINISTRADOR,)

    def test_func(self):
        return self.request.user.rol in self.roles_permitidos

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()


def rol_requerido(*roles):
    """Decorador equivalente para vistas basadas en funciones."""

    def decorador(vista):
        @wraps(vista)
        def envoltura(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login

                return redirect_to_login(request.get_full_path())
            if request.user.rol not in roles:
                raise PermissionDenied
            return vista(request, *args, **kwargs)

        return envoltura

    return decorador
