import os
import tkinter as tk
from Faturas.faturas import faturas
from Guias.guias import guias
from core.gui_utils import centralizar_janela

class PainelPrincipal:
    def centralizar_janela(self):
        centralizar_janela(self.root)
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.root = tk.Tk()
        self.root.title("📂 Arquivador de Documentos")
        self.root.geometry("350x600")
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
        
        tk.Label(self.root, text="v2.1", font=("Arial", 8), fg="gray").pack(side="bottom", pady=5)


    def abrir_faturas(self):
        faturas()
    
    def abrir_guias(self):
        guias()

if __name__ == "__main__":
    PainelPrincipal()
