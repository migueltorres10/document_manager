import os
from Guias.visualizador_guias import VisualizadorGuias
from core.processador_base import processar_documentos

def guias():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    processar_documentos(base_dir, VisualizadorGuias)

if __name__ == "__main__":
    guias()
