import os
import re
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

encoded_password = urllib.parse.quote_plus(PASSWORD)
DATABASE_URL = (
    f"mssql+pyodbc://{USER}:{encoded_password}@{HOST}:{PORT}/{DB_NAME}"
    f"?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Encrypt=no"
)

engine = create_engine(DATABASE_URL).execution_options(isolation_level="AUTOCOMMIT")

scripts = [
    "01_Estructura_Tablas.sql",
    "02_Catalogos_Iniciales.sql",
    "03_Vistas.sql",
    "04_Procedimientos.sql",
    "05_Triggers.sql",
    "06_Indices.sql",
    "07_Mock_Data.sql",
    "08_Seguridad_Roles_Permisos.sql",
    "09_Add_Auth_Columns.sql"
]

def run_script(filename):
    path = os.path.join("scripts", filename)
    print(f"Executing {filename}...")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Split by GO statement (case insensitive)
    batches = re.split(r'(?i)^\s*GO\s*$', content, flags=re.MULTILINE)
    
    with engine.connect() as conn:
        for batch in batches:
            if batch.strip():
                try:
                    conn.execute(text(batch))
                except Exception as e:
                    print(f"Error in {filename} batch: {e}")
                    # Continue with other batches/scripts if possible

if __name__ == "__main__":
    for script in scripts:
        run_script(script)
    print("All scripts executed.")
