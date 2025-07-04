import tkinter as tk
from tkinter import ttk, messagebox
import qrcode
import calendar
import os
from config import connect_bd
from core.db_helpers import carregar_equipas

# --- Função principal para gerar o QR ---
def gerar_qr():
    ano = entry_ano.get()
    mes_nome = combo_mes.get()
    equipa = combo_equipa.get()

    if not ano.isdigit() or not mes_nome or not equipa:
        messagebox.showerror("Erro", "Preencha todos os campos corretamente.")
        return

    # Converter mês para número
    try:
        mes_num = list(calendar.month_name).index(mes_nome)
    except ValueError:
        messagebox.showerror("Erro", "Mês inválido.")
        return

    mes_formatado = f"{mes_num:02d}"
    dados = f"Ano: {ano}\nMês: {mes_formatado}\nEquipa: {equipa}"
    qr = qrcode.make(dados)

    # Criar nome de arquivo
    nome_arquivo = f"qr_{ano}_{mes_formatado}_{equipa.replace(' ', '_')}.png"
    qr.save(nome_arquivo)

    messagebox.showinfo("Sucesso", f"QR Code salvo como {nome_arquivo}")

# --- Interface Tkinter ---
root = tk.Tk()
root.title("Gerador de QR Code de Equipa")

# Ano
tk.Label(root, text="Ano:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
entry_ano = tk.Entry(root)
entry_ano.grid(row=0, column=1, padx=5, pady=5)

# Mês
tk.Label(root, text="Mês:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
combo_mes = ttk.Combobox(root, values=list(calendar.month_name)[1:], state="readonly")
combo_mes.grid(row=1, column=1, padx=5, pady=5)

# Equipa
tk.Label(root, text="Equipa:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
equipas = carregar_equipas()
nomes_equipas = [e["nome"] for e in equipas]
combo_equipa = ttk.Combobox(root, values=nomes_equipas, state="readonly")
combo_equipa.grid(row=2, column=1, padx=5, pady=5)

# Botão
btn_gerar = tk.Button(root, text="Gerar QR Code", command=gerar_qr)
btn_gerar.grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()
