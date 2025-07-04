from dotenv import load_dotenv
import os
import pyodbc

load_dotenv()

def connect_bd(initial):
    driver = os.getenv(f"{initial}_DB_DRIVER")
    server = os.getenv(f"{initial}_DB_SERVER")
    database = os.getenv(f"{initial}_DB_DATABASE")
    user = os.getenv(f"{initial}_DB_USER")
    pwd = os.getenv(f"{initial}_DB_PASSWORD")

    if not all([driver, server, database, user, pwd]):
        raise EnvironmentError(f"❌ Variáveis de ambiente incompletas para o prefixo '{initial}'")
                               
    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={pwd};"
    )

    return pyodbc.connect(conn_str)

# Caminhos de dependências externas (.env)
POPPLER_PATH = os.getenv("POPPLER_PATH")
TESSERACT_CMD = os.getenv("TESSERACT_CMD")
SUMATRA_PATH = os.getenv("SUMATRA_PATH")

try:
    conn_forn = connect_bd("S")
    conn_docs = connect_bd("D")
    print("✅ Ambas as conexões foram estabelecidas com sucesso.")
except Exception as e:
    print("❌ Erro ao conectar:", e)
