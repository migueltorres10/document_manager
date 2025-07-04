import os
from Faturas.visualizador_faturas import VisualizadorFaturas
from core.processador_base import processar_documentos

def faturas():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    processar_documentos(base_dir, VisualizadorFaturas)

if __name__ == "__main__":
    faturas()
