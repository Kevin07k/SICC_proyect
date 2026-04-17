import os
import urllib.parse # Importante para codificar la contraseña
from dotenv import load_dotenv
from sqlalchemy import create_engine

# --- 1. Cargar Variables de Entorno ---
load_dotenv()

# --- 2. Obtener Datos de Conexión ---
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Verificación
if not all([USER, PASSWORD, HOST, PORT, DB_NAME]):
    raise ValueError("¡Faltan una o más variables de entorno de la base de datos en el archivo .env!")

# --- 3. Codificar la contraseña ---

encoded_password = urllib.parse.quote_plus(PASSWORD)

# --- 4. Construir la URL de Conexión ---
DATABASE_URL = (
    f"mssql+pyodbc://{USER}:{encoded_password}@{HOST}:{PORT}/{DB_NAME}"
    f"?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Encrypt=no"
)

# --- 5. Crear el Motor (Engine) ---
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

# --- 6. Crear la Sesión ---
#SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)

# --- 7. Dependencia de FastAPI (get_session) ---
def get_session():
    connection = engine.connect()
    # db = SessionLocal()
    try:
        yield connection
    finally:
        connection.close()