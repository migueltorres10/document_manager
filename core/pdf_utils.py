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
    Junta dois arquivos PDF, inserindo todas as páginas de um PDF (`pdf_a_adicionar`) em uma posição específica de outro PDF (`pdf_base`).
    Arg:
        pdf_base (str): Caminho para o arquivo PDF base onde as páginas serão inseridas.
        pdf_a_adicionar (str): Caminho para o arquivo PDF cujas páginas serão adicionadas.
        destino (str, opcional): Caminho para salvar o PDF resultante. Se não for fornecido, será criado um novo arquivo com sufixo '_merged'.
        pagina_destino (int, opcional): Índice da página no PDF base onde as páginas do PDF a adicionar serão inseridas. O padrão é -1 (adiciona ao final).
    Return:
        str: Caminho do arquivo PDF resultante.
    """
    try:
        doc_base = fitz.open(pdf_base)
        doc_novo = fitz.open(pdf_a_adicionar)

        doc_base.insert_pdf(doc_novo, start_at=pagina_destino)

        if not destino:
            # Cria nome com sufixo _merged
            base_name = os.path.splitext(pdf_base)[0]
            destino = f"{base_name}_merged.pdf"

        try:
            doc_base.save(destino, incremental=False)
        except Exception as e:
            raise RuntimeError(f"Erro ao juntar PDFs: {e}")
        finally:
            doc_base.close()
            doc_novo.close()

        return destino

    except Exception as e:
        raise RuntimeError(f"Erro ao juntar PDFs: {e}")


