## Faturas/faturas.py

import os
from Faturas.visualizador_faturas import VisualizadorFaturas
from core.processador_base import processar_documentos
from core.logger import configurar_logger
logger = configurar_logger(__name__)

def faturas():
    """
    Função principal para processar documentos na pasta de Faturas.
    - Define o diretório base como o diretório atual do ficheiro.
    - Chama a função de processamento genérico.
    """
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logger.info(f"Iniciando processamento de faturas em: {base_dir}")
        processar_documentos(base_dir, VisualizadorFaturas)
    except Exception as e:
        logger.exception("Erro ao processar faturas:")

if __name__ == "__main__":
    faturas()
