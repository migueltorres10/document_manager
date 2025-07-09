# core/db_helpers.py

from datetime import datetime
from config import connect_bd
from core.logger import configurar_logger
logger = configurar_logger(__name__)

# Conecta a base de dados D ou S
def get_conn_d():
    """
    Estabelece conexão com a base de dados de documentos (D).
    
    Returns:
        pyodbc.Connection: Objeto de conexão.
    """
    return connect_bd("D")
def get_conn_s():
    """
    Estabelece conexão com a base de dados do sistema (S).
    
    Returns:
        pyodbc.Connection: Objeto de conexão.
    """
    return connect_bd("S")

# Obtém o timestamp atual formatado
def timestamp_agora():
    """
    Retorna timestamp atual no formato 'YYYY-MM-DD HH:MM:SS'.
    
    Returns:
        str: Timestamp formatado.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def obter_fornecedores():
    """
    Obtém todos os fornecedores da base de dados do sistema (S).

    Returns:
        dict: Dicionário com NIF como chave e nome do fornecedor como valor.
    """

    # Conecta à base de dados do sistema e obtém os fornecedores
    # Retorna um dicionário com NIF como chave e nome do fornecedor como valor
    # Se não houver fornecedores, retorna um dicionário vazio
    logger.info("Carregando fornecedores da base de dados...")
    conn = get_conn_s()
    fornecedores = {}
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT RTRIM(ncont), RTRIM(nome) FROM fl")
        fornecedores = {nif: nome for nif, nome in cursor.fetchall()}
        if not fornecedores:
            logger.warning("Nenhum fornecedor encontrado na base de dados.")
        else:
            logger.info(f"{len(fornecedores)} fornecedores carregados da base de dados.")
    except Exception as e:
        logger.exception(f"❌ Erro ao obter fornecedores: {e}")
    finally:
        conn.close()
    return fornecedores

def obter_clientes():
    """
    Obtém todos os clientes da base de dados do sistema (S).

    Returns:
        dict: Dicionário com NIF como chave e nome do cliente como valor.
    """
    # Conecta à base de dados do sistema e obtém os clientes
    # Retorna um dicionário com NIF como chave e nome do cliente como valor
    # Se não houver clientes, retorna um dicionário vazio
    logger.info("Carregando clientes da base de dados...")
    conn = get_conn_s()
    clientes = {}
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT RTRIM(ncont), RTRIM(nome) FROM cl")
        clientes = {nif: nome for nif, nome in cursor.fetchall()}
        if not clientes:
            logger.warning("Nenhum cliente encontrado na base de dados.")
        else:
            logger.info(f"{len(clientes)} clientes carregados da base de dados.")
    except Exception as e:
        logger.exception(f"❌ Erro ao obter clientes: {e}")
    finally:
        conn.close()
    return clientes

def gravar_guia_bd(fornecedor, numero, ano, data, processo, caminho_pdf):
    """
    Grava uma guia na base de dados de documentos (D).
    Args:
        fornecedor (str): NIF do fornecedor.
        numero (str): Número do documento.
        ano (int): Ano do documento.
        data (str): Data do documento no formato 'YYYY-MM-DD'.
        processo (str): Referência do processo associado.
        caminho_pdf (str): Caminho do arquivo PDF da guia.
    Returns:
        None
    Raises:
        Exception: Se ocorrer um erro ao gravar a guia.
    """
    # Conecta à base de dados de documentos e grava a guia
    # Insere os dados na tabela 'guias'
    # Se ocorrer um erro, registra a exceção e fecha a conexão
    logger.info("Gravando guia na base de dados...")
    conn = get_conn_d()
    try:
        cursor = conn.cursor()
        data_registo = timestamp_agora()
        cursor.execute("""
            INSERT INTO guias (fornecedor, numero_doc, data_doc, ano, processo, caminho_ficheiro, data_insercao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (fornecedor, numero, data, ano, processo, caminho_pdf, data_registo))
        conn.commit()
        logger.info("✅ Guia gravada com sucesso.")
    except Exception as e:
        logger.exception(f"❌ Erro ao gravar guia: {e}")
    finally:
        conn.close()

