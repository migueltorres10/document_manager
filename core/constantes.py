## constantes.py

# Mapeamento de campos QR code em documentos comunicados à AT (Faturas, Guias, Recibos)
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

# Lista de meses
MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
         "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

# Mapeamento de meses para números
MESES_MAP = {
    nome: idx + 1 for idx, nome in enumerate(MESES)
}

# Tipos de documentos e seus códigos
TIPOS_DOCUMENTOS = {
    "Guias": "GR",
    "Faturas": "F",
    "Recibos": "R",
    "Folhas de Obra": "FO",
    "Folhas de Faltas": "FF",
    "Folhas de Assiduidade": "FA",
    "Faturas Emitidas": "F-E",
    "Recibos Emitidos": "R-E",
    "Guias Emitidas": "GR-E",
}

# Estrutura de diretórios a criar no início
DOCUMENTOS_COM_PASTAS = {
    "Guias": ["entrada"],
    "Faturas": ["entrada"],
    "Folhas_Obra": ["entrada", "geradas"],
    "Folhas_Assiduidade": ["entrada", "geradas"],
    "Folhas_Faltas": ["entrada", "geradas"],
    "Faturas_Emitidas": ["entrada"],
    "Recibos_Emitidos": ["entrada"],
    "Guias_Emitidas": ["entrada"]
}

PASTAS_DOCUMENTOS = {
    "Guias": "GR",
    "Faturas": "F",
    "Recibos": "R",
    "Folhas_Obra": "FO",
    "Folhas_Faltas": "FF",
    "Folhas_Assiduidade": "FA",
    "Faturas_Emitidas": "F-E",
    "Recibos_Emitidos": "R-E",
    "Guias_Emitidas": "GR-E",
}

PASTAS = [f"{doc}/{sub}" for doc, subs in DOCUMENTOS_COM_PASTAS.items() for sub in subs]