import tkinter as tk
from tkinter import ttk, messagebox
from services.turma_service import TurmaService
from datetime import datetime

class TurmasInterface:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.parent_frame.configure(bg='white')
        self.turma_service = TurmaService()
        self.turma_editando = None
        self.create_interface()
        self.carregar_turmas()
    
    def create_interface(self):
        """Cria interface simplificada de turmas"""
        # Container principal
        main_container = tk.Frame(self.parent_frame, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(
            main_container,
            text="🏫 Gestão de Turmas",
            font=('Arial', 24, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 30))
        
        # Notebook
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba Cadastro
        cadastro_frame = tk.Frame(notebook, bg='white')
        notebook.add(cadastro_frame, text="📝 Cadastro")
        
        # Aba Lista
        lista_frame = tk.Frame(notebook, bg='white')
        notebook.add(lista_frame, text="📋 Lista de Turmas")
        
        self.create_cadastro_form(cadastro_frame)
        self.create_lista_turmas(lista_frame)
    
    def create_cadastro_form(self, parent):
        """Formulário simplificado apenas com dados acadêmicos"""
        form_container = tk.Frame(parent, bg='white')
        form_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Seção dados da turma
        dados_frame = tk.LabelFrame(
            form_container,
            text="  📚 Dados Acadêmicos da Turma  ",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        dados_frame.pack(fill=tk.X, pady=(0, 30))
        
        content = tk.Frame(dados_frame, bg='white')
        content.pack(fill=tk.X, padx=30, pady=20)
        
        # Nome da Turma
        tk.Label(content, text="Nome da Turma *:", 
                font=('Arial', 12, 'bold'), 
                bg='white', fg='#2c3e50').grid(row=0, column=0, sticky='w', pady=10)
        
        self.nome_var = tk.StringVar()
        nome_entry = tk.Entry(content, textvariable=self.nome_var, width=40,
                             font=('Arial', 12), relief='solid', bd=1)
        nome_entry.grid(row=0, column=1, sticky='ew', pady=10, padx=(15, 0))
        
        # Série/Ano
        tk.Label(content, text="Série/Ano *:", 
                font=('Arial', 12, 'bold'), 
                bg='white', fg='#2c3e50').grid(row=1, column=0, sticky='w', pady=10)
        
        self.serie_var = tk.StringVar()
        serie_entry = tk.Entry(content, textvariable=self.serie_var, width=20,
                              font=('Arial', 12), relief='solid', bd=1)
        serie_entry.grid(row=1, column=1, sticky='w', pady=10, padx=(15, 0))
        
        # Ano Letivo
        tk.Label(content, text="Ano Letivo *:", 
                font=('Arial', 12, 'bold'), 
                bg='white', fg='#2c3e50').grid(row=2, column=0, sticky='w', pady=10)
        
        self.ano_letivo_var = tk.StringVar(value=str(datetime.now().year))
        ano_entry = tk.Entry(content, textvariable=self.ano_letivo_var, width=10,
                            font=('Arial', 12), relief='solid', bd=1)
        ano_entry.grid(row=2, column=1, sticky='w', pady=10, padx=(15, 0))
        
        content.columnconfigure(1, weight=1)
        
        # Informação sobre dados financeiros
        info_frame = tk.Frame(form_container, bg='#e8f4fd', relief='solid', bd=1)
        info_frame.pack(fill=tk.X, pady=(0, 30), ipady=15)
        
        tk.Label(
            info_frame,
            text="ℹ️ Informação Importante",
            font=('Arial', 12, 'bold'),
            bg='#e8f4fd',
            fg='#0c5460'
        ).pack(pady=(0, 5))
        
        tk.Label(
            info_frame,
            text="Os dados financeiros (mensalidade, desconto, multa) agora são configurados\n"
                 "individualmente para cada aluno no cadastro de alunos.",
            font=('Arial', 10),
            bg='#e8f4fd',
            fg='#0c5460',
            justify=tk.CENTER
        ).pack()
        
        # Botões
        buttons_frame = tk.Frame(form_container, bg='white')
        buttons_frame.pack(fill=tk.X)
        
        separator = tk.Frame(buttons_frame, height=2, bg='#dee2e6')
        separator.pack(fill=tk.X, pady=(0, 20))
        
        self.salvar_btn = tk.Button(
            buttons_frame,
            text="💾 Salvar Turma",
            command=self.salvar_turma,
            font=('Arial', 14, 'bold'),
            bg='#28a745',
            fg='white',
            padx=30, pady=12, relief='flat', cursor='hand2'
        )
        self.salvar_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        limpar_btn = tk.Button(
            buttons_frame,
            text="🔄 Limpar",
            command=self.limpar_formulario,
            font=('Arial', 14, 'bold'),
            bg='#6c757d',
            fg='white',
            padx=30, pady=12, relief='flat', cursor='hand2'
        )
        limpar_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        self.cancelar_btn = tk.Button(
            buttons_frame,
            text="❌ Cancelar Edição",
            command=self.cancelar_edicao,
            font=('Arial', 14, 'bold'),
            bg='#dc3545',
            fg='white',
            padx=30, pady=12, relief='flat', cursor='hand2'
        )
        self.cancelar_btn.pack(side=tk.LEFT)
        self.cancelar_btn.pack_forget()
    
    def create_lista_turmas(self, parent):
        """Lista de turmas simplificada"""
        lista_container = tk.Frame(parent, bg='white')
        lista_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Tabela
        table_frame = tk.LabelFrame(
            lista_container,
            text="  📋 Turmas Cadastradas  ",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        table_content = tk.Frame(table_frame, bg='white')
        table_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Treeview
        columns = ('ID', 'Nome', 'Série', 'Ano Letivo', 'Alunos')
        self.tree = ttk.Treeview(table_content, columns=columns, show='headings', height=15)
        
        # Configurar colunas
        column_widths = {'ID': 50, 'Nome': 250, 'Série': 150, 'Ano Letivo': 100, 'Alunos': 80}
        
        for col in columns:
            self.tree.heading(col, text=col, anchor='center')
            self.tree.column(col, width=column_widths[col], anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_content, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_content, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        table_content.grid_rowconfigure(0, weight=1)
        table_content.grid_columnconfigure(0, weight=1)
        
        # Botões de ação
        action_frame = tk.Frame(table_frame, bg='white')
        action_frame.pack(fill=tk.X, padx=20, pady=(10, 15))
        
        separator2 = tk.Frame(action_frame, height=2, bg='#dee2e6')
        separator2.pack(fill=tk.X, pady=(0, 15))
        
        editar_btn = tk.Button(
            action_frame, text="✏️ Editar", command=self.editar_turma,
            font=('Arial', 11, 'bold'), bg='#007bff',
            fg='white', padx=20, pady=8, relief='flat', cursor='hand2'
        )
        editar_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        excluir_btn = tk.Button(
            action_frame, text="🗑️ Excluir", command=self.excluir_turma,
            font=('Arial', 11, 'bold'), bg='#dc3545',
            fg='white', padx=20, pady=8, relief='flat', cursor='hand2'
        )
        excluir_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        atualizar_btn = tk.Button(
            action_frame, text="🔄 Atualizar", command=self.carregar_turmas,
            font=('Arial', 11, 'bold'), bg='#6c757d',
            fg='white', padx=20, pady=8, relief='flat', cursor='hand2'
        )
        atualizar_btn.pack(side=tk.LEFT)
        
        # Bind duplo clique
        self.tree.bind('<Double-1>', lambda e: self.editar_turma())
    
    def validar_formulario(self):
        """Valida campos obrigatórios"""
        erros = []
        
        if not self.nome_var.get().strip():
            erros.append("Nome da turma é obrigatório")
        
        if not self.serie_var.get().strip():
            erros.append("Série/Ano é obrigatório")
        
        if not self.ano_letivo_var.get().strip():
            erros.append("Ano letivo é obrigatório")
        else:
            try:
                int(self.ano_letivo_var.get())
            except ValueError:
                erros.append("Ano letivo deve ser um número válido")
        
        return erros
    
    def salvar_turma(self):
        """Salva turma com dados simplificados"""
        erros = self.validar_formulario()
        if erros:
            messagebox.showerror("Erro de Validação", "\n".join(erros))
            return
        
        try:
            turma_data = {
                'nome': self.nome_var.get().strip(),
                'serie': self.serie_var.get().strip(),
                'ano_letivo': self.ano_letivo_var.get().strip()
            }
            
            if self.turma_editando:
                turma_data['id'] = self.turma_editando
            
            resultado = self.turma_service.salvar_turma(turma_data)
            
            if resultado['success']:
                acao = "atualizada" if self.turma_editando else "cadastrada"
                messagebox.showinfo("Sucesso", f"✅ Turma {acao} com sucesso!")
                self.limpar_formulario()
                self.cancelar_edicao()
                self.carregar_turmas()
            else:
                messagebox.showerror("Erro", f"❌ Erro: {resultado['error']}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"❌ Erro inesperado: {str(e)}")
    
    def editar_turma(self):
        """Edita turma selecionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma turma para editar!")
            return
        
        try:
            item = self.tree.item(selection[0])
            turma_id = item['values'][0]
            
            turma = self.turma_service.buscar_turma_por_id(turma_id)
            if not turma:
                messagebox.showerror("Erro", "Turma não encontrada!")
                return
            
            # Preencher formulário
            self.nome_var.set(turma['nome'])
            self.serie_var.set(turma['serie'])
            self.ano_letivo_var.set(turma['ano_letivo'])
            
            # Modo edição
            self.turma_editando = turma_id
            self.salvar_btn.config(text="💾 Atualizar Turma")
            self.cancelar_btn.pack(side=tk.LEFT, padx=(15, 0))
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar turma: {str(e)}")
    
    def cancelar_edicao(self):
        """Cancela edição"""
        self.turma_editando = None
        self.salvar_btn.config(text="💾 Salvar Turma")
        self.cancelar_btn.pack_forget()
    
    def excluir_turma(self):
        """Exclui turma"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma turma para excluir!")
            return
        
        item = self.tree.item(selection[0])
        turma_id = item['values'][0]
        turma_nome = item['values'][1]
        
        if messagebox.askyesno("Confirmar", f"Excluir turma '{turma_nome}'?"):
            resultado = self.turma_service.excluir_turma(turma_id)
            if resultado['success']:
                messagebox.showinfo("Sucesso", "Turma excluída!")
                self.carregar_turmas()
            else:
                messagebox.showerror("Erro", resultado['error'])
    
    def limpar_formulario(self):
        """Limpa formulário"""
        self.nome_var.set("")
        self.serie_var.set("")
        self.ano_letivo_var.set(str(datetime.now().year))
    
    def carregar_turmas(self):
        """Carrega lista de turmas"""
        try:
            # Limpar tabela
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            turmas = self.turma_service.listar_turmas()
            
            for turma in turmas:
                valores = (
                    turma['id'],
                    turma['nome'],
                    turma['serie'],
                    turma['ano_letivo'],
                    turma.get('total_alunos', 0)
                )
                self.tree.insert('', tk.END, values=valores)
            
            print(f"✅ {len(turmas)} turmas carregadas")
            
        except Exception as e:
            print(f"Erro ao carregar turmas: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar turmas: {str(e)}")
