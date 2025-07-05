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
    carregar_processos, 
    obter_clientes,
    recarregar_equipas,
    recarregar_processos,
    folha_obra_bd,
    inserir_meses_folha_obra
)
from core.ocr_utils import ler_dados_qr

from core.file_utils import (
    mover_pdf_folha_obra, 
    limpar_nome_ficheiro
)

from core.constantes import (
    MESES,
    MESES_MAP,
)

from processos import GestorProcessos
from equipas import GestorEquipas


class VisualizadorFolhasObra:
    def abrir_gestor_processos(self):
        self.root.after(100, lambda: GestorProcessos(on_close=self.recarregar_processos))

    def abrir_gestor_equipas(self):
        self.root.after(100, lambda: GestorEquipas(on_close=self.recarregar_equipas))

    def __init__(self, pasta_pdf, base_dir):
        self.pasta_pdf = pasta_pdf
        self.base_dir = base_dir
        self.pdfs = listar_pdfs(pasta_pdf)
        self.index_atual = 0
        self.equipas = carregar_equipas(as_dict=True)
        self.processos = carregar_processos()
        self.clientes = obter_clientes()
        self.meses_var = []



        if not self.pdfs:
            mostrar_mensagem("erro", "Nenhuma folha de obra encontrada.")
            return

        self._inicializar_interface()
        self.abrir_pdf_atual()

    def _inicializar_interface(self):
        self.root = tk.Toplevel()
        self.root.title("Visualizador de Folhas de Obra")
        self.root.geometry("350x750")
        centralizar_janela(self.root)
        self.root.attributes('-topmost', 1)

        self.processo_var = tk.StringVar()
        self.cliente_var = tk.StringVar()
        self.equipa_var = tk.StringVar()
        self.descricao_var = tk.StringVar()
        self.ano_var = tk.StringVar()
        self.nome_ficheiro_var = tk.StringVar()


        self._criar_formulario()
        self._criar_navegacao()
        self._criar_acoes()

    def _criar_formulario(self):
        self._adicionar_label_entry("Processo:", self.processo_var, is_combobox="processo")
        self._adicionar_label_entry("Cliente:", self.cliente_var)
        self._adicionar_label_entry("Equipa:", self.equipa_var, is_combobox="equipa")
        self._adicionar_label_entry("Descrição:", self.descricao_var)
        self._adicionar_label_entry("Ano:", self.ano_var)
        self._adicionar_label_entry("Nome do Ficheiro:", self.nome_ficheiro_var)

        #Seleção de meses
        frame_meses = tk.LabelFrame(self.root, text="Meses de Trabalho")
        frame_meses.pack(pady=10)
        meses =MESES
        for i, mes in enumerate(meses):
            var = tk.BooleanVar()
            cb = tk.Checkbutton(
                frame_meses,
                text=mes,
                variable=var
            )
            cb.grid(row=i // 3, column=i % 3, sticky="w", padx=5, pady=2)
            self.meses_var.append((mes, var))


    def _criar_navegacao(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)
        tk.Button(frame, text="◀ Anterior", width=12, command=self.mostrar_anterior).pack(side="left", padx=5)
        tk.Button(frame, text="Próximo ▶", width=12, command=self.mostrar_proximo).pack(side="left", padx=5)
        tk.Button(self.root, text="🧾 Gerir Processos", command=self.abrir_gestor_processos).pack(pady=5)
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
            if is_combobox == "processo":
                valores_processo = [f"{p['referencia']} - {p['nome_cliente']}" for p in self.processos]
                combo["values"] = valores_processo
                combo.bind("<KeyRelease>", self.filtrar_processos)
                combo.bind("<<ComboboxSelected>>", self.atualizar_cliente_a_partir_do_processo)
                self.combo_processo = combo
            elif is_combobox == "equipa":
                valores = [f"{k} - {v}" for k, v in self.equipas.items()]
                combo["values"] = valores
                combo.bind("<KeyRelease>", self.filtrar_equipas)
                self.combo_equipa = combo
            combo.pack(pady=5)


        elif texto.lower().startswith("descrição"):
            self.descricao_widget = tk.Text(self.root, height=3, width=40)
            self.descricao_widget.pack(pady=5)

        else:
            state = "readonly" if texto.lower().startswith("cliente") else "normal"
            entry = tk.Entry(self.root, textvariable=var, width=40, state=state)
            entry.pack(pady=5)

            if texto.lower().startswith("ano"):
                entry.config(width=10)


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

    def filtrar_processos(self, event=None):
        processos_dict = {p["referencia"]: p["nome_cliente"] for p in self.processos}
        filtrar_combobox_por_texto(self.combo_processo, processos_dict, self.processo_var.get())

    def filtrar_equipas(self, event=None):
        filtrar_combobox_por_texto(self.combo_equipa, self.equipas, self.equipa_var.get())


    def recarregar_processos(self):
        self.processos = recarregar_processos()
        valores_processo = [f"{p['referencia']} - {p['nome_cliente']}" for p in self.processos]
        self.combo_processo["values"] = valores_processo

    def recarregar_equipas(self):
        self.equipas = recarregar_equipas(as_dict=True)
        valores = [f"{p['id']} - {p['nome']}" for p in self.equipas]
        self.combo_equipa["values"] = valores

    def salvar_dados(self):
        processo_str = self.processo_var.get().strip()
        cliente_nome = self.cliente_var.get().strip()
        equipa_str = self.equipa_var.get().strip()
        descricao = self.descricao_widget.get("1.0", "end").strip()
        ano = self.ano_var.get().strip()
        nome_ficheiro = self.nome_ficheiro_var.get().strip()


        if not all([processo_str, equipa_str, ano, nome_ficheiro]):
            mostrar_mensagem("aviso", "Todos os campos obrigatórios devem ser preenchidos.")
            return

        processo_ref = processo_str.split(" - ")[0]
        equipa_id = equipa_str.split(" - ")[0]

        meses_selecionados = [MESES_MAP[m] for m, var in self.meses_var if var.get()]
        if not meses_selecionados:
            mostrar_mensagem("aviso", "Selecione pelo menos um mês de trabalho.")
            return
        meses_str = ''.join(f"{m:02d}" for m in meses_selecionados)

        nome_pdf = self.pdfs[self.index_atual]
        caminho_pdf = os.path.join(self.pasta_pdf, nome_pdf)
                # Procurar NIF do cliente a partir do nome
        cliente_nif = None
        for nif, nome in self.clientes.items():  # self.clientes deve vir de carregar_clientes()
            if nome == cliente_nome:
                cliente_nif = nif
                break

        if not cliente_nif:
            mostrar_mensagem("Erro", "Cliente não encontrado na base de dados.")
            return


        try:

            nome_pdf_final = f"{ano}{meses_str}_{limpar_nome_ficheiro(nome_ficheiro)}.pdf"

            destino = mover_pdf_folha_obra(
                caminho_pdf,
                processo_ref,
                cliente_nif,
                os.path.join(self.base_dir, "arquivados"),
                nome_final=nome_pdf_final
            )

            folha_id = folha_obra_bd(
                processo=processo_ref,
                cliente=cliente_nif,
                equipa=equipa_id,
                descricao=descricao,
                ano=ano,
                caminho_pdf=destino
            )


            if folha_id:
                inserir_meses_folha_obra(folha_id, meses_selecionados)
                mostrar_mensagem("info", "Folha de obra gravada com sucesso.")
            else:
                mostrar_mensagem("erro", "Erro ao gravar folha de obra na base de dados.")
                return

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
        self.processo_var.set("")
        self.cliente_var.set("")
        self.equipa_var.set("")
        self.ano_var.set("")
        self.nome_ficheiro_var.set("")
        self.descricao_widget.delete("1.0", "end")
        for _, var in self.meses_var:
            var.set(False)


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
        self.ano_var.set("")
        self.equipa_var.set("")

        dados_qr = ler_dados_qr(caminho_pdf)
        if not dados_qr:
            return

        ano = dados_qr.get("ano")
        equipa_id = dados_qr.get("equipa")

        if ano:
            self.ano_var.set(ano)

        if equipa_id and equipa_id.isdigit():
            nome = self.equipas.get(int(equipa_id))
            if nome:
                self.equipa_var.set(f"{equipa_id} - {nome}")

    
    def atualizar_cliente_a_partir_do_processo(self, event=None):
        valor = self.processo_var.get()
        referencia = valor.split(" - ")[0] if " - " in valor else valor
        for p in self.processos:
            if p["referencia"] == referencia:
                self.cliente_var.set(p["nome_cliente"])
                break
