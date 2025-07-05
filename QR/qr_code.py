# QR/qr_code.py
import os
import tkinter as tk
from tkinter import ttk, messagebox
from core.db_helpers import carregar_equipas
from core.gui_utils import centralizar_janela
from core.constantes import MESES, MESES_MAP, TIPOS_DOCUMENTOS
from core.global_utils import inserir_qr_no_excel
import qrcode


class GeradorQRCode:
    def __init__(self):
        self.equipas = carregar_equipas()
        self.inserir_qr_no_excel = inserir_qr_no_excel
        print(f"[DEBUG] Equipas carregadas: {self.equipas}")
        self.meses_var = []
        self.meses_checkbuttons = []
        self.tipo_documento = None

        self._inicializar_interface()

    def _inicializar_interface(self):
        self.root = tk.Toplevel()
        self.root.title("Gerador de QRCode para Documentos Internos")
        self.root.geometry("350x400")
        centralizar_janela(self.root)
        self.root.attributes('-topmost', 1)

        self.equipa_var = tk.StringVar()
        self.ano_var = tk.StringVar()
        self.tipo_var = tk.StringVar()  # Definindo o tipo padrão

        self._criar_widgets()

    def _criar_widgets(self):
        self._adicionar_label_entry("Equipa:", self.equipa_var, is_combobox="equipa")
        self._adicionar_label_entry("Ano:", self.ano_var)
        self._adicionar_label_entry("Tipo de Documento:", self.tipo_var, is_combobox=True)


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

        tk.Button(self.root, text="Gerar QRCode", command=self.gerar_qrcode).pack(pady=15)

    def _tipo_selecionado(self, tipo):
        self.tipo_var.set(tipo)
        if tipo == "Folhas de Obra":
            for cb, (_, var) in zip(self.meses_checkbuttons, self.meses_var):
                cb.config(state="disabled")
                var.set(False)
        else:
            for cb in self.meses_checkbuttons:
                cb.config(state="normal")

    def _adicionar_label_entry(self, texto, var, is_combobox=False):
        tk.Label(self.root, text=texto).pack(pady=5)
        if is_combobox:
            combo = ttk.Combobox(self.root, textvariable=var, state="normal", width=40)
            if texto.lower().startswith("equipa"):
                valores = [f"{id} - {nome}" for id, nome in self.equipas.items()]
                combo["values"] = valores
                combo.bind("<KeyRelease>", self.filtrar_equipas)
                self.combo_equipa = combo
            elif texto.lower().startswith("tipo"):
                tipos_validos = ["Folhas de Obra", "Folhas Faltas", "Folhas Assiduidade"]
                combo["values"] = tipos_validos
                combo.bind("<<ComboboxSelected>>", lambda e: self._tipo_selecionado(combo.get()))
            combo.pack(pady=5)
        else:
            entry = tk.Entry(self.root, textvariable=var, width=40)
            if texto.lower().startswith("ano"):
                entry.config(width=10)
            entry.pack(pady=5)

    def filtrar_equipas(self, event):
        texto = self.equipa_var.get().lower()
        filtrados = [f"{id} - {nome}" for id, nome in self.equipas.items() if texto in nome.lower()]
        self.combo_equipa['values'] = filtrados

    def gerar_qrcode(self):
        tipo_documento = self.tipo_var.get().strip()
        equipa_str = self.equipa_var.get().strip()

        if " - " not in equipa_str:
            messagebox.showwarning("Equipa inválida", "Selecione uma equipa válida.")
            return

        equipa_id = equipa_str.split(" - ")[0].strip()
        equipa_nome = self.equipas.get(int(equipa_id), "Desconhecida")

        ano = self.ano_var.get().strip()
        if not ano.isdigit() or len(ano) != 4:
            messagebox.showwarning("Ano inválido", "Insira um ano válido com 4 dígitos (ex: 2025).")
            return

        if tipo_documento not in TIPOS_DOCUMENTOS:
            messagebox.showwarning("Tipo inválido", "Selecione um tipo de documento válido.")
            return

        meses_selecionados = [mes for mes, var in self.meses_var if var.get()]
        if tipo_documento == "Folhas de Obra":
            meses_selecionados = [None]

        if not meses_selecionados:
            messagebox.showwarning("Mês obrigatório", "Selecione pelo menos um mês.")
            return

        # Caminho do template base
        template_base = os.path.join("templates", f"{TIPOS_DOCUMENTOS[tipo_documento]}_Base.xlsx")
        documentos_gerados = []

        for mes in meses_selecionados:
            conteudo_qr = f"equipa={equipa_id};ano={ano}"
            nome_mes = "Geral"
            if mes:
                mes_num = MESES_MAP.get(mes)
                conteudo_qr += f";mes={mes_num:02d}"
                nome_mes = mes.lower()

            # Gera QR
            qr = qrcode.make(conteudo_qr)

            # Caminho QR temporário
            qr_temp_path = os.path.join("temp", f"qr_{equipa_id}_{ano}_{nome_mes}.png")
            os.makedirs("temp", exist_ok=True)
            qr.save(qr_temp_path)

            # Pasta e nome final do documento
            pasta_saida = os.path.join(tipo_documento, "geradas", ano, equipa_nome)
            os.makedirs(pasta_saida, exist_ok=True)
            nome_ficheiro = f"{ano}_{nome_mes}_{equipa_nome}.xlsx"
            caminho_final = os.path.join(pasta_saida, nome_ficheiro)

            # Verifica duplicação para tipos sensíveis
            if tipo_documento != "Folhas de Obra" and os.path.exists(caminho_final):
                print(f"[INFO] Já existe: {caminho_final} — ignorado")
                continue

            # Copia template e insere QR
            from core.global_utils import inserir_qr_no_excel
            inserir_qr_no_excel(template_base, caminho_final, qr_temp_path)

            documentos_gerados.append(caminho_final)
            print(f"[OK] Documento gerado: {caminho_final}")

        if documentos_gerados:
            messagebox.showinfo("Sucesso", f"{len(documentos_gerados)} documento(s) gerado(s) com sucesso!")
        else:
            messagebox.showinfo("Nada feito", "Nenhum documento foi gerado (possivelmente já existiam")

if __name__ == "__main__":
    GeradorQRCode()
