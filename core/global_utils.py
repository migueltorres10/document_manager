##global_utils.py

from openpyxl import load_workbook
from openpyxl.drawing.image import Image as ExcelImage
from core.logger import configurar_logger
import os

logger = configurar_logger(__name__)

# Constantes para as células onde os QR Codes serão inseridos
QR_CELULAS_POR_TIPO = {
    "FO_Base": "V2",
    "FF_Base": "O1",
    "FA_Base": "K2"
}

# Constantes para as áreas de impressão de cada template
PRINT_AREAS = {
    "FO_Base": "A1:Y63",
    "FF_Base": "A1:Q41",
    "FA_Base": "A1:N48"
}

def preencher_dados_excel(ws, nome_template, dados):
    """
    Preenche as células do Excel com os dados apropriados para o template.

    Args:
        ws: Worksheet ativa do openpyxl.
        nome_template (str): Nome base do template (ex: 'FO_Base').
        dados (dict): Dicionário com chaves como 'ano', 'equipa', 'mes'.
    """
    if nome_template == "FO_Base":
        ws["J4"] = dados.get("ano", "")
        ws["D2"] = dados.get("equipa", "")

    elif nome_template == "FF_Base":
        ws["D3"] = dados.get("ano", "")
        ws["D7"] = dados.get("equipa", "")
        ws["D5"] = dados.get("mes", "")

    elif nome_template == "FA_Base":
        ws["E6"] = dados.get("ano", "")
        ws["F4"] = dados.get("equipa", "")
        ws["H6"] = dados.get("mes", "")

    else:
        logger.warning(f"Template '{nome_template}' não tem mapeamento para preenchimento de células.")


def inserir_qr_no_excel(template_path, destino_path, imagem_qr_path, dados=None):
    if dados is None:
        dados = {}
    """
    Insere um QR code e preenche dados em uma folha Excel com base num template.
    
    Args:
        template_path (str): Caminho do ficheiro Excel base (modelo).
        destino_path (str): Caminho onde o ficheiro final será guardado.
        imagem_qr_path (str): Caminho da imagem do QR code a ser inserida.
        dados (dict): Dicionário com chaves como 'ano', 'equipa' e 'mes' para preenchimento.

    Returns:
        None
    """
    try:
        wb = load_workbook(template_path)
        ws = wb.active

        # Verificar se o template é suportado
        nome_template = os.path.splitext(os.path.basename(template_path))[0]
        if nome_template not in QR_CELULAS_POR_TIPO:
            logger.error(f"Template '{nome_template}' não suportado.")
            return

        # Definir a orientação da página com base no template
        if nome_template == "FF_Base":
            ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
        else:
            ws.page_setup.orientation = ws.ORIENTATION_PORTRAIT

        # Inserir imagem QR
        celula_destino = QR_CELULAS_POR_TIPO.get(nome_template)
        if not celula_destino:
            logger.error(f"Template '{nome_template}' sem célula QR definida.")
            return
        
        # Inserir a imagem do QR code na célula especificada 
        img = ExcelImage(imagem_qr_path)
        img.width = 100
        img.height = 100
        ws.add_image(img, celula_destino)

        # Definir a área de impressão se existir para o template
        area = PRINT_AREAS.get(nome_template)
        if area:
            ws.print_area = area
            logger.info(f"Área de impressão definida: {area}")

        # Preencher dados no Excel
        preencher_dados_excel(ws, nome_template, dados)

        # Guardar ficheiro final
        wb.save(destino_path)
        logger.exception("Falha ao inserir QR e preencher dados.")

    except Exception as e:
        logger.exception(f"Erro ao inserir QR no Excel: {e}")


