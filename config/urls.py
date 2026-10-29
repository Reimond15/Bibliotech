from django.contrib import admin
from django.urls import include, path

from apps.accounts.views import home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("cuentas/", include("apps.accounts.urls")),
    path("catalogo/", include("apps.catalog.urls")),
]
