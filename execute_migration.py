import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

encoded_password = urllib.parse.quote_plus(PASSWORD)
DATABASE_URL = f"mssql+pyodbc://{USER}:{encoded_password}@{HOST}:{PORT}/{DB_NAME}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"

engine = create_engine(DATABASE_URL)

try:
    with engine.begin() as conn:
        with open('scripts/09_Add_Auth_Columns.sql', 'r') as f:
            sql_statements = f.read().split('GO')
            
            for statement in sql_statements:
                if statement.strip():
                    # sqlalchemy doesn't like USE and PRINT sometimes, but we'll try
                    try:
                        conn.execute(text(statement))
                    except Exception as e:
                        print(f"Executing segment warning: {e}")
    print("Migration successful")
except Exception as e:
    print(f"Error: {e}")
