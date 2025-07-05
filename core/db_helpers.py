# core/db_helpers.py

from datetime import datetime
from config import connect_bd
from core.constantes import MESES_MAP

def obter_fornecedores():
    conn = connect_bd("S")
    fornecedores = {}
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT RTRIM(ncont), RTRIM(nome) FROM fl")
        fornecedores = {nif: nome for nif, nome in cursor.fetchall()}
    except Exception as e:
        print(f"❌ Erro ao obter fornecedores: {e}")
    finally:
        conn.close()
    return fornecedores

def obter_clientes():
    conn = connect_bd("S")
    clientes = {}
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT RTRIM(ncont), RTRIM(nome) FROM cl")
        clientes = {nif: nome for nif, nome in cursor.fetchall()}
    except Exception as e:
        print(f"❌ Erro ao obter clientes: {e}")
    finally:
        conn.close()
    return clientes

def carregar_processos():
    conn = connect_bd("D")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT referencia, nif_cliente, descricao FROM processos")
        dados = cursor.fetchall()
    finally:
        conn.close()

    clientes = obter_clientes()
    return [{
        "referencia": ref,
        "nif_cliente": nif,
        "nome_cliente": clientes.get(nif, "Desconhecido"),
        "descricao": desc
    } for ref, nif, desc in dados]

def carregar_equipas(as_dict=True):
    from config import connect_bd
    conn = connect_bd("D")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM equipas ORDER BY nome")
    resultados = cursor.fetchall()
    conn.close()

    if as_dict:
        return {id_: nome for id_, nome in resultados}
    else:
        return [{"id": id_, "nome": nome} for id_, nome in resultados]


def gravar_guia_bd(fornecedor, numero, ano, data, processo, caminho_pdf):
    conn = connect_bd("D")
    try:
        cursor = conn.cursor()
        data_registo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO guias (fornecedor, numero_doc, data_doc, ano, processo, caminho_ficheiro, data_insercao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (fornecedor, numero, data, ano, processo, caminho_pdf, data_registo))
        conn.commit()
        print("✅ Guia gravada com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao gravar guia: {e}")
    finally:
        conn.close()

def gravar_fatura_bd(fornecedor, tipo_doc, numero, ano, data, base, iva, total, processo, caminho_pdf):
    conn = connect_bd("D")
    try:
        cursor = conn.cursor()
        data_registo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO documentos_faturacao (
                fornecedor, tipo_doc, numero_doc, ano, data_doc,
                valor_base, iva, total, processo, caminho_ficheiro, data_insercao
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (fornecedor, tipo_doc, numero, ano, data, base, iva, total, processo, caminho_pdf, data_registo))
        conn.commit()
        print("✅ Fatura gravada com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao gravar fatura: {e}")
    finally:
        conn.close()

def folha_obra_bd(processo, cliente, equipa, descricao, ano, caminho_pdf):
    conn = connect_bd("D")
    try:
        cursor = conn.cursor()
        data_registo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO folhas_obra (processo, cliente, equipa, descricao, ano, caminho_ficheiro, data_insercao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (processo, cliente, equipa, descricao, ano, caminho_pdf, data_registo))
        cursor.execute("SELECT TOP 1 id FROM folhas_obra ORDER BY id DESC")
        folha_id = cursor.fetchone()[0]
        conn.commit()
        print("✅ Folha de obra gravada com sucesso.")
        return folha_id
    except Exception as e:
        print(f"❌ Erro ao gravar folha de obra: {e}")
        return None
    finally:
        conn.close()

def inserir_meses_folha_obra(folha_id, lista_meses):
    conn = connect_bd("D")
    try:
        cursor = conn.cursor()
        for mes_nome in lista_meses:
            numero_mes = MESES_MAP.get(mes_nome)
            if numero_mes:
                cursor.execute("""
                    INSERT INTO folhas_obra_meses (folha_id, mes)
                    VALUES (?, ?)
                """, (folha_id, numero_mes))
            else:
                print(f"⚠️ Mês inválido: {mes_nome}")
        conn.commit()
        print("✅ Meses associados à folha de obra.")
    except Exception as e:
        print(f"❌ Erro ao inserir meses: {e}")
    finally:
        conn.close()

def folha_assiduidade_bd(equipa_id, mes, ano, caminho_pdf):
    conn = connect_bd("D")
    try:
        cursor = conn.cursor()
        data_registo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO folhas_assiduidade (equipa, mes, ano, caminho_ficheiro, data_insercao)
            VALUES (?, ?, ?, ?, ?)
        """, (equipa_id, mes, ano, caminho_pdf, data_registo))
        cursor.execute("SELECT TOP 1 id FROM folhas_assiduidade ORDER BY id DESC")
        folha_id = cursor.fetchone()[0]
        conn.commit()
        print("✅ Folha de assiduidade gravada com sucesso.")
        return folha_id
    except Exception as e:
        print(f"❌ Erro ao gravar folha de assiduidade: {e}")
        return None
    finally:
        conn.close()

def folha_faltas_bd(equipa_id, mes, ano, caminho_pdf):
    conn = connect_bd("D")
    try:
        cursor = conn.cursor()
        data_registo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO folhas_faltas (equipa, mes, ano, caminho_ficheiro, data_insercao)
            VALUES (?, ?, ?, ?, ?)
        """, (equipa_id, mes, ano, caminho_pdf, data_registo))
        cursor.execute("SELECT TOP 1 id FROM folhas_faltas ORDER BY id DESC")
        folha_id = cursor.fetchone()[0]
        conn.commit()
        print("✅ Folha de faltas gravada com sucesso.")
        return folha_id
    except Exception as e:
        print(f"❌ Erro ao gravar folha de faltas: {e}")
        return None
    finally:
        conn.close()
