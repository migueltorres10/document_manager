## core/file_utils.py

import os
import shutil
import re
from pathlib import Path
import fitz  # PyMuPDF
from core.constantes import PASTAS
from core.logger import configurar_logger
logger = configurar_logger(__name__)

def dividir_e_mover_pdf(pasta_origem, pasta_obsoletos, pasta_separados):
    """
    Divide cada PDF da pasta de origem em páginas únicas e salva-as na pasta de separados.
    Move o PDF original para a pasta de obsoletos.
    
    Args:
        pasta_origem (str): Caminho da pasta com os PDFs originais.
        pasta_obsoletos (str): Caminho onde os originais serão movidos.
        pasta_separados (str): Caminho onde os PDFs separados por página serão guardados.
    
    Returns:
        list[str]: Lista de nomes de arquivos processados.
    """

    # Verifica se as pastas existem, caso contrário, cria-as
    Path(pasta_obsoletos).mkdir(parents=True, exist_ok=True)
    Path(pasta_separados).mkdir(parents=True, exist_ok=True)
    arquivos_processados = []

    #Loop para percorrer apenas os arquivos PDF na pasta de origem
    for arquivo in os.listdir(pasta_origem):
        if not arquivo.lower().endswith(".pdf"):
            continue
        # Caminhos completos para o PDF original e destino
        caminho_pdf = os.path.join(pasta_origem, arquivo)
        # Caminho para mover o PDF original para a pasta de obsoletos
        destino_obsoleto = os.path.join(pasta_obsoletos, arquivo)
        # Nome base do arquivo sem extensão
        nome_base = Path(arquivo).stem

        try:
            # Abre o PDF e divide em páginas
            doc = fitz.open(caminho_pdf)
            for i in range(len(doc)):
                # Cria uma nova página com a página atual do PDF
                nova_pagina = fitz.open()
                # Insere a página atual no novo documento
                nova_pagina.insert_pdf(doc, from_page=i, to_page=i)
                # Define o nome do novo arquivo com o índice da página
                novo_nome = f"{nome_base}_p{i+1}.pdf"
                # Define o caminho completo para salvar a nova página
                caminho_saida = os.path.join(pasta_separados, novo_nome)
                # Salva a nova página como um PDF
                nova_pagina.save(caminho_saida)
                nova_pagina.close()
            doc.close()
            # Move o PDF original para a pasta de obsoletos
            shutil.move(caminho_pdf, destino_obsoleto)
            arquivos_processados.append(arquivo)
            logger.info(f"✅ {arquivo} dividido e movido com sucesso.")
        except Exception as e:
            logger.exception(f"Erro ao processar {arquivo}: {e}")
    return arquivos_processados


def limpar_nome_ficheiro(nome):
    """
    Limpa o nome do ficheiro removendo caracteres inválidos para nome de arquivo
    e substituindo espaços por underscores.

    Args:
        nome (str): Nome original.

    Returns:
        str: Nome limpo.
    """
    # Remove caracteres inválidos e substitui espaços por underscores
    nome_limpo = re.sub(r'[\\/*?:"<>|]', '', nome)
    # Remove acentos e caracteres especiais
    nome_limpo = re.sub(r'\s+', '_', nome_limpo.strip())
    return nome_limpo

def renomear_pdf(caminho_pdf, numero, ano):
    """
    Renomeia um PDF com base no número e ano informados.

    Args:
        caminho_pdf (str): Caminho do arquivo original.
        numero (str): Número do documento.
        ano (str/int): Ano do documento.

    Returns:
        str: Caminho do novo arquivo renomeado.

    Raises:
        ValueError: Se número ou ano estiverem ausentes.
        FileExistsError: Se o nome de destino já existir.
    """
    logger.info(f"Renomeando PDF: {caminho_pdf} para {numero} - {ano}")
    # Verifica se o caminho do PDF existe
    if not all([numero, ano]):
        logger.error("Número e ano são obrigatórios para renomear o PDF.")
        raise ValueError("Número e ano são obrigatórios.")
    # Limpar o numero para evitar caracteres inválidos
    numero_limpo = limpar_nome_ficheiro(numero)
    # Nomear o novo arquivo com o número
    novo_nome = f"{numero_limpo}.pdf"
    # Verifica se o caminho do PDF existe
    novo_caminho = os.path.join(os.path.dirname(caminho_pdf), novo_nome)
    if os.path.exists(novo_caminho):
        logger.error(f"Já existe um arquivo com o nome: {novo_caminho}")
        raise FileExistsError(f"Já existe: {novo_caminho}")
    os.rename(caminho_pdf, novo_caminho)
    logger.info(f"PDF renomeado para: {novo_caminho}")
    # Retorna o novo caminho do arquivo
    return novo_caminho

