import os
import tkinter as tk
from turtle import right
from Faturas.faturas import faturas
from Guias.guias import guias
from core.gui_utils import centralizar_janela
from QR.qr_code import GeradorQRCode
from Digitalizar.digitalizar import digitalizar
from core.constantes import PASTAS
from processos import GestorProcessos
from equipas import GestorEquipas
from Folhas_Obra.folhasobra import folhasobra
from Folhas_Assiduidade.folhasassiduidade import folhasassiduidade 
from Folhas_Faltas.folhasasfaltas import folhasfaltas


def criar_pastas():
    for pasta in PASTAS:
        if not os.path.exists(pasta):
            os.makedirs(pasta)

class PainelPrincipal:
    def centralizar_janela(self):
        centralizar_janela(self.root)
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.root = tk.Tk()
        self.root.title("📂 Arquivador de Documentos")
        self.root.geometry("350x800")
        self.root.resizable(False, False)
        self.centralizar_janela()
        self._criar_widgets()
        self.root.mainloop()

    def _criar_widgets(self):
        
        tk.Label(self.root, text="📋 Selecione uma opção", font=("Helvetica", 16)).pack(pady=20)

        tk.Button(
            self.root, text="🧾 Processar e Visualizar Faturas", width=35, height=2, command=self.abrir_faturas).pack(pady=20)
        
        tk.Button(
            self.root, text="📄 Processar e Visualizar Guias", width=35, height=2, command=self.abrir_guias).pack(pady=20)
        tk.Button(
            self.root, text="📑 Processar e Visualizar Folhas de Obra", width=35, height=2, command=self.abrir_folhas_obra
        ).pack(pady=20)

        tk.Button(
            self.root, text="📅 Processar e Visualizar Folhas de Assiduidade", width=35, height=2, command=self.abrir_folhas_assiduidade).pack(pady=20)
        
        tk.Button(
            self.root, text="❗ Processar e Visualizar Folhas de Faltas", width=35, height=2, command=self.abrir_folhas_faltas
        ).pack(pady=20)
        
        tk.Button(
            self.root, text="📂 Gestor de Processos", width=35, height=2, command=self.abrir_gestor_processos
        ).pack(pady=20)

        tk.Button(
            self.root, text="👥 Gestor de Equipas", width=35, height=2, command=self.abrir_gestor_equipas
        ).pack(pady=20)
        
        
            # Frame para agrupar os dois botões lado a lado
        frame_qr_digital = tk.Frame(self.root, bg="#f0f0f0")
        frame_qr_digital.pack(pady=20, fill="x", expand=True)

        # Distribui igualmente as colunas
        for col in range(2):
            frame_qr_digital.columnconfigure(col, weight=1)

        # QRCode
        tk.Button(
            frame_qr_digital, text="📑 Imprir\nDocumentos", height=4, command=GeradorQRCode
        ).grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Digitalizar
        tk.Button(
            frame_qr_digital, text="📠 Digitalizar\nDocumentos", height=4, command=self.digitalizar
        ).grid(row=0, column=1, padx=5, pady=5, sticky="nsew")


    def abrir_faturas(self):
        faturas()
    
    def abrir_guias(self):
        guias()

    def abrir_folhas_obra(self):
        folhasobra()

    def abrir_folhas_assiduidade(self):
        folhasassiduidade()

    def abrir_folhas_faltas(self):
        folhasfaltas()

    def digitalizar(self):
        digitalizar()

    def abrir_gestor_processos(self):
        gestor = GestorProcessos(on_close=self.centralizar_janela)
        gestor.root.protocol("WM_DELETE_WINDOW", gestor.fechar_janela)
        gestor.root.mainloop()

    def abrir_gestor_equipas(self):
        gestor = GestorEquipas(on_close=self.centralizar_janela)
        gestor.root.protocol("WM_DELETE_WINDOW", gestor.fechar_janela)
        gestor.root.mainloop()


if __name__ == "__main__":
    criar_pastas()
    PainelPrincipal()
