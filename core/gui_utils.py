# core/gui_utils.py
import tkinter as tk
from tkinter import messagebox, ttk

def filtrar_combobox_por_texto(combobox, clientes_dict, texto):
    texto = texto.lower()
    valores = [
        f"{nif} - {nome}"
        for nif, nome in clientes_dict.items()
        if texto in nome.lower() or texto in nif.lower()
    ]
    combobox["values"] = valores

def atualizar_listbox_por_filtro(listbox, dados, campos, termo, formato_linha):
    listbox.delete(0, "end")
    termo = termo.lower()
    for item in dados:
        if any(termo in str(item[campo]).lower() for campo in campos):
            listbox.insert("end", formato_linha(item))

def centralizar_janela(janela):
    janela.update_idletasks()
    largura = janela.winfo_width()
    altura = janela.winfo_height()
    x = (janela.winfo_screenwidth() // 2) - (largura // 2)
    y = (janela.winfo_screenheight() // 2) - (altura // 2)
    janela.geometry(f"{largura}x{altura}+{x}+{y}")

def mostrar_mensagem(tipo, texto):
    if tipo == "info":
        messagebox.showinfo("Informação", texto)
    elif tipo == "erro":
        messagebox.showerror("Erro", texto)
    elif tipo == "aviso":
        messagebox.showwarning("Aviso", texto)

def confirmar_eliminacao(nome, acao_callback):
    resposta = messagebox.askyesno("Confirmar eliminação", f"Deseja eliminar '{nome}'?")
    if resposta:
        try:
            acao_callback()
            mostrar_mensagem("info", f"'{nome}' eliminado com sucesso.")
        except Exception as e:
            mostrar_mensagem("erro", f"Erro ao eliminar '{nome}': {e}")
