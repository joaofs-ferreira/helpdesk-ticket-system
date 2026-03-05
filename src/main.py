import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from collections import namedtuple


class Aluno(namedtuple('Aluno', ['nome', 'email'])):
    @classmethod
    def exibir_tickets(cls, aluno_id, cursor, lista_widget):
        criador_tipo = "Aluno"
        cursor.execute("SELECT * FROM Ticket WHERE criador_id = %s AND criador_tipo = %s", (aluno_id, criador_tipo))
        tickets = cursor.fetchall()
        cls.exibir_tickets_na_lista(tickets, lista_widget)

    @staticmethod
    def exibir_tickets_na_lista(tickets, lista_widget):
        lista_widget.delete(0, tk.END)
        [lista_widget.insert(tk.END, f"ID: {ticket[0]}, Data: {ticket[2]}, Estado: {ticket[3]}, Descrição: {ticket[4]}, Tipo: {ticket[5]}") for ticket in tickets]

class Tecnico(namedtuple('Tecnico', ['nome', 'email'])):
    @classmethod
    def exibir_tickets(cls, cursor, lista_widget):
        tickets = cls.obter_tickets(cursor)
        cls.exibir_tickets_na_lista(tickets, lista_widget)

    @staticmethod
    def exibir_tickets_na_lista(tickets, lista_widget):
        lista_widget.delete(0, tk.END)
        [lista_widget.insert(tk.END, f"ID: {ticket[0]}, Data: {ticket[2]}, Estado: {ticket[3]}, Descrição: {ticket[4]}, Tipo: {ticket[5]}") for ticket in tickets]

    @staticmethod
    def obter_tickets(cursor):
        cursor.execute("SELECT * FROM Ticket")
        return cursor.fetchall()

class Diretor(namedtuple('Diretor', ['nome', 'email'])):
    @classmethod
    def exibir_tickets(cls, cursor, lista_widget):
        cursor.execute("SELECT * FROM Ticket")
        tickets = cursor.fetchall()
        cls.exibir_tickets_na_lista(tickets, lista_widget)
    
    @staticmethod
    def exibir_tickets_na_lista(tickets, lista_widget):
        lista_widget.delete(0, tk.END)
        [lista_widget.insert(tk.END, f"ID: {ticket[0]}, Data: {ticket[2]}, Estado: {ticket[3]}, Descrição: {ticket[4]}, Tipo: {ticket[5]}") for ticket in tickets]


