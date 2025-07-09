import os
import tkinter as tk
from tkinter import ttk
import datetime
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
    abrir_pdf_externo,
    fechar_sumatra
)
from core.db_helpers import (
    obter_fornecedores,
    gravar_fatura_bd,
    carregar_recarregar_processos
)

from core.ocr_utils import (
    extrair_dados_qrcode_de_pdf
)

from core.file_utils import (
    mover_pdf_para_pasta_destino,
    renomear_pdf
)

from core.visualizador_utils import (
    abrir_pdf_atual,
    mostrar_anterior,
    mostrar_proximo,
    terminar
)

from processos import GestorProcessos


class VisualizadorFaturas:
    """
    Classe para visualizar e gerir faturas PDF.
    Permite navegar entre faturas, extrair dados de QR codes, salvar informações no banco de dados,
    e mover PDFs para pastas organizadas.
    """
    def __init__(self, pasta_pdf, base_dir):
        self.pasta_pdf = pasta_pdf
        self.base_dir = base_dir
        self.pdfs = listar_pdfs(pasta_pdf)
        # Inicializa o índice atual para a primeira fatura
        self.index_atual = 0
        self.fornecedores = obter_fornecedores()
        self.processos = carregar_recarregar_processos()

        if not self.pdfs:
            mostrar_mensagem("erro", "Nenhuma Fatura encontrada na pasta 'separados'.")
            logger.error("Nenhuma Fatura encontrada na pasta 'separados'.")
            return

        logger.info("Iniciando visualizador de faturas com PDFs encontrados: %s", self.pdfs)
        self._inicializar_interface()
        # Abre o primeiro PDF na lista
        self.abrir_pdf_atual()

    def _inicializar_interface(self):
        """
        Inicializa a interface gráfica para o visualizador de faturas.
        Cria campos de entrada, botões de navegação e ações para manipulação de faturas.
        """
        self.root = tk.Toplevel()
        self.root.title("Visualizador de Faturas")
        self.root.geometry("350x760")
        centralizar_janela(self.root)
        self.root.attributes('-topmost', 1)

        # Variáveis para armazenar os dados do formulário
        self.fornecedor_var = tk.StringVar()
        self.processo_var = tk.StringVar()
        self.entry_ano = tk.Entry(self.root)
        self.entry_numero = tk.Entry(self.root)
        self.entry_data = tk.Entry(self.root)
        self.entry_tipo = tk.Entry(self.root)
        self.entry_base = tk.Entry(self.root)
        self.entry_iva = tk.Entry(self.root)
        self.entry_total = tk.Entry(self.root)

        self._criar_formulario()
        self._criar_navegacao()
        self._criar_acoes()

    def _criar_formulario(self):
        """
        Cria o formulário de entrada para os dados da fatura.
        Adiciona campos para fornecedor, tipo de documento, ano, número, data, base, IVA, total e processo.
        """
        self._adicionar_label_entry("Fornecedor:", self.fornecedor_var, is_combobox=True)
        self._adicionar_label_entry("Tipo de Documento:", self.entry_tipo)
        self._adicionar_label_entry("Ano:", self.entry_ano)
        self._adicionar_label_entry("Número:", self.entry_numero)
        self._adicionar_label_entry("Data:", self.entry_data)
        self._adicionar_label_entry("Base:", self.entry_base)
        self._adicionar_label_entry("IVA:", self.entry_iva)
        self._adicionar_label_entry("Total:", self.entry_total)
        self._adicionar_label_entry("Número de Processo:", self.processo_var, is_combobox="processo")

    def _criar_navegacao(self):
        """
        Cria os botões de navegação para percorrer as faturas.
        Adiciona botões para abrir o PDF atual, navegar para a fatura anterior e próxima,
        e abrir o gestor de processos.
        """
        frame = tk.Frame(self.root)
        frame.pack(pady=10)
        tk.Button(frame, text="◀ Anterior", width=12, command=self.mostrar_anterior).pack(side="left", padx=5)
        tk.Button(frame, text="Próximo ▶", width=12, command=self.mostrar_proximo).pack(side="left", padx=5)
        tk.Button(self.root, text="📎 Gerir Processos", command=self.abrir_gestor_processos).pack(pady=5)

    def _criar_acoes(self):
        """
        Cria os botões de ação para salvar dados, eliminar PDF e terminar o visualizador.
        Adiciona botões para salvar os dados da fatura, eliminar o PDF atual e fechar o visualizador.
        """
        frame = tk.Frame(self.root)
        frame.pack(pady=15)
        tk.Button(frame, text="📂 Salvar", width=25, command=self.salvar_dados).pack(pady=3)
        tk.Button(frame, text="🗑 Eliminar", width=25, command=self.eliminar_pdf).pack(pady=3)
        tk.Button(frame, text="⏹ Terminar", width=25, command=self.terminar).pack(pady=3)

    def _adicionar_label_entry(self, label, var, is_combobox=False):
        """
        Adiciona um rótulo e um campo de entrada ou combobox à interface.
        Args:
            label (str): Texto do rótulo.
            var (tk.Variable): Variável associada ao campo de entrada.
            is_combobox (bool or str): Se True, cria um combobox; se "processo", cria um combobox específico para processos.
        Returns:
            None
        """
        tk.Label(self.root, text=label).pack(pady=5)
        # Se for um combobox, cria o combobox com os valores apropriados
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
        # Se for um campo de entrada, cria o campo de entrada normal
        else:
            var.pack()

    def abrir_pdf_atual(self):
        abrir_pdf_atual(self.pdfs, self.index_atual, self.pasta_pdf, self.preencher_dados_qr)

    def mostrar_anterior(self):
        self.index_atual = mostrar_anterior(self.pdfs, self.index_atual, self.abrir_pdf_atual, doc_nome="fatura")

    def mostrar_proximo(self):
        self.index_atual = mostrar_proximo(self.pdfs, self.index_atual, self.abrir_pdf_atual, doc_nome="fatura")

    def terminar(self):
        terminar(self.root)        

    def abrir_gestor_processos(self):
        """
        Abre o gestor de processos e recarrega a lista de processos após o fechamento.
        """
        self.root.after(100, lambda: GestorProcessos(on_close=self.recarregar_processos))

    def recarregar_processos(self):
        """
        Recarrega a lista de processos e atualiza o combobox de processos.
        """
        self.processos = carregar_recarregar_processos()
        self.combo_processo["values"] = [f"{p['referencia']} - {p['nome_cliente']}" for p in self.processos]

    def salvar_dados(self):
        """
        Salva os dados da fatura no banco de dados e move o PDF para a pasta de destino.
        Verifica se todos os campos obrigatórios estão preenchidos e se os valores numéricos são válidos.
        Se houver erros, exibe mensagens apropriadas.
        """
        # Obtém os valores dos campos de entrada
        fornecedor_nome = self.fornecedor_var.get().strip()
        tipodoc = self.entry_tipo.get().strip()
        ano = self.entry_ano.get().strip()
        numero = self.entry_numero.get().strip()
        data = self.entry_data.get().strip()
        processo_str = self.processo_var.get().strip()
        processo = processo_str.split(" - ")[0] if processo_str else ""

        try:
            # Tenta converter os valores numéricos
            base = float(self.entry_base.get().strip())
            iva = float(self.entry_iva.get().strip())
            total = float(self.entry_total.get().strip())
            logger.debug(f"Valores convertidos: Base={base}, IVA={iva}, Total={total}")
        except ValueError:
            logger.error("Erro ao converter valores numéricos: Base, IVA e Total devem ser números válidos.")
            mostrar_mensagem("erro", "Base, IVA e Total devem ser números válidos.")
            return

        if not all([fornecedor_nome, tipodoc, ano, numero, data, base, iva, total]):
            logger.warning("Campos obrigatórios não preenchidos.")
            mostrar_mensagem("aviso", "Preencha todos os campos obrigatórios.")
            return

        fornecedor_nif = next((nif for nif, nome in self.fornecedores.items() if nome == fornecedor_nome), None)
        if not fornecedor_nif:
            logger.error(f"Fornecedor '{fornecedor_nome}' não encontrado na base de dados.")
            mostrar_mensagem("erro", "Fornecedor não encontrado na base de dados.")
            return

        try:
            # Tenta converter a data para o formato correto
            data_formatada = datetime.datetime.strptime(data, "%Y-%m-%d").date()
            logger.debug(f"Data formatada: {data_formatada}")
        except ValueError:
            logger.error(f"Formato de data inválido: {data}. Deve ser YYYY-MM-DD.")
            mostrar_mensagem("erro", "Formato de data inválido. Use YYYY-MM-DD.")
            return

        nome_pdf = self.pdfs[self.index_atual]
        caminho_pdf = os.path.join(self.pasta_pdf, nome_pdf)

        try:
            logger.info(f"Salvando fatura: {fornecedor_nome}, Tipo: {tipodoc}, Número: {numero}, Ano: {ano}, Data: {data_formatada}, Base: {base}, IVA: {iva}, Total: {total}, Processo: {processo}")
            destino = mover_pdf_para_pasta_destino(caminho_pdf, fornecedor_nome, ano, os.path.join(self.base_dir, "arquivados"))
            final = renomear_pdf(destino, numero, ano)

            gravar_fatura_bd(
                fornecedor=fornecedor_nif,
                tipo_doc=tipodoc,
                numero=numero,
                ano=ano,
                data=data_formatada,
                base=base,
                iva=iva,
                total=total,
                processo=processo,
                caminho_pdf=final
            )

            mostrar_mensagem("info", "Fatura gravada e movida com sucesso.")
            logger.info("Fatura gravada e movida com sucesso.")
            del self.pdfs[self.index_atual]

            if self.pdfs:
                if self.index_atual >= len(self.pdfs):
                    self.index_atual = len(self.pdfs) - 1
                self.abrir_pdf_atual()
            else:
                mostrar_mensagem("info", "Nenhum PDF restante.")
                logger.info("Nenhum PDF restante, fechando visualizador.")
                self.root.destroy()

        except FileExistsError as fe:
            logger.error(f"Erro ao salvar fatura: Ficheiro duplicado {fe}")
            mostrar_mensagem("erro", f"Ficheiro duplicado: {fe}")
        except Exception as e:
            logger.exception(f"Erro ao salvar fatura: {e}")
            mostrar_mensagem("erro", f"Erro ao salvar fatura: {e}")

    def eliminar_pdf(self):
        """
        Elimina o PDF atual da lista e do sistema de arquivos.
        Se não houver PDFs, exibe uma mensagem de aviso.
        Se o PDF for eliminado com sucesso, atualiza a lista de PDFs e abre o próximo PDF.
        """
        if not self.pdfs:
            return

        nome_pdf = self.pdfs[self.index_atual]
        caminho_pdf = os.path.join(self.pasta_pdf, nome_pdf)

        def acao():
            logger.info(f"Eliminando PDF: {nome_pdf}")
            if os.path.exists(caminho_pdf):
                os.remove(caminho_pdf)

            del self.pdfs[self.index_atual]
            logger.info(f"PDF {nome_pdf} eliminado com sucesso.")
            mostrar_mensagem("info", f"PDF '{nome_pdf}' eliminado com sucesso.")
            if self.pdfs:
                if self.index_atual >= len(self.pdfs):
                    self.index_atual = len(self.pdfs) - 1
                self.abrir_pdf_atual()
            else:
                mostrar_mensagem("info", "Nenhum PDF restante.")
                logger.info("Nenhum PDF restante, fechando visualizador.")
                self.root.destroy()

        confirmar_eliminacao(nome_pdf, acao)

    def preencher_dados_qr(self, caminho_pdf):
        """
        Preenche os campos do formulário com os dados extraídos do QR code no PDF.
        Args:
            caminho_pdf (str): Caminho do arquivo PDF a ser processado.
        """
        logger.info(f"Preenchendo dados do QR code do PDF: {caminho_pdf}")
        campos = [self.entry_tipo, self.entry_data, self.entry_ano, self.entry_base, self.entry_iva, self.entry_total, self.entry_numero]
        for campo in campos:
            campo.delete(0, tk.END)
        self.fornecedor_var.set("")
        self.processo_var.set("")

        dados_qr = extrair_dados_qrcode_de_pdf(caminho_pdf)
        if not dados_qr:
            logger.warning("Nenhum dado QR code encontrado no PDF.")
            return

        fornecedor_nome = self.fornecedores.get(dados_qr.get("nif_emitente"))
        if fornecedor_nome:
            self.fornecedor_var.set(fornecedor_nome)


        self.entry_tipo.insert(0, dados_qr.get("tipo_doc", ""))
        data_qr = dados_qr.get("data_doc", "").strip()

        data_formatada = None
        for formato in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y%m%d"):
            try:
                data_formatada = datetime.datetime.strptime(data_qr, formato).date()
                logger.debug(f"Data formatada com sucesso: {data_formatada} usando formato '{formato}'")
                break
            except ValueError:
                logger.debug(f"Formato de data '{formato}' não corresponde: {data_qr}")
                continue

        if data_formatada:
            self.entry_data.insert(0, data_formatada.isoformat())
            self.entry_ano.insert(0, str(data_formatada.year))

        self.entry_numero.insert(0, dados_qr.get("numero_doc", ""))
        self.entry_base.insert(0, dados_qr.get("valor_tributavel", ""))
        self.entry_iva.insert(0, dados_qr.get("total_iva", ""))
        self.entry_total.insert(0, dados_qr.get("total_doc", ""))
