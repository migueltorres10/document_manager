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
    Args:
        pdfs (list): Lista de nomes de arquivos PDF.
        index_atual (int): Índice do PDF atual na lista.
        pasta_pdf (str): Caminho da pasta onde os PDFs estão localizados.
        preencher_callback (function): Função a ser chamada após abrir o PDF.
    Returns:
        None
    """
    if not pdfs:
        return
    fechar_sumatra()
    caminho_pdf = os.path.join(pasta_pdf, pdfs[index_atual])
    logger.info(f"Abrindo PDF: {caminho_pdf}")
    abrir_pdf_externo(caminho_pdf)
    preencher_callback(caminho_pdf)

def abrir_pdf_atual_com_rotacao(pdfs, index, pasta_pdf, preencher_callback):
    if not pdfs:
        return
    fechar_sumatra()
    caminho_pdf = os.path.join(pasta_pdf, pdfs[index])
    try:
        rodar_pdf_90graus(caminho_pdf)
    except Exception as e:
        mostrar_mensagem("erro", f"Erro ao rodar PDF: {e}")
        return
    abrir_pdf_externo(caminho_pdf)
    preencher_callback(caminho_pdf)


def mostrar_anterior(pdfs, index_atual, callback, doc_nome="documento"):
    """
    Mostra o PDF anterior na lista de PDFs.
    Args:
        pdfs (list): Lista de nomes de arquivos PDF.
        index_atual (int): Índice do PDF atual na lista.
        callback (function): Função a ser chamada após mudar o índice.
        doc_nome (str): Nome do documento para mensagens.
    Returns:
        int: Novo índice atual após a mudança.
    """
    if index_atual > 0:
        index_atual -= 1
        callback()
    else:
        mostrar_mensagem("aviso", f"Já está no primeiro {doc_nome}.")
        logger.info(f"Já está no primeiro {doc_nome}.")
    return index_atual


def mostrar_proximo(pdfs, index_atual, callback, doc_nome="documento"):
    """
    Mostra o próximo PDF na lista de PDFs.
    Args:
        pdfs (list): Lista de nomes de arquivos PDF.
        index_atual (int): Índice do PDF atual na lista.
        callback (function): Função a ser chamada após mudar o índice.
        doc_nome (str): Nome do documento para mensagens.
    Returns:
        int: Novo índice atual após a mudança.
    """
    if index_atual < len(pdfs) - 1:
        index_atual += 1
        callback()
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
