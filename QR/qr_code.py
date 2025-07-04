# QR/qr_code.py
import os
import tkinter as tk
from tkinter import ttk, messagebox
import qrcode
from utils import carregar_equipas
from core.gui_utils import centralizar_janela, filtrar_combobox_por_texto
from core.constantes import MESES, MESES_MAP

class GeradorQRCode:
    def __init__(self):
        self.equipas = carregar_equipas()
        self.meses_var = []

        self._inicializar_interface()

    def _inicializar_interface(self):
        self.root = tk.Toplevel()
        self.root.title("Gerador de QRCode para Documentos Internos")
        self.root.geometry("400x300")
        centralizar_janela(self.root)
        self.root.attributes('-topmost', 1)

        self.equipa_var = tk.StringVar()
        self.ano_var = tk.StringVar()

        self._criar_widgets()

    def _criar_widgets(self):
        self._adicionar_label_entry("Equipa:", self.equipa_var, is_combobox="equipa")
        self._adicionar_label_entry("Ano:", self.ano_var)

        frame_meses = tk.LabelFrame(self.root, text="Mês de Trabalho")
        frame_meses.pack(pady=10)

        def on_mes_selecionado(mes_index):
            for i, (_, var) in enumerate(self.meses_var):
                if i != mes_index:
                    var.set(False)

        for i, mes in enumerate(MESES):
            var = tk.BooleanVar()
            cb = tk.Checkbutton(
                frame_meses,
                text=mes,
                variable=var,
                command=lambda i=i: on_mes_selecionado(i)
            )
            cb.grid(row=i // 3, column=i % 3, sticky="w", padx=5, pady=2)
            self.meses_var.append((mes, var))

        tk.Button(self.root, text="Gerar QRCode", command=self.gerar_qrcode).pack(pady=15)

    def _adicionar_label_entry(self, texto, var, is_combobox=False):
        tk.Label(self.root, text=texto).pack(pady=5)
        if is_combobox:
            combo = ttk.Combobox(self.root, textvariable=var, state="normal", width=40)
            if texto.lower().startswith("equipa"):
                valores = [f"{p['id']} - {p['nome']}" for p in self.equipas]
                combo["values"] = valores
                combo.bind("<KeyRelease>", self.filtrar_equipas)
                self.combo_equipa = combo
            combo.pack(pady=5)
        else:
            entry = tk.Entry(self.root, textvariable=var, width=40)
            if texto.lower().startswith("ano"):
                entry.config(width=10)
            entry.pack(pady=5)

    def filtrar_equipas(self, event):
        texto = self.equipa_var.get().lower()
        filtrados = [f"{e['id']} - {e['nome']}" for e in self.equipas if texto in e["nome"].lower()]
        self.combo_equipa['values'] = filtrados

    def obter_mes_selecionado(self):
        for mes, var in self.meses_var:
            if var.get():
                return mes
        return None

    def gerar_qrcode(self):
        equipa_str = self.equipa_var.get().strip()
        print(f"[DEBUG] equipa_var.get(): '{self.equipa_var.get()}'")
        print(f"[DEBUG] equipa_str (após strip): '{equipa_str}'")

        if " - " not in equipa_str:
            print("[DEBUG] ' - ' não encontrado na string da equipa.")
            messagebox.showwarning("Equipa inválida", "Selecione uma equipa válida.")
            return

        equipa_id = equipa_str.split(" - ")[0].strip()
        print(f"[DEBUG] equipa_id extraído: '{equipa_id}'")

        ids_validos = [str(e["id"]) for e in self.equipas]
        print(f"[DEBUG] Lista de IDs válidos: {ids_validos}")

        if equipa_id not in ids_validos:
            print(f"[DEBUG] ID '{equipa_id}' não está na lista de IDs válidos.")
            messagebox.showwarning("Equipa inválida", f"O ID '{equipa_id}' não é reconhecido.")
            return

        ano = self.ano_var.get().strip()
        mes = self.obter_mes_selecionado()
        print(f"[DEBUG] Ano: '{ano}', Mês: '{mes}'")

        conteudo_qr = f"equipa={equipa_id}"
        if ano:
            conteudo_qr += f";ano={ano}"
        if mes:
            mes_num = MESES_MAP.get(mes)
            conteudo_qr += f";mes={mes_num:02d}"

        print(f"[DEBUG] Conteúdo do QR: {conteudo_qr}")

        qr = qrcode.make(conteudo_qr)

        partes = [equipa_id]
        if ano:
            partes.append(ano)
        if mes:
            partes.append(f"{MESES_MAP[mes]:02d}")
        nome_ficheiro = "_".join(partes) + ".png"

        pasta_qr = os.path.join(os.path.dirname(__file__), "gerados")
        os.makedirs(pasta_qr, exist_ok=True)

        caminho_completo = os.path.join(pasta_qr, nome_ficheiro)
        qr.save(caminho_completo)

        print(f"[DEBUG] QR Code guardado em: {caminho_completo}")
        messagebox.showinfo("Sucesso", f"QR Code guardado como:\n{nome_ficheiro}")

if __name__ == "__main__":
    GeradorQRCode()
