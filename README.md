# 🛡️ SICC — Sistema de Gestión de Incidentes de Ciberseguridad

Sistema web para la gestión integral de incidentes de ciberseguridad, construido con **FastAPI**, **Jinja2**, **SQL Server** (Docker) y control de acceso basado en roles (DBA, Gerente, Vendedor).

---

## 📋 Tabla de Contenidos

- [Requisitos Previos](#-requisitos-previos)
- [Instalación Paso a Paso](#-instalación-paso-a-paso)
  - [Paso 1 — Instalar Controladores ODBC](#paso-1--instalar-controladores-odbc)
  - [Paso 2 — Crear el Contenedor de SQL Server](#paso-2--crear-el-contenedor-de-sql-server)
  - [Paso 3 — Crear la Base de Datos](#paso-3--crear-la-base-de-datos)
  - [Paso 4 — Clonar el Repositorio](#paso-4--clonar-el-repositorio)
  - [Paso 5 — Crear el Entorno Virtual](#paso-5--crear-el-entorno-virtual)
  - [Paso 6 — Instalar Dependencias](#paso-6--instalar-dependencias)
  - [Paso 7 — Configurar Variables de Entorno](#paso-7--configurar-variables-de-entorno)
  - [Paso 8 — Inicializar la Base de Datos](#paso-8--inicializar-la-base-de-datos)
  - [Paso 9 — Levantar el Servidor](#paso-9--levantar-el-servidor)
- [Acceso al Sistema](#-acceso-al-sistema)
- [Ejecución Rápida (ya configurado)](#-ejecución-rápida-ya-configurado)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Solución de Errores Comunes](#-solución-de-errores-comunes)

---

## 🚀 Requisitos Previos

| Herramienta | Versión Recomendada | Propósito |
|---|---|---|
| **Docker** | 20.10+ | Contenedor de SQL Server |
| **Python** | 3.10+ | Backend FastAPI |
| **ODBC Driver 18** | Microsoft SQL Server | Conexión Python ↔ SQL Server |
| **Git** | Cualquiera | Clonar el repositorio |

---

## 🛠️ Instalación Paso a Paso

### Paso 1 — Instalar Controladores ODBC

Dado que el proyecto utiliza `pyodbc` para conectarse a SQL Server, es obligatorio instalar los controladores ODBC a nivel de sistema operativo.

<details>
<summary><strong>🐧 Fedora / RHEL</strong></summary>

```bash
# Driver Manager
sudo dnf install unixODBC unixODBC-devel

# Driver de Microsoft
sudo curl -o /etc/yum.repos.d/mssql-release.repo https://packages.microsoft.com/config/rhel/9/prod.repo
sudo dnf install -y msodbcsql18
```
</details>

<details>
<summary><strong>🐧 Ubuntu / Debian</strong></summary>

```bash
# Agregar repositorio de Microsoft
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg
curl -fsSL https://packages.microsoft.com/config/ubuntu/24.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list

# Instalar drivers
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc unixodbc-dev libodbc2 odbcinst
```
</details>

<details>
<summary><strong>🐧 Arch Linux / Manjaro</strong></summary>

```bash
# Driver Manager
sudo pacman -S unixodbc

# Driver de Microsoft (AUR)
yay -S msodbcsql18
```
</details>

---

### Paso 2 — Crear el Contenedor de SQL Server

```bash
docker run -e "ACCEPT_EULA=Y" \
           -e "SA_PASSWORD=Sebas2005" \
           -p 1434:1433 \
           --name sql_server_container \
           -d mcr.microsoft.com/mssql/server:2025-latest
```

> **Nota:** El puerto **1434** del host se mapea al **1433** del contenedor.

Verificar que el contenedor esté corriendo:

```bash
docker ps
```

---

### Paso 3 — Crear la Base de Datos

```bash
docker exec -it sql_server_container /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "Sebas2005" -C \
  -Q "CREATE DATABASE DB_GestionIncidentes;"
```

Verificar que se creó correctamente:

```bash
docker exec -it sql_server_container /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "Sebas2005" -C \
  -Q "SELECT name FROM sys.databases WHERE name = 'DB_GestionIncidentes';"
```

---

### Paso 4 — Clonar el Repositorio

```bash
git clone git@github.com:Kevin07k/SICC_proyect.git
cd SICC_proyect
```

---

### Paso 5 — Crear el Entorno Virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

> 💡 Sabrás que el entorno está activo cuando veas `(venv)` al inicio de tu terminal.

---

### Paso 6 — Instalar Dependencias

```bash
pip install -r requirements.txt
```

Dependencias del proyecto:

| Paquete | Función |
|---|---|
| `fastapi[standard]` | Framework web + servidor de desarrollo (Uvicorn) |
| `sqlmodel` | ORM (SQLAlchemy + Pydantic) |
| `pyodbc` | Driver de conexión a SQL Server |
| `python-dotenv` | Lectura de variables desde `.env` |
| `Jinja2` | Motor de templates HTML |
| `python-multipart` | Manejo de formularios HTTP |

---

### Paso 7 — Configurar Variables de Entorno

Copia el archivo de ejemplo y edítalo:

```bash
cp .env.example .env
```

Contenido del archivo `.env`:

```env
DB_HOST=localhost
DB_PORT=1434
DB_NAME=DB_GestionIncidentes
DB_USER=sa
DB_PASSWORD=Sebas2005
```

---

### Paso 8 — Inicializar la Base de Datos

Ejecuta el script que crea todas las tablas, vistas, procedimientos, triggers, datos y roles:

```bash
python init_db.py
```

Este script ejecuta automáticamente los 8 scripts SQL en orden:

| Orden | Script | Descripción |
|---|---|---|
| 01 | `01_Estructura_Tablas.sql` | Crea el esquema de tablas |
| 02 | `02_Catalogos_Iniciales.sql` | Inserta catálogos (tipos, prioridades, sedes, usuarios) |
| 03 | `03_Vistas.sql` | Genera vistas para dashboard y métricas |
| 04 | `04_Procedimientos.sql` | Procedimientos de borrado, cierre y escalamiento |
| 05 | `05_Triggers.sql` | Triggers de auditoría e historial |
| 06 | `06_Indices.sql` | Índices para optimización de consultas |
| 07 | `07_Mock_Data.sql` | Datos de demostración (registros de prueba) |
| 08 | `08_Seguridad_Roles_Permisos.sql` | Roles y permisos por usuario |

Salida esperada:

```
Executing 01_Estructura_Tablas.sql...
Executing 02_Catalogos_Iniciales.sql...
Executing 03_Vistas.sql...
Executing 04_Procedimientos.sql...
Executing 05_Triggers.sql...
Executing 06_Indices.sql...
Executing 07_Mock_Data.sql...
Executing 08_Seguridad_Roles_Permisos.sql...
All scripts executed.
```

---

### Paso 9 — Levantar el Servidor

```bash
fastapi dev app/main.py
```

Salida esperada:

```
   FastAPI   Starting development server 🚀
    server   Server started at http://127.0.0.1:8000
--- INICIANDO SISTEMA SICC ---
Verificando base de datos...
--- TABLAS LISTAS ---
      INFO   Application startup complete.
```

Endpoints disponibles:

| URL | Descripción |
|---|---|
| `http://127.0.0.1:8000` | Aplicación principal (login) |
| `http://127.0.0.1:8000/docs` | Documentación Swagger UI |
| `http://127.0.0.1:8000/redoc` | Documentación ReDoc |

---

## 🔐 Acceso al Sistema

El sistema implementa 3 roles con diferentes niveles de permisos:

| Rol | Usuario | Contraseña | Permisos |
|---|---|---|---|
| 🔧 **DBA** | `dba` | `dba123` | Control total del sistema |
| 📊 **Gerente** | `gerente` | `gerente123` | Solo consultas y reportes |
| 🛒 **Vendedor** | `vendedor` | `vendedor123` | Insertar y actualizar registros |

---

## ⚡ Ejecución Rápida (ya configurado)

Si ya realizaste la instalación completa y solo necesitas volver a ejecutar el proyecto:

```bash
# 1. Iniciar el contenedor de SQL Server
docker start sql_server_container

# 2. Activar el entorno virtual
source venv/bin/activate

# 3. Levantar el servidor
fastapi dev app/main.py
```

---

## 📁 Estructura del Proyecto

```
SICC_proyect/
├── app/
│   ├── api/                    # Rutas y endpoints
│   │   ├── auth.py             #   └─ Login / logout
│   │   ├── dashboard.py        #   └─ Dashboard principal
│   │   ├── incidentes.py       #   └─ CRUD de incidentes
│   │   ├── activos.py          #   └─ CRUD de activos
│   │   ├── usuarios.py         #   └─ CRUD de usuarios
│   │   ├── sedes.py            #   └─ CRUD de sedes
│   │   ├── bitacora.py         #   └─ Bitácora de auditoría
│   │   └── admin.py            #   └─ Administración
│   ├── core/                   # Configuración central
│   │   ├── auth.py             #   └─ Lógica de autenticación
│   │   ├── database.py         #   └─ Conexión a SQL Server
│   │   └── context.py          #   └─ Contexto de la app
│   ├── crud/                   # Operaciones a la BD
│   │   ├── incidentes.py       #   └─ Queries de incidentes
│   │   ├── activos.py          #   └─ Queries de activos
│   │   ├── usuarios.py         #   └─ Queries de usuarios
│   │   ├── sedes.py            #   └─ Queries de sedes
│   │   ├── categorias.py       #   └─ Queries de categorías
│   │   ├── bitacora.py         #   └─ Queries de bitácora
│   │   └── dashboard.py        #   └─ Queries del dashboard
│   ├── models/                 # Modelos de datos (ORM)
│   ├── schemas/                # Validación de datos (Pydantic)
│   ├── static/                 # Archivos estáticos
│   │   ├── css/                #   └─ Estilos
│   │   ├── js/                 #   └─ JavaScript
│   │   └── img/                #   └─ Imágenes
│   ├── templates/              # Plantillas HTML (Jinja2)
│   │   ├── auth/               #   └─ Login
│   │   ├── incidentes/         #   └─ Vistas de incidentes
│   │   ├── activos/            #   └─ Vistas de activos
│   │   ├── usuarios/           #   └─ Vistas de usuarios
│   │   ├── sedes/              #   └─ Vistas de sedes
│   │   ├── categorias/         #   └─ Vistas de categorías
│   │   ├── base.html           #   └─ Layout base (navbar, sidebar)
│   │   └── index.html          #   └─ Dashboard principal
│   └── main.py                 # Punto de entrada de la aplicación
├── scripts/                    # Scripts SQL
│   ├── 01_Estructura_Tablas.sql
│   ├── 02_Catalogos_Iniciales.sql
│   ├── 03_Vistas.sql
│   ├── 04_Procedimientos.sql
│   ├── 05_Triggers.sql
│   ├── 06_Indices.sql
│   ├── 07_Mock_Data.sql
│   └── 08_Seguridad_Roles_Permisos.sql
├── init_db.py                  # Script de inicialización de BD
├── requirements.txt            # Dependencias de Python
├── .env                        # Variables de entorno (no versionado)
├── .env.example                # Ejemplo de variables de entorno
└── .gitignore
```

---

## 🧰 Tecnologías Utilizadas

| Tecnología | Uso |
|---|---|
| **FastAPI** | Framework web backend |
| **Jinja2** | Motor de templates HTML |
| **SQL Server 2025** | Base de datos relacional |
| **Docker** | Contenedor para SQL Server |
| **SQLAlchemy / SQLModel** | ORM y manejo de conexiones |
| **pyodbc + ODBC Driver 18** | Driver de conexión a SQL Server |
| **TailwindCSS** | Estilos frontend |
| **Python 3.10+** | Lenguaje del backend |

---

## ⚠️ Solución de Errores Comunes

### `[Errno 98] Address already in use` — Puerto 8000 ocupado

```bash
# Matar el proceso que ocupa el puerto
kill -9 $(lsof -ti:8000)

# Volver a levantar
fastapi dev app/main.py
```

### `RuntimeError: install "fastapi[standard]"` — FastAPI no encontrado

```bash
# Asegúrate de estar dentro del entorno virtual
source venv/bin/activate
pip install "fastapi[standard]"
```

### Error de conexión a la base de datos

```bash
# Verificar que el contenedor Docker está corriendo
docker ps

# Si está detenido, iniciarlo
docker start sql_server_container

# Esperar ~10 segundos y reintentar
```

### `ODBC Driver 18 for SQL Server not found`

Instala el driver ODBC siguiendo las instrucciones del [Paso 1](#paso-1--instalar-controladores-odbc) según tu distribución de Linux.

### Recrear la base de datos desde cero

Si necesitas reiniciar completamente la base de datos:

```bash
# Eliminar la BD existente
docker exec -it sql_server_container /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "Sebas2005" -C \
  -Q "DROP DATABASE DB_GestionIncidentes;"

# Volver a crearla
docker exec -it sql_server_container /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "Sebas2005" -C \
  -Q "CREATE DATABASE DB_GestionIncidentes;"

# Ejecutar los scripts
python init_db.py
```

---

## 📄 Licencia

© 2025 SICC Proyect — Todos los derechos reservados.
