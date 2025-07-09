#folhasassiduidade.py

import os
from Folhas_Assiduidade.visualizador_fa import VisualizadorFolhasAssiduidade
from core.processador_base import processar_documentos
from core.logger import configurar_logger
logger = configurar_logger(__name__)

def folhasassiduidade():
    """
    Função principal para processar documentos na pasta de Folhas de Assiduidade.
    - Define o diretório base como o diretório atual do ficheiro.
    - Chama a função de processamento genérico.
    """
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logger.info(f"Iniciando processamento de folhas de assiduidade em: {base_dir}")
        processar_documentos(base_dir, VisualizadorFolhasAssiduidade)
    except Exception as e:
        logger.exception("Erro ao processar folhas de assiduidade:")

if __name__ == "__main__":
    folhasassiduidade()