import os
import subprocess
import tkinter as tk
from tkinter import messagebox
from core.gui_utils import centralizar_janela
from core.constantes import TIPOS_DOCUMENTOS
from datetime import datetime
from config import NAPS2_PATH


def digitalizar():
    janela = tk.Toplevel()
    janela.title("Digitalizar Documento")
    janela.geometry("350x250")
    centralizar_janela(janela)
    janela.attributes('-topmost', 1)

    opcoes_nomes = list(TIPOS_DOCUMENTOS.keys())
    tipo_var = tk.StringVar(value=opcoes_nomes[0])

    tk.Label(janela, text="Selecione o tipo de documento:").pack(pady=10)
    tk.OptionMenu(janela, tipo_var, *opcoes_nomes).pack(pady=5)

    def digitalizar_naps2():
        nome_tipo = tipo_var.get()
        if nome_tipo not in TIPOS_DOCUMENTOS:
            messagebox.showerror("Erro", "Tipo inválido.")
            return

        pasta_destino = os.path.join(nome_tipo, "entrada")
        os.makedirs(pasta_destino, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        sigla = TIPOS_DOCUMENTOS[nome_tipo]
        nome_ficheiro = f"{sigla}_{timestamp}.pdf"
        output_path = os.path.join(pasta_destino, nome_ficheiro)



        try:
            subprocess.run([
                NAPS2_PATH,
                "scan",
                "--output", output_path,
                "--profile", "Default"
            ], check=True)

            messagebox.showinfo("Sucesso", f"Ficheiro digitalizado:\n{output_path}")

        except FileNotFoundError:
            messagebox.showerror("Erro", f"NAPS2 Console não encontrado em:\n{NAPS2_PATH}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Erro ao digitalizar", f"Erro durante a digitalização:\n{e}")

    tk.Button(janela, text="Iniciar digitalização", command=digitalizar_naps2).pack(pady=20)
    tk.Button(janela, text="Fechar", command=janela.destroy).pack(pady=10)
