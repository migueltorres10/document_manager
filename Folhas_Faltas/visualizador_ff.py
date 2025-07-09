## folhas_faltas/visualizador_ff.py

import os
import tkinter as tk
from tkinter import ttk
from core.pdf_utils import rodar_pdf_90graus
from core.logger import configurar_logger
logger = configurar_logger(__name__)


from core.gui_utils import (
    filtrar_combobox_por_texto,
    centralizar_janela,
    confirmar_eliminacao,
    mostrar_mensagem
)
from core.pdf_utils import (
    listar_pdfs,
)
from core.db_helpers import (
    carregar_recarregar_equipas,
    folha_faltas_bd
)
from core.ocr_utils import ler_dados_qr

from core.file_utils import (
    mover_pdf_equipa
)

from core.visualizador_utils import (
    abrir_pdf_atual_com_rotacao,
    mostrar_anterior,
    mostrar_proximo,
    terminar
)

from core.constantes import (
    MESES,
    MESES_MAP,
)

from equipas import GestorEquipas


class VisualizadorFolhasFaltas:
    """
    Classe para visualizar e gerenciar folhas de faltas PDF.
    Permite navegar entre folhas, preencher dados, salvar e eliminar folhas.
    """
    def abrir_gestor_equipas(self):
        self.root.after(100, lambda: GestorEquipas(on_close=self.recarregar_equipas))

    def __init__(self, pasta_pdf, base_dir):
        self.pasta_pdf = pasta_pdf
        self.base_dir = base_dir
        self.pdfs = listar_pdfs(pasta_pdf)
        self.index_atual = 0
        self.equipas = carregar_recarregar_equipas(as_dict=True)
        self.meses_var = []

        if not self.pdfs:
            mostrar_mensagem("erro", "Nenhuma folha de assiduídade encontrada.")
            logger.warning("Nenhuma folha de faltas encontrada na pasta 'separados'.")
            return

        self._inicializar_interface()
        self.abrir_pdf_atual()

    def _inicializar_interface(self):
        self.root = tk.Toplevel()
        self.root.title("Visualizador de Folhas de Faltas")
        self.root.geometry("350x750")
        centralizar_janela(self.root)
        self.root.attributes('-topmost', 1)

        self.equipa_var = tk.StringVar()
        self.ano_var = tk.StringVar()

        self._criar_formulario()
        self._criar_navegacao()
        self._criar_acoes()

    def _criar_formulario(self):
        self._adicionar_label_entry("Equipa:", self.equipa_var, is_combobox="equipa")
        self._adicionar_label_entry("Ano:", self.ano_var)

        #Seleção de meses
        frame_meses = tk.LabelFrame(self.root, text="Meses de Trabalho")
        frame_meses.pack(pady=10)

        self.mes_var = tk.StringVar(value="")  # Apenas um mês

        for i, mes in enumerate(MESES):
            rb = tk.Radiobutton(
                frame_meses,
                text=mes,
                variable=self.mes_var,
                value=mes
            )
            rb.grid(row=i // 3, column=i % 3, sticky="w", padx=5, pady=2)

    def _criar_navegacao(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)
        tk.Button(frame, text="◀ Anterior", width=12, command=self.mostrar_anterior).pack(side="left", padx=5)
        tk.Button(frame, text="Próximo ▶", width=12, command=self.mostrar_proximo).pack(side="left", padx=5)
        tk.Button(self.root, text="🧾 Gerir Equipas", command=self.abrir_gestor_equipas).pack(pady=5)

    def _criar_acoes(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=15)
        tk.Button(frame, text="📂 Salvar", width=25, command=self.salvar_dados).pack(pady=3)
        tk.Button(frame, text="🗑 Eliminar", width=25, command=self.eliminar_pdf).pack(pady=3)
        tk.Button(frame, text="⏹ Terminar", width=25, command=self.terminar).pack(pady=3)

    def _adicionar_label_entry(self, texto, var, is_combobox=False):
        tk.Label(self.root, text=texto).pack(pady=5)
        if is_combobox:
            combo = ttk.Combobox(self.root, textvariable=var, state="normal", width=40)
            if is_combobox == "equipa":
                valores = [f"{k} - {v}" for k, v in self.equipas.items()]
                combo["values"] = valores
                combo.bind("<KeyRelease>", self.filtrar_equipas)
                self.combo_equipa = combo
            combo.pack(pady=5)
        else:
            entry = tk.Entry(self.root, textvariable=var, width=40)
            entry.pack(pady=5)

    def abrir_pdf_atual(self):
        abrir_pdf_atual_com_rotacao(self.pdfs, self.index_atual, self.pasta_pdf, self.preencher_dados_qr)

    def mostrar_anterior(self):
        self.index_atual = mostrar_anterior(self.pdfs, self.index_atual, self.abrir_pdf_atual, doc_nome="folha")

    def mostrar_proximo(self):
        self.index_atual = mostrar_proximo(self.pdfs, self.index_atual, self.abrir_pdf_atual, doc_nome="folha")

    def terminar(self):
        terminar(self.root)

    def atualizar_lista_pdfs(self):
        self.pdfs = listar_pdfs(self.pasta_pdf)

    def filtrar_equipas(self, event=None):
        filtrar_combobox_por_texto(self.combo_equipa, self.equipas, self.equipa_var.get())

    def filtrar_equipas(self, event=None):
        filtrar_combobox_por_texto(self.combo_equipa, self.equipas, self.equipa_var.get())

    def recarregar_equipas(self):
        self.equipas = carregar_recarregar_equipas(as_dict=True)
        valores = [f"{p['id']} - {p['nome']}" for p in self.equipas]
        self.combo_equipa["values"] = valores

    def salvar_dados(self):
        equipa_str = self.equipa_var.get().strip()
        ano = self.ano_var.get().strip()
        mes_nome = self.mes_var.get().strip()

        if not all([equipa_str, ano, mes_nome]):
            mostrar_mensagem("aviso", "Todos os campos obrigatórios devem ser preenchidos.")
            logger.warning("Campos obrigatórios não preenchidos.")
            return

        try:
            equipa_id, nome_equipa = equipa_str.split(" - ", 1)
        except ValueError:
            mostrar_mensagem("erro", "Formato inválido para equipa.")
            logger.error(f"Formato inválido: {equipa_str}")
            return

        mes_num = MESES_MAP.get(mes_nome)
        if mes_num is None:
            mostrar_mensagem("erro", f"Mês inválido: '{mes_nome}'")
            return

        nome_pdf = self.pdfs[self.index_atual]
        caminho_pdf = os.path.join(self.pasta_pdf, nome_pdf)
        nome_pdf_final = f"{mes_nome.lower()}.pdf"

        try:
            destino = mover_pdf_equipa(
                caminho_pdf, nome_equipa, ano, nome_pdf_final,
                os.path.join(self.base_dir, "arquivados")
            )

            folha_faltas_bd(
                equipa_id=int(equipa_id),
                mes=f"{mes_num:02d}",
                ano=int(ano),
                caminho_pdf=destino
            )

            logger.info(f"Folha de faltas gravada: {destino}")
            mostrar_mensagem("info", "Folha de faltas gravada com sucesso.")
            del self.pdfs[self.index_atual]

            if self.pdfs:
                if self.index_atual >= len(self.pdfs):
                    self.index_atual = len(self.pdfs) - 1
                self.abrir_pdf_atual()
            else:
                mostrar_mensagem("info", "Nenhum PDF restante.")
                logger.info("Nenhum PDF restante.")
                self.root.destroy()

        except FileExistsError as fe:
            logger.warning(f"Ficheiro duplicado: {fe}")
            mostrar_mensagem("erro", f"Ficheiro duplicado: {fe}")
        except Exception as e:
            logger.exception("Erro ao gravar folha de faltas:")
            mostrar_mensagem("erro", f"Erro ao gravar folha de faltas: {e}")

        self.atualizar_lista_pdfs()

    def eliminar_pdf(self):
        if not self.pdfs:
            return

        nome_pdf = self.pdfs[self.index_atual]
        caminho_pdf = os.path.join(self.pasta_pdf, nome_pdf)

        def acao():
            if os.path.exists(caminho_pdf):
                os.remove(caminho_pdf)
            del self.pdfs[self.index_atual]
            mostrar_mensagem("info", f"Folha '{nome_pdf}' eliminada com sucesso.")
            logger.info(f"Folha '{nome_pdf}' eliminada.")
            if self.pdfs:
                if self.index_atual >= len(self.pdfs):
                    self.index_atual = len(self.pdfs) - 1
                self.abrir_pdf_atual()
            else:
                self.root.destroy()

        confirmar_eliminacao(nome_pdf, acao)
        self.atualizar_lista_pdfs()

    def limpar_campos(self):
        self.equipa_var.set("")
        self.ano_var.set("")
        self.mes_var.set("")

    def preencher_dados_qr(self, caminho_pdf):
        self.limpar_campos()

        dados_qr = ler_dados_qr(caminho_pdf)
        if not dados_qr:
            logger.warning("QR Code não contém dados úteis.")
            return

        ano = dados_qr.get("ano")
        equipa_id = dados_qr.get("equipa")
        mes = dados_qr.get("mes")

        if ano:
            self.ano_var.set(ano)

        if equipa_id and equipa_id.isdigit():
            nome = self.equipas.get(int(equipa_id))
            if nome:
                self.equipa_var.set(f"{equipa_id} - {nome}")

        if mes and mes in [f"{n:02d}" for n in MESES_MAP.values()]:
            mes_nome = next((nome for nome, num in MESES_MAP.items() if f"{num:02d}" == mes), None)
            if mes_nome:
                self.mes_var.set(mes_nome)