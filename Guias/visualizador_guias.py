import os
import tkinter as tk
from tkinter import ttk
import datetime

from core.gui_utils import (
    filtrar_combobox_por_texto,
    centralizar_janela,
    confirmar_eliminacao,
    mostrar_mensagem
)
from core.pdf_utils import (
    listar_pdfs,
    abrir_pdf_externo,
    fechar_sumatra
)
from core.db_helpers import (
    obter_fornecedores,
    gravar_guia_bd,
    carregar_processos
)

from core.ocr_utils import (
    extrair_dados_qrcode_de_pdf
)

from core.file_utils import (
    mover_pdf_para_pasta_destino,
    renomear_pdf
)
from processos import GestorProcessos


class VisualizadorGuias:
    def __init__(self, pasta_pdf, base_dir):
        self.pasta_pdf = pasta_pdf
        self.base_dir = base_dir
        self.pdfs = listar_pdfs(pasta_pdf)
        self.index_atual = 0
        self.fornecedores = obter_fornecedores()
        self.processos = carregar_processos()

        if not self.pdfs:
            mostrar_mensagem("erro", "Nenhuma Guia encontrada na pasta 'separados'.")
            return

        self._inicializar_interface()
        self.abrir_pdf_atual()

    def _inicializar_interface(self):
        self.root = tk.Toplevel()
        self.root.title("Visualizador de Guias")
        self.root.geometry("350x600")
        centralizar_janela(self.root)
        self.root.attributes('-topmost', 1)

        self.fornecedor_var = tk.StringVar()
        self.processo_var = tk.StringVar()
        self.entry_ano = tk.Entry(self.root)
        self.entry_numero = tk.Entry(self.root)
        self.entry_data = tk.Entry(self.root)

        self._criar_formulario()
        self._criar_navegacao()
        self._criar_acoes()

    def _criar_formulario(self):
        self._adicionar_label_entry("Fornecedor:", self.fornecedor_var, is_combobox=True)
        self._adicionar_label_entry("Ano:", self.entry_ano)
        self._adicionar_label_entry("Número do Documento:", self.entry_numero)
        self._adicionar_label_entry("Data do Documento:", self.entry_data)
        self._adicionar_label_entry("Número de Processo:", self.processo_var, is_combobox="processo")

    def _criar_navegacao(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)
        tk.Button(frame, text="◀ Anterior", width=12, command=self.mostrar_anterior).pack(side="left", padx=5)
        tk.Button(frame, text="Próximo ▶", width=12, command=self.mostrar_proximo).pack(side="left", padx=5)
        tk.Button(self.root, text="📎 Gerir Processos", command=self.abrir_gestor_processos).pack(pady=5)

    def _criar_acoes(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=15)
        tk.Button(frame, text="📂 Salvar", width=25, command=self.salvar_dados).pack(pady=3)
        tk.Button(frame, text="🗑 Eliminar", width=25, command=self.eliminar_pdf).pack(pady=3)
        tk.Button(frame, text="⏹ Terminar", width=25, command=self.terminar).pack(pady=3)

    def _adicionar_label_entry(self, label, var, is_combobox=False):
        tk.Label(self.root, text=label).pack(pady=5)
        if is_combobox:
            combo = ttk.Combobox(self.root, textvariable=var, width=40)
            if "Fornecedor" in label:
                combo["values"] = list(self.fornecedores.values())
                combo.bind("<KeyRelease>", lambda e: filtrar_combobox_por_texto(combo, self.fornecedores, var.get()))
                self.combo_fornecedor = combo
            elif "Processo" in label:
                valores = [f"{p['referencia']} - {p['nome_cliente']}" for p in self.processos]
                combo["values"] = valores
                combo.bind("<KeyRelease>", lambda e: filtrar_combobox_por_texto(combo, {
                    p["referencia"]: p["nome_cliente"] for p in self.processos
                }, var.get()))
                self.combo_processo = combo
            combo.pack()
        else:
            var.pack()

    def abrir_pdf_atual(self):
        if not self.pdfs:
            return
        fechar_sumatra()
        caminho_pdf = os.path.join(self.pasta_pdf, self.pdfs[self.index_atual])
        abrir_pdf_externo(caminho_pdf)
        self.preencher_dados_qr(caminho_pdf)

    def mostrar_anterior(self):
        if self.index_atual > 0:
            self.index_atual -= 1
            self.abrir_pdf_atual()

    def mostrar_proximo(self):
        if self.index_atual < len(self.pdfs) - 1:
            self.index_atual += 1
            self.abrir_pdf_atual()

    def terminar(self):
        fechar_sumatra()
        self.root.destroy()

    def abrir_gestor_processos(self):
        self.root.after(100, lambda: GestorProcessos(on_close=self.recarregar_processos))

    def recarregar_processos(self):
        self.processos = carregar_processos()
        self.combo_processo["values"] = [f"{p['referencia']} - {p['nome_cliente']}" for p in self.processos]

    def salvar_dados(self):
        fornecedor_nome = self.fornecedor_var.get().strip()
        ano = self.entry_ano.get().strip()
        numero = self.entry_numero.get().strip()
        data = self.entry_data.get().strip()
        processo_str = self.processo_var.get().strip()
        processo = processo_str.split(" - ")[0] if processo_str else ""

        if not all([fornecedor_nome, ano, numero, data]):
            mostrar_mensagem("aviso", "Preencha todos os campos obrigatórios.")
            return

        fornecedor_nif = next((nif for nif, nome in self.fornecedores.items() if nome == fornecedor_nome), None)
        if not fornecedor_nif:
            mostrar_mensagem("erro", "Fornecedor não encontrado na base de dados.")
            return

        try:
            data_formatada = datetime.datetime.strptime(data, "%Y-%m-%d").date()
        except ValueError:
            mostrar_mensagem("erro", "Formato de data inválido. Use YYYY-MM-DD.")
            return

        nome_pdf = self.pdfs[self.index_atual]
        caminho_pdf = os.path.join(self.pasta_pdf, nome_pdf)

        try:
            destino = mover_pdf_para_pasta_destino(caminho_pdf, fornecedor_nome, ano, os.path.join(self.base_dir, "arquivados"))
            final = renomear_pdf(destino, numero, ano)

            gravar_guia_bd(fornecedor_nif, numero, ano, data_formatada, processo, final)

            mostrar_mensagem("info", "Guia gravada e movida com sucesso.")
            del self.pdfs[self.index_atual]

            if self.pdfs:
                if self.index_atual >= len(self.pdfs):
                    self.index_atual = len(self.pdfs) - 1
                self.abrir_pdf_atual()
            else:
                mostrar_mensagem("info", "Nenhum PDF restante.")
                self.root.destroy()

        except FileExistsError as fe:
            mostrar_mensagem("erro", f"Ficheiro duplicado: {fe}")
        except Exception as e:
            mostrar_mensagem("erro", f"Erro ao salvar guia: {e}")

    def eliminar_pdf(self):
        if not self.pdfs:
            return

        nome_pdf = self.pdfs[self.index_atual]
        caminho_pdf = os.path.join(self.pasta_pdf, nome_pdf)

        def acao():
            if os.path.exists(caminho_pdf):
                os.remove(caminho_pdf)
            del self.pdfs[self.index_atual]
            if self.pdfs:
                if self.index_atual >= len(self.pdfs):
                    self.index_atual = len(self.pdfs) - 1
                self.abrir_pdf_atual()
            else:
                mostrar_mensagem("info", "Nenhum PDF restante.")
                self.root.destroy()

        confirmar_eliminacao(nome_pdf, acao)

    def preencher_dados_qr(self, caminho_pdf):
        self.entry_ano.delete(0, tk.END)
        self.entry_data.delete(0, tk.END)
        self.entry_numero.delete(0, tk.END)
        self.fornecedor_var.set("")
        self.processo_var.set("")

        dados_qr = extrair_dados_qrcode_de_pdf(caminho_pdf)
        if not dados_qr:
            return

        fornecedor_nome = self.fornecedores.get(dados_qr.get("nif_emitente"))
        if fornecedor_nome:
            self.fornecedor_var.set(fornecedor_nome)

        data_qr = dados_qr.get("data_doc", "").strip()
        data_formatada = None
        for formato in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y%m%d"):
            try:
                data_formatada = datetime.datetime.strptime(data_qr, formato).date()
                break
            except ValueError:
                continue

        if data_formatada:
            self.entry_data.insert(0, data_formatada.isoformat())
            self.entry_ano.insert(0, str(data_formatada.year))

        self.entry_numero.insert(0, dados_qr.get("numero_doc", ""))
