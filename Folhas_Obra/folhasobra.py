#folhasobra.py

import os
from Folhas_Obra.visualizador_fo import VisualizadorFolhasObra
from core.processador_base import processar_documentos

def folhasobra():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    processar_documentos(base_dir, VisualizadorFolhasObra)

if __name__ == "__main__":
    folhasobra()