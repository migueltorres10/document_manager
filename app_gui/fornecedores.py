# fornecedores.py
import tkinter as tk
from Guias.guias import guias
from Faturas.faturas import faturas
# from Recibos.recibos import recibos  # Substitua se tiver esse módulo

def abrir_janela_fornecedores(master):
    janela = tk.Toplevel(master)
    janela.title("📦 Documentos de Fornecedores")
    janela.geometry("300x250")

    tk.Label(janela, text="Selecione o tipo de documento:", font=("Helvetica", 12, "bold")).pack(pady=15)

    tk.Button(janela, text="📄 Guias", width=30, command=guias).pack(pady=5)
    tk.Button(janela, text="🧾 Faturas", width=30, command=faturas).pack(pady=5)
    tk.Button(janela, text="📃 Recibos", width=30, command=lambda: print("Recibos - em desenvolvimento")).pack(pady=5)
