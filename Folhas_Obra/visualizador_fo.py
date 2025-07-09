## Folhas_Obra/visualizador_fo.py

import os
import tkinter as tk
from tkinter import ttk
from core.logger import configurar_logger
logger = configurar_logger(__name__)

from core.gui_utils import (
    filtrar_combobox_por_texto,
    centralizar_janela,
    confirmar_eliminacao,
    mostrar_mensagem
)
from core.pdf_utils import (
    listar_pdfs
)
from core.db_helpers import (
    carregar_recarregar_equipas,
    carregar_recarregar_processos,
    obter_clientes,
    folha_obra_bd,
    inserir_meses_folha_obra
)
from core.ocr_utils import ler_dados_qr

from core.file_utils import (
    mover_pdf_folha_obra, 
    limpar_nome_ficheiro
)

from core.visualizador_utils import (
    abrir_pdf_atual,
    mostrar_anterior,   
    mostrar_proximo,
    terminar
)
from core.constantes import (
    MESES,
    MESES_MAP,
)

from processos import GestorProcessos
from equipas import GestorEquipas


class VisualizadorFolhasObra:
    """
    Classe para visualizar e gerenciar folhas de obra PDF.
    Permite navegar entre folhas, preencher dados, salvar e eliminar folhas.
    """
    def abrir_gestor_processos(self):
        self.root.after(100, lambda: GestorProcessos(on_close=self.recarregar_processos))

    def abrir_gestor_equipas(self):
        self.root.after(100, lambda: GestorEquipas(on_close=self.recarregar_equipas))

    def mostrar_mensagem(self, tipo, texto):
        mostrar_mensagem(tipo, texto, parent=self.root)

    def __init__(self, pasta_pdf, base_dir):
        self.pasta_pdf = pasta_pdf
        self.base_dir = base_dir
        self.pdfs = listar_pdfs(pasta_pdf)
        self.index_atual = 0
        self.equipas = carregar_recarregar_equipas(as_dict=True)
        self.processos = carregar_recarregar_processos()
        self.clientes = obter_clientes()
        self.meses_var = []



        if not self.pdfs:
            mostrar_mensagem("erro", "Nenhuma folha de obra encontrada.")
            logger.warning("Nenhuma folha de obra encontrada na pasta 'separados'.")
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
        abrir_pdf_atual(self.pdfs, self.index_atual, self.pasta_pdf, self.preencher_dados_qr)

    def mostrar_anterior(self):
        self.index_atual = mostrar_anterior(self.pdfs, self.index_atual, self.abrir_pdf_atual, doc_nome="folha")

    def mostrar_proximo(self):
        self.index_atual = mostrar_proximo(self.pdfs, self.index_atual, self.abrir_pdf_atual, doc_nome="folha")

    def terminar(self):
        terminar(self.root)

    def atualizar_lista_pdfs(self):
        self.pdfs = listar_pdfs(self.pasta_pdf)

    def filtrar_processos(self, event=None):
        processos_dict = {p["referencia"]: p["nome_cliente"] for p in self.processos}
        filtrar_combobox_por_texto(self.combo_processo, processos_dict, self.processo_var.get())

    def filtrar_equipas(self, event=None):
        filtrar_combobox_por_texto(self.combo_equipa, self.equipas, self.equipa_var.get())


    def recarregar_processos(self):
        self.processos = carregar_recarregar_processos()
        logger.debug(f"Processos carregados: {self.processos}")
        valores_processo = [f"{p['referencia']} - {p['nome_cliente']}" for p in self.processos]
        self.combo_processo["values"] = valores_processo
        texto_atual = self.processo_var.get()
        if texto_atual:
            self.filtrar_processos()

    def recarregar_equipas(self):
        self.equipas = carregar_recarregar_equipas(as_dict=True)
        valores = [f"{p['id']} - {p['nome']}" for p in self.equipas]
        self.combo_equipa["values"] = valores
        texto_atual = self.equipa_var.get()
        if texto_atual:
            self.filtrar_equipas()


    def salvar_dados(self):
        """
        Valida, move e grava uma folha de obra na base de dados,
        associando-a ao processo, cliente, equipa e meses selecionados.
        """
        processo_str = self.processo_var.get().strip()
        cliente_nome = self.cliente_var.get().strip()
        equipa_str = self.equipa_var.get().strip()
        descricao = self.descricao_widget.get("1.0", "end").strip()
        ano = self.ano_var.get().strip()
        nome_ficheiro = self.nome_ficheiro_var.get().strip()

        if not all([processo_str, equipa_str, ano, nome_ficheiro]):
            mostrar_mensagem("aviso", "Todos os campos obrigatórios devem ser preenchidos.")
            logger.warning("Tentativa de salvar com campos obrigatórios em falta.")
            return

        try:
            processo_ref = processo_str.split(" - ")[0]
            equipa_id = equipa_str.split(" - ")[0]
        except ValueError as ve:
            logger.error(f"Erro ao extrair processo/equipa: {ve}")
            mostrar_mensagem("erro", "Formato inválido para processo ou equipa.")
            return

        # Verifica meses selecionados
        meses_selecionados = [MESES_MAP[m] for m, var in self.meses_var if var.get()]
        if not meses_selecionados:
            mostrar_mensagem("aviso", "Selecione pelo menos um mês de trabalho.")
            logger.info("Nenhum mês selecionado ao tentar salvar folha.")
            return
        meses_str = ''.join(f"{m:02d}" for m in meses_selecionados)

        # Identificação do ficheiro e subpasta destino
        nome_pdf_original = self.pdfs[self.index_atual]
        caminho_pdf = os.path.join(self.pasta_pdf, nome_pdf_original)
        nome_pdf_final = f"{ano}{meses_str}_{limpar_nome_ficheiro(nome_ficheiro)}.pdf"
        subpasta = f"{processo_ref}-{cliente_nome}"

        # Buscar NIF do cliente
        cliente_nif = next((nif for nif, nome in self.clientes.items() if nome == cliente_nome), None)
        if not cliente_nif:
            mostrar_mensagem("erro", f"Cliente '{cliente_nome}' não encontrado na base de dados.")
            logger.warning(f"Cliente '{cliente_nome}' não encontrado.")
            return

        try:
            destino = mover_pdf_folha_obra(
                caminho_pdf, subpasta,
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
                logger.info(f"Folha de obra '{nome_pdf_final}' gravada com ID {folha_id}")
            else:
                mostrar_mensagem("erro", "Erro ao gravar folha de obra na base de dados.")
                logger.error("Função folha_obra_bd devolveu None.")
                return

            del self.pdfs[self.index_atual]

            if self.pdfs:
                if self.index_atual >= len(self.pdfs):
                    self.index_atual = len(self.pdfs) - 1
                self.abrir_pdf_atual()
            else:
                mostrar_mensagem("info", "Todos os documentos foram processados.")
                self.root.destroy()

        except FileExistsError as fe:
            logger.warning(f"Ficheiro duplicado: {fe}")
            mostrar_mensagem("erro", f"Ficheiro duplicado: {fe}")
        except Exception as e:
            logger.exception("Erro ao gravar folha de obra:")
            mostrar_mensagem("erro", f"Ocorreu um erro ao gravar: {e}")

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
        """
        Elimina o ficheiro PDF atual da lista e do disco, com confirmação do utilizador.
        """
        if not self.pdfs:
            return

        nome_pdf = self.pdfs[self.index_atual]
        caminho_pdf = os.path.join(self.pasta_pdf, nome_pdf)

        def acao():
            try:
                if os.path.exists(caminho_pdf):
                    os.remove(caminho_pdf)
                    logger.info(f"Ficheiro '{nome_pdf}' eliminado do disco.")
                else:
                    logger.warning(f"Tentou eliminar ficheiro inexistente: {nome_pdf}")

                del self.pdfs[self.index_atual]
                mostrar_mensagem("info", f"Ficheiro '{nome_pdf}' eliminado.")

                if self.pdfs:
                    if self.index_atual >= len(self.pdfs):
                        self.index_atual = len(self.pdfs) - 1
                    self.abrir_pdf_atual()
                else:
                    self.root.destroy()
            except Exception as e:
                logger.exception(f"Erro ao eliminar ficheiro: {e}")
                mostrar_mensagem("erro", f"Erro ao eliminar: {e}")

        confirmar_eliminacao(nome_pdf, acao)
        self.atualizar_lista_pdfs()

    def preencher_dados_qr(self, caminho_pdf):
        """
        Lê dados do QR code do PDF e preenche os campos 'ano' e 'equipa' automaticamente.
        """
        self.limpar_campos()
        dados_qr = ler_dados_qr(caminho_pdf)

        if not dados_qr:
            logger.info("QR Code não contém dados reconhecíveis.")
            return

        ano = dados_qr.get("ano")
        equipa_id = dados_qr.get("equipa")

        if ano:
            self.ano_var.set(ano)
            logger.debug(f"Ano definido via QR: {ano}")

        if equipa_id and equipa_id.isdigit():
            nome = self.equipas.get(int(equipa_id))
            if nome:
                self.equipa_var.set(f"{equipa_id} - {nome}")
                logger.debug(f"Equipa preenchida via QR: {equipa_id} - {nome}")
            else:
                logger.warning(f"Equipa ID {equipa_id} do QR não encontrada.")

    
    def atualizar_cliente_a_partir_do_processo(self, event=None):
        """
        Atualiza o campo 'cliente' automaticamente ao selecionar um processo.
        """
        valor = self.processo_var.get()
        referencia = valor.split(" - ")[0] if " - " in valor else valor

        for p in self.processos:
            if p["referencia"] == referencia:
                self.cliente_var.set(p["nome_cliente"])
                logger.debug(f"Cliente atualizado para: {p['nome_cliente']}")
                return

        logger.warning(f"Referência de processo não encontrada: {referencia}")