def gravar_fatura_bd(fornecedor, tipo_doc, numero, ano, data, base, iva, total, processo, caminho_pdf):
    """
    Grava uma fatura na base de dados de documentos (D).
    Args:
        fornecedor (str): NIF do fornecedor.
        tipo_doc (str): Tipo do documento (ex: "Fatura", "Fatura-Recibo").
        numero (str): Número do documento.
        ano (int): Ano do documento.
        data (str): Data do documento no formato 'YYYY-MM-DD'.
        base (float): Valor base da fatura.
        iva (float): Valor do IVA da fatura.
        total (float): Valor total da fatura.
        processo (str): Referência do processo associado.
        caminho_pdf (str): Caminho do arquivo PDF da fatura.
    Returns:
        None
    Raises:
        Exception: Se ocorrer um erro ao gravar a fatura.
    """
    # Conecta à base de dados de documentos e grava a fatura
    # Insere os dados na tabela 'documentos_faturacao'
    # Se ocorrer um erro, registra a exceção e fecha a conexão
    logger.info("Gravando fatura na base de dados...")
    conn = get_conn_d()
    try:
        cursor = conn.cursor()
        data_registo = timestamp_agora()
        cursor.execute("""
            INSERT INTO documentos_faturacao (
                fornecedor, tipo_doc, numero_doc, ano, data_doc,
                valor_base, iva, total, processo, caminho_ficheiro, data_insercao
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (fornecedor, tipo_doc, numero, ano, data, base, iva, total, processo, caminho_pdf, data_registo))
        conn.commit()
        logger.info("✅ Fatura gravada com sucesso.")
    except Exception as e:
        logger.exception(f"❌ Erro ao gravar fatura: {e}")
    finally:
        conn.close()

def folha_obra_bd(processo, cliente, equipa, descricao, ano, caminho_pdf):
    """
    Grava uma folha de obra na base de dados de documentos (D).
    Args:
        processo (str): Referência do processo associado.
        cliente (str): NIF do cliente.
        equipa (str): ID da equipa responsável.
        descricao (str): Descrição da folha de obra.
        ano (int): Ano da folha de obra.
        caminho_pdf (str): Caminho do arquivo PDF da folha de obra.
    Returns:
        int: ID da folha de obra gravada, ou None se ocorrer um erro.
    Raises:
        Exception: Se ocorrer um erro ao gravar a folha de obra.    
    """
    # Conecta à base de dados de documentos e grava a folha de obra
    # Insere os dados na tabela 'folhas_obra'
    # Se ocorrer um erro, registra a exceção e fecha a conexão
    logger.info("Gravando folha de obra na base de dados...")
    conn = get_conn_d()
    try:
        cursor = conn.cursor()
        data_registo = timestamp_agora()
        cursor.execute("""
            INSERT INTO folhas_obra (processo, cliente, equipa, descricao, ano, caminho_ficheiro, data_insercao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (processo, cliente, equipa, descricao, ano, caminho_pdf, data_registo))
        cursor.execute("SELECT TOP 1 id FROM folhas_obra ORDER BY id DESC")
        folha_id = cursor.fetchone()[0]
        conn.commit()
        logger.info("✅ Folha de obra gravada com sucesso.")
        return folha_id
    except Exception as e:
        logger.exception(f"❌ Erro ao gravar folha de obra: {e}")
        return None
    finally:
        conn.close()

def inserir_meses_folha_obra(folha_id, lista_meses):
    """
    Insere meses na tabela de folhas de obra.
    Args:
        folha_id (int): ID da folha de obra.
        lista_meses (list): Lista de meses a serem inseridos (1 a 12).
    Returns:
        None
    Raises:
        Exception: Se ocorrer um erro ao inserir os meses.
    """
    # Conecta à base de dados de documentos e insere os meses na tabela 'folhas_obra_meses'
    # Verifica se os meses estão entre 1 e 12
    # Se ocorrer um erro, registra a exceção e fecha a conexão
    logger.info("Inserindo meses na folha de obra...")
    conn = get_conn_d()
    try:
        cursor = conn.cursor()
        for numero_mes in lista_meses:
            if isinstance(numero_mes, int) and 1 <= numero_mes <= 12:
                cursor.execute("""
                    INSERT INTO folhas_obra_meses (folha_id, mes)
                    VALUES (?, ?)
                """, (folha_id, numero_mes))
            else:
                logger.warning(f"❌ Mês inválido: {numero_mes}. Deve ser um inteiro entre 1 e 12.")
        conn.commit()
        logger.info("✅ Meses inseridos com sucesso na folha de obra.")
    except Exception as e:
        print(f"❌ Erro ao inserir meses: {e}")
    finally:
        conn.close()

def folha_assiduidade_bd(equipa_id, mes, ano, caminho_pdf):
    """
    Grava uma folha de assiduidade na base de dados de documentos (D).
    Args:
        equipa_id (int): ID da equipa responsável.
        mes (str): Mês da folha de assiduidade (formato 'MM').
        ano (int): Ano da folha de assiduidade.
        caminho_pdf (str): Caminho do arquivo PDF da folha de assiduidade.
    Returns:
        int: ID da folha de assiduidade gravada, ou None se ocorrer um erro.
    Raises:
        Exception: Se ocorrer um erro ao gravar a folha de assiduidade.
    """
    # Conecta à base de dados de documentos e grava a folha de assiduidade
    # Insere os dados na tabela 'folhas_assiduidade'
    # Se ocorrer um erro, registra a exceção e fecha a conexão
    logger.info("Gravando folha de assiduidade na base de dados...")
    conn = get_conn_d()
    try:
        cursor = conn.cursor()
        data_registo = timestamp_agora()
        cursor.execute("""
            INSERT INTO folhas_assiduidade (equipa, mes, ano, caminho_ficheiro, data_insercao)
            VALUES (?, ?, ?, ?, ?)
        """, (equipa_id, mes, ano, caminho_pdf, data_registo))
        cursor.execute("SELECT TOP 1 id FROM folhas_assiduidade ORDER BY id DESC")
        folha_id = cursor.fetchone()[0]
        conn.commit()
        logger.info("✅ Folha de assiduidade gravada com sucesso.")
        return folha_id
    except Exception as e:
        logger.exception(f"❌ Erro ao gravar folha de assiduidade: {e}")
        return None
    finally:
        conn.close()

def folha_faltas_bd(equipa_id, mes, ano, caminho_pdf):
    """
    Grava uma folha de faltas na base de dados de documentos (D).
    Args:
        equipa_id (int): ID da equipa responsável.
        mes (str): Mês da folha de faltas (formato 'MM').
        ano (int): Ano da folha de faltas.
        caminho_pdf (str): Caminho do arquivo PDF da folha de faltas.
    Returns:    
        int: ID da folha de faltas gravada, ou None se ocorrer um erro.
    Raises:
        Exception: Se ocorrer um erro ao gravar a folha de faltas.
    """
    # Conecta à base de dados de documentos e grava a folha de faltas
    # Insere os dados na tabela 'folhas_faltas'
    # Se ocorrer um erro, registra a exceção e fecha a conexão
    logger.info("Gravando folha de faltas na base de dados...")
    conn = get_conn_d()
    try:
        cursor = conn.cursor()
        data_registo = timestamp_agora()
        cursor.execute("""
            INSERT INTO folhas_faltas (equipa, mes, ano, caminho_ficheiro, data_insercao)
            VALUES (?, ?, ?, ?, ?)
        """, (equipa_id, mes, ano, caminho_pdf, data_registo))
        cursor.execute("SELECT TOP 1 id FROM folhas_faltas ORDER BY id DESC")
        folha_id = cursor.fetchone()[0]
        conn.commit()
        logger.info("✅ Folha de faltas gravada com sucesso.")
        return folha_id
    except Exception as e:
        logger.exception(f"❌ Erro ao gravar folha de faltas: {e}")
        return None
    finally:
        conn.close()

def carregar_recarregar_equipas(as_dict=True):
    """
    Carrega a lista de equipas da base de dados.

    Args:
        as_dict (bool): Se True, retorna dict {id: nome}. Se False, lista de dicts.

    Returns:
        dict | list: Equipas.
    """
    conn = get_conn_d()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM equipas ORDER BY nome")
        resultados = cursor.fetchall()
        if not resultados:
            logger.warning("Nenhuma equipa encontrada na base de dados.")
        else:
            logger.info(f"{len(resultados)} equipas carregadas.")
        return {id_: nome for id_, nome in resultados} if as_dict else [{"id": id_, "nome": nome} for id_, nome in resultados]
    except Exception as e:
        logger.exception("Erro ao carregar equipas.")
        return {} if as_dict else []
    finally:
        conn.close()
        

def carregar_recarregar_processos():
    """
    Carrega todos os processos da base de dados e associa o nome do cliente pelo NIF.

    Returns:
        list[dict]: Lista de processos com referência, cliente e descrição.
    """
    conn = get_conn_d()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT referencia, nif_cliente, descricao FROM processos")
        dados = cursor.fetchall()
        if not dados:
            logger.warning("Nenhum processo encontrado na base de dados.")
        else:
            logger.info(f"{len(dados)} processos carregados da base de dados.")
    except Exception as e:
        logger.exception("Erro ao carregar processos.")
        return []
    finally:
        conn.close()

    clientes = obter_clientes() or {}
    return [{
        "referencia": ref,
        "nif_cliente": nif,
        "nome_cliente": clientes.get(nif, f"Desconhecido ({nif})"),
        "descricao": desc
    } for ref, nif, desc in dados]


