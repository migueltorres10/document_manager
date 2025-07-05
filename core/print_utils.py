import os
import subprocess
from config import LIBREOFFICE_PATH, SUMATRA_PATH


def converter_para_pdf(ficheiro_excel):
    try:
        subprocess.run([
            LIBREOFFICE_PATH,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", os.path.dirname(ficheiro_excel),
            ficheiro_excel
        ], check=True)

        pdf_path = os.path.splitext(ficheiro_excel)[0] + ".pdf"
        return pdf_path if os.path.exists(pdf_path) else None

    except Exception as e:
        print(f"[ERRO] Falha ao converter para PDF: {e}")
        return None



def imprimir_pdf_no_windows(caminho_pdf, copias=1):
    if not os.path.exists(caminho_pdf):
        print(f"[ERRO] PDF não encontrado: {caminho_pdf}")
        return

    try:
        for i in range(copias):
            print(f"[INFO] A imprimir cópia {i + 1} de {copias} via SumatraPDF...")
            subprocess.run([
                SUMATRA_PATH,
                "-print-to-default",
                "-silent",
                caminho_pdf
            ], check=True)
        print(f"[OK] {copias} cópia(s) enviada(s) para impressão.")
    except subprocess.CalledProcessError as e:
        print(f"[ERRO] SumatraPDF falhou: {e}")
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")

