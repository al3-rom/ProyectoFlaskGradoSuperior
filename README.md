# Proyecto_Flask_GradoSuperior
# Proyecto 1
**Versión 0.3**

🏪 Descripción del Proyecto

Wannapop - es una aplicación web inspirada en Wallapop, desarrollada como trabajo académico para el Ciclo Formativo de Grado Superior.
El objetivo principal es construir una plataforma de compraventa de productos de segunda mano, donde los usuarios puedan registrarse, publicar anuncios, gestionar sus productos, todo dentro de un entorno moderno y seguro.

El proyecto está desarrollado con Flask (Python) como framework principal, e implementa una arquitectura modular con MVC, soporte para bases de datos SQL (SQLite, MySQL, PostgreSQL) y compatibilidad con Docker para su despliegue.

✨ Características principales

🔐 Sistema de registro, login y roles de usuario (comprador / vendedor / admin / moderator)

📸 Publicación de productos con imágenes, precios y descripciones

🔎 Buscador y filtros dinámicos por categoría o palabra clave

📊 Panel de administración para gestionar usuarios y productos

🧱 Arquitectura escalable con SQLAlchemy y Blueprints

🐳 Compatibilidad con Docker (MySQL / PostgreSQL)

💾 Versión local con SQLite para desarrollo rápido


---

## 🧰 Requisitos

* **Python 3.12+** (recomendado)
* **pip** (incluido con Python)
* **Git**
* **Docker** (opcional, para usar MySQL o Postgres contenerizado)

---

## He creado 2 usuarios de prueba:

Admin223@gmail.com - Usuario con role 'Admin' (Admin)
User223@gmail.com - Usuarior con role 'Wanner' (Usuario normal)

Contraseña: 321321321 para ambos.


## 🐍 Paso 1: Crear el entorno virtual `.venv`

```bash
# macOS / Linux
python -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\activate
````

Para salir del entorno virtual:

```bash
deactivate
```

---

## 📦 Paso 2: Instalar dependencias

Con el entorno virtual **activado**:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

# !!! Haciamos con Docker pero os dejo solo con la base de datos local !!!   (SQLite)

## 🐳 Paso 3: Ejecutar con Docker (opcional)

Para ejecutar Flask contenerizado con **MySQL**:

1. Mover todo el contenido de la carpeta `docker_mysql` al **root** del proyecto.
2. Configurar la variable `DATABASE_URI` en el archivo `.env`.

   * En `env.example` hay un ejemplo para MySQL con Docker.
3. Ejecutar:

```bash
docker-compose up
```

---

## Docker PostgreSQL
Para ejecutar Flask contenerizado con **PostgreSQL**:

1. Necesitas sacar docker-compose.yml, DockerFile a raiz del proeycto desde la carpeta docker_postgres

2. Debes entrar en config.py y encontrar esa linia:

SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URI") <-- cambiar "DATABASE_URI" si quieres usar `Aiven`. Si quieres usar docker a "DATABASE_URL"
Si quieres usar sqlite - deja como esta ahora (SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(os.path.dirname(__file__), "sqlite", "database.db"))

en .env poner la linea de `DATABASE_URI` como un comentario # y dejar la siguiente linia:
DATABASE_URL=postgresql+psycopg2://app:app@localhost:5432/mydatabase
```bash
docker-compose up
```

---

## 🛠 Carpeta `Tools`

En esta carpeta se encuentra script de Python para:

* Migrar bases de datos **SQLite** a **MySQL**

---

## 📂 Estructura del proyecto

```
2526-projecte-1-equip_07/
│
├─ docker_mysql/           # Archivos de Docker para MySQL
├─ docker_postgres/        # Archivos de Docker para Postgres
├─ docs/                   # Mapa de sitio + Diagrama de roles y permisos
├─ sqlite/                 # Base de datos inicial + extras
├─ tools/                  # Script de migración de SQLite a MySQL
├─ wannapop/               # Carpeta principal de la app
├─ .env.example            # Ejemplo de configuración de variables de entorno
├─ app.py                  # Archivo principal para iniciar app Flask
├─ config.py               # Archivo de config de la app Flask
├─ README.md               # Documentación del proyecto
└─ requirements.txt        # Dependencias del proyecto
```

---

## 🚀 Uso del proyecto

Con el entorno virtual activado, ejecutar la aplicación:

```bash
python app.py
```

Acceder en el navegador a:

```
http://127.0.0.1:5000/
```

Si se usa **Docker**, después de `docker-compose up` la aplicación estará disponible en el mismo puerto configurado en `docker-compose.yml`.

---

## 🤝 Contribución

1. Hacer un fork del proyecto
2. Crear una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Hacer commit de los cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Hacer push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir un Pull Request

---

## 👥 Autores

* **Nikita Rodionov**
* **Alejandro Romero Stankevich**
