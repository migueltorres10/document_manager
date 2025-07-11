# core/pdf_utils.py

import os
import subprocess
from config import SUMATRA_PATH
import fitz
import tempfile
import shutil
from core.logger import configurar_logger
logger = configurar_logger(__name__)


def listar_pdfs(pasta):
    """
    Lista todos os arquivos PDF em uma pasta.

    Args:
        pasta (str): Caminho da pasta a ser listada.

    Returns:
        list[str]: Lista de nomes de arquivos PDF encontrados.
    """
    try:
        return [f for f in os.listdir(pasta) if f.lower().endswith(".pdf")]
    except FileNotFoundError:
        logger.error(f"Pasta não encontrada: {pasta}")
        return []
    except Exception as e:
        logger.exception(f"Erro ao listar PDFs na pasta '{pasta}': {e}")
        return []


def abrir_pdf_externo(caminho_pdf):
    """
    Abre um ficheiro PDF com o SumatraPDF.

    Args:
        caminho_pdf (str): Caminho para o ficheiro PDF.

    Returns:
        None
    """
    try:
        subprocess.Popen(
            [SUMATRA_PATH, "-reuse-instance", "-fullscreen", caminho_pdf],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        logger.info(f"PDF aberto com Sumatra: {caminho_pdf}")
    except Exception as e:
        logger.exception(f"Erro ao abrir PDF com Sumatra: {e}")
        raise


def fechar_sumatra():
    """
    Fecha todas as instâncias do SumatraPDF.

    Returns:
        None
    """
    try:
        subprocess.run(
            ["taskkill", "/IM", "SumatraPDF.exe", "/F"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        logger.info("SumatraPDF encerrado.")
    except Exception as e:
        logger.exception(f"Erro ao fechar SumatraPDF: {e}")


def rodar_pdf_90graus(input_path):
    """
    Roda todas as páginas de um PDF em 90 graus no sentido horário.

    Args:
        input_path (str): Caminho do ficheiro PDF a ser rotacionado.

    Returns:
        None

    Raises:
        Exception: Se ocorrer erro na leitura, escrita ou substituição do PDF.
    """
    try:
        doc = fitz.open(input_path)

        for page in doc:
            page.set_rotation((page.rotation + 90) % 360)

        # Criar ficheiro temporário seguro
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            temp_path = tmp.name

        doc.save(temp_path)
        doc.close()

        # Substituir o original
        shutil.move(temp_path, input_path)
        logger.info(f"PDF rotacionado com sucesso: {input_path}")
    except Exception as e:
        logger.exception(f"Erro ao rodar PDF: {e}")
        raise

def juntar_pdfs_em_posicao(pdf_base, pdf_a_adicionar, destino=None, pagina_destino=-1):
    """
    Junta páginas de um PDF a outro PDF base, na posição desejada.
    Se não for passado destino, o ficheiro original é substituído com segurança.
    """
    try:
        doc_base = fitz.open(pdf_base)
        doc_novo = fitz.open(pdf_a_adicionar)

        doc_base.insert_pdf(doc_novo, start_at=pagina_destino)

        if not destino or destino == pdf_base:
            # Cria ficheiro temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                temp_path = tmp.name
            doc_base.save(temp_path)
            doc_base.close()
            doc_novo.close()
            shutil.move(temp_path, pdf_base)
            return pdf_base
        else:
            doc_base.save(destino)
            return destino

    except Exception as e:
        raise RuntimeError(f"Erro ao juntar PDFs: {e}")
    finally:
        if not doc_base.is_closed:
            doc_base.close()
        if not doc_novo.is_closed:
            doc_novo.close()



