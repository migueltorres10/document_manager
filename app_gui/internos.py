# internos.py
import tkinter as tk
from Folhas_Obra.folhasobra import folhasobra
from Folhas_Faltas.folhasasfaltas import folhasfaltas
from Folhas_Assiduidade.folhasassiduidade import folhasassiduidade

def abrir_janela_internos(master):
    janela = tk.Toplevel(master)
    janela.title("🏢 Documentos Internos")
    janela.geometry("300x250")

    tk.Label(janela, text="Selecione o tipo de documento:", font=("Helvetica", 12, "bold")).pack(pady=15)

    tk.Button(janela, text="🧾 Folhas de Obra", width=30, command=folhasobra).pack(pady=5)
    tk.Button(janela, text="📋 Folhas de Faltas", width=30, command=folhasfaltas).pack(pady=5)
    tk.Button(janela, text="📅 Folhas de Assiduidade", width=30, command=folhasassiduidade).pack(pady=5)
