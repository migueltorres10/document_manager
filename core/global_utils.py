from openpyxl import load_workbook
from openpyxl.drawing.image import Image as ExcelImage
import os

QR_CELULAS_POR_TIPO = {
    "FO_Base": "V2",
    "FF_Base": "O1",
    "FA_Base": "K2"
}

PRINT_AREAS = {
    "FO_Base": "A1:Y63",
    "FF_Base": "A1:Q41",
    "FA_Base": "A1:N48"
}

def mes_selecionado(meses_var, mes_atual, var_atual):
    if var_atual.get():
        for mes, var in meses_var:
            if mes != mes_atual:
                var.set(False)


def inserir_qr_no_excel(template_path, destino_path, imagem_qr_path):
    try:
        wb = load_workbook(template_path)
        ws = wb.active

        nome_template = os.path.splitext(os.path.basename(template_path))[0]

        # Inserir imagem
        celula_destino = QR_CELULAS_POR_TIPO.get(nome_template)
        if not celula_destino:
            print(f"[ERRO] Template '{nome_template}' sem célula QR definida.")
            return

        img = ExcelImage(imagem_qr_path)
        img.width = 100
        img.height = 100
        ws.add_image(img, celula_destino)

        # Definir manualmente a área de impressão, se necessário
        area = PRINT_AREAS.get(nome_template)
        if area:
            ws.print_area = area
            print(f"[INFO] Área de impressão definida: {area}")

        wb.save(destino_path)
        print(f"[QR INSERIDO] {destino_path} em {celula_destino}")

    except Exception as e:
        print(f"[ERRO] Falha ao inserir QR: {e}")