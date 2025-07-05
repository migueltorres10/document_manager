import fitz  # PyMuPDF

def inserir_qr_em_pdf(pdf_path, imagem_qr, output_path, pagina=None, margem=20, tamanho=(100, 100)):
    """
    Insere um QR code no canto inferior direito de uma ou todas as páginas de um PDF.

    Args:
        pdf_path (str): Caminho para o PDF original.
        imagem_qr (str): Caminho da imagem do QR Code (PNG).
        output_path (str): Caminho para salvar o PDF modificado.
        pagina (int, opcional): Número da página (0-index). Se None, aplica a todas.
        margem (int): Distância do canto.
        tamanho (tuple): Tamanho (largura, altura) da imagem em pontos.
    """
    doc = fitz.open(pdf_path)

    paginas_alvo = [pagina] if pagina is not None else range(len(doc))

    for i in paginas_alvo:
        page = doc[i]
        largura, altura = page.rect.width, page.rect.height

        # Define a posição no canto inferior direito
        x1 = largura - tamanho[0] - margem
        y1 = altura - tamanho[1] - margem
        x2 = largura - margem
        y2 = altura - margem

        rect = fitz.Rect(x1, y1, x2, y2)
        page.insert_image(rect, filename=imagem_qr)

    doc.save(output_path)
    doc.close()
    print(f"[INFO] QR code inserido em '{output_path}'")

inserir_qr_em_pdf(
    pdf_path="documento_original.pdf",
    imagem_qr="qr_123_2025_06.png",
    output_path="documento_com_qr.pdf",
    pagina=None,  # ou 0 para apenas na primeira
    margem=20,
    tamanho=(80, 80)
)