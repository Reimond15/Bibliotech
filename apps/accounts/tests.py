from django.test import TestCase
from django.urls import reverse

from .models import Membresia, Usuario


class AutenticacionTests(TestCase):
    def setUp(self):
        self.membresia = Membresia.objects.create(tipo="Estudiante")
        self.admin = Usuario.objects.create_user("admin1", password="Clave12345!", rol=Usuario.Rol.ADMINISTRADOR)
        self.alumno = Usuario.objects.create_user(
            "alumno1", password="Clave12345!", rol=Usuario.Rol.USUARIO, membresia=self.membresia
        )

    def test_login_correcto_redirige_al_inicio(self):
        r = self.client.post(reverse("accounts:login"), {"username": "admin1", "password": "Clave12345!"})
        self.assertRedirects(r, reverse("home"))

    def test_login_incorrecto_muestra_error(self):
        r = self.client.post(reverse("accounts:login"), {"username": "admin1", "password": "mala"})
        self.assertContains(r, "Usuario o contraseña incorrectos.")

    def test_cuenta_desactivada_no_inicia_sesion(self):
        self.alumno.is_active = False
        self.alumno.save()
        r = self.client.post(reverse("accounts:login"), {"username": "alumno1", "password": "Clave12345!"})
        self.assertEqual(r.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_contrasena_se_guarda_encriptada(self):
        self.assertNotEqual(self.admin.password, "Clave12345!")
        self.assertTrue(self.admin.password.startswith(("pbkdf2_", "scrypt$", "argon2")))

    def test_pagina_privada_exige_sesion(self):
        r = self.client.get(reverse("home"))
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("accounts:login"), r.url)


class GestionUsuariosTests(TestCase):
    def setUp(self):
        self.membresia = Membresia.objects.create(tipo="Estudiante")
        self.admin = Usuario.objects.create_user("admin1", password="Clave12345!", rol=Usuario.Rol.ADMINISTRADOR)
        self.alumno = Usuario.objects.create_user(
            "alumno1", password="Clave12345!", rol=Usuario.Rol.USUARIO, membresia=self.membresia
        )

    def test_usuario_final_no_puede_ver_lista_de_usuarios(self):
        self.client.force_login(self.alumno)
        self.assertEqual(self.client.get(reverse("accounts:usuarios")).status_code, 403)

    def test_admin_crea_usuario(self):
        self.client.force_login(self.admin)
        r = self.client.post(
            reverse("accounts:usuario_crear"),
            {
                "username": "nuevo",
                "first_name": "Ana",
                "last_name": "Pérez",
                "email": "ana@example.com",
                "rol": Usuario.Rol.USUARIO,
                "membresia": self.membresia.pk,
                "password1": "OtraClave2026!",
                "password2": "OtraClave2026!",
            },
        )
        self.assertRedirects(r, reverse("accounts:usuarios"))
        self.assertTrue(Usuario.objects.filter(username="nuevo").exists())

    def test_usuario_final_exige_membresia(self):
        self.client.force_login(self.admin)
        r = self.client.post(
            reverse("accounts:usuario_crear"),
            {"username": "sinmem", "rol": Usuario.Rol.USUARIO, "password1": "OtraClave2026!", "password2": "OtraClave2026!"},
        )
        self.assertContains(r, "deben tener un tipo de membresía")

    def test_admin_desactiva_y_reactiva_usuario(self):
        self.client.force_login(self.admin)
        url = reverse("accounts:usuario_estado", args=[self.alumno.pk])
        self.client.post(url)
        self.alumno.refresh_from_db()
        self.assertFalse(self.alumno.is_active)
        self.client.post(url)
        self.alumno.refresh_from_db()
        self.assertTrue(self.alumno.is_active)

    def test_admin_no_puede_desactivarse_a_si_mismo(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("accounts:usuario_estado", args=[self.admin.pk]))
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_busqueda_de_usuarios(self):
        self.client.force_login(self.admin)
        r = self.client.get(reverse("accounts:usuarios"), {"q": "alumno"})
        self.assertContains(r, "alumno1")
        self.assertNotContains(r, "admin1</td>")
