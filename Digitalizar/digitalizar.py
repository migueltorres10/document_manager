## Digitalizar/digitalizar.py

import os
import subprocess
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import shutil
import time

from core.gui_utils import centralizar_janela
from core.constantes import PASTAS_DOCUMENTOS
from config import HP_SCAN_EXECUTABLE
from core.logger import configurar_logger

# Logger configurado
logger = configurar_logger(__name__)

# Pasta padrão onde os ficheiros digitalizados são colocados pelo software da HP
PASTA_PADRAO_HP = os.path.join(os.path.dirname(__file__), "Digitalizações")
os.makedirs(PASTA_PADRAO_HP, exist_ok=True)


def digitalizar():
    """
    Abre uma janela tkinter para iniciar o processo de digitalização via scanner HP.
    O utilizador escolhe o tipo de documento e o ficheiro digitalizado é automaticamente
    movido para a pasta correta com nome formatado.
    """
    janela = tk.Toplevel()
    janela.title("Digitalizar Documento")
    janela.geometry("350x250")
    centralizar_janela(janela)
    janela.attributes('-topmost', 1)

    opcoes_nomes = list(PASTAS_DOCUMENTOS.keys())
    tipo_var = tk.StringVar(value=opcoes_nomes[0])

    tk.Label(janela, text="Selecione o tipo de documento:").pack(pady=10)
    tk.OptionMenu(janela, tipo_var, *opcoes_nomes).pack(pady=5)

    def digitalizar_hp():
        """
        Inicia o processo de digitalização usando o executável da HP,
        aguarda que um novo PDF apareça na pasta temporária,
        e move o ficheiro digitalizado para o destino apropriado.
        """
        nome_tipo = tipo_var.get()
        if nome_tipo not in PASTAS_DOCUMENTOS:
            logger.error("Tipo de documento inválido selecionado.")
            messagebox.showerror("Erro", "Tipo de documento inválido.")
            return

        pasta_destino = os.path.join(nome_tipo, "entrada")
        os.makedirs(pasta_destino, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        sigla = PASTAS_DOCUMENTOS[nome_tipo]
        nome_ficheiro = f"{sigla}_{timestamp}.pdf"
        output_path = os.path.join(pasta_destino, nome_ficheiro)

        try:
            if not HP_SCAN_EXECUTABLE or not os.path.exists(HP_SCAN_EXECUTABLE):
                logger.error("Caminho do scanner HP inválido ou não definido.")
                messagebox.showerror("Erro", "Scanner não configurado corretamente.")
                return

            logger.info("🖨️ Iniciando digitalização...")
            arquivos_antes = set(os.listdir(PASTA_PADRAO_HP))

            subprocess.Popen([HP_SCAN_EXECUTABLE])
            messagebox.showinfo("Digitalização", "Digitalize o documento e clique OK quando terminar.")

            tempo_limite = 30  # segundos
            inicio = time.time()
            novo_arquivo = None

            while time.time() - inicio < tempo_limite:
                
                arquivos_depois = set(os.listdir(PASTA_PADRAO_HP))
                novos = arquivos_depois - arquivos_antes
                if novos:
                    novos_ordenados = sorted(
                        novos,
                        key=lambda f: os.path.getmtime(os.path.join(PASTA_PADRAO_HP, f)),
                        reverse=True
                    )
                    novo_arquivo = novos_ordenados[0]
                    break
                time.sleep(1)

            if not novo_arquivo:
                logger.warning("Nenhum ficheiro novo detetado após digitalização.")
                messagebox.showerror("Erro", "Nenhum novo ficheiro encontrado.")
                return

            origem = os.path.join(PASTA_PADRAO_HP, novo_arquivo)
            shutil.move(origem, output_path)
            logger.info(f"📄 Ficheiro digitalizado guardado em: {output_path}")
            messagebox.showinfo("Sucesso", f"Ficheiro digitalizado:\n{output_path}")

        except Exception as e:
            logger.exception("Erro durante o processo de digitalização.")
            messagebox.showerror("Erro", f"Ocorreu um erro:\n{e}")

    tk.Button(janela, text="Iniciar digitalização", command=digitalizar_hp).pack(pady=20)
    tk.Button(janela, text="Fechar", command=janela.destroy).pack(pady=10)
