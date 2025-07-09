from dotenv import load_dotenv
import os
import pyodbc
from core.logger import configurar_logger
# Configuração do logger
logger = configurar_logger(__name__)

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def connect_bd(initial):
    """
    Conecta-se à base de dados usando variáveis de ambiente com prefixo.

    Args:
        initial (str): Prefixo ('D' ou 'S') para as variáveis de ambiente.

    Returns:
        pyodbc.Connection: Objeto de conexão à base de dados.

    Raises:
        EnvironmentError: Se alguma variável necessária estiver ausente.
        pyodbc.Error: Se a conexão falhar.
    """
    driver = os.getenv(f"{initial}_DB_DRIVER")
    server = os.getenv(f"{initial}_DB_SERVER")
    database = os.getenv(f"{initial}_DB_DATABASE")
    user = os.getenv(f"{initial}_DB_USER")
    pwd = os.getenv(f"{initial}_DB_PASSWORD")

    if not all([driver, server, database, user, pwd]):
        logger.error(f"Variáveis de ambiente incompletas para o prefixo '{initial}'")
        raise EnvironmentError(f"❌ Variáveis de ambiente incompletas para o prefixo '{initial}'")

    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={pwd};"
    )

    return pyodbc.connect(conn_str)


# Caminhos para dependências externas
POPPLER_PATH = os.getenv("POPPLER_PATH")
TESSERACT_CMD = os.getenv("TESSERACT_CMD")
SUMATRA_PATH = os.getenv("SUMATRA_PATH")
NAPS2_PATH = os.getenv("NAPS2_PATH")
LIBREOFFICE_PATH = os.getenv("LIBREOFFICE_PATH")
HP_SCAN_EXECUTABLE = os.getenv("HPSCANNER_PATH")

# Validação de caminhos externos importantes
for var_name, path in {
    "POPPLER_PATH": POPPLER_PATH,
    "TESSERACT_CMD": TESSERACT_CMD,
    "SUMATRA_PATH": SUMATRA_PATH,
    #"NAPS2_PATH": NAPS2_PATH,
    "LIBREOFFICE_PATH": LIBREOFFICE_PATH,
    "HPSCANNER_PATH": HP_SCAN_EXECUTABLE
}.items():
    if not path or not os.path.exists(path):
        logger.warning(f"[AVISO] {var_name} não está definido ou caminho é inválido: {path}")


# Teste de conexão (executado apenas se correr como script principal)
if __name__ == "__main__":
    try:
        conn_forn = connect_bd("S")
        conn_docs = connect_bd("D")
        logger.info("✅ Ambas as conexões foram estabelecidas com sucesso.")
        conn_forn.close()
        conn_docs.close()
    except Exception as e:
        logger.exception("❌ Erro ao conectar às bases de dados:")
