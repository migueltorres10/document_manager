## Guias/guias.py

import os
from Guias.visualizador_guias import VisualizadorGuias
from core.processador_base import processar_documentos
from core.logger import configurar_logger
logger = configurar_logger(__name__)

def guias():
    """
    Função principal para processar documentos na pasta de Guias.
    - Define o diretório base como o diretório atual do ficheiro.
    - Chama a função de processamento genérico.
    """
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logger.info(f"Iniciando processamento de guias em: {base_dir}")
        processar_documentos(base_dir, VisualizadorGuias)
    except Exception as e:
        logger.exception("Erro ao processar guias:")

if __name__ == "__main__":
    guias()
