# SICC - Sistema de Gestión de Incidentes de Ciberseguridad

Este proyecto es una API en **FastAPI** para la gestión de incidentes de ciberseguridad, conectada a una base de datos **Microsoft SQL Server** (usualmente alojada en Docker) mediante ODBC y SQLAlchemy.

## 🚀 Requisitos Previos

Dado que este proyecto utiliza `pyodbc` para conectarse a SQL Server, es obligatorio instalar los controladores ODBC a nivel de sistema operativo antes de instalar las dependencias de Python.

### 🐧 Instalación de Controladores ODBC (Linux)

#### Para Fedora (y derivados de RHEL)

1. Instalar el Driver Manager base (`unixODBC`):

   ```bash
   sudo dnf install unixODBC unixODBC-devel
   ```

2. Instalar el Driver oficial de Microsoft para SQL Server (`msodbcsql18`):

   ```bash
   sudo curl -o /etc/yum.repos.d/mssql-release.repo https://packages.microsoft.com/config/rhel/9/prod.repo
   sudo dnf install -y msodbcsql18
   ```

#### Para Arch Linux (y derivados como Manjaro/EndeavourOS)

1. Instalar el Driver Manager desde los repositorios oficiales:

   ```bash
   sudo pacman -S unixodbc
   ```

2. Instalar el Driver oficial de Microsoft desde el AUR (usando `yay` o `paru`):

   ```bash
   yay -S msodbcsql18
   ```

*(Nota: Durante la instalación del driver de Microsoft, se te pedirá aceptar los términos de la licencia).*

---

## 🛠️ Instalación del Proyecto

1. **Clonar el repositorio y entrar en la carpeta:**

   ```bash
   git clone git@github.com:Kevin07k/SICC_proyect.git
   cd SICC_proyect
   ```

2. **Crear y activar un entorno virtual:**

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Instalar las dependencias de Python:**

   ```bash
   pip install -r requirements.txt
   ```

   *(Asegúrate de tener FastAPI, Uvicorn, SQLAlchemy, pyodbc, etc. instalados).*

4. **Configurar las variables de entorno:**
   Crea un archivo `.env` en la raíz del proyecto basándote en un archivo de ejemplo (`.env.example` si existe) con los datos de tu conexión a la base de datos:

   ```env
   DB_USER=sa
   DB_PASSWORD=TuPassword123
   DB_HOST=127.0.0.1
   DB_PORT=1433
   DB_NAME=DB_GestionIncidentes
   ```

---

## 🗄️ Inicialización de Base de Datos

Antes de encender la API, debes crear la base de datos y sus tablas en tu instancia de SQL Server usando los scripts proporcionados en la carpeta `scripts/`.

1. Conéctate a tu contenedor de SQL Server a través de un gestor como Azure Data Studio, DBeaver o la extensión de SQL Server en VS Code.
2. Ejecuta primero **`scripts/DataBase.sql`** (Este script hace un Clean Install, creando la DB y las tablas).
3. (Opcional) Ejecuta **`scripts/Data_DataBase.sql`** si deseas poblar la base de datos con datos y registros de prueba para el Dashboard.

---

## 🔥 Ejecución del Servidor

Para levantar la API en modo de desarrollo local (con recarga automática de cambios):

```bash
fastapi dev app/main.py
```

El servidor iniciará la aplicación en:

- **API URL:** `http://127.0.0.1:8000`
- **Documentación Swagger UI:** `http://127.0.0.1:8000/docs`
- **Documentación ReDoc:** `http://127.0.0.1:8000/redoc`

*(Nota: En producción debes utilizar `fastapi run app/main.py` para un mejor rendimiento).*
