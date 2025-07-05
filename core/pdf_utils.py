# core/pdf_utils.py
import os
import subprocess
from config import SUMATRA_PATH


def listar_pdfs(pasta):
    try:
        return [f for f in os.listdir(pasta) if f.lower().endswith(".pdf")]
    except FileNotFoundError:
        print("❌ Pasta não encontrada:", pasta)
        return []


def abrir_pdf_externo(caminho_pdf):
    try:
        subprocess.Popen([SUMATRA_PATH, "-reuse-instance", caminho_pdf],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Erro ao abrir PDF com Sumatra: {e}")
        raise


def fechar_sumatra():
    try:
        subprocess.run(["taskkill", "/IM", "SumatraPDF.exe", "/F"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Erro ao fechar SumatraPDF: {e}")
