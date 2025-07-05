# QR/qr_code.py
import os
import tkinter as tk
from tkinter import ttk, messagebox
import qrcode
from core.db_helpers import carregar_equipas
from core.gui_utils import centralizar_janela
from core.constantes import MESES, MESES_MAP, TIPOS_DOCUMENTOS

class GeradorQRCode:
    def __init__(self):
        self.equipas = carregar_equipas()
        print(f"[DEBUG] Equipas carregadas: {self.equipas}")
        self.meses_var = []
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

        tk.Button(self.root, text="Gerar QRCode", command=self.gerar_qrcode).pack(pady=15)

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
                combo.bind("<<ComboboxSelected>>", lambda e: self.tipo_var.set(combo.get()))
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
        print(f"[DEBUG] equipa_var.get(): '{self.equipa_var.get()}'")
        print(f"[DEBUG] equipa_str (após strip): '{equipa_str}'")

        if " - " not in equipa_str:
            print("[DEBUG] ' - ' não encontrado na string da equipa.")
            messagebox.showwarning("Equipa inválida", "Selecione uma equipa válida.")
            return

        equipa_id = equipa_str.split(" - ")[0].strip()
        print(f"[DEBUG] equipa_id extraído: '{equipa_id}'")

        ids_validos = [str(eid) for eid in self.equipas.keys()]
        print(f"[DEBUG] Lista de IDs válidos: {ids_validos}")

        if equipa_id not in ids_validos:
            print(f"[DEBUG] ID '{equipa_id}' não está na lista de IDs válidos.")
            messagebox.showwarning("Equipa inválida", f"O ID '{equipa_id}' não é reconhecido.")
            return

        ano = self.ano_var.get().strip()
        if not ano.isdigit() or len(ano) != 4:
            messagebox.showwarning("Ano inválido", "Insira um ano válido com 4 dígitos (ex: 2025).")
            return
        
        
        if tipo_documento not in TIPOS_DOCUMENTOS:
            messagebox.showwarning("Tipo inválido", "Selecione um tipo de documento válido.")
            return
        
        meses_selecionados = [mes for mes, var in self.meses_var if var.get()]

        if not meses_selecionados:
            meses_selecionados = [None]

        for mes in meses_selecionados:
            conteudo_qr = f"equipa={equipa_id}"
            if ano:
                conteudo_qr += f";ano={ano}"
            if mes:
                mes_num = MESES_MAP.get(mes)
                conteudo_qr += f";mes={mes_num:02d}"

            qr = qrcode.make(conteudo_qr)

            partes = [equipa_id]
            if ano:
                partes.append(ano)
            if mes:
                partes.append(f"{MESES_MAP[mes]:02d}")
            nome_ficheiro = "_".join(partes) + ".png"

            partes_pasta = [
                os.path.join(os.path.dirname(__file__), ".."),
                tipo_documento,
                "minutas",
                ano,
                self.equipas[int(equipa_id)]  # Nome da equipa
            ]

            if mes:
                partes_pasta.append(f"{MESES_MAP[mes]:02d}")
            pasta_qr = os.path.join(*partes_pasta)
            os.makedirs(pasta_qr, exist_ok=True)

            caminho_completo = os.path.join(pasta_qr, nome_ficheiro)
            qr.save(caminho_completo)
            print(f"[DEBUG] QR Code guardado em: {caminho_completo}")

        messagebox.showinfo("Sucesso", f"{len(meses_selecionados)} QR Code(s) gerado(s) com sucesso!")

if __name__ == "__main__":
    GeradorQRCode()
