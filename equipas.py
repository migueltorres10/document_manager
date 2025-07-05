import tkinter as tk
from tkinter import ttk, messagebox
from core.db_helpers import carregar_equipas
from core.gui_utils import filtrar_combobox_por_texto, atualizar_listbox_por_filtro
from config import connect_bd


class GestorEquipas:
    def __init__(self, on_close=None):
        self.equipas = carregar_equipas(as_dict=False)
        self.id_selecionado = None
        self.on_close = on_close
        self.inicializar_interface()

    def inicializar_interface(self):
        self.root = tk.Toplevel()
        self.root.title("Gestor de Equipas")
        self.root.geometry("400x400")

        # Filtro
        tk.Label(self.root, text="Pesquisar:").pack(pady=2)
        self.pesquisa_var = tk.StringVar()
        self.entry_pesquisa = tk.Entry(self.root, textvariable=self.pesquisa_var)
        self.entry_pesquisa.pack(fill=tk.X, padx=10)
        self.entry_pesquisa.bind("<KeyRelease>", self.atualizar_lista_evento)

        # Listbox
        self.listbox = tk.Listbox(self.root, height=8)
        self.listbox.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.carregar_detalhes)

        self.atualizar_lista_evento()

        # Formulário
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=5, fill='x')

        tk.Label(frame, text="ID Equipa:").grid(row=0, column=0, sticky='e', pady=2)
        self.id_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.id_var, width=30, state="readonly").grid(row=0, column=1, sticky='w', pady=2)

        tk.Label(frame, text="Nome:").grid(row=1, column=0, sticky='e', pady=2)
        self.nome_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.nome_var, width=30).grid(row=1, column=1, sticky='w', pady=2)

        # Botões
        botoes = tk.Frame(self.root)
        botoes.pack(pady=10)

        tk.Button(botoes, text="Novo", width=10, command=self.nova_equipa).grid(row=0, column=0, padx=5)
        tk.Button(botoes, text="Salvar", width=10, command=self.salvar_equipa).grid(row=0, column=1, padx=5)
        tk.Button(botoes, text="Eliminar", width=10, command=self.eliminar_equipa).grid(row=0, column=2, padx=5)
        tk.Button(botoes, text="Fechar", width=10, command=self.fechar_janela).grid(row=0, column=3, padx=5)


    def fechar_janela(self):
        if self.on_close:
            self.on_close()
        self.root.destroy()

    def filtrar_equipas(self, event=None):
        filtrar_combobox_por_texto(
            self.entry_pesquisa, self.listbox, self.equipas, "nome")

    def atualizar_lista_evento(self, event=None):
        atualizar_listbox_por_filtro(
            self.listbox, 
            self.equipas, 
            campos=["id", "nome"],
            termo=self.pesquisa_var.get(),
            formato_linha=lambda x: f"{x['id']} - {x['nome']}"
        )

    def carregar_detalhes(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return

        linha = self.listbox.get(sel[0])
        id_str, nome = linha.split(" - ", 1)
        self.id_selecionado = int(id_str)
        self.id_var.set(id_str)
        self.nome_var.set(nome)

    def nova_equipa(self):
        self.id_selecionado = None
        self.id_var.set("")
        self.nome_var.set("")

    def salvar_equipa(self):
        nome = self.nome_var.get().strip()

        if not nome:
            messagebox.showwarning("Dados inválidos", "O nome não pode estar vazio.")
            return


        conn = connect_bd("D")
        cursor = conn.cursor()
        try:
            if self.id_selecionado:
                cursor.execute("UPDATE equipas SET nome = ? WHERE id = ?", (nome, self.id_selecionado))
            else:
                cursor.execute("INSERT INTO equipas (nome) VALUES (?)", (nome,))
            conn.commit()
            messagebox.showinfo("Sucesso", "Equipa salva com sucesso.")
            self.equipas = carregar_equipas(as_dict=False)
            self.atualizar_lista_evento()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
        finally:
            conn.close()

    def eliminar_equipa(self):
        if not self.id_selecionado:
            messagebox.showwarning("Selecionar", "Selecione uma equipa.")
            return

        confirm = messagebox.askyesno("Confirmação", f"Eliminar equipa {self.id_selecionado}?")
        if not confirm:
            return

        conn = connect_bd("D")
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM equipas WHERE id = ?", (self.id_selecionado,))
            conn.commit()
            messagebox.showinfo("Removido", "Equipa eliminada com sucesso.")
            self.nova_equipa()
            self.equipas = carregar_equipas(as_dict=False)
            self.atualizar_lista_evento()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao eliminar: {e}")
        finally:
            conn.close()


def main():
    root = tk.Tk()
    root.withdraw()
    GestorEquipas(on_close=root.destroy)
    root.mainloop()


if __name__ == "__main__":
    main()
