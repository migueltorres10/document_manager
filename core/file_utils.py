import os
import shutil
import re
from pathlib import Path
import fitz  # PyMuPDF

def dividir_e_mover_pdf(pasta_origem, pasta_obsoletos, pasta_separados):
    Path(pasta_obsoletos).mkdir(parents=True, exist_ok=True)
    Path(pasta_separados).mkdir(parents=True, exist_ok=True)
    arquivos_processados = []

    for arquivo in os.listdir(pasta_origem):
        if not arquivo.lower().endswith(".pdf"):
            continue
        caminho_pdf = os.path.join(pasta_origem, arquivo)
        destino_obsoleto = os.path.join(pasta_obsoletos, arquivo)
        nome_base = Path(arquivo).stem

        try:
            doc = fitz.open(caminho_pdf)
            for i in range(len(doc)):
                nova_pagina = fitz.open()
                nova_pagina.insert_pdf(doc, from_page=i, to_page=i)
                novo_nome = f"{nome_base}_p{i+1}.pdf"
                caminho_saida = os.path.join(pasta_separados, novo_nome)
                nova_pagina.save(caminho_saida)
                nova_pagina.close()
            doc.close()
            shutil.move(caminho_pdf, destino_obsoleto)
            arquivos_processados.append(arquivo)
        except Exception as e:
            print(f"❌ Erro ao dividir {arquivo}: {e}")
    return arquivos_processados

def limpar_nome_ficheiro(nome):
    nome_limpo = re.sub(r'[\\/*?:"<>|]', '', nome)
    nome_limpo = re.sub(r'\s+', '_', nome_limpo.strip())
    return nome_limpo

def renomear_pdf(caminho_pdf, numero, ano):
    if not all([numero, ano]):
        raise ValueError("Número e ano são obrigatórios.")
    numero_limpo = limpar_nome_ficheiro(numero)
    novo_nome = f"{numero_limpo}.pdf"
    novo_caminho = os.path.join(os.path.dirname(caminho_pdf), novo_nome)
    if os.path.exists(novo_caminho):
        raise FileExistsError(f"Já existe: {novo_caminho}")
    os.rename(caminho_pdf, novo_caminho)
    return novo_caminho

def mover_pdf_para_pasta_destino(caminho_pdf, fornecedor, ano, pasta_base):
    if not all([fornecedor, ano]):
        raise ValueError("Fornecedor e ano são obrigatórios.")
    pasta_destino = os.path.join(pasta_base, ano, fornecedor)
    os.makedirs(pasta_destino, exist_ok=True)
    nome_original = os.path.basename(caminho_pdf)
    novo_caminho = os.path.join(pasta_destino, nome_original)
    if os.path.exists(novo_caminho):
        raise FileExistsError(f"O ficheiro já existe em: {novo_caminho}")
    shutil.move(caminho_pdf, novo_caminho)
    return novo_caminho

def mover_pdf_folha_obra(caminho_pdf, processo, cliente, pasta_base, nome_final=None):
    if not all([processo, cliente]):
        raise ValueError("Processo e cliente são obrigatórios.")
    pasta_destino = os.path.join(pasta_base, processo, cliente)
    os.makedirs(pasta_destino, exist_ok=True)
    nome_pdf = nome_final if nome_final else os.path.basename(caminho_pdf)
    destino = os.path.join(pasta_destino, nome_pdf)
    if os.path.exists(destino):
        raise FileExistsError(f"Já existe: {destino}")
    shutil.move(caminho_pdf, destino)
    return destino

def mover_pdf_equipa(caminho_pdf, equipa_id, ano, nome_final, pasta_base):
    pasta_destino = os.path.join(pasta_base, ano, f"Equipa_{equipa_id}")
    os.makedirs(pasta_destino, exist_ok=True)
    destino = os.path.join(pasta_destino, nome_final)
    if os.path.exists(destino):
        raise FileExistsError(f"Já existe: {destino}")
    shutil.move(caminho_pdf, destino)
    return destino
