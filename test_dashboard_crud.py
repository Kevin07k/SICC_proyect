import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import urllib.parse
from app.crud import dashboard as crud

load_dotenv()

USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT", "1434")
DB_NAME = os.getenv("DB_NAME")

encoded_password = urllib.parse.quote_plus(PASSWORD)
DATABASE_URL = (
    f"mssql+pyodbc://{USER}:{encoded_password}@{HOST}:{PORT}/{DB_NAME}"
    f"?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Encrypt=no"
)

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        print("Testing get_conteo_incidentes_por_tipo...")
        res1 = crud.get_conteo_incidentes_por_tipo(conn)
        print(f"Result: {res1}")

        print("\nTesting get_conteo_incidentes_por_prioridad...")
        res2 = crud.get_conteo_incidentes_por_prioridad(conn)
        print(f"Result: {res2}")

        print("\nTesting get_conteo_incidentes_criticos...")
        res3 = crud.get_conteo_incidentes_criticos(conn)
        print(f"Result: {res3}")
        
    print("\nAll CRUD tests passed!")
except Exception as e:
    print(f"\nError during tests: {e}")
    import traceback
    traceback.print_exc()
