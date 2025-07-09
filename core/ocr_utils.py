## ocr_utils.py

from pdf2image import convert_from_path
import pytesseract
import pdfplumber
from pyzbar.pyzbar import decode
from datetime import datetime
from core.constantes import QR_FIELD_MAP
from config import POPPLER_PATH, TESSERACT_CMD
import os
from core.logger import configurar_logger
logger = configurar_logger(__name__)

# Configura o caminho do Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def verificar_se_pdf_tem_texto(pdf_path):
    """
    Verifica se o PDF contém texto legível.
    Args:
        pdf_path (str): Caminho do arquivo PDF.
    Returns:
        bool: True se o PDF contém texto, False caso contrário.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                if page.extract_text():
                    return True
    except Exception as e:
        logger.warning(f"Erro ao verificar texto no PDF: {e}")
    return False

def pdf_para_texto(pdf_path):
    """
    Extrai texto de um PDF, primeiro tentando com pdfplumber e, se falhar, usando OCR.
    Args:
        pdf_path (str): Caminho do arquivo PDF.
    Returns:
        str: Texto extraído do PDF ou None se não for possível extrair.
    """
    logger.info(f"Extraindo texto do PDF: {pdf_path}")
    try:
        if verificar_se_pdf_tem_texto(pdf_path):
            with pdfplumber.open(pdf_path) as pdf:
                texto = "\n".join([page.extract_text() or "" for page in pdf.pages])
                logger.debug("Texto extraído com sucesso usando pdfplumber.")
                return texto
        else:
            imagens = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
            texto_ocr = [
                pytesseract.image_to_string(img, lang="por", config="--oem 3 --psm 6").strip()
                for img in imagens
            ]
            logger.debug("Texto extraído com sucesso usando OCR.")
            return "\n".join(texto_ocr)
    except Exception as e:
        logger.exception(f"Erro ao extrair texto do PDF: {e}")
        return None

def extrair_dados_qrcode_de_pdf(pdf_path):
    """ Extrai dados de QR code de um PDF.
    Args:
        pdf_path (str): Caminho do arquivo PDF.
    Returns:
        dict: Dicionário com os dados extraídos do QR code ou vazio se não encontrado.
    """
    logger.info(f"Tentando extrair QR Code do PDF: {pdf_path}")
    try:
        imagens = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
        for img in imagens:
            resultado_qr = decode(img)
            if resultado_qr:
                texto = resultado_qr[0].data.decode("utf-8")
                logger.debug(f"QR Code lido com conteúdo: {texto}")
                return parse_qrcode_para_dicionario(texto)
        logger.info("Nenhum QR Code encontrado no PDF.")
    except Exception as e:
        logger.exception(f"Erro ao extrair QR Code: {e}")
    return {}

def parse_qrcode_para_dicionario(texto_qrcode):
    """ Converte o texto do QR code em um dicionário.
    Args:
        texto_qrcode (str): Texto do QR code.
    Returns:
        dict: Dicionário com os dados extraídos do QR code.
    """
    try:
        partes = texto_qrcode.strip().split("*")
        dados_raw = {
            p.split(":")[0]: p.split(":")[1]
            for p in partes if ":" in p
        }
        dados_mapeados = {QR_FIELD_MAP.get(k, k): v for k, v in dados_raw.items()}
        logger.debug(f"QR Code convertido para dicionário: {dados_mapeados}")
        return dados_mapeados
    except Exception as e:
        logger.exception(f"Erro ao parsear QR Code: {e}")
        return {}

def extrair_ano(data_doc=None):
    """ Extrai o ano de um documento, seja do texto ou da data atual.
    Args:
        data_doc (str): Data do documento no formato 'YYYY-MM-DD' ou similar.
    Returns:
        str: Ano extraído ou o ano atual se não for possível extrair.
    """
    if data_doc and len(data_doc) >= 4:
        return data_doc[:4]
    return str(datetime.now().year)

def ler_dados_qr(pdf_path):
    """ Lê dados de QR code de um PDF e retorna como dicionário.
    Args:
        pdf_path (str): Caminho do arquivo PDF.
    Returns:
        dict: Dicionário com os dados do QR code ou None se não encontrado.
    """
    logger.info(f"Lendo QR Code bruto do PDF: {pdf_path}")
    try:
        imagens = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
        for img in imagens:
            resultado_qr = decode(img)
            if resultado_qr:
                texto = resultado_qr[0].data.decode("utf-8")
                logger.debug(f"Texto QR bruto: {texto}")
                dados = {}
                for par in texto.split(";"):
                    if "=" in par:
                        chave, valor = par.split("=", 1)
                        dados[chave.strip()] = valor.strip()
                return dados
        logger.info("Nenhum QR bruto encontrado no PDF.")
        return None
    except Exception as e:
        logger.exception(f"Erro ao ler QR bruto: {e}")
        return None
