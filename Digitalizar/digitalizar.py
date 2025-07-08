import os
import subprocess
import tkinter as tk
from tkinter import messagebox
from core.gui_utils import centralizar_janela
from core.constantes import TIPOS_DOCUMENTOS
from datetime import datetime
from config import HP_SCAN_EXECUTABLE
import shutil
import time

PASTA_PADRAO_HP = os.path.join(os.path.dirname(__file__), "Digitalizações")
os.makedirs(PASTA_PADRAO_HP, exist_ok=True)


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

    def digitalizar_hp():
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
            # Lista arquivos antes da digitalização
            arquivos_antes = set(os.listdir(PASTA_PADRAO_HP))

            subprocess.Popen([HP_SCAN_EXECUTABLE])  # abre interface de digitalização

            messagebox.showinfo("Digitalização", "Digitalize o documento e clique OK quando terminar.")

            # Espera o novo arquivo aparecer
            tempo_limite = 30  # segundos
            inicio = time.time()
            novo_arquivo = None

            while time.time() - inicio < tempo_limite:
                arquivos_depois = set(os.listdir(PASTA_PADRAO_HP))
                novos = arquivos_depois - arquivos_antes
                if novos:
                    # Pega o mais recente
                    novos_ordenados = sorted(novos, key=lambda f: os.path.getmtime(os.path.join(PASTA_PADRAO_HP, f)), reverse=True)
                    novo_arquivo = novos_ordenados[0]
                    break
                time.sleep(1)

            if not novo_arquivo:
                messagebox.showerror("Erro", "Nenhum novo ficheiro encontrado.")
                return

            origem = os.path.join(PASTA_PADRAO_HP, novo_arquivo)
            shutil.move(origem, output_path)
            messagebox.showinfo("Sucesso", f"Ficheiro digitalizado:\n{output_path}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro na digitalização:\n{e}")

    tk.Button(janela, text="Iniciar digitalização", command=digitalizar_hp).pack(pady=20)
    tk.Button(janela, text="Fechar", command=janela.destroy).pack(pady=10)
