import tkinter as tk
from tkinter import ttk, messagebox
from services.aluno_service import AlunoService
from utils.formatters import format_date, parse_date, validate_date, calculate_age, format_currency, validate_cpf
from utils.input_formatters import SmartEntry, NumberOnlyEntry, CurrencyEntry, InputFormatter
from datetime import datetime, date
import re

class AlunosInterface:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.parent_frame.configure(bg='white')
        self.aluno_service = AlunoService()
        self.aluno_editando = None
        self.responsaveis_data = []  # Lista para múltiplos responsáveis
        self.formatter = InputFormatter()  # Instância do formatador
        
        try:
            self.create_interface()
            self.carregar_alunos()
        except Exception as e:
            print(f"Erro ao criar interface de alunos: {e}")
            self.show_error_interface(str(e))
    
    def show_error_interface(self, error_msg):
        """Interface de erro"""
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
        
        tk.Button(
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
        ).pack(pady=20)
    
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
        """Interface completa com dados financeiros e múltiplos responsáveis"""
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
        
        # Notebook
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba Cadastro
        cadastro_frame = tk.Frame(notebook, bg='white')
        notebook.add(cadastro_frame, text="📝 Cadastro")
        
        # Aba Lista
        lista_frame = tk.Frame(notebook, bg='white')
        notebook.add(lista_frame, text="📋 Lista de Alunos")
        
        self.create_cadastro_completo(cadastro_frame)
        self.create_lista_tab(lista_frame)
    
    def create_cadastro_completo(self, parent):
        """Cadastro completo com scroll e múltiplas seções"""
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
        
        # Formulário com seções
        self.create_form_sections(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_form_sections(self, parent):
        """Cria formulário organizado em seções"""
        form_container = tk.Frame(parent, bg='white')
        form_container.pack(fill=tk.X, padx=40, pady=20)
        
        # Seção 1: Dados Pessoais
        self.create_dados_pessoais(form_container)
        
        # Seção 2: Dados Financeiros (simplificado)
        self.create_dados_financeiros(form_container)
        
        # Seção 3: Responsáveis
        self.create_secao_responsaveis(form_container)
        
        # Botões de ação
        self.create_action_buttons(form_container)
    
    def create_dados_pessoais(self, parent):
        """Seção dados pessoais com formatação inteligente"""
        pessoais_frame = tk.LabelFrame(
            parent,
            text="  👤 Dados Pessoais do Aluno  ",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        pessoais_frame.pack(fill=tk.X, pady=(0, 20))
        
        content = tk.Frame(pessoais_frame, bg='white')
        content.pack(fill=tk.X, padx=20, pady=15)
        
        # Nome (linha 1)
        tk.Label(content, text="Nome Completo *:", 
                font=('Arial', 11, 'bold'), 
                bg='white', 
                fg='#2c3e50').grid(row=0, column=0, sticky='w', pady=8)
        
        self.nome_var = tk.StringVar()
        nome_entry = tk.Entry(content, textvariable=self.nome_var, width=50,
                             font=('Arial', 11), relief='solid', bd=1)
        nome_entry.grid(row=0, column=1, columnspan=3, sticky='ew', pady=8, padx=(10, 0))
        
        # Data nascimento com formatação inteligente (linha 2)
        tk.Label(content, text="Data Nascimento *:", 
                font=('Arial', 11, 'bold'), 
                bg='white', 
                fg='#2c3e50').grid(row=1, column=0, sticky='w', pady=8)
        
        self.data_nasc_var = tk.StringVar()
        self.data_entry = SmartEntry(
            content, self.data_nasc_var, 'date',
            width=12, font=('Arial', 11), relief='solid', bd=1
        )
        self.data_entry.grid(row=1, column=1, sticky='w', pady=8, padx=(10, 20))
        
        # CPF com formatação inteligente (linha 2 - continuação)
        tk.Label(content, text="CPF:", 
                font=('Arial', 11, 'bold'), 
                bg='white', 
                fg='#2c3e50').grid(row=1, column=2, sticky='w', pady=8)
        
        self.cpf_var = tk.StringVar()
        self.cpf_entry = SmartEntry(
            content, self.cpf_var, 'cpf',
            width=15, font=('Arial', 11), relief='solid', bd=1
        )
        self.cpf_entry.grid(row=1, column=3, sticky='w', pady=8, padx=(10, 0))
        
        # Sexo e nacionalidade (linha 3)
        tk.Label(content, text="Sexo:", 
                font=('Arial', 11, 'bold'), 
                bg='white', 
                fg='#2c3e50').grid(row=2, column=0, sticky='w', pady=8)
        
        self.sexo_var = tk.StringVar()
        sexo_combo = ttk.Combobox(content, textvariable=self.sexo_var, 
                                 values=['Masculino', 'Feminino'], width=12, state='readonly')
        sexo_combo.grid(row=2, column=1, sticky='w', pady=8, padx=(10, 20))
        
        tk.Label(content, text="Nacionalidade:", 
                font=('Arial', 11, 'bold'), 
                bg='white', 
                fg='#2c3e50').grid(row=2, column=2, sticky='w', pady=8)
        
        self.nacionalidade_var = tk.StringVar(value="Brasileira")
        nac_entry = tk.Entry(content, textvariable=self.nacionalidade_var, width=15,
                            font=('Arial', 11), relief='solid', bd=1)
        nac_entry.grid(row=2, column=3, sticky='w', pady=8, padx=(10, 0))
        
        # Telefone com formatação inteligente (linha 4)
        tk.Label(content, text="Telefone:", 
                font=('Arial', 11, 'bold'), 
                bg='white', 
                fg='#2c3e50').grid(row=3, column=0, sticky='w', pady=8)
        
        self.telefone_var = tk.StringVar()
        self.telefone_entry = SmartEntry(
            content, self.telefone_var, 'phone',
            width=16, font=('Arial', 11), relief='solid', bd=1
        )
        self.telefone_entry.grid(row=3, column=1, sticky='w', pady=8, padx=(10, 20))
        
        # Endereço (linha 5)
        tk.Label(content, text="Endereço:", 
                font=('Arial', 11, 'bold'), 
                bg='white', 
                fg='#2c3e50').grid(row=4, column=0, sticky='w', pady=8)
        
        self.endereco_var = tk.StringVar()
        end_entry = tk.Entry(content, textvariable=self.endereco_var, width=50,
                            font=('Arial', 11), relief='solid', bd=1)
        end_entry.grid(row=4, column=1, columnspan=3, sticky='ew', pady=8, padx=(10, 0))
        
        # Turma e Status (linha 6)
        tk.Label(content, text="Turma *:", 
                font=('Arial', 11, 'bold'), 
                bg='white', 
                fg='#2c3e50').grid(row=5, column=0, sticky='w', pady=8)
        
        self.turma_var = tk.StringVar()
        self.turma_combo = ttk.Combobox(content, textvariable=self.turma_var, 
                                       width=25, state='readonly')
        self.turma_combo.grid(row=5, column=1, columnspan=2, sticky='ew', pady=8, padx=(10, 20))
        
        tk.Label(content, text="Status:", 
                font=('Arial', 11, 'bold'), 
                bg='white', 
                fg='#2c3e50').grid(row=5, column=3, sticky='w', pady=8)
        
        self.status_var = tk.StringVar(value="Ativo")
        status_combo = ttk.Combobox(content, textvariable=self.status_var, 
                                   values=['Ativo', 'Inativo'], width=12, state='readonly')
        status_combo.grid(row=5, column=4, sticky='w', pady=8, padx=(10, 0))
        
        content.columnconfigure(1, weight=1)
        
        # Carregar turmas
        self.carregar_turmas_dropdown()
    
    def create_dados_financeiros(self, parent):
        """Seção dados financeiros simplificada - apenas mensalidade"""
        financeiro_frame = tk.LabelFrame(
            parent,
            text="  💰 Dados Financeiros  ",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#e67e22',
            bd=2,
            relief='groove'
        )
        financeiro_frame.pack(fill=tk.X, pady=(0, 20))
        
        content = tk.Frame(financeiro_frame, bg='white')
        content.pack(fill=tk.X, padx=20, pady=15)
        
        # Valor da mensalidade (único campo financeiro no cadastro)
        tk.Label(content, text="Valor da Mensalidade *:", 
                font=('Arial', 11, 'bold'), 
                bg='white', 
                fg='#2c3e50').grid(row=0, column=0, sticky='w', pady=8)
        
        self.mensalidade_var = tk.StringVar(value="0,00")
        self.mensalidade_entry = CurrencyEntry(
            content, self.mensalidade_var,
            width=12, font=('Arial', 11), bg='white'
        )
        self.mensalidade_entry.grid(row=0, column=1, sticky='w', pady=8, padx=(10, 20))
        
        # Informação sobre quando aplicar descontos e multas
        info_frame = tk.Frame(content, bg='#e8f4fd', relief='solid', bd=1)
        info_frame.grid(row=1, column=0, columnspan=4, sticky='ew', pady=(15, 0), ipady=15)
        
        tk.Label(
            info_frame,
            text="ℹ️ Informação Importante",
            font=('Arial', 12, 'bold'),
            bg='#e8f4fd',
            fg='#0c5460'
        ).pack(pady=(0, 5))
        
        tk.Label(
            info_frame,
            text="Descontos e multas serão aplicados individualmente no momento\n"
                 "do registro de cada pagamento na aba Financeiro.",
            font=('Arial', 10),
            bg='#e8f4fd',
            fg='#0c5460',
            justify=tk.CENTER
        ).pack()
        
        content.columnconfigure(3, weight=1)
    
    def create_secao_responsaveis(self, parent):
        """Seção para múltiplos responsáveis"""
        responsaveis_frame = tk.LabelFrame(
            parent,
            text="  👨‍👩‍👧‍👦 Responsáveis pelo Aluno  ",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#8e44ad',
            bd=2,
            relief='groove'
        )
        responsaveis_frame.pack(fill=tk.X, pady=(0, 20))
        
        content = tk.Frame(responsaveis_frame, bg='white')
        content.pack(fill=tk.X, padx=20, pady=15)
        
        # Botões de gerenciamento
        btn_frame = tk.Frame(content, bg='white')
        btn_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Button(
            btn_frame, text="➕ Adicionar Responsável", 
            command=self.adicionar_responsavel,
            bg='#28a745', fg='white', font=('Arial', 10, 'bold'),
            padx=15, pady=5, relief='flat', cursor='hand2'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            btn_frame, text="✏️ Editar Selecionado", 
            command=self.editar_responsavel,
            bg='#007bff', fg='white', font=('Arial', 10, 'bold'),
            padx=15, pady=5, relief='flat', cursor='hand2'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            btn_frame, text="🗑️ Remover Selecionado", 
            command=self.remover_responsavel,
            bg='#dc3545', fg='white', font=('Arial', 10, 'bold'),
            padx=15, pady=5, relief='flat', cursor='hand2'
        ).pack(side=tk.LEFT)
        
        # Lista de responsáveis
        lista_frame = tk.Frame(content, bg='white')
        lista_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview para responsáveis
        columns = ('Nome', 'Telefone', 'Parentesco', 'Principal')
        self.responsaveis_tree = ttk.Treeview(lista_frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            self.responsaveis_tree.heading(col, text=col, anchor='center')
            if col == 'Nome':
                self.responsaveis_tree.column(col, width=200, anchor='w')
            elif col == 'Principal':
                self.responsaveis_tree.column(col, width=80, anchor='center')
            else:
                self.responsaveis_tree.column(col, width=120, anchor='center')
        
        # Scrollbar para responsáveis
        resp_scroll = ttk.Scrollbar(lista_frame, orient='vertical', command=self.responsaveis_tree.yview)
        self.responsaveis_tree.configure(yscrollcommand=resp_scroll.set)
        
        self.responsaveis_tree.pack(side='left', fill='both', expand=True)
        resp_scroll.pack(side='right', fill='y')
        
        # Configurar tags para responsável principal
        self.responsaveis_tree.tag_configure('principal', background='#e8f5e8')
    
    def create_action_buttons(self, parent):
        """Botões de ação do formulário"""
        buttons_frame = tk.Frame(parent, bg='white')
        buttons_frame.pack(fill=tk.X, pady=(30, 0))
        
        # Separador
        separator = tk.Frame(buttons_frame, height=2, bg='#dee2e6')
        separator.pack(fill=tk.X, pady=(0, 20))
        
        self.salvar_btn = tk.Button(
            buttons_frame,
            text="💾 Salvar Aluno",
            command=self.salvar_aluno,
            font=('Arial', 14, 'bold'),
            bg='#28a745',
            fg='white',
            padx=30, pady=12, relief='flat', cursor='hand2'
        )
        self.salvar_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        limpar_btn = tk.Button(
            buttons_frame,
            text="🔄 Limpar Formulário",
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
        self.cancelar_btn.pack_forget()  # Oculto inicialmente
    
    def carregar_turmas_dropdown(self):
        """Carrega turmas no dropdown"""
        try:
            turmas = self.aluno_service.listar_turmas()
            valores = [turma['display'] for turma in turmas]
            self.turma_combo['values'] = valores
            self.turmas_map = {turma['display']: turma['id'] for turma in turmas}
        except Exception as e:
            print(f"Erro ao carregar turmas: {e}")
    
    # Métodos para gerenciar responsáveis
    def adicionar_responsavel(self):
        """Abre janela para adicionar responsável"""
        self.abrir_janela_responsavel()
    
    def editar_responsavel(self):
        """Edita responsável selecionado"""
        selection = self.responsaveis_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um responsável para editar!")
            return
        
        # Encontrar responsável na lista
        item = self.responsaveis_tree.item(selection[0])
        nome = item['values'][0]
        
        for i, resp in enumerate(self.responsaveis_data):
            if resp['nome'] == nome:
                self.abrir_janela_responsavel(i)
                break
    
    def remover_responsavel(self):
        """Remove responsável selecionado"""
        selection = self.responsaveis_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um responsável para remover!")
            return
        
        item = self.responsaveis_tree.item(selection[0])
        nome = item['values'][0]
        
        if messagebox.askyesno("Confirmar", f"Remover responsável '{nome}'?"):
            # Remover da lista
            self.responsaveis_data = [r for r in self.responsaveis_data if r['nome'] != nome]
            
            # Se era principal, definir outro como principal
            if not any(r.get('principal', False) for r in self.responsaveis_data) and self.responsaveis_data:
                self.responsaveis_data[0]['principal'] = True
            
            self.atualizar_lista_responsaveis()
    
    def abrir_janela_responsavel(self, index_editar=None):
        """Janela de responsável com formatação inteligente e botões funcionais"""
        resp_window = tk.Toplevel(self.parent_frame)
        resp_window.title("👤 Responsável")
        resp_window.geometry("500x400")
        resp_window.resizable(False, False)
        resp_window.configure(bg='white')
        resp_window.transient(self.parent_frame)  # Modal
        resp_window.grab_set()  # Bloquear interação com janela pai
        
        # Centralizar
        resp_window.update_idletasks()
        x = (resp_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (resp_window.winfo_screenheight() // 2) - (400 // 2)
        resp_window.geometry(f"500x400+{x}+{y}")
        
        # Header
        header = tk.Frame(resp_window, bg='#8e44ad', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = "✏️ Editar Responsável" if index_editar is not None else "➕ Adicionar Responsável"
        tk.Label(
            header, text=title,
            font=('Arial', 16, 'bold'), fg='white', bg='#8e44ad'
        ).pack(expand=True)
        
        # Formulário principal
        main_form = tk.Frame(resp_window, bg='white')
        main_form.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # === CAMPOS DO FORMULÁRIO ===
        
        # Nome Completo
        tk.Label(main_form, text="Nome Completo *:", 
                font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w', pady=(0, 5))
        
        nome_resp_var = tk.StringVar()
        nome_resp_entry = tk.Entry(main_form, textvariable=nome_resp_var, 
                                  font=('Arial', 12), relief='solid', bd=2, bg='#f8f9fa')
        nome_resp_entry.pack(fill=tk.X, pady=(0, 15), ipady=10)
        
        # Telefone com formatação inteligente
        tk.Label(main_form, text="Telefone *:", 
                font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w', pady=(0, 5))
        
        tel_resp_var = tk.StringVar()
        tel_resp_entry = SmartEntry(
            main_form, tel_resp_var, 'phone',
            font=('Arial', 12), relief='solid', bd=2, bg='#f8f9fa'
        )
        tel_resp_entry.pack(fill=tk.X, pady=(0, 15), ipady=10)
        
        # Parentesco
        tk.Label(main_form, text="Parentesco *:", 
                font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w', pady=(0, 5))
        
        parentesco_var = tk.StringVar()
        parentesco_combo = ttk.Combobox(
            main_form, textvariable=parentesco_var, 
            values=['Pai', 'Mãe', 'Avô', 'Avó', 'Tio(a)', 'Tia', 'Responsável Legal', 'Outro'], 
            state='readonly', font=('Arial', 12)
        )
        parentesco_combo.pack(fill=tk.X, pady=(0, 15), ipady=10)
        
        # Responsável Principal
        principal_var = tk.BooleanVar()
        principal_frame = tk.Frame(main_form, bg='white')
        principal_frame.pack(fill=tk.X, pady=(0, 20))
        
        principal_check = tk.Checkbutton(
            principal_frame, 
            text="✅ Responsável Principal (recebe comunicações prioritárias)", 
            variable=principal_var, 
            font=('Arial', 11, 'bold'), 
            bg='white',
            fg='#27ae60'
        )
        principal_check.pack(anchor='w')
        
        # Informação sobre responsável principal
        info_label = tk.Label(
            principal_frame,
            text="ℹ️ Apenas um responsável pode ser principal por vez",
            font=('Arial', 9),
            bg='white',
            fg='#6c757d'
        )
        info_label.pack(anchor='w', pady=(5, 0))
        
        # === PREENCHER DADOS SE EDITANDO ===
        if index_editar is not None:
            resp_data = self.responsaveis_data[index_editar]
            nome_resp_var.set(resp_data['nome'])
            tel_resp_entry.set_value(resp_data.get('telefone_formatted', resp_data['telefone']))
            parentesco_var.set(resp_data['parentesco'])
            principal_var.set(resp_data.get('principal', False))
        
        # === FUNÇÕES DE VALIDAÇÃO E SALVAMENTO ===
        
        def validar_campos():
            """Valida campos obrigatórios"""
            erros = []
            
            if not nome_resp_var.get().strip():
                erros.append("• Nome é obrigatório!")
            
            if not tel_resp_var.get().strip():
                erros.append("• Telefone é obrigatório!")
            else:
                # Validar telefone
                telefone_limpo = tel_resp_entry.get_clean_value()
                if len(telefone_limpo) < 10:
                    erros.append("• Telefone deve ter pelo menos 10 dígitos!")
            
            if not parentesco_var.get():
                erros.append("• Parentesco é obrigatório!")
            
            return erros
        
        def salvar_responsavel():
            """Salva responsável na lista"""
            # Validar campos
            erros = validar_campos()
            if erros:
                messagebox.showerror("❌ Erro de Validação", "\n".join(erros))
                return
            
            try:
                # Dados do responsável
                resp_data = {
                    'nome': nome_resp_var.get().strip(),
                    'telefone': tel_resp_entry.get_clean_value(),  # Valor limpo para BD
                    'telefone_formatted': tel_resp_var.get().strip(),  # Valor formatado para exibição
                    'parentesco': parentesco_var.get(),
                    'principal': principal_var.get()
                }
                
                # Verificar se nome já existe (evitar duplicatas)
                nomes_existentes = [r['nome'].lower() for i, r in enumerate(self.responsaveis_data) if i != index_editar]
                if resp_data['nome'].lower() in nomes_existentes:
                    messagebox.showerror("❌ Erro", "Já existe um responsável com este nome!")
                    return
                
                # Se marcado como principal, desmarcar outros
                if resp_data['principal']:
                    for r in self.responsaveis_data:
                        r['principal'] = False
                
                # Adicionar ou editar
                if index_editar is not None:
                    self.responsaveis_data[index_editar] = resp_data
                    acao = "atualizado"
                else:
                    self.responsaveis_data.append(resp_data)
                    acao = "adicionado"
                
                # Se é o primeiro responsável ou nenhum é principal, marcar como principal
                if len(self.responsaveis_data) == 1 or not any(r.get('principal', False) for r in self.responsaveis_data):
                    if self.responsaveis_data:
                        self.responsaveis_data[0]['principal'] = True
                
                # Atualizar lista visual
                self.atualizar_lista_responsaveis()
                
                # Mensagem de sucesso
                messagebox.showinfo("✅ Sucesso", f"Responsável {acao} com sucesso!")
                
                # Fechar janela
                resp_window.destroy()
                
            except Exception as e:
                messagebox.showerror("❌ Erro", f"Erro inesperado: {str(e)}")
        
        def cancelar_responsavel():
            """Cancela adição/edição do responsável"""
            resp_window.destroy()
        
        def salvar_com_enter(event=None):
            """Permite salvar com Enter"""
            salvar_responsavel()
        
        # === BOTÕES DE AÇÃO ===
        
        # Separador
        separator = tk.Frame(main_form, height=2, bg='#dee2e6')
        separator.pack(fill=tk.X, pady=(20, 20))
        
        # Frame dos botões
        btn_frame = tk.Frame(main_form, bg='white')
        btn_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Botão Salvar
        salvar_btn = tk.Button(
            btn_frame, 
            text="💾 Salvar Responsável", 
            command=salvar_responsavel,
            bg='#28a745', 
            fg='white', 
            font=('Arial', 13, 'bold'),
            padx=25, 
            pady=12, 
            relief='flat', 
            cursor='hand2',
            activebackground='#218838'
        )
        salvar_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # Botão Cancelar
        cancelar_btn = tk.Button(
            btn_frame, 
            text="❌ Cancelar", 
            command=cancelar_responsavel,
            bg='#6c757d', 
            fg='white', 
            font=('Arial', 13, 'bold'),
            padx=25, 
            pady=12, 
            relief='flat', 
            cursor='hand2',
            activebackground='#5a6268'
        )
        cancelar_btn.pack(side=tk.LEFT)
        
        # === ATALHOS DE TECLADO ===
        
        # Enter para salvar
        resp_window.bind('<Return>', salvar_com_enter)
        resp_window.bind('<KP_Enter>', salvar_com_enter)  # Enter do teclado numérico
        
        # Escape para cancelar
        resp_window.bind('<Escape>', lambda e: cancelar_responsavel())
        
        # Bind Enter nos campos individuais
        nome_resp_entry.bind('<Return>', salvar_com_enter)
        tel_resp_entry.bind('<Return>', salvar_com_enter)
        parentesco_combo.bind('<Return>', salvar_com_enter)
        
        # === CONFIGURAÇÕES FINAIS ===
        
        # Focar no primeiro campo
        nome_resp_entry.focus_set()
        
        # Aguardar fechamento da janela
        resp_window.wait_window()
    
    def atualizar_lista_responsaveis(self):
        """Atualiza lista visual de responsáveis com melhor formatação"""
        # Limpar árvore
        for item in self.responsaveis_tree.get_children():
            self.responsaveis_tree.delete(item)
        
        # Adicionar responsáveis
        for i, resp in enumerate(self.responsaveis_data):
            principal_text = "✅ Sim" if resp.get('principal', False) else "❌ Não"
            tag = 'principal' if resp.get('principal', False) else ''
            
            # Usar telefone formatado para exibição, se disponível
            telefone_display = resp.get('telefone_formatted', self.formatter.format_phone_smart(resp.get('telefone', '')))
            
            valores = (
                resp['nome'],
                telefone_display, 
                resp['parentesco'],
                principal_text
            )
            
            self.responsaveis_tree.insert('', tk.END, values=valores, tags=(tag,))
        
        # Atualizar contador
        total_responsaveis = len(self.responsaveis_data)
        principais = sum(1 for r in self.responsaveis_data if r.get('principal', False))
        
        print(f"📋 Responsáveis atualizados: {total_responsaveis} total, {principais} principal(is)")
    
    def validar_responsaveis(self):
        """Validação específica para responsáveis"""
        if not self.responsaveis_data:
            return ["Pelo menos um responsável é obrigatório"]
        
        erros = []
        
        # Verificar se há responsável principal
        principais = [r for r in self.responsaveis_data if r.get('principal', False)]
        if not principais:
            erros.append("Deve haver pelo menos um responsável principal")
        elif len(principais) > 1:
            erros.append("Apenas um responsável pode ser principal")
        
        # Verificar duplicatas de telefone
        telefones = [r['telefone'] for r in self.responsaveis_data if r.get('telefone')]
        if len(telefones) != len(set(telefones)):
            erros.append("Telefones duplicados encontrados")
        
        # Verificar se todos os responsáveis têm nome e telefone
        for i, resp in enumerate(self.responsaveis_data):
            if not resp.get('nome', '').strip():
                erros.append(f"Responsável {i+1}: Nome é obrigatório")
            
            if not resp.get('telefone', '').strip():
                erros.append(f"Responsável {i+1}: Telefone é obrigatório")
        
        return erros
    
    def validar_formulario(self):
        """Validação simplificada sem campos de desconto/multa"""
        erros = []
        
        # Dados pessoais
        if not self.nome_var.get().strip():
            erros.append("Nome é obrigatório")
        
        if not self.data_nasc_var.get().strip():
            erros.append("Data de nascimento é obrigatória")
        else:
            # Validar data usando valor limpo
            data_limpa = self.data_entry.get_clean_value()
            if len(data_limpa) != 8:
                erros.append("Data inválida - digite 8 números (ddmmaaaa)")
            else:
                try:
                    day = int(data_limpa[:2])
                    month = int(data_limpa[2:4])
                    year = int(data_limpa[4:8])
                    date(year, month, day)  # Validar se é uma data válida
                except ValueError:
                    erros.append("Data inválida")
        
        if not self.turma_var.get():
            erros.append("Turma é obrigatória")
        
        # CPF (opcional, mas se preenchido deve ser válido)
        cpf_limpo = self.cpf_entry.get_clean_value()
        if cpf_limpo and len(cpf_limpo) != 11:
            erros.append("CPF deve ter 11 dígitos")
        
        # Apenas validar mensalidade
        try:
            mensalidade = self.mensalidade_entry.get_float_value()
            if mensalidade < 0:
                erros.append("Valor da mensalidade não pode ser negativo")
        except:
            erros.append("Valor da mensalidade inválido")
        
        # Responsáveis
        erros_responsaveis = self.validar_responsaveis()
        erros.extend(erros_responsaveis)
        
        return erros
    
    def salvar_aluno(self):
        """Salva aluno com validação corrigida"""
        # Mostrar que está processando
        self.salvar_btn.config(text="⏳ Salvando...", state='disabled')
        
        try:
            erros = self.validar_formulario()
            if erros:
                messagebox.showerror("❌ Erro de Validação", 
                                   f"Corrija os seguintes problemas:\n\n" + "\n".join(f"• {erro}" for erro in erros))
                return
            
            # Converter data limpa para formato do banco
            data_limpa = self.data_entry.get_clean_value()
            if len(data_limpa) == 8:
                data_formatada = f"{data_limpa[4:8]}-{data_limpa[2:4]}-{data_limpa[:2]}"
            else:
                data_formatada = None
            
            # Dados do aluno (apenas mensalidade nos dados financeiros)
            aluno_data = {
                'nome': self.nome_var.get().strip(),
                'data_nascimento': data_formatada,
                'cpf': self.cpf_entry.get_clean_value() or None,
                'sexo': self.sexo_var.get() or None,
                'nacionalidade': self.nacionalidade_var.get().strip() or 'Brasileira',
                'telefone': self.telefone_entry.get_clean_value() or None,
                'endereco': self.endereco_var.get().strip() or None,
                'turma_id': self.turmas_map[self.turma_var.get()],
                'status': self.status_var.get(),
                'valor_mensalidade': self.mensalidade_entry.get_float_value()
            }
            
            if self.aluno_editando:
                aluno_data['id'] = self.aluno_editando
            
            print(f"💾 Salvando aluno: {aluno_data['nome']}")
            print(f"📋 Responsáveis: {len(self.responsaveis_data)}")
            print(f"💰 Mensalidade: R$ {aluno_data['valor_mensalidade']:.2f}")
            
            resultado = self.aluno_service.salvar_aluno(aluno_data, self.responsaveis_data)
            
            if resultado['success']:
                acao = "atualizado" if self.aluno_editando else "cadastrado"
                
                # Gerar mensalidades apenas para alunos novos
                if not self.aluno_editando:
                    print(f"💰 Gerando mensalidades para novo aluno ID: {resultado['id']}")
                    mensalidades_resultado = self.aluno_service.gerar_mensalidades_aluno(resultado['id'])
                    
                    if mensalidades_resultado['success']:
                        parcelas = mensalidades_resultado.get('mensalidades_criadas', 0)
                        periodo = f" de {mensalidades_resultado.get('mes_inicio', '')} a Dezembro"
                        parcelas_info = f"\n💰 {parcelas} mensalidades geradas{periodo}!"
                    else:
                        parcelas_info = f"\n⚠️ Aviso: Erro ao gerar mensalidades - {mensalidades_resultado.get('error', '')}"
                else:
                    parcelas_info = ""
                
                messagebox.showinfo("✅ Sucesso", 
                                   f"Aluno {acao} com sucesso!{parcelas_info}")
                
                self.limpar_formulario()
                self.cancelar_edicao()
                self.carregar_alunos()
            else:
                messagebox.showerror("❌ Erro", f"Erro ao salvar aluno:\n{resultado['error']}")
                
        except Exception as e:
            print(f"❌ Erro completo: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("❌ Erro", f"Erro inesperado:\n{str(e)}")
        
        finally:
            # Restaurar botão
            acao_texto = "💾 Atualizar Aluno" if self.aluno_editando else "💾 Salvar Aluno"
            self.salvar_btn.config(text=acao_texto, state='normal')
    
    def limpar_formulario(self):
        """Limpa formulário simplificado"""
        # Dados pessoais
        self.nome_var.set("")
        self.data_nasc_var.set("")
        self.cpf_var.set("")
        self.sexo_var.set("")
        self.nacionalidade_var.set("Brasileira")
        self.telefone_var.set("")
        self.endereco_var.set("")
        self.turma_var.set("")
        self.status_var.set("Ativo")
        
        # Apenas mensalidade
        self.mensalidade_entry.set_float_value(0.0)
        
        # Responsáveis
        self.responsaveis_data = []
        self.atualizar_lista_responsaveis()
    
    def cancelar_edicao(self):
        """Cancela edição"""
        self.aluno_editando = None
        self.salvar_btn.config(text="💾 Salvar Aluno")
        self.cancelar_btn.pack_forget()
    
    def create_lista_tab(self, parent):
        """Cria aba de lista de alunos"""
        lista_container = tk.Frame(parent, bg='white')
        lista_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Filtros
        filter_frame = tk.LabelFrame(
            lista_container,
            text="  🔍 Filtros  ",
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
            text="  📋 Alunos Cadastrados  ",
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
        columns = ('ID', 'Nome', 'CPF', 'Idade', 'Turma', 'Mensalidade', 'Responsável', 'Status')
        self.tree = ttk.Treeview(table_content, columns=columns, show='headings', height=15)
        
        # Configurar colunas
        column_widths = {'ID': 50, 'Nome': 180, 'CPF': 120, 'Idade': 60, 'Turma': 120, 
                        'Mensalidade': 100, 'Responsável': 150, 'Status': 80}
        
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
    
    def editar_aluno(self):
        """Edita aluno com campos simplificados"""
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
            
            # Preencher dados pessoais
            self.nome_var.set(aluno['nome'])
            
            # Data com formatação
            if aluno['data_nascimento']:
                try:
                    data_obj = datetime.strptime(aluno['data_nascimento'], '%Y-%m-%d')
                    data_formatada = data_obj.strftime('%d%m%Y')
                    self.data_entry.set_value(data_formatada)
                except:
                    self.data_nasc_var.set('')
            
            # CPF com formatação
            if aluno.get('cpf'):
                self.cpf_entry.set_value(aluno['cpf'])
            
            # Telefone com formatação
            if aluno.get('telefone'):
                self.telefone_entry.set_value(aluno['telefone'])
            
            self.sexo_var.set(aluno.get('sexo', '') or '')
            self.nacionalidade_var.set(aluno.get('nacionalidade', '') or 'Brasileira')
            self.endereco_var.set(aluno.get('endereco', '') or '')
            self.status_var.set(aluno['status'])
            
            # Apenas mensalidade
            self.mensalidade_entry.set_float_value(aluno.get('valor_mensalidade', 0))
            
            # Selecionar turma
            for display, turma_id in self.turmas_map.items():
                if turma_id == aluno['turma_id']:
                    self.turma_var.set(display)
                    break
            
            # Responsáveis
            self.responsaveis_data = aluno.get('responsaveis', [])
            self.atualizar_lista_responsaveis()
            
            # Modo edição
            self.aluno_editando = aluno_id
            self.salvar_btn.config(text="💾 Atualizar Aluno")
            self.cancelar_btn.pack(side=tk.LEFT, padx=(15, 0))
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar aluno: {str(e)}")
    
    def excluir_aluno(self):
        """Exclui aluno"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um aluno para excluir!")
            return
        
        item = self.tree.item(selection[0])
        aluno_id = item['values'][0]
        aluno_nome = item['values'][1]
        
        if messagebox.askyesno("Confirmar", f"Excluir aluno '{aluno_nome}' e todos os dados relacionados?"):
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
        hist_window.geometry("900x600")
        hist_window.configure(bg='white')
        
        tk.Label(
            hist_window, text=f"💰 Histórico Financeiro - {nome}",
            font=('Arial', 16, 'bold'), bg='white', fg='#2c3e50'
        ).pack(pady=20)
        
        if not historico:
            tk.Label(
                hist_window, text="Nenhum registro encontrado",
                font=('Arial', 12), bg='white', fg='#6c757d'
            ).pack(expand=True)
        else:
            # Tabela de histórico
            hist_frame = tk.Frame(hist_window, bg='white')
            hist_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            columns = ('Mês/Ano', 'Valor', 'Desconto', 'Multa', 'Final', 'Vencimento', 'Pagamento', 'Status')
            hist_tree = ttk.Treeview(hist_frame, columns=columns, show='headings', height=15)
            
            for col in columns:
                hist_tree.heading(col, text=col, anchor='center')
                hist_tree.column(col, width=100, anchor='center')
            
            # Scrollbar
            hist_scroll = ttk.Scrollbar(hist_frame, orient='vertical', command=hist_tree.yview)
            hist_tree.configure(yscrollcommand=hist_scroll.set)
            
            hist_tree.pack(side='left', fill='both', expand=True)
            hist_scroll.pack(side='right', fill='y')
            
            # Preencher dados
            for reg in historico:
                valores = (
                    reg['mes_referencia'].replace('-', '/'),
                    format_currency(reg['valor_original']),
                    format_currency(reg['desconto_aplicado']),
                    format_currency(reg['multa_aplicada']),
                    format_currency(reg['valor_final']),
                    format_date(reg['data_vencimento']),
                    format_date(reg['data_pagamento']) if reg['data_pagamento'] else '-',
                    reg['status']
                )
                hist_tree.insert('', tk.END, values=valores)
        
        tk.Button(
            hist_window, text="Fechar", command=hist_window.destroy,
            bg='#6c757d', fg='white', font=('Arial', 11, 'bold'),
            padx=20, pady=8
        ).pack(pady=20)
    
    def carregar_alunos(self, turma_id=None):
        """Carrega lista de alunos"""
        try:
            # Limpar tabela
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            alunos = self.aluno_service.listar_alunos(turma_id)
            
            for aluno in alunos:
                # Formatar CPF para exibição
                cpf_display = self.formatter.format_cpf_smart(aluno.get('cpf', '')) if aluno.get('cpf') else '-'
                
                valores = (
                    aluno['id'],
                    aluno['nome'][:25] + "..." if len(aluno['nome']) > 25 else aluno['nome'],
                    cpf_display,
                    aluno['idade'],
                    f"{aluno['turma_nome']} - {aluno['turma_serie']}",
                    format_currency(aluno.get('valor_mensalidade', 0)),
                    aluno['responsavel_principal'][:20] + "..." if len(aluno['responsavel_principal']) > 20 else aluno['responsavel_principal'],
                    '✅ Ativo' if aluno['status'] == 'Ativo' else '❌ Inativo'
                )
                self.tree.insert('', tk.END, values=valores)
            
            print(f"✅ {len(alunos)} alunos carregados")
            
        except Exception as e:
            print(f"Erro ao carregar alunos: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar alunos: {str(e)}")
