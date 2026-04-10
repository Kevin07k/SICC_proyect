import os
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

print(f"Connecting to: {HOST}:{PORT}/{DB_NAME}")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT COUNT(*) FROM information_schema.tables"))
        count = result.scalar()
        print(f"Success! Database has {count} tables.")
except Exception as e:
    print(f"Error connecting to database: {e}")
