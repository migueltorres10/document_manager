#folhasobra.py

import os
from Folhas_Obra.visualizador_fo import VisualizadorFolhasObra
from core.processador_base import processar_documentos
from core.logger import configurar_logger
logger = configurar_logger(__name__)

def folhasobra():
    """
    Função principal para processar documentos na pasta de Folhas de Obra.
    - Define o diretório base como o diretório atual do ficheiro.
    - Chama a função de processamento genérico.
    """
    try:
        logger.info("Iniciando processamento de folhas de obra.")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        processar_documentos(base_dir, VisualizadorFolhasObra)
    except Exception as e:
        logger.exception("Erro ao processar folhas de obra:")

if __name__ == "__main__":
    folhasobra()