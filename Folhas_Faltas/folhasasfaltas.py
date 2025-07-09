## folhas_faltas/folhasfaltas.py

import os
from Folhas_Faltas.visualizador_ff import VisualizadorFolhasFaltas
from core.processador_base import processar_documentos
from core.logger import configurar_logger
logger = configurar_logger(__name__)

def folhasfaltas():
    """
    Função principal para processar documentos na pasta de Folhas de Faltas.
    - Define o diretório base como o diretório atual do ficheiro.
    - Chama a função de processamento genérico.
    """
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logger.info(f"Iniciando processamento de folhas de faltas em: {base_dir}")
        processar_documentos(base_dir, VisualizadorFolhasFaltas)
    except Exception as e:
        logger.exception("Erro ao processar folhas de faltas:")
        
if __name__ == "__main__":
    folhasfaltas()