def mover_pdf_para_pasta_destino(caminho_pdf, fornecedor, ano, pasta_base):
    """
    Move um PDF para a pasta final de acordo com o fornecedor e ano.

    Args:
        caminho_pdf (str): Caminho atual do PDF.
        fornecedor (str): Nome do fornecedor.
        ano (str/int): Ano do documento.
        pasta_base (str): Caminho base da estrutura de arquivos.

    Returns:
        str: Caminho final do PDF.

    Raises:
        ValueError: Se fornecedor ou ano estiverem ausentes.
        FileExistsError: Se o destino já existir.
    """
    logger.info(f"Mover PDF: {caminho_pdf} para {fornecedor}/{ano}")
    # Verifica se fornecedor e ano estão presentes
    if not all([fornecedor, ano]):
        logger.error("Fornecedor e ano são obrigatórios para mover o PDF.")
        raise ValueError("Fornecedor e ano são obrigatórios.")    
    # Define o nme da pasta de destino
    pasta_destino = os.path.join(pasta_base, ano, fornecedor)
    os.makedirs(pasta_destino, exist_ok=True)
    nome_original = os.path.basename(caminho_pdf)
    novo_caminho = os.path.join(pasta_destino, nome_original)
    # Verifica se o arquivo já existe no destino
    if os.path.exists(novo_caminho):
        logger.error(f"O ficheiro já existe em: {novo_caminho}")
        raise FileExistsError(f"O ficheiro já existe em: {novo_caminho}")
    # Move o PDF para a nova pasta
    shutil.move(caminho_pdf, novo_caminho)
    logger.info(f"PDF movido para: {novo_caminho}")
    return novo_caminho

def mover_pdf_folha_obra(caminho_pdf, subpasta, pasta_base, nome_final=None):
    """
    Move um PDF da folha de obra para uma subpasta específica.

    Args:
        caminho_pdf (str): Caminho do PDF atual.
        subpasta (str): Nome da subpasta (ex: processo ou cliente).
        pasta_base (str): Pasta base das folhas de obra.
        nome_final (str, optional): Novo nome do arquivo (com extensão). Se None, mantém original.

    Returns:
        str: Caminho final do PDF.
    """
    logger.info(f"Mover PDF: {caminho_pdf} para subpasta: {subpasta}")
    # Verifica se a subpasta é válida
    if not subpasta:
        logger.error("Nome da subpasta é obrigatório para mover o PDF.")
        raise ValueError("Nome da subpasta é obrigatório.")

    # Define o caminho da subpasta e cria se não existir
    subpasta = limpar_nome_ficheiro(subpasta)
    pasta_destino = os.path.join(pasta_base, subpasta)
    os.makedirs(pasta_destino, exist_ok=True)
    # Define o nome do PDF final
    nome_pdf = nome_final if nome_final else os.path.basename(caminho_pdf)        
    destino = os.path.join(pasta_destino, nome_pdf)

    # Verifica se o destino já existe
    if os.path.exists(destino):
        logger.error(f"Já existe um arquivo com o nome: {destino}")
        raise FileExistsError(f"Já existe: {destino}")
    # Move o PDF para a subpasta
    shutil.move(caminho_pdf, destino)
    logger.info(f"PDF movido para: {destino}")
    return destino


def mover_pdf_equipa(caminho_pdf, nome_equipa, ano, nome_final, pasta_base):
    """
    Move um PDF para a pasta da equipa e ano correspondentes.

    Args:
        caminho_pdf (str): Caminho do PDF.
        nome_equipa (str): Nome da equipa.
        ano (str/int): Ano do documento.
        nome_final (str): Nome do ficheiro destino (com extensão).
        pasta_base (str): Caminho base onde o PDF será movido.

    Returns:
        str: Caminho final do PDF.

    Raises:
        FileExistsError: Se o arquivo já existir no destino.
    """
    logger.info(f"Mover PDF: {caminho_pdf} para equipa: {nome_equipa}, ano: {ano}")
    # Verifica se o nome da equipa e ano estão presentes
    if not all([nome_equipa, ano]):
        logger.error("Nome da equipa e ano são obrigatórios para mover o PDF.")
        raise ValueError("Nome da equipa e ano são obrigatórios.")
    # Define o nome da pasta de destino e cria se não existir
    pasta_destino = os.path.join(pasta_base, ano, nome_equipa)
    os.makedirs(pasta_destino, exist_ok=True)
    destino = os.path.join(pasta_destino, nome_final)
    # Verifica se o arquivo já existe no destino
    if os.path.exists(destino):
        logger.error(f"Já existe um arquivo com o nome: {destino}")
        raise FileExistsError(f"Já existe: {destino}")
    # Move o PDF para a pasta de destino
    shutil.move(caminho_pdf, destino)
    logger.info(f"PDF movido para: {destino}")
    return destino

def criar_pastas():
    """
    Cria as pastas definidas na constante PASTAS, caso ainda não existam.
    """
    logger.info("Criando pastas definidas em PASTAS...")
    for pasta in PASTAS:
        if not os.path.exists(pasta):
            os.makedirs(pasta)
            logger.info(f"Pasta {pasta} criada.")

