#folhasassiduidade.py

import os
from Folhas_Assiduidade.visualizador_fa import VisualizadorFolhasAssiduidade
from core.processador_base import processar_documentos

def folhasassiduidade():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    processar_documentos(base_dir, VisualizadorFolhasAssiduidade)

if __name__ == "__main__":
    folhasassiduidade()