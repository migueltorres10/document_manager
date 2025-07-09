# QR/qr_code.py
import os
import tkinter as tk
from tkinter import ttk, messagebox
from core.db_helpers import carregar_recarregar_equipas
from core.gui_utils import centralizar_janela
from core.constantes import MESES, MESES_MAP, TIPOS_DOCUMENTOS
from core.global_utils import inserir_qr_no_excel
import qrcode
from core.print_utils import converter_para_pdf, imprimir_pdf_no_windows
from tkinter import simpledialog
from core.logger import configurar_logger
from core.gui_utils import filtrar_combobox_por_texto
logger = configurar_logger(__name__)



class GeradorQRCode:
    """
    Classe para gerar QR Codes para documentos internos, como folhas de obra, faltas e assiduidade.
    Esta classe cria uma interface gráfica para selecionar equipa, ano, tipo de documento e meses de trabalho.
    Gera QR Codes e insere em documentos Excel baseados em templates.
    A classe também lida com a impressão dos documentos gerados.
    """
    def __init__(self):
        """
        Inicializa a classe, carrega as equipas e configura a interface gráfica.
        """
        # Carrega as equipas do banco de dados
        self.equipas = carregar_recarregar_equipas()
        self.inserir_qr_no_excel = inserir_qr_no_excel
        logger.debug(f"Equipas carregadas: {self.equipas}")
        # Inicializa a variavel para meses
        self.meses_var = []
        # Lista de checkbuttons para os meses
        self.meses_checkbuttons = []
        # Variável para armazenar o tipo de documento selecionado
        self.tipo_documento = None        
        self._inicializar_interface()

    def _inicializar_interface(self):
        """
        Inicializa a interface gráfica para o gerador de QR Code.
        Cria campos para selecionar equipa, ano, tipo de documento e meses de trabalho.
        """
        # Cria a janela principal
        self.root = tk.Toplevel()
        self.root.title("Gerador de QRCode para Documentos Internos")
        self.root.geometry("350x400")
        centralizar_janela(self.root)
        self.root.attributes('-topmost', 1)

        # Variáveis para armazenar os valores dos campos
        self.equipa_var = tk.StringVar()
        self.ano_var = tk.StringVar()
        self.tipo_var = tk.StringVar()

        self._criar_widgets()

    def _criar_widgets(self):
        """
        Cria os widgets da interface gráfica, incluindo labels, entradas e checkbuttons.
        """
        # Frame para o formulário
        self._adicionar_label_entry("Equipa:", self.equipa_var, is_combobox="equipa")
        self._adicionar_label_entry("Ano:", self.ano_var)
        # Frame para o tipo de documento
        self._adicionar_label_entry("Tipo de Documento:", self.tipo_var, is_combobox=True)
        
        # Checkbuttons para os meses
        frame_meses = tk.LabelFrame(self.root, text="Mês de Trabalho")
        frame_meses.pack(pady=10)

        for i, mes in enumerate(MESES):
            var = tk.BooleanVar()
            cb = tk.Checkbutton(
                frame_meses,
                text=mes,
                variable=var
            )
            cb.grid(row=i // 3, column=i % 3, sticky="w", padx=5, pady=2)
            self.meses_var.append((mes, var))
            self.meses_checkbuttons.append(cb)

        # Botão para gerar QR Code
        tk.Button(self.root, text="Gerar QRCode", command=self.gerar_qrcode).pack(pady=15)

    def _tipo_selecionado(self, tipo):
        """
        Atualiza a interface com base no tipo de documento selecionado.
        Desabilita os meses se o tipo for "Folhas de Obra".
        """
        logger.debug(f"Tipo de documento selecionado: {tipo}")
        self.tipo_var.set(tipo)
        # Desabilita os meses se for "Folhas de Obra"
        if tipo == "Folhas de Obra":
            for cb, (_, var) in zip(self.meses_checkbuttons, self.meses_var):
                cb.config(state="disabled")
                var.set(False)
        # Se for outro tipo, habilita os meses
        else:
            for cb in self.meses_checkbuttons:
                cb.config(state="normal")

    def _adicionar_label_entry(self, texto, var, is_combobox=False):
        """
        Adiciona um label e uma entrada (Entry ou Combobox) à interface gráfica.
        Args:
            texto (str): Texto do label.
            var (tk.StringVar): Variável associada à entrada.
            is_combobox (bool): Se True, cria uma Combobox; caso contrário, cria um Entry.
        Returns:
            None    
        """
        logger.debug(f"Adicionando label e entrada: {texto}")
        tk.Label(self.root, text=texto).pack(pady=5)
        if is_combobox:
            # Cria uma Combobox para equipas ou tipos de documento
            combo = ttk.Combobox(self.root, textvariable=var, state="normal", width=40)
            if texto.lower().startswith("equipa"):
                valores = [f"{id} - {nome}" for id, nome in self.equipas.items()]
                combo["values"] = valores
                combo.bind("<KeyRelease>", self.filtrar_equipas)
                self.combo_equipa = combo
            elif texto.lower().startswith("tipo"):
                tipos_validos = ["Folhas_Obra", "Folhas_Faltas", "Folhas_Assiduidade"]
                combo["values"] = tipos_validos
                combo.bind("<<ComboboxSelected>>", lambda e: self._tipo_selecionado(combo.get()))
            combo.pack(pady=5)
        else:
            # Cria um Entry para ano ou outros textos
            entry = tk.Entry(self.root, textvariable=var, width=40)
            if texto.lower().startswith("ano"):
                entry.config(width=10)
            entry.pack(pady=5)


    def filtrar_equipas(self, event):
        filtrar_combobox_por_texto(self.combo_equipa, self.equipas, self.equipa_var.get())

    def gerar_qrcode(self):
        """
        Gera QR Codes para os documentos internos com base nos dados inseridos.
        Verifica se os campos estão preenchidos corretamente e gera os documentos Excel com QR Codes.
        """
        logger.debug("Iniciando geração de QR Code")
        tipo_documento = self.tipo_var.get().strip()
        equipa_str = self.equipa_var.get().strip()
        # Verifica se a equipa foi selecionada corretamente
        if " - " not in equipa_str:
            logger.warning("Equipa inválida selecionada")
            messagebox.showwarning("Equipa inválida", "Selecione uma equipa válida.")
            return

        # Extrai ID e nome da equipa    
        equipa_id = equipa_str.split(" - ")[0].strip()
        equipa_nome = self.equipas.get(int(equipa_id), "Desconhecida")
        # Verifica se o ano é válido
        ano = self.ano_var.get().strip()
        if not ano.isdigit() or len(ano) != 4:
            logger.warning(f"Ano inválido: {ano}")
            messagebox.showwarning("Ano inválido", "Insira um ano válido com 4 dígitos (ex: 2025).")
            return
        # Verifica se o tipo de documento é válido
        if tipo_documento not in TIPOS_DOCUMENTOS:
            logger.warning(f"Tipo de documento inválido: {tipo_documento}")
            messagebox.showwarning("Tipo inválido", "Selecione um tipo de documento válido.")
            return
        # Verifica se pelo menos um mês foi selecionado
        meses_selecionados = [mes for mes, var in self.meses_var if var.get()]
        if tipo_documento == "Folhas de Obra":
            meses_selecionados = [None]
            logger.debug("Tipo de documento é 'Folhas de Obra', meses serão ignorados.")

        if not meses_selecionados:
            logger.warning("Nenhum mês selecionado")
            messagebox.showwarning("Mês obrigatório", "Selecione pelo menos um mês.")
            return

        # Caminho do template base
        template_base = os.path.join("templates", f"{TIPOS_DOCUMENTOS[tipo_documento]}_Base.xlsx")
        documentos_gerados = []

        # Loop pelos meses selecionados
        logger.debug(f"Meses selecionados: {meses_selecionados}")
        for mes in meses_selecionados:
            # Define o conteúdo do QR Code
            logger.debug(f"Gerando QR Code para equipa: {equipa_id}, ano: {ano}, mês: {mes}")
            conteudo_qr = f"equipa={equipa_id};ano={ano}"
            # Define o mês como "Geral" inicialmente
            nome_mes = "Geral"
            if mes:
                # Se o mês for especificado, adiciona ao conteúdo do QR
                mes_num = MESES_MAP.get(mes)                
                conteudo_qr += f";mes={mes_num:02d}"
                logger.debug(f"Conteúdo do QR Code: {conteudo_qr}")
                nome_mes = mes.lower()

            # Gera QR
            qr = qrcode.make(conteudo_qr)
            logger.debug(f"QR Code gerado para: {conteudo_qr}")

            # Caminho QR temporário
            qr_temp_path = os.path.join("temp", f"qr_{equipa_id}_{ano}_{nome_mes}.png")
            os.makedirs("temp", exist_ok=True)
            # Salva o QR Code em um arquivo temporário
            logger.debug(f"Salvando QR Code em: {qr_temp_path}")
            qr.save(qr_temp_path)

            # Pasta e nome final do documento
            pasta_saida = os.path.join(tipo_documento, "geradas", ano, equipa_nome)
            os.makedirs(pasta_saida, exist_ok=True)
            nome_ficheiro = f"{ano}_{nome_mes}_{equipa_nome}.xlsx"
            caminho_final = os.path.join(pasta_saida, nome_ficheiro)

            # Verifica duplicação para tipos sensíveis
            if tipo_documento != "Folhas de Obra" and os.path.exists(caminho_final):
                logger.info(f"Documento já existe: {caminho_final}")
                continue

            # Copia template e insere QR
            self.inserir_qr_no_excel(
                template_base,
                caminho_final,
                qr_temp_path,
                dados={
                    "ano": ano,
                    "equipa": equipa_nome,
                    "mes": mes  # pode ser None
                }
            )
            logger.debug(f"Documento gerado: {caminho_final}")


            pdf_path = converter_para_pdf(caminho_final)
            if pdf_path:
                if tipo_documento == "Folhas_Obra":
                    copias = simpledialog.askinteger(
                        "Número de Cópias",
                        f"Quantas cópias imprimir para {equipa_nome} ({ano})?",
                        minvalue=1,
                        initialvalue=1,
                        parent=self.root
                    )
                    if copias:
                        msg = (
                            f"Tipo: {tipo_documento}\nEquipa: {equipa_nome}\nAno: {ano}\nMês: {nome_mes.title()}\n"
                            f"Cópias: {copias}\n\nDeseja continuar com a impressão?"
                        )
                        if messagebox.askyesno("Confirmar Impressão", msg):
                            logger.info(f"Imprimindo {copias}x: {pdf_path}")
                            imprimir_pdf_no_windows(pdf_path, copias)
                else:
                    msg = (
                        f"Tipo: {tipo_documento}\nEquipa: {equipa_nome}\nAno: {ano}\nMês: {nome_mes.title()}\n\n"
                        "Deseja continuar com a impressão?"
                    )
                    if messagebox.askyesno("Confirmar Impressão", msg):
                        logger.info(f"Imprimindo 1x: {pdf_path}")
                        imprimir_pdf_no_windows(pdf_path)

            documentos_gerados.append(caminho_final)
            logger.info(f"Documento gerado: {caminho_final}")

        if documentos_gerados:
            messagebox.showinfo("Sucesso", f"{len(documentos_gerados)} documento(s) gerado(s) com sucesso!")
        else:
            messagebox.showinfo("Nada feito", "Nenhum documento foi gerado (possivelmente já existiam)")

if __name__ == "__main__":
    app = GeradorQRCode()
