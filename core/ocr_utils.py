from pdf2image import convert_from_path
import pytesseract
import pdfplumber
from pyzbar.pyzbar import decode
from datetime import datetime
from core.constantes import QR_FIELD_MAP
from config import POPPLER_PATH, TESSERACT_CMD

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def verificar_se_pdf_tem_texto(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                if page.extract_text():
                    return True
    except Exception:
        pass
    return False

def pdf_para_texto(pdf_path):
    print(f"📌 Extraindo texto do PDF: {pdf_path}")
    if verificar_se_pdf_tem_texto(pdf_path):
        try:
            with pdfplumber.open(pdf_path) as pdf:
                return "\n".join([page.extract_text() or "" for page in pdf.pages])
        except Exception as e:
            print(f"❌ Erro ao extrair com pdfplumber: {e}")
    try:
        imagens = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
        texto_final = [pytesseract.image_to_string(img, lang="por", config="--oem 3 --psm 6").strip() for img in imagens]
        return "\n".join(texto_final)
    except Exception as e:
        print(f"❌ Erro ao converter imagem para texto: {e}")
        return None

def extrair_dados_qrcode_de_pdf(pdf_path):
    try:
        imagens = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
        for img in imagens:
            resultado_qr = decode(img)
            if resultado_qr:
                texto = resultado_qr[0].data.decode("utf-8")
                return parse_qrcode_para_dicionario(texto)
    except Exception as e:
        print(f"Erro ao extrair QR code: {e}")
    return {}

def parse_qrcode_para_dicionario(texto_qrcode):
    try:
        partes = texto_qrcode.strip().split("*")
        dados_raw = {p.split(":")[0]: p.split(":")[1] for p in partes if ":" in p}
        return {QR_FIELD_MAP.get(k, k): v for k, v in dados_raw.items()}
    except Exception as e:
        print(f"❌ Erro ao parsear QR Code: {e}")
        return {}

def extrair_ano(data_doc=None):
    if data_doc and len(data_doc) >= 4:
        return data_doc[:4]
    return str(datetime.now().year)
