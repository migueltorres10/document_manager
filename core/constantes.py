QR_FIELD_MAP = {
    "A": "nif_emitente",
    "B": "nif_adquirente",
    "C": "pais_emitente",
    "D": "tipo_doc",
    "E": "tem_iva",
    "F": "data_doc",
    "G": "numero_doc",
    "H": "hash",
    "I1": "pais_adquirente",
    "I7": "valor_tributavel",
    "I8": "valor_iva",
    "N": "total_iva",
    "O": "total_doc",
    "Q": "chave_seguranca",
    "R": "regime_iva"
}

MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
         "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

MESES_MAP = {
    nome: idx + 1 for idx, nome in enumerate(MESES)
}
