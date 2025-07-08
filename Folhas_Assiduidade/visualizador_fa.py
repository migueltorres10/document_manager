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
    carregar_equipas, 
    recarregar_equipas,
    folha_assiduidade_bd
)
from core.ocr_utils import ler_dados_qr

from core.file_utils import (
    mover_pdf_equipa
)

from core.constantes import (
    MESES,
    MESES_MAP,
)

from equipas import GestorEquipas


class VisualizadorFolhasAssiduidade:

    def abrir_gestor_equipas(self):
        self.root.after(100, lambda: GestorEquipas(on_close=self.recarregar_equipas))

    def __init__(self, pasta_pdf, base_dir):
        self.pasta_pdf = pasta_pdf
        self.base_dir = base_dir
        self.pdfs = listar_pdfs(pasta_pdf)
        self.index_atual = 0
        self.equipas = carregar_equipas(as_dict=True)
        self.meses_var = []

        if not self.pdfs:
            mostrar_mensagem("erro", "Nenhuma folha de assiduídade encontrada.")
            return

        self._inicializar_interface()
        self.abrir_pdf_atual()

    def _inicializar_interface(self):
        self.root = tk.Toplevel()
        self.root.title("Visualizador de Folhas de Assiduidade")
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

    def atualizar_lista_pdfs(self):
        self.pdfs = listar_pdfs(self.pasta_pdf)

    def filtrar_equipas(self, event=None):
        filtrar_combobox_por_texto(self.combo_equipa, self.equipas, self.equipa_var.get())

    def recarregar_equipas(self):
        self.equipas = recarregar_equipas(as_dict=True)
        valores = [f"{p['id']} - {p['nome']}" for p in self.equipas]
        self.combo_equipa["values"] = valores

    def salvar_dados(self):
        equipa_str = self.equipa_var.get().strip()
        ano = self.ano_var.get().strip()


        if not all([equipa_str, ano]):
            mostrar_mensagem("aviso", "Todos os campos obrigatórios devem ser preenchidos.")
            return

        equipa_id = equipa_str.split(" - ")[0]
        nome_equipa = equipa_str.split(" - ")[1]

        mes_selecionado = self.mes_var.get()
        if not mes_selecionado:
            mostrar_mensagem("aviso", "Selecione um mês de trabalho.")
            return

        mes_num = MESES_MAP.get(mes_selecionado)
        mes_str = f"{mes_num:02d}"
        nome_pdf_original = self.pdfs[self.index_atual]
        caminho_pdf = os.path.join(self.pasta_pdf, nome_pdf_original)
        nome_pdf_final = f"{mes_num}.pdf" #Deve ser o nome do mês selecionado por extenso

        try:
            nome_pdf_final = f"{mes_num}.pdf"


            destino = mover_pdf_equipa(
                caminho_pdf,
                nome_equipa,
                ano,
                nome_pdf_final,
                os.path.join(self.base_dir, "arquivados")
            )

            folha_assiduidade_bd(
                equipa_id,
                mes_str,
                int(ano),
                destino
            )

            del self.pdfs[self.index_atual]

            if self.pdfs:
                if self.index_atual >= len(self.pdfs):
                    self.index_atual = len(self.pdfs) - 1
                self.abrir_pdf_atual()
            else:
                self.root.destroy()

        except FileExistsError as fe:
            mostrar_mensagem("erro", f"Ficheiro duplicado: {fe}")
        except Exception as e:
            mostrar_mensagem("erro", f"Erro ao gravar folha de obra: {e}")

        self.atualizar_lista_pdfs()

    def limpar_campos(self):
        self.equipa_var.set("")
        self.ano_var.set("")
        self.mes_var.set("")


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
                self.root.destroy()

        confirmar_eliminacao(nome_pdf, acao)
        self.atualizar_lista_pdfs()

    def preencher_dados_qr(self, caminho_pdf):
        self.limpar_campos()

        dados_qr = ler_dados_qr(caminho_pdf)
        if not dados_qr:
            return

        ano = dados_qr.get("ano")
        equipa_id = dados_qr.get("equipa")
        mes = dados_qr.get("mes")  # Esperado no formato "08"

        if ano:
            self.ano_var.set(ano)

        if equipa_id and equipa_id.isdigit():
            nome = self.equipas.get(int(equipa_id))
            if nome:
                self.equipa_var.set(f"{equipa_id} - {nome}")

        if mes and mes in [f"{n:02d}" for n in MESES_MAP.values()]:
            # Converte número para nome do mês (ex: "08" → "Agosto")
            mes_nome = next((nome for nome, num in MESES_MAP.items() if f"{num:02d}" == mes), None)
            if mes_nome:
                self.mes_var.set(mes_nome)
