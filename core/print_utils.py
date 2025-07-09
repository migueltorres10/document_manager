## print_utils.py

import os
import subprocess
from config import LIBREOFFICE_PATH, SUMATRA_PATH
from core.logger import configurar_logger

logger = configurar_logger(__name__)


def converter_para_pdf(ficheiro_excel):
    """
    Converte um ficheiro Excel para PDF usando o LibreOffice em modo headless.

    Args:
        ficheiro_excel (str): Caminho do ficheiro Excel (.xlsx, .xls, etc.).

    Returns:
        str | None: Caminho do PDF convertido ou None em caso de erro.
    """
    try:
        subprocess.run([
            LIBREOFFICE_PATH,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", os.path.dirname(ficheiro_excel),
            ficheiro_excel
        ], check=True)

        pdf_path = os.path.splitext(ficheiro_excel)[0] + ".pdf"
        if os.path.exists(pdf_path):
            logger.info(f"Conversão bem-sucedida: {pdf_path}")
            return pdf_path
        else:
            logger.error("Conversão falhou: PDF não encontrado.")
            return None

    except subprocess.CalledProcessError as e:
        logger.error(f"Erro na conversão para PDF (LibreOffice): {e}")
    except Exception as e:
        logger.exception(f"Falha inesperada ao converter para PDF: {e}")
    return None


def imprimir_pdf_no_windows(caminho_pdf, copias=1):
    """
    Imprime um ficheiro PDF usando o SumatraPDF no Windows.

    Args:
        caminho_pdf (str): Caminho do ficheiro PDF.
        copias (int): Número de cópias a imprimir.

    Returns:
        None
    """
    if not os.path.exists(caminho_pdf):
        logger.error(f"PDF não encontrado: {caminho_pdf}")
        return

    try:
        for i in range(copias):
            logger.info(f"A imprimir cópia {i + 1} de {copias} via SumatraPDF...")
            subprocess.run([
                SUMATRA_PATH,
                "-print-to-default",
                "-silent",
                caminho_pdf
            ], check=True)

        logger.info(f"{copias} cópia(s) enviada(s) para impressão com sucesso.")

    except subprocess.CalledProcessError as e:
        logger.error(f"SumatraPDF falhou ao imprimir: {e}")
    except Exception as e:
        logger.exception(f"Erro inesperado durante a impressão: {e}")


