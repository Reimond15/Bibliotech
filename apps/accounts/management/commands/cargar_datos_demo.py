"""Carga datos de ejemplo: membresías, un usuario por rol, categorías y libros."""

from django.core.management.base import BaseCommand

from apps.accounts.models import Membresia, Usuario
from apps.catalog.models import Categoria, Libro

CLAVE_DEMO = "Biblio2026!"

CATEGORIAS = ["Programación", "Bases de datos", "Redes", "Literatura", "Matemáticas"]

LIBROS = [
    ("Clean Code", "Robert C. Martin", "9780132350884", "Programación", 3),
    ("Fluent Python", "Luciano Ramalho", "9781492056355", "Programación", 2),
    ("Database System Concepts", "Silberschatz, Korth", "9780078022159", "Bases de datos", 2),
    ("Redes de Computadoras", "Andrew S. Tanenbaum", "9786073205825", "Redes", 4),
    ("Cien años de soledad", "Gabriel García Márquez", "9780307474728", "Literatura", 5),
    ("Cálculo", "James Stewart", "9786075266183", "Matemáticas", 1),
]


class Command(BaseCommand):
    help = "Crea datos de demostración (usuarios admin, biblio y estudiante + catálogo)."

    def handle(self, *args, **options):
        estudiante, _ = Membresia.objects.get_or_create(
            tipo="Estudiante", defaults={"dias_prestamo": 7, "max_prestamos": 3}
        )
        Membresia.objects.get_or_create(tipo="Docente", defaults={"dias_prestamo": 15, "max_prestamos": 5})

        cuentas = [
            ("admin", "Administrador", "BiblioTech", Usuario.Rol.ADMINISTRADOR, None),
            ("biblio", "Bibliotecaria", "Demo", Usuario.Rol.BIBLIOTECARIO, None),
            ("estudiante", "Estudiante", "Demo", Usuario.Rol.USUARIO, estudiante),
        ]
        for username, nombre, apellido, rol, membresia in cuentas:
            usuario, creado = Usuario.objects.get_or_create(
                username=username,
                defaults={"first_name": nombre, "last_name": apellido, "rol": rol, "membresia": membresia},
            )
            if creado:
                usuario.set_password(CLAVE_DEMO)
                usuario.save()
                self.stdout.write(f"Usuario creado: {username}")

        categorias = {nombre: Categoria.objects.get_or_create(nombre=nombre)[0] for nombre in CATEGORIAS}
        for titulo, autor, isbn, categoria, cantidad in LIBROS:
            Libro.objects.get_or_create(
                isbn=isbn,
                defaults={
                    "titulo": titulo,
                    "autor": autor,
                    "categoria": categorias[categoria],
                    "cantidad_total": cantidad,
                    "cantidad_disponible": cantidad,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Listo. Contraseña de las cuentas demo: {CLAVE_DEMO}"))
