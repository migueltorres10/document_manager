# main_app.py
import tkinter as tk
from app_gui.fornecedores import abrir_janela_fornecedores
from app_gui.internos import abrir_janela_internos
from app_gui.fgs import abrir_janela_fgs
from QR.qr_code import GeradorQRCode
from Digitalizar.digitalizar import digitalizar

class PainelPrincipal:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📂 Gestor de Documentos")
        self.root.geometry("350x400")
        self.root.resizable(False, False)
        self._criar_widgets()
        self.root.mainloop()

    def _criar_widgets(self):
        tk.Label(self.root, text="📋 Selecione uma Categoria", font=("Helvetica", 16, "bold")).pack(pady=30)

        self._adicionar_botao("📦 Documentos de Fornecedores", abrir_janela_fornecedores)
        self._adicionar_botao("🏢 Documentos Internos", abrir_janela_internos)
        self._adicionar_botao("🏛️ Documentos FGS", abrir_janela_fgs)

        self._criar_botoes_utilitarios()

    def _adicionar_botao(self, texto, comando):
        tk.Button(self.root, text=texto, width=35, height=2, command=lambda: comando(self.root)).pack(pady=15)

    def _criar_botoes_utilitarios(self):
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(pady=20, fill="x", expand=True)

        for col in range(2):
            frame.columnconfigure(col, weight=1)

        tk.Button(
            frame, text="📑 Imprimir\nDocumentos", height=4, command=GeradorQRCode
        ).grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        tk.Button(
            frame, text="📠 Digitalizar\nDocumentos", height=4, command=digitalizar
        ).grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

if __name__ == "__main__":
    PainelPrincipal()
