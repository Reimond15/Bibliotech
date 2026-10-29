from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Membresia, Usuario

from . import services
from .models import Categoria, Libro


class BaseCatalogo(TestCase):
    def setUp(self):
        self.cat_prog = Categoria.objects.create(nombre="Programación")
        self.cat_lit = Categoria.objects.create(nombre="Literatura")
        self.libro = Libro.objects.create(
            titulo="Clean Code", autor="Robert Martin", isbn="111", categoria=self.cat_prog,
            cantidad_total=3, cantidad_disponible=3,
        )
        self.agotado = Libro.objects.create(
            titulo="Cien años de soledad", autor="García Márquez", isbn="222", categoria=self.cat_lit,
            cantidad_total=1, cantidad_disponible=0,
        )
        self.admin = Usuario.objects.create_user("admin1", password="x", rol=Usuario.Rol.ADMINISTRADOR)
        self.biblio = Usuario.objects.create_user("biblio1", password="x", rol=Usuario.Rol.BIBLIOTECARIO)
        mem = Membresia.objects.create(tipo="Estudiante")
        self.alumno = Usuario.objects.create_user("alumno1", password="x", rol=Usuario.Rol.USUARIO, membresia=mem)


class BusquedaTests(BaseCatalogo):
    def test_busca_por_titulo_autor_e_isbn(self):
        self.assertEqual(list(services.buscar_libros("clean")), [self.libro])
        self.assertEqual(list(services.buscar_libros("márquez")), [self.agotado])
        self.assertEqual(list(services.buscar_libros("111")), [self.libro])

    def test_filtra_por_categoria(self):
        self.assertEqual(list(services.buscar_libros(categoria=self.cat_lit.pk)), [self.agotado])

    def test_filtra_por_disponibilidad(self):
        self.assertEqual(list(services.buscar_libros(disponibilidad="disponible")), [self.libro])
        self.assertEqual(list(services.buscar_libros(disponibilidad="prestado")), [self.agotado])

    def test_los_tres_roles_pueden_buscar(self):
        for usuario in (self.admin, self.biblio, self.alumno):
            self.client.force_login(usuario)
            self.assertEqual(self.client.get(reverse("catalog:libros")).status_code, 200)

    def test_anonimo_es_redirigido(self):
        self.assertEqual(self.client.get(reverse("catalog:libros")).status_code, 302)


class CrudLibrosTests(BaseCatalogo):
    def datos(self, **extra):
        base = {"titulo": "Fluent Python", "autor": "Ramalho", "isbn": "333",
                "categoria": self.cat_prog.pk, "cantidad_total": 4}
        base.update(extra)
        return base

    def test_admin_registra_libro_con_todos_los_ejemplares_disponibles(self):
        self.client.force_login(self.admin)
        r = self.client.post(reverse("catalog:libro_crear"), self.datos())
        self.assertRedirects(r, reverse("catalog:libros"))
        nuevo = Libro.objects.get(isbn="333")
        self.assertEqual(nuevo.cantidad_disponible, 4)

    def test_isbn_duplicado_es_rechazado(self):
        self.client.force_login(self.admin)
        r = self.client.post(reverse("catalog:libro_crear"), self.datos(isbn="111"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Libro.objects.filter(isbn="111").count(), 1)

    def test_editar_total_ajusta_disponibles(self):
        self.libro.cantidad_disponible = 1  # 2 prestados
        self.libro.save()
        self.client.force_login(self.admin)
        self.client.post(reverse("catalog:libro_editar", args=[self.libro.pk]),
                         self.datos(titulo="Clean Code", isbn="111", cantidad_total=5))
        self.libro.refresh_from_db()
        self.assertEqual((self.libro.cantidad_total, self.libro.cantidad_disponible), (5, 3))

    def test_total_no_puede_ser_menor_que_los_prestados(self):
        self.libro.cantidad_disponible = 0  # 3 prestados
        self.libro.save()
        self.client.force_login(self.admin)
        r = self.client.post(reverse("catalog:libro_editar", args=[self.libro.pk]),
                             self.datos(titulo="Clean Code", isbn="111", cantidad_total=2))
        self.assertContains(r, "prestados")

    def test_admin_elimina_libro(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("catalog:libro_eliminar", args=[self.libro.pk]))
        self.assertFalse(Libro.objects.filter(pk=self.libro.pk).exists())

    def test_bibliotecario_y_usuario_no_pueden_modificar_catalogo(self):
        for usuario in (self.biblio, self.alumno):
            self.client.force_login(usuario)
            self.assertEqual(self.client.get(reverse("catalog:libro_crear")).status_code, 403)
            self.assertEqual(self.client.post(reverse("catalog:libro_eliminar", args=[self.libro.pk])).status_code, 403)
        self.assertTrue(Libro.objects.filter(pk=self.libro.pk).exists())

    def test_categoria_con_libros_no_se_elimina(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("catalog:categoria_eliminar", args=[self.cat_prog.pk]))
        self.assertTrue(Categoria.objects.filter(pk=self.cat_prog.pk).exists())
