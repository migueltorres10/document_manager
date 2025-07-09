#folhasfaltas.py

import os
from Folhas_Faltas.visualizador_ff import VisualizadorFolhasFaltas
from core.processador_base import processar_documentos

def folhasfaltas():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    processar_documentos(base_dir, VisualizadorFolhasFaltas)

if __name__ == "__main__":
    folhasfaltas()