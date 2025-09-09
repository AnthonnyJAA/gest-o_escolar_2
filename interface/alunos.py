import tkinter as tk
from tkinter import ttk, messagebox
from services.aluno_service import AlunoService
from utils.formatters import format_phone, validate_phone, format_date, parse_date, validate_date, calculate_age, format_currency, format_cpf, validate_cpf
from datetime import datetime, date
import re

class AlunosInterface:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.parent_frame.configure(bg='white')
        self.aluno_service = AlunoService()
        self.aluno_editando = None
        
        try:
            self.create_interface()
            self.carregar_alunos()
        except Exception as e:
            print(f"Erro ao criar interface de alunos: {e}")
            self.show_error_interface(str(e))
    
    def show_error_interface(self, error_msg):
        """Mostra interface de erro caso algo dê errado"""
        error_frame = tk.Frame(self.parent_frame, bg='white')
        error_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            error_frame,
            text="⚠️ Erro na Interface de Alunos",
            font=('Arial', 18, 'bold'),
            bg='white',
            fg='#dc3545'
        ).pack(pady=(100, 20))
        
        tk.Label(
            error_frame,
            text=f"Erro: {error_msg}",
            font=('Arial', 12),
            bg='white',
            fg='#6c757d',
            wraplength=600
        ).pack(pady=10)
        
        retry_btn = tk.Button(
            error_frame,
            text="🔄 Tentar Novamente",
            command=self.retry_interface,
            font=('Arial', 11, 'bold'),
            bg='#007bff',
            fg='white',
            padx=20,
            pady=10,
            relief='flat',
            cursor='hand2'
        )
        retry_btn.pack(pady=20)
    
    def retry_interface(self):
        """Tenta recriar a interface"""
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        try:
            self.create_interface()
            self.carregar_alunos()
        except Exception as e:
            self.show_error_interface(str(e))
    
    def create_interface(self):
        """Cria a interface completa de alunos"""
        # Container principal
        main_container = tk.Frame(self.parent_frame, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(
            main_container,
            text="👥 Gestão de Alunos",
            font=('Arial', 24, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 30))
        
        # Criar notebook para organizar melhor
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba 1: Cadastro
        cadastro_frame = tk.Frame(notebook, bg='white')
        notebook.add(cadastro_frame, text="📝 Cadastro")
        
        # Aba 2: Lista
        lista_frame = tk.Frame(notebook, bg='white')
        notebook.add(lista_frame, text="📋 Lista de Alunos")
        
        # Criar conteúdo das abas
        self.create_cadastro_tab(cadastro_frame)
        self.create_lista_tab(lista_frame)
    
    def create_cadastro_tab(self, parent):
        """Cria a aba de cadastro"""
        # Container com scroll
        canvas = tk.Canvas(parent, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Formulário
        self.create_simple_form(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_simple_form(self, parent):
        """Cria formulário simples e funcional - COM CPF"""
        # Container do formulário
        form_container = tk.Frame(parent, bg='white')
        form_container.pack(fill=tk.X, padx=40, pady=20)
        
        # Seção 1: Dados Básicos do Aluno
        basic_frame = tk.LabelFrame(
            form_container,
            text="  Dados do Aluno  ",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        basic_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Grid básico
        basic_content = tk.Frame(basic_frame, bg='white')
        basic_content.pack(fill=tk.X, padx=20, pady=15)
        
        # Nome (linha 1)
        tk.Label(basic_content, text="Nome Completo *:", 
                font=('Arial', 10, 'bold'), 
                bg='white', 
                fg='#2c3e50').grid(row=0, column=0, sticky='w', pady=5)
        
        self.nome_var = tk.StringVar()
        nome_entry = tk.Entry(basic_content, textvariable=self.nome_var, width=40,
                             font=('Arial', 10), relief='solid', bd=1)
        nome_entry.grid(row=0, column=1, columnspan=2, sticky='ew', pady=5, padx=(10, 0))
        
        # Data nascimento e CPF (linha 2)
        tk.Label(basic_content, text="Data Nascimento *:", 
                font=('Arial', 10, 'bold'), 
                bg='white', 
                fg='#2c3e50').grid(row=1, column=0, sticky='w', pady=5)
        
        self.data_nasc_var = tk.StringVar()
        data_entry = tk.Entry(basic_content, textvariable=self.data_nasc_var, width=15,
                             font=('Arial', 10), relief='solid', bd=1)
        data_entry.grid(row=1, column=1, sticky='w', pady=5, padx=(10, 20))
        data_entry.bind('<KeyRelease>', self.format_date_entry)
        
        tk.Label(basic_content, text="CPF:", 
                font=('Arial', 10, 'bold'), 
                bg='white', 
                fg='#2c3e50').grid(row=1, column=2, sticky='w', pady=5)
        
        self.cpf_var = tk.StringVar()
        cpf_entry = tk.Entry(basic_content, textvariable=self.cpf_var, width=15,
                            font=('Arial', 10), relief='solid', bd=1)
        cpf_entry.grid(row=1, column=3, sticky='w', pady=5, padx=(10, 0))
        cpf_entry.bind('<KeyRelease>', self.format_cpf_entry)
        
        # Sexo e nacionalidade (linha 3)
        tk.Label(basic_content, text="Sexo:", 
                font=('Arial', 10, 'bold'), 
                bg='white', 
                fg='#2c3e50').grid(row=2, column=0, sticky='w', pady=5)
        
        self.sexo_var = tk.StringVar()
        sexo_combo = ttk.Combobox(basic_content, textvariable=self.sexo_var, 
                                 values=['Masculino', 'Feminino'], width=12, state='readonly')
        sexo_combo.grid(row=2, column=1, sticky='w', pady=5, padx=(10, 20))
        
        tk.Label(basic_content, text="Nacionalidade:", 
                font=('Arial', 10, 'bold'), 
                bg='white', 
                fg='#2c3e50').grid(row=2, column=2, sticky='w', pady=5)
        
        self.nacionalidade_var = tk.StringVar(value="Brasileira")
        nac_entry = tk.Entry(basic_content, textvariable=self.nacionalidade_var, width=15,
                            font=('Arial', 10), relief='solid', bd=1)
        nac_entry.grid(row=2, column=3, sticky='w', pady=5, padx=(10, 0))
        
        # Telefone (linha 4)
        tk.Label(basic_content, text="Telefone:", 
                font=('Arial', 10, 'bold'), 
                bg='white', 
                fg='#2c3e50').grid(row=3, column=0, sticky='w', pady=5)
        
        self.telefone_var = tk.StringVar()
        tel_entry = tk.Entry(basic_content, textvariable=self.telefone_var, width=15,
                            font=('Arial', 10), relief='solid', bd=1)
        tel_entry.grid(row=3, column=1, sticky='w', pady=5, padx=(10, 20))
        tel_entry.bind('<KeyRelease>', self.format_phone_entry)
        
        # Endereço (linha 5)
        tk.Label(basic_content, text="Endereço:", 
                font=('Arial', 10, 'bold'), 
                bg='white', 
                fg='#2c3e50').grid(row=4, column=0, sticky='w', pady=5)
        
        self.endereco_var = tk.StringVar()
        end_entry = tk.Entry(basic_content, textvariable=self.endereco_var, width=50,
                            font=('Arial', 10), relief='solid', bd=1)
        end_entry.grid(row=4, column=1, columnspan=3, sticky='ew', pady=5, padx=(10, 0))
        
        # Turma e Status (linha 6)
        tk.Label(basic_content, text="Turma *:", 
                font=('Arial', 10, 'bold'), 
                bg='white', 
                fg='#2c3e50').grid(row=5, column=0, sticky='w', pady=5)
        
        self.turma_var = tk.StringVar()
        self.turma_combo = ttk.Combobox(basic_content, textvariable=self.turma_var, 
                                       width=25, state='readonly')
        self.turma_combo.grid(row=5, column=1, columnspan=2, sticky='ew', pady=5, padx=(10, 20))
        
        tk.Label(basic_content, text="Status:", 
                font=('Arial', 10, 'bold'), 
                bg='white', 
                fg='#2c3e50').grid(row=5, column=3, sticky='w', pady=5)
        
        self.status_var = tk.StringVar(value="Ativo")
        status_combo = ttk.Combobox(basic_content, textvariable=self.status_var, 
                                   values=['Ativo', 'Inativo'], width=12, state='readonly')
        status_combo.grid(row=5, column=4, sticky='w', pady=5, padx=(10, 0))
        
        # Configurar grid
        basic_content.columnconfigure(1, weight=1)
        
        # Carregar turmas
        self.carregar_turmas_dropdown()
        
        # Seção 2: Responsável Financeiro
        resp_frame = tk.LabelFrame(
            form_container,
            text="  Responsável Financeiro  ",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        resp_frame.pack(fill=tk.X, pady=(0, 20))
        
        resp_content = tk.Frame(resp_frame, bg='white')
        resp_content.pack(fill=tk.X, padx=20, pady=15)
        
        # Nome do responsável
        tk.Label(resp_content, text="Nome do Responsável *:", 
                font=('Arial', 10, 'bold'), 
                bg='white', 
                fg='#2c3e50').grid(row=0, column=0, sticky='w', pady=5)
        
        self.resp_nome_var = tk.StringVar()
        resp_nome_entry = tk.Entry(resp_content, textvariable=self.resp_nome_var, width=30,
                                  font=('Arial', 10), relief='solid', bd=1)
        resp_nome_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 20))
        
        # Telefone do responsável
        tk.Label(resp_content, text="Telefone *:", 
                font=('Arial', 10, 'bold'), 
                bg='white', 
                fg='#2c3e50').grid(row=0, column=2, sticky='w', pady=5)
        
        self.resp_telefone_var = tk.StringVar()
        resp_tel_entry = tk.Entry(resp_content, textvariable=self.resp_telefone_var, width=15,
                                 font=('Arial', 10), relief='solid', bd=1)
        resp_tel_entry.grid(row=0, column=3, sticky='w', pady=5, padx=(10, 0))
        resp_tel_entry.bind('<KeyRelease>', self.format_resp_phone)
        
        # Parentesco
        tk.Label(resp_content, text="Parentesco:", 
                font=('Arial', 10, 'bold'), 
                bg='white', 
                fg='#2c3e50').grid(row=1, column=0, sticky='w', pady=5)
        
        self.resp_parentesco_var = tk.StringVar(value="Responsável")
        parentesco_combo = ttk.Combobox(resp_content, textvariable=self.resp_parentesco_var, 
                                       values=['Pai', 'Mãe', 'Avô', 'Avó', 'Responsável'], 
                                       width=15, state='readonly')
        parentesco_combo.grid(row=1, column=1, sticky='w', pady=5, padx=(10, 0))
        
        resp_content.columnconfigure(1, weight=1)
        
        # Botões
        buttons_frame = tk.Frame(form_container, bg='white')
        buttons_frame.pack(fill=tk.X, pady=(30, 0))
        
        # Separador
        separator = tk.Frame(buttons_frame, height=2, bg='#dee2e6')
        separator.pack(fill=tk.X, pady=(0, 20))
        
        self.salvar_btn = tk.Button(
            buttons_frame,
            text="💾 Salvar Aluno",
            command=self.salvar_aluno,
            font=('Arial', 12, 'bold'),
            bg='#28a745',
            fg='white',
            padx=25, pady=10, relief='flat', cursor='hand2'
        )
        self.salvar_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        limpar_btn = tk.Button(
            buttons_frame,
            text="🔄 Limpar",
            command=self.limpar_formulario,
            font=('Arial', 12, 'bold'),
            bg='#6c757d',
            fg='white',
            padx=25, pady=10, relief='flat', cursor='hand2'
        )
        limpar_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        self.cancelar_btn = tk.Button(
            buttons_frame,
            text="❌ Cancelar Edição",
            command=self.cancelar_edicao,
            font=('Arial', 12, 'bold'),
            bg='#dc3545',
            fg='white',
            padx=25, pady=10, relief='flat', cursor='hand2'
        )
        self.cancelar_btn.pack(side=tk.LEFT)
        self.cancelar_btn.pack_forget()  # Oculto inicialmente
    
    def create_lista_tab(self, parent):
        """Cria a aba de lista de alunos"""
        # Container principal
        lista_container = tk.Frame(parent, bg='white')
        lista_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Filtros
        filter_frame = tk.LabelFrame(
            lista_container,
            text="  Filtros  ",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        filter_frame.pack(fill=tk.X, pady=(0, 20))
        
        filter_content = tk.Frame(filter_frame, bg='white')
        filter_content.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(filter_content, text="Filtrar por turma:", 
                font=('Arial', 10, 'bold'),
                bg='white', 
                fg='#2c3e50').pack(side=tk.LEFT)
        
        self.filtro_turma_var = tk.StringVar(value="Todas")
        self.filtro_turma_combo = ttk.Combobox(
            filter_content, textvariable=self.filtro_turma_var, 
            width=25, state='readonly'
        )
        self.filtro_turma_combo.pack(side=tk.LEFT, padx=(10, 20))
        
        filter_btn = tk.Button(
            filter_content, text="🔍 Filtrar", command=self.aplicar_filtro,
            font=('Arial', 10, 'bold'), bg='#007bff',
            fg='white', padx=15, pady=5, relief='flat', cursor='hand2'
        )
        filter_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_filter_btn = tk.Button(
            filter_content, text="🔄 Limpar", command=self.limpar_filtro,
            font=('Arial', 10, 'bold'), bg='#6c757d',
            fg='white', padx=15, pady=5, relief='flat', cursor='hand2'
        )
        clear_filter_btn.pack(side=tk.LEFT)
        
        # Carregar filtro de turmas
        self.carregar_filtro_turmas()
        
        # Tabela
        table_frame = tk.LabelFrame(
            lista_container,
            text="  Alunos Cadastrados  ",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        table_content = tk.Frame(table_frame, bg='white')
        table_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Treeview
        columns = ('ID', 'Nome', 'CPF', 'Idade', 'Turma', 'Telefone', 'Responsável', 'Status')
        self.tree = ttk.Treeview(table_content, columns=columns, show='headings', height=15)
        
        # Configurar colunas
        column_widths = {'ID': 50, 'Nome': 200, 'CPF': 120, 'Idade': 60, 'Turma': 150, 
                        'Telefone': 120, 'Responsável': 180, 'Status': 80}
        
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
            action_frame, text="✏️ Editar", command=self.editar_aluno,
            font=('Arial', 10, 'bold'), bg='#007bff',
            fg='white', padx=15, pady=8, relief='flat', cursor='hand2'
        )
        editar_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        excluir_btn = tk.Button(
            action_frame, text="🗑️ Excluir", command=self.excluir_aluno,
            font=('Arial', 10, 'bold'), bg='#dc3545',
            fg='white', padx=15, pady=8, relief='flat', cursor='hand2'
        )
        excluir_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        historico_btn = tk.Button(
            action_frame, text="💰 Histórico", command=self.ver_historico_financeiro,
            font=('Arial', 10, 'bold'), bg='#fd7e14',
            fg='white', padx=15, pady=8, relief='flat', cursor='hand2'
        )
        historico_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        atualizar_btn = tk.Button(
            action_frame, text="🔄 Atualizar", command=self.carregar_alunos,
            font=('Arial', 10, 'bold'), bg='#6c757d',
            fg='white', padx=15, pady=8, relief='flat', cursor='hand2'
        )
        atualizar_btn.pack(side=tk.LEFT)
        
        # Bind duplo clique
        self.tree.bind('<Double-1>', lambda e: self.editar_aluno())
    
    # Métodos auxiliares
    def format_date_entry(self, event=None):
        """Formata data enquanto digita"""
        text = self.data_nasc_var.get()
        numbers = re.sub(r'\D', '', text)
        
        if len(numbers) >= 8:
            formatted = f"{numbers[:2]}/{numbers[2:4]}/{numbers[4:8]}"
        elif len(numbers) >= 4:
            formatted = f"{numbers[:2]}/{numbers[2:4]}/{numbers[4:]}"
        elif len(numbers) >= 2:
            formatted = f"{numbers[:2]}/{numbers[2:]}"
        else:
            formatted = numbers
        
        if formatted != text:
            self.data_nasc_var.set(formatted)
    
    def format_cpf_entry(self, event=None):
        """Formata CPF enquanto digita"""
        cpf = self.cpf_var.get()
        formatted = format_cpf(cpf)
        if formatted != cpf:
            self.cpf_var.set(formatted)
    
    def format_phone_entry(self, event=None):
        """Formata telefone enquanto digita"""
        phone = self.telefone_var.get()
        formatted = format_phone(phone)
        if formatted != phone:
            self.telefone_var.set(formatted)
    
    def format_resp_phone(self, event=None):
        """Formata telefone do responsável"""
        phone = self.resp_telefone_var.get()
        formatted = format_phone(phone)
        if formatted != phone:
            self.resp_telefone_var.set(formatted)
    
    def carregar_turmas_dropdown(self):
        """Carrega turmas no dropdown"""
        try:
            turmas = self.aluno_service.listar_turmas()
            valores = [turma['display'] for turma in turmas]
            self.turma_combo['values'] = valores
            self.turmas_map = {turma['display']: turma['id'] for turma in turmas}
        except Exception as e:
            print(f"Erro ao carregar turmas: {e}")
    
    def carregar_filtro_turmas(self):
        """Carrega turmas no filtro"""
        try:
            turmas = self.aluno_service.listar_turmas()
            valores = ["Todas"] + [turma['display'] for turma in turmas]
            self.filtro_turma_combo['values'] = valores
            self.filtro_turmas_map = {turma['display']: turma['id'] for turma in turmas}
            self.filtro_turmas_map["Todas"] = None
        except Exception as e:
            print(f"Erro ao carregar filtro turmas: {e}")
    
    def aplicar_filtro(self):
        """Aplica filtro por turma"""
        turma_selecionada = self.filtro_turma_var.get()
        turma_id = self.filtro_turmas_map.get(turma_selecionada)
        self.carregar_alunos(turma_id)
    
    def limpar_filtro(self):
        """Limpa filtro"""
        self.filtro_turma_var.set("Todas")
        self.carregar_alunos()
    
    def validar_formulario(self):
        """Valida formulário - COM VALIDAÇÃO DE CPF"""
        erros = []
        
        if not self.nome_var.get().strip():
            erros.append("Nome é obrigatório")
        
        if not self.data_nasc_var.get().strip():
            erros.append("Data de nascimento é obrigatória")
        elif not validate_date(self.data_nasc_var.get()):
            erros.append("Data inválida (use DD/MM/AAAA)")
        
        # Validação CPF (opcional, mas se preenchido deve ser válido)
        cpf = self.cpf_var.get().strip()
        if cpf and not validate_cpf(cpf):
            erros.append("CPF inválido")
        
        if not self.turma_var.get():
            erros.append("Turma é obrigatória")
        
        if not self.resp_nome_var.get().strip():
            erros.append("Nome do responsável é obrigatório")
        
        if not self.resp_telefone_var.get().strip():
            erros.append("Telefone do responsável é obrigatório")
        
        return erros
    
    def salvar_aluno(self):
        """Salva aluno - COM DADOS DE CPF"""
        erros = self.validar_formulario()
        if erros:
            messagebox.showerror("Erro de Validação", "\n".join(erros))
            return
        
        try:
            # Dados do aluno (COM CPF)
            aluno_data = {
                'nome': self.nome_var.get().strip(),
                'data_nascimento': parse_date(self.data_nasc_var.get()),
                'cpf': self.cpf_var.get().strip() or None,
                'sexo': self.sexo_var.get() or None,
                'endereco': self.endereco_var.get().strip() or None,
                'telefone': self.telefone_var.get().strip() or None,
                'nacionalidade': self.nacionalidade_var.get().strip() or 'Brasileira',
                'turma_id': self.turmas_map[self.turma_var.get()],
                'status': self.status_var.get()
            }
            
            if self.aluno_editando:
                aluno_data['id'] = self.aluno_editando
            
            # Dados do responsável
            responsaveis_data = [{
                'nome': self.resp_nome_var.get().strip(),
                'telefone': self.resp_telefone_var.get().strip(),
                'parentesco': self.resp_parentesco_var.get()
            }]
            
            resultado = self.aluno_service.salvar_aluno(aluno_data, responsaveis_data)
            
            if resultado['success']:
                acao = "atualizado" if self.aluno_editando else "cadastrado"
                messagebox.showinfo("Sucesso", f"Aluno {acao} com sucesso!")
                
                if not self.aluno_editando:
                    self.aluno_service.gerar_mensalidades_aluno(resultado['id'])
                
                self.limpar_formulario()
                self.cancelar_edicao()
                self.carregar_alunos()
            else:
                messagebox.showerror("Erro", f"Erro: {resultado['error']}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")
    
    def editar_aluno(self):
        """Edita aluno selecionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um aluno para editar!")
            return
        
        try:
            item = self.tree.item(selection[0])
            aluno_id = item['values'][0]
            
            aluno = self.aluno_service.buscar_aluno_por_id(aluno_id)
            if not aluno:
                messagebox.showerror("Erro", "Aluno não encontrado!")
                return
            
            # Preencher formulário (COM CPF)
            self.nome_var.set(aluno['nome'])
            self.data_nasc_var.set(format_date(aluno['data_nascimento']))
            self.cpf_var.set(aluno.get('cpf', '') or '')
            self.sexo_var.set(aluno['sexo'] or '')
            self.endereco_var.set(aluno['endereco'] or '')
            self.telefone_var.set(aluno['telefone'] or '')
            self.nacionalidade_var.set(aluno['nacionalidade'] or 'Brasileira')
            self.status_var.set(aluno['status'])
            
            # Selecionar turma
            for display, turma_id in self.turmas_map.items():
                if turma_id == aluno['turma_id']:
                    self.turma_var.set(display)
                    break
            
            # Responsável (pegar o primeiro)
            if aluno['responsaveis']:
                resp = aluno['responsaveis'][0]
                self.resp_nome_var.set(resp['nome'])
                self.resp_telefone_var.set(resp['telefone'])
                self.resp_parentesco_var.set(resp['parentesco'])
            
            # Modo edição
            self.aluno_editando = aluno_id
            self.salvar_btn.config(text="💾 Atualizar Aluno")
            self.cancelar_btn.pack(side=tk.LEFT, padx=(15, 0))
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar aluno: {str(e)}")
    
    def cancelar_edicao(self):
        """Cancela edição"""
        self.aluno_editando = None
        self.salvar_btn.config(text="💾 Salvar Aluno")
        self.cancelar_btn.pack_forget()
    
    def excluir_aluno(self):
        """Exclui aluno"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um aluno para excluir!")
            return
        
        item = self.tree.item(selection[0])
        aluno_id = item['values'][0]
        aluno_nome = item['values'][1]
        
        if messagebox.askyesno("Confirmar", f"Excluir aluno '{aluno_nome}'?"):
            resultado = self.aluno_service.excluir_aluno(aluno_id)
            if resultado['success']:
                messagebox.showinfo("Sucesso", "Aluno excluído!")
                self.carregar_alunos()
            else:
                messagebox.showerror("Erro", resultado['error'])
    
    def ver_historico_financeiro(self):
        """Ver histórico financeiro"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um aluno!")
            return
        
        item = self.tree.item(selection[0])
        aluno_id = item['values'][0]
        aluno_nome = item['values'][1]
        
        historico = self.aluno_service.buscar_historico_financeiro(aluno_id)
        self.mostrar_historico(aluno_nome, historico)
    
    def mostrar_historico(self, nome, historico):
        """Mostra janela de histórico"""
        hist_window = tk.Toplevel()
        hist_window.title(f"Histórico - {nome}")
        hist_window.geometry("800x500")
        hist_window.configure(bg='white')
        
        tk.Label(hist_window, text=f"💰 Histórico Financeiro - {nome}",
                font=('Arial', 16, 'bold'), bg='white',
                fg='#2c3e50').pack(pady=20)
        
        if not historico:
            tk.Label(hist_window, text="Nenhum registro encontrado",
                    font=('Arial', 12), bg='white',
                    fg='#6c757d').pack(expand=True)
        else:
            # Criar tabela simples
            info_text = tk.Text(hist_window, height=20, font=('Courier', 10))
            info_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Cabeçalho
            info_text.insert(tk.END, "MÊS/ANO    VALOR      STATUS      VENCIMENTO\n")
            info_text.insert(tk.END, "-" * 50 + "\n")
            
            for reg in historico:
                linha = f"{reg['mes_referencia']:<10} {format_currency(reg['valor_final']):<10} {reg['status']:<12} {format_date(reg['data_vencimento'])}\n"
                info_text.insert(tk.END, linha)
            
            info_text.config(state=tk.DISABLED)
        
        tk.Button(hist_window, text="Fechar", command=hist_window.destroy,
                 bg='#6c757d', fg='white',
                 font=('Arial', 11, 'bold'), padx=20, pady=8).pack(pady=20)
    
    def limpar_formulario(self):
        """Limpa formulário - COM CAMPO CPF"""
        self.nome_var.set("")
        self.data_nasc_var.set("")
        self.cpf_var.set("")
        self.sexo_var.set("")
        self.endereco_var.set("")
        self.telefone_var.set("")
        self.nacionalidade_var.set("Brasileira")
        self.turma_var.set("")
        self.status_var.set("Ativo")
        self.resp_nome_var.set("")
        self.resp_telefone_var.set("")
        self.resp_parentesco_var.set("Responsável")
    
    def carregar_alunos(self, turma_id=None):
        """Carrega lista de alunos"""
        try:
            # Limpar tabela
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            alunos = self.aluno_service.listar_alunos(turma_id)
            
            for aluno in alunos:
                valores = (
                    aluno['id'],
                    aluno['nome'][:30] + "..." if len(aluno['nome']) > 30 else aluno['nome'],
                    aluno.get('cpf', '-') or '-',
                    aluno['idade'],
                    f"{aluno['turma_nome']} - {aluno['turma_serie']}",
                    format_phone(aluno['telefone']) if aluno['telefone'] else '-',
                    aluno['responsavel_principal'][:25] + "..." if len(aluno['responsavel_principal']) > 25 else aluno['responsavel_principal'],
                    '✅ Ativo' if aluno['status'] == 'Ativo' else '❌ Inativo'
                )
                self.tree.insert('', tk.END, values=valores)
            
            print(f"✅ {len(alunos)} alunos carregados")
            
        except Exception as e:
            print(f"Erro ao carregar alunos: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar alunos: {str(e)}")
