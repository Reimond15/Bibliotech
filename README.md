# BiblioTech — Sistema de Gestión de Biblioteca Digital

Proyecto de Programación 3 · Entregable 3 (Avance funcional)

**Integrante:** Reimond Peña · **Matrícula:** 2022-1749 · **Carrera:** Desarrollo de Software

BiblioTech digitaliza el control de una biblioteca escolar: catálogo de libros, usuarios con roles,
préstamos, devoluciones y reportes. Este avance implementa **dos módulos funcionando** sobre una base
de datos real:

| Módulo | Qué incluye | Requisitos que cubre |
| --- | --- | --- |
| **Autenticación y usuarios** (`apps/accounts`) | Inicio y cierre de sesión, tres roles (administrador, bibliotecario, usuario), registro, edición, búsqueda y activación/desactivación de usuarios, membresías, control de acceso por rol | RF-01, RF-04, RF-11, seguridad |
| **Catálogo de libros** (`apps/catalog`) | Registro, edición y eliminación de libros, categorías, buscador por título, autor, ISBN, categoría y disponibilidad | RF-02, RF-03, RF-05 |

Pendiente para los siguientes entregables: préstamos y devoluciones (RF-06 a RF-08, RF-12),
notificaciones (RF-09) y reportes (RF-10).

## Tecnologías

- Python 3.12 o superior
- Django 6 (arquitectura monolito en capas)
- SQLite (archivo `db.sqlite3`, se crea al migrar; se puede cambiar a PostgreSQL en `config/settings.py`)

## Instalación y ejecución

```bash
# 1. Clonar el repositorio y entrar a la carpeta
git clone <URL-DEL-REPOSITORIO>
cd bibliotech

# 2. Crear y activar un entorno virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear la base de datos (conexión a SQLite)
python manage.py migrate

# 5. Cargar datos de ejemplo (usuarios y libros)
python manage.py cargar_datos_demo

# 6. Iniciar el servidor
python manage.py runserver
```

Abrir <http://127.0.0.1:8000/> en el navegador.

### Cuentas de prueba

Todas usan la contraseña `Biblio2026!`.

| Usuario | Rol | Qué puede hacer |
| --- | --- | --- |
| `admin` | Administrador | Todo: usuarios, categorías y catálogo |
| `biblio` | Bibliotecario | Buscar libros (los préstamos llegan en el siguiente entregable) |
| `estudiante` | Usuario | Buscar libros |

Para entrar al panel de Django (`/admin/`) crea un superusuario con `python manage.py createsuperuser`.

## Pruebas

```bash
python manage.py test
```

Hay 23 pruebas automáticas: inicio de sesión, contraseñas con hash, permisos por rol, gestión de
usuarios, búsqueda y CRUD del catálogo, reglas de inventario.

## Estructura del proyecto

```
bibliotech/
├── manage.py
├── requirements.txt
├── config/                  # Configuración del proyecto (settings, urls)
├── apps/
│   ├── accounts/            # Módulo 1: autenticación y usuarios
│   │   ├── models.py        #   Capa de datos: Usuario, Membresia
│   │   ├── services.py      #   Capa de negocio: búsqueda, activar/desactivar
│   │   ├── permissions.py   #   Control de acceso por rol
│   │   ├── forms.py         #   Validación de formularios
│   │   ├── views.py / urls.py   # Capa de presentación
│   │   ├── templates/accounts/
│   │   └── management/commands/cargar_datos_demo.py
│   └── catalog/             # Módulo 2: catálogo de libros
│       ├── models.py        #   Categoria, Libro
│       ├── services.py     #   Búsqueda e inventario
│       ├── forms.py, views.py, urls.py
│       └── templates/catalog/
├── templates/               # Plantilla base, inicio, 403, paginación
└── static/css/              # Estilos
```

Cada módulo separa **modelos** (datos), **servicios** (reglas de negocio), **formularios**
(validación) y **vistas/plantillas** (presentación), siguiendo la arquitectura en capas del diseño.

## Reglas de negocio implementadas

- Las contraseñas se guardan con hash; nunca en texto plano.
- Los usuarios finales deben tener una membresía; el personal no.
- Un administrador no puede desactivar su propia cuenta; una cuenta desactivada no inicia sesión.
- El ISBN es único. Al registrar un libro, todos los ejemplares quedan disponibles.
- Si se cambia la cantidad de ejemplares de un libro, los disponibles se ajustan y el total nunca
  puede ser menor que los ejemplares prestados.
- Una categoría con libros no se puede eliminar.
- Solo el administrador modifica el catálogo; los tres roles pueden buscar libros.

## Documentación de diseño

Arquitectura, casos de uso, diagrama de clases, secuencia, DER, modelo relacional y wireframes
están en el documento «BiblioTech: Diseño técnico del sistema».
