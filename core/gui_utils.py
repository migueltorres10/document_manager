# core/gui_utils.py

import tkinter as tk
from tkinter import messagebox, Toplevel
from core.logger import configurar_logger
logger = configurar_logger(__name__)


def filtrar_combobox_por_texto(combobox, clientes_dict, texto):
    """
    Filtra os valores de um combobox com base no texto fornecido.
    Args:
        combobox (ttk.Combobox): O combobox a ser filtrado.
        clientes_dict (dict): Dicionário com NIFs como chaves e nomes como valores.
        texto (str): Texto a ser pesquisado no combobox.
    Returns:
        None: Atualiza o combobox com os valores filtrados.
    """

    try:
        texto = texto.lower()
        valores = [
            f"{nif} - {nome}"
            for nif, nome in clientes_dict.items()
            if texto in nome.lower() or texto in str(nif).lower()
        ]
        combobox["values"] = valores
        logger.debug(f"Combobox atualizado com {len(valores)} valores para filtro: '{texto}'")
    except Exception as e:
        logger.exception(f"Erro ao filtrar combobox: {e}")

def atualizar_listbox_por_filtro(listbox, dados, campos, termo, formato_linha):
    """
    Atualiza um Listbox com os dados filtrados com base no termo de pesquisa.
    Args:
        listbox (tk.Listbox): O Listbox a ser atualizado.
        dados (list): Lista de dicionários com os dados a serem filtrados.
        campos (list): Lista de chaves dos dicionários a serem pesquisadas.
        termo (str): Termo de pesquisa para filtrar os dados.
        formato_linha (function): Função que formata cada linha a ser exibida no Listbox.
    Returns:
        None: Atualiza o Listbox com os dados filtrados.
    """
    try:
        listbox.delete(0, "end")
        termo = termo.lower()
        total = 0

        for item in dados:
            if any(termo in str(item[campo]).lower() for campo in campos):
                listbox.insert("end", formato_linha(item))
                total += 1

        logger.debug(f"Listbox filtrado com termo '{termo}'. {total} itens exibidos.")
    except Exception as e:
        logger.exception(f"Erro ao atualizar listbox: {e}")

def centralizar_janela(janela):
    """
    Centraliza a janela na tela.
    Args:
        janela (tk.Tk): A janela a ser centralizada.
    Returns:
        None: Atualiza a geometria da janela para centralizá-la.
    """
    try:
        janela.update_idletasks()
        largura = janela.winfo_width()
        altura = janela.winfo_height()
        x = (janela.winfo_screenwidth() // 2) - (largura // 2)
        y = (janela.winfo_screenheight() // 2) - (altura // 2)
        janela.geometry(f"{largura}x{altura}+{x}+{y}")
        logger.debug("Janela centralizada com sucesso.")
    except Exception as e:
        logger.exception(f"Erro ao centralizar janela: {e}")

def mostrar_mensagem(tipo, texto, parent=None):
    """
    Mostra uma mensagem ao usuário com base no tipo especificado.
    Args:
        tipo (str): Tipo da mensagem ("info", "erro", "aviso").
        texto (str): Texto da mensagem a ser exibida.
        parent (tk.Tk or None): Janela pai para a caixa de diálogo. Se None, cria uma janela invisível.
    Returns:
        None: Exibe a mensagem apropriada na interface gráfica.
    """
    if parent is None:
        parent = tk.Tk()
        parent.withdraw()

    # Janela auxiliar invisível para forçar foco
    top = Toplevel(parent)
    top.withdraw()
    top.attributes('-topmost', True)
    top.update()

    logger.debug(f"Mostrando mensagem do tipo '{tipo}': {texto}")
    if tipo == "info":
        messagebox.showinfo("Informação", texto, parent=top)
    elif tipo == "erro":
        messagebox.showerror("Erro", texto, parent=top)
    elif tipo == "aviso":
        messagebox.showwarning("Aviso", texto, parent=top)
    else:
        logger.warning(f"Tipo de mensagem desconhecido: {tipo}")
        messagebox.showinfo("Mensagem", texto, parent=top)
    top.destroy()

def confirmar_eliminacao(nome, acao_callback):
    """
    Solicita confirmação para eliminar um item e executa a ação de eliminação se confirmado.
    Args:
        nome (str): Nome do item a ser eliminado.
        acao_callback (function): Função a ser chamada se a eliminação for confirmada.
    Returns:
        None: Exibe uma caixa de diálogo de confirmação e executa a ação se confirmado.
    """
    try:
        resposta = messagebox.askyesno("Confirmar eliminação", f"Deseja eliminar '{nome}'?")
        if resposta:
            acao_callback()
            logger.info(f"Item '{nome}' eliminado com sucesso.")
            mostrar_mensagem("info", f"'{nome}' eliminado com sucesso.")
        else:
            logger.debug(f"Eliminação de '{nome}' cancelada pelo utilizador.")
    except Exception as e:
        logger.exception(f"Erro ao eliminar '{nome}': {e}")
        mostrar_mensagem("erro", f"Erro ao eliminar '{nome}': {e}")