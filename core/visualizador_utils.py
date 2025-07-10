# core/visualizacao_utils.py

from core.pdf_utils import abrir_pdf_externo, fechar_sumatra
from core.gui_utils import mostrar_mensagem
from core.pdf_utils import rodar_pdf_90graus
import os
from core.logger import configurar_logger
logger = configurar_logger(__name__)

def abrir_pdf_atual(pdfs, index_atual, pasta_pdf, preencher_callback):
    """
    Abre o PDF atual na lista de PDFs.
    """
    if not pdfs:
        logger.warning("Lista de PDFs vazia — nada para abrir.")
        return

    if not (0 <= index_atual < len(pdfs)):
        logger.error(f"Índice fora do intervalo: {index_atual} (máximo: {len(pdfs) - 1})")
        return

    fechar_sumatra()
    caminho_pdf = os.path.join(pasta_pdf, pdfs[index_atual])
    logger.info(f"Abrindo PDF no índice {index_atual}: {caminho_pdf}")

    try:
        abrir_pdf_externo(caminho_pdf)
        preencher_callback(caminho_pdf)
    except Exception as e:
        logger.exception(f"Erro ao abrir e preencher PDF '{caminho_pdf}': {e}")


def abrir_pdf_atual_com_rotacao(pdfs, index, pasta_pdf, preencher_callback):
    if not pdfs:
        logger.warning("Lista de PDFs vazia — nada para abrir com rotação.")
        return

    if not (0 <= index < len(pdfs)):
        logger.error(f"Índice fora do intervalo: {index} (máximo: {len(pdfs) - 1})")
        return

    fechar_sumatra()
    caminho_pdf = os.path.join(pasta_pdf, pdfs[index])
    logger.info(f"Abrindo PDF com rotação no índice {index}: {caminho_pdf}")

    try:
        rodar_pdf_90graus(caminho_pdf)
        abrir_pdf_externo(caminho_pdf)
        preencher_callback(caminho_pdf)
    except Exception as e:
        logger.exception(f"Erro ao rodar e abrir PDF '{caminho_pdf}': {e}")
        mostrar_mensagem("erro", f"Erro ao rodar PDF: {e}")


def mostrar_anterior(lista_len, index_atual, doc_nome="documento"):
    """
    Retorna o índice anterior se possível, senão mantém e mostra aviso.
    """
    if index_atual > 0:
        index_atual -= 1
        logger.info(f"← Navegar para o anterior ({doc_nome}): {index_atual}")
    else:
        mostrar_mensagem("aviso", f"Já está no primeiro {doc_nome}.")
        logger.info(f"Já está no primeiro {doc_nome}.")
    return index_atual


def mostrar_proximo(lista_len, index_atual, doc_nome="documento"):
    """
    Retorna o índice seguinte se possível, senão mantém e mostra aviso.
    """
    if index_atual < lista_len - 1:
        index_atual += 1
        logger.info(f"→ Navegar para o próximo ({doc_nome}): {index_atual}")
    else:
        mostrar_mensagem("aviso", f"Já está no último {doc_nome}.")
        logger.info(f"Já está no último {doc_nome}.")
    return index_atual


def terminar(root):
    """
    Fecha o visualizador e encerra o SumatraPDF.
    Args:
        root (tk.Tk): Instância da janela principal do Tkinter.
    Returns:
        None
    """
    fechar_sumatra()
    logger.info("Fechando visualizador e encerrando SumatraPDF.")
    root.destroy()