class TicketManager:
    def __init__(self, interface_grafica, conexao, cursor):
        self.interface_grafica = interface_grafica
        self.conexao = conexao
        self.cursor = cursor

        self.entry_nome = None
        self.entry_email = None
        self.entry_descricao = None

        self.frames = {"Aluno": tk.Frame(), "Diretor": tk.Frame(), "Técnico": tk.Frame()}

        self.lista_tickets = tk.Listbox(width=80, height=10)
        self.lista_tickets.pack()

        self.btn_exibir_tickets = tk.Button(text="Exibir Tickets", command=self.exibir_tickets)
        self.btn_exibir_tickets.pack(pady=10)

    def configurar_widgets(self, modo):
        for widget in self.frames[modo].winfo_children():
            widget.destroy()

        if modo == "Aluno":
            tk.Label(self.frames[modo], text="Nome do Aluno:").pack()
            self.entry_nome = tk.Entry(self.frames[modo], width=35)
            self.entry_nome.pack(pady=5)

            tk.Label(self.frames[modo], text="Email do Aluno:").pack()
            self.entry_email = tk.Entry(self.frames[modo], width=35)
            self.entry_email.pack(pady=5)

            tk.Label(self.frames[modo], text="Descrição:").pack()
            self.entry_descricao = tk.Text(self.frames[modo], width=35, height=5, wrap="word", padx=5, pady=5, relief="solid", borderwidth=1)
            self.entry_descricao.pack(pady=5)

            btn_adicionar_ticket = tk.Button(self.frames[modo], text="Adicionar Ticket", command=self.adicionar_ticket)
            btn_adicionar_ticket.pack(pady=15)

        elif modo == "Técnico":
            tk.Label(self.frames[modo], text="Nome do Técnico:").pack()
            self.entry_nome = tk.Entry(self.frames[modo], width=35)
            self.entry_nome.pack(pady=5)

            tk.Label(self.frames[modo], text="Email do Técnico:").pack()
            self.entry_email = tk.Entry(self.frames[modo], width=35)
            self.entry_email.pack(pady=5)

            btn_atualizar_ticket = tk.Button(self.frames[modo], text="Atualizar Ticket",
                                             command=self.atualizar_ticket_tecnico)
            btn_atualizar_ticket.pack(pady=10)

        elif modo == "Diretor":
            tk.Label(self.frames[modo], text="Nome do Diretor:").pack()
            self.entry_nome = tk.Entry(self.frames[modo], width=35)
            self.entry_nome.pack(pady=5)

            tk.Label(self.frames[modo], text="Email do Diretor:").pack()
            self.entry_email = tk.Entry(self.frames[modo], width=35)
            self.entry_email.pack(pady=5)

            tk.Label(self.frames[modo], text="Descrição:").pack()
            self.entry_descricao = tk.Text(self.frames[modo], width=35, height=5, wrap="word", padx=5, pady=5, relief="solid", borderwidth=1)
            self.entry_descricao.pack(pady=5)

            btn_adicionar_ticket = tk.Button(self.frames[modo], text="Adicionar Ticket", command=self.adicionar_ticket)
            btn_adicionar_ticket.pack(pady=15)

            btn_eliminar_ticket = tk.Button(self.frames[modo], text="Eliminar Ticket", command=self.eliminar_ticket)
            btn_eliminar_ticket.pack(pady=15)

    def adicionar_ticket(self):
        criador_nome = self.entry_nome.get()
        criador_email = self.entry_email.get()
        descricao = self.entry_descricao.get("1.0", tk.END)

        if not criador_nome or not criador_email or not descricao:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
            return

        criador_tipo = self.interface_grafica.combo_modos.get()
        criador = None

        if criador_tipo == "Aluno":
            criador = Aluno(nome=criador_nome, email=criador_email)
        elif criador_tipo == "Diretor":
            criador = Diretor(nome=criador_nome, email=criador_email)

        criador_id = self.obter_id_criador(criador.nome, criador.email, criador_tipo)

        if criador_id is not None:
            estado_padrao = "em_analise"
            self.cursor.execute("INSERT INTO Ticket (criador_id, estado, descricao, criador_tipo) VALUES (%s, %s, %s, %s)", (criador_id, estado_padrao, descricao, criador_tipo))
            self.conexao.commit()
            messagebox.showinfo("Sucesso", "Ticket adicionado com sucesso!")
            self.exibir_tickets()
        else:
            messagebox.showerror("Erro", f"{criador_tipo} não encontrado.")

    def exibir_tickets(self):
        modo_leitura = self.interface_grafica.combo_modos.get()

        for frame in self.frames.values():
            frame.pack_forget()

        self.frames[modo_leitura].pack()
        self.configurar_widgets(modo_leitura)

        if modo_leitura == "Aluno":
            Aluno.exibir_tickets(1, self.cursor, self.lista_tickets)
        elif modo_leitura == "Diretor":
            Diretor.exibir_tickets(self.cursor, self.lista_tickets)
        elif modo_leitura == "Técnico":
            Tecnico.exibir_tickets(self.cursor, self.lista_tickets)

    def obter_id_criador(self, nome, email, tipo):
        tabela = tipo
        self.cursor.execute(f"SELECT id FROM {tabela} WHERE nome = %s AND email = %s", (nome, email))
        criador_id = self.cursor.fetchone()

        if criador_id is not None:
            return criador_id[0]

        return None
    
    def obter_id_diretor(self, nome_dir, email_dir):
        diretor = Diretor(nome_dir, email_dir)
        self.cursor.execute("SELECT id FROM Diretor WHERE nome = %s AND email = %s", (diretor.nome, diretor.email))
        diretor_id = self.cursor.fetchone()

        if diretor_id is not None:
            return diretor_id[0]

        return None

    def eliminar_ticket(self):
        nome_dir = self.entry_nome.get()
        email_dir = self.entry_email.get()
        
        if not nome_dir or not email_dir:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos necessários.")
            return

        dir = Diretor(nome_dir, email_dir)
        dir_id = self.obter_id_diretor(dir.nome, dir.email)

        if dir_id is not None:
            resposta = messagebox.askquestion("Eliminar Ticket", "Tem certeza que deseja eliminar este ticket?")
            if resposta == "yes":
                selected_index = self.lista_tickets.curselection()
                if selected_index:
                    ticket_id = self.obter_id_ticket_selecionado(selected_index[0])
                    self.cursor.execute("DELETE FROM Ticket WHERE id = %s", (ticket_id,))
                    self.conexao.commit()
                    messagebox.showinfo("Sucesso", "Ticket eliminado com sucesso!")
            else:
                messagebox.showerror("Erro", "Diretor não encontrado.")
                    
        self.exibir_tickets()
   

    def obter_id_ticket_selecionado(self, index):
        parts = self.lista_tickets.get(index).split(":")
        if len(parts) >= 2:
            ticket_id = parts[1].strip().split(',')[0]
            return int(ticket_id)
        return None

    def obter_id_tec(self, nome_tec, email_tec):
        self.cursor.execute("SELECT id FROM Tecnico WHERE nome = %s AND email = %s", (nome_tec, email_tec))
        tec_id = self.cursor.fetchone()

        if tec_id is not None:
            return tec_id[0]

        return None

    def atualizar_ticket_tecnico(self):
        nome_tec = self.entry_nome.get()
        email_tec = self.entry_email.get()

        if not nome_tec or not email_tec:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos necessários.")
            return

        tec = Tecnico(nome_tec, email_tec)
        tec_id = self.obter_id_tec(tec.nome, tec.email)

        if tec_id is not None:
            selected_index = self.lista_tickets.curselection()
            if not selected_index:
                messagebox.showinfo("Informação", "Por favor, selecione um ticket antes de atualizar.")
                return

        if tec_id is not None:
            selected_index = self.lista_tickets.curselection()
            if selected_index:
                ticket_id = self.obter_id_ticket_selecionado(selected_index[0])
                self.cursor.execute("SELECT estado FROM Ticket WHERE id = %s", (ticket_id,))
                estado_atual = self.cursor.fetchone()
                if estado_atual is not None and estado_atual[0] == 'remendado':
                    messagebox.showinfo("Informação", "Este ticket já está 'remendado'. Não é possível atualizar novamente.")
                else:
                    self.cursor.execute("UPDATE Ticket SET estado = %s WHERE id = %s", ('remendado', ticket_id))
                    self.conexao.commit()
                    messagebox.showinfo("Sucesso", "Estado do ticket atualizado para 'remendado'.")
                    self.exibir_tickets()
        else:
            messagebox.showerror("Erro", "Técnico não encontrado.")

class InterfaceGrafica:
    def __init__(self):
        self.janela = tk.Tk()
        self.janela.geometry("600x600")
        self.janela.resizable(True, True)
        self.janela.title("Sistema de Tickets - ULP")

        modos = ["Aluno", "Diretor", "Técnico"]
        self.combo_modos = ttk.Combobox(self.janela, values=modos)
        self.combo_modos.set("Aluno")
        self.combo_modos.pack(pady=10)

        conexao = mysql.connector.connect(
            host='localhost',
            user='root',
            password='12345678',
            database='db_ticket',
        )
        cursor = conexao.cursor()

        self.ticket_manager = TicketManager(self, conexao, cursor)
        self.ticket_manager.configurar_widgets("Aluno")

        self.janela.protocol("WM_DELETE_WINDOW", self.janela.destroy)
        self.janela.mainloop()

# Seção principal do programa
def main():
    try:
        interface_grafica = InterfaceGrafica()

    except mysql.connector.Error as err:
        messagebox.showerror("Erro de Conexão", f"Erro ao conectar ao banco de dados: {err}")

if __name__ == "__main__":
    main()

