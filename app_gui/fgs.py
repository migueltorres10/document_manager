# fgs.py
import tkinter as tk

# from Faturas_Emitidas.faturas_emitidas import faturas_emitidas
# from Recibos_Emitidos.recibos_emitidos import recibos_emitidos
# from Guias_Emitidas.guias_emitidas import guias_emitidas

def abrir_janela_fgs(master):
    janela = tk.Toplevel(master)
    janela.title("🏛️ Documentos FGS")
    janela.geometry("300x250")

    tk.Label(janela, text="Selecione o tipo de documento:", font=("Helvetica", 12, "bold")).pack(pady=15)

    tk.Button(janela, text="🧾 Faturas Emitidas (F-E)", width=30, command=lambda: print("Faturas Emitidas")).pack(pady=5)
    tk.Button(janela, text="📃 Recibos Emitidos (R-E)", width=30, command=lambda: print("Recibos Emitidos")).pack(pady=5)
    tk.Button(janela, text="📄 Guias Emitidas (GR-E)", width=30, command=lambda: print("Guias Emitidas")).pack(pady=5)
