import tkinter as tk
from tkinter import ttk, messagebox
from services.aluno_service import AlunoService
from utils.formatters import format_currency, format_date
from datetime import datetime, date
import re

class AlunosInterface:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.parent_frame.configure(bg='white')
        
        self.aluno_service = AlunoService()
        
        # Variáveis
        self.alunos_data = []
        self.turmas_data = []
        self.aluno_selecionado = None
        
        try:
            self.create_interface()
            self.carregar_dados()
        except Exception as e:
            self.mostrar_erro(f"Erro ao criar interface de alunos: {e}")

    def create_interface(self):
        """Cria interface de alunos"""
        
        # Container principal
        main_container = tk.Frame(self.parent_frame, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # === CABEÇALHO ===
        header_frame = tk.Frame(main_container, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            header_frame,
            text="👥 Gestão de Alunos",
            font=('Arial', 24, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(side=tk.LEFT)
        
        # Botões do cabeçalho
        btn_frame = tk.Frame(header_frame, bg='white')
        btn_frame.pack(side=tk.RIGHT)
        
        tk.Button(
            btn_frame,
            text="➕ Novo Aluno",
            command=self.novo_aluno,
            font=('Arial', 10, 'bold'),
            bg='#28a745',
            fg='white',
            padx=15,
            pady=5,
            relief='flat'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            btn_frame,
            text="🔄 Atualizar",
            command=self.carregar_dados,
            font=('Arial', 10, 'bold'),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=5,
            relief='flat'
        ).pack(side=tk.LEFT)
        
        # === ABAS ===
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba Lista
        self.frame_lista = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.frame_lista, text="📋 Lista de Alunos")
        self.criar_aba_lista()
        
        # Aba Cadastro
        self.frame_cadastro = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.frame_cadastro, text="📝 Cadastro")
        self.criar_aba_cadastro()

    def criar_aba_lista(self):
        """Cria aba de listagem"""
        
        # === FILTROS ===
        filter_frame = tk.LabelFrame(
            self.frame_lista,
            text=" 🔍 Filtros ",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        filter_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        filter_content = tk.Frame(filter_frame, bg='white')
        filter_content.pack(fill=tk.X, padx=10, pady=10)
        
        # Filtro por turma
        tk.Label(filter_content, text="Filtrar por turma:", font=('Arial', 10, 'bold'), bg='white').pack(side=tk.LEFT)
        
        self.turma_var = tk.StringVar(value="Todas")
        self.turma_combo = ttk.Combobox(
            filter_content, textvariable=self.turma_var,
            values=["Todas"], width=25, state="readonly"
        )
        self.turma_combo.pack(side=tk.LEFT, padx=(5, 15))
        
        # Botões de filtro
        tk.Button(
            filter_content,
            text="🔍 Filtrar",
            command=self.filtrar_alunos,
            font=('Arial', 9, 'bold'),
            bg='#3498db',
            fg='white',
            padx=10,
            relief='flat'
        ).pack(side=tk.LEFT, padx=(10, 5))
        
        tk.Button(
            filter_content,
            text="🗑️ Limpar",
            command=self.limpar_filtros,
            font=('Arial', 9, 'bold'),
            bg='#6c757d',
            fg='white',
            padx=10,
            relief='flat'
        ).pack(side=tk.LEFT)
        
        # === LISTA DE ALUNOS ===
        list_frame = tk.LabelFrame(
            self.frame_lista,
            text=" 👥 Alunos Cadastrados ",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        # TreeView
        tree_frame = tk.Frame(list_frame, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('id', 'nome', 'cpf', 'idade', 'turma', 'mensalidade', 'responsavel', 'status')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)
        
        # Configurar colunas
        colunas_config = {
            'id': ('ID', 50),
            'nome': ('Nome', 200),
            'cpf': ('CPF', 120),
            'idade': ('Idade', 60),
            'turma': ('Turma', 150),
            'mensalidade': ('Mensalidade', 100),
            'responsavel': ('Responsável', 150),
            'status': ('Status', 80)
        }
        
        for col, (heading, width) in colunas_config.items():
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, minwidth=50)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Grid
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        # Tags
        self.tree.tag_configure('ativo', background='#d4edda')
        self.tree.tag_configure('inativo', background='#f8d7da')
        
        # === BOTÕES DE AÇÃO ===
        btn_frame = tk.Frame(list_frame, bg='white')
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        buttons = [
            ("✏️ Editar", self.editar_aluno, "#007bff"),
            ("🗑️ Excluir", self.excluir_aluno, "#dc3545"),
            ("📊 Histórico", self.ver_historico, "#fd7e14"),
            ("🔄 Atualizar", self.carregar_dados, "#6c757d")
        ]
        
        for texto, comando, cor in buttons:
            tk.Button(
                btn_frame,
                text=texto,
                command=comando,
                font=('Arial', 10, 'bold'),
                bg=cor,
                fg='white',
                padx=15,
                pady=8,
                relief='flat'
            ).pack(side=tk.LEFT, padx=(0, 10))

    def criar_aba_cadastro(self):
        """Cria aba de cadastro/edição COM BOTÕES"""
        
        # Container com scroll
        canvas = tk.Canvas(self.frame_cadastro, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame_cadastro, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='white')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # === DADOS DO ALUNO ===
        self.criar_secao_dados_aluno()
        
        # === RESPONSÁVEIS ===
        self.criar_secao_responsaveis()
        
        # === BOTÕES DE AÇÃO ===
        self.criar_botoes_cadastro()
        
        # Inicializar variáveis do formulário
        self.inicializar_variaveis_form()

    def criar_secao_dados_aluno(self):
        """Cria seção de dados do aluno"""
        
        dados_frame = tk.LabelFrame(
            self.scrollable_frame,
            text=" 👤 Dados do Aluno ",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        dados_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Grid para organizar campos
        form_frame = tk.Frame(dados_frame, bg='white')
        form_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # Linha 1: Nome e CPF
        row = 0
        tk.Label(form_frame, text="Nome Completo *", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky='w', pady=(0, 5))
        self.entry_nome = tk.Entry(form_frame, font=('Arial', 11), width=40)
        self.entry_nome.grid(row=row+1, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        tk.Label(form_frame, text="CPF", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=2, sticky='w', padx=(20, 0), pady=(0, 5))
        self.entry_cpf = tk.Entry(form_frame, font=('Arial', 11), width=20)
        self.entry_cpf.grid(row=row+1, column=2, sticky='ew', padx=(20, 0), pady=(0, 10))
        
        # Linha 2: Data de nascimento e Sexo
        row += 2
        tk.Label(form_frame, text="Data de Nascimento *", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky='w', pady=(0, 5))
        self.entry_data_nasc = tk.Entry(form_frame, font=('Arial', 11), width=15)
        self.entry_data_nasc.grid(row=row+1, column=0, sticky='w', pady=(0, 10))
        self.entry_data_nasc.insert(0, "DD/MM/AAAA")
        self.entry_data_nasc.bind('<FocusIn>', self.limpar_placeholder)
        
        tk.Label(form_frame, text="Sexo", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=1, sticky='w', padx=(20, 0), pady=(0, 5))
        self.sexo_var = tk.StringVar(value="Masculino")
        sexo_combo = ttk.Combobox(form_frame, textvariable=self.sexo_var, values=["Masculino", "Feminino"], state="readonly", width=12)
        sexo_combo.grid(row=row+1, column=1, sticky='w', padx=(20, 0), pady=(0, 10))
        
        tk.Label(form_frame, text="Nacionalidade", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=2, sticky='w', padx=(20, 0), pady=(0, 5))
        self.entry_nacionalidade = tk.Entry(form_frame, font=('Arial', 11), width=20)
        self.entry_nacionalidade.grid(row=row+1, column=2, sticky='ew', padx=(20, 0), pady=(0, 10))
        self.entry_nacionalidade.insert(0, "Brasileira")
        
        # Linha 3: Telefone e Turma
        row += 2
        tk.Label(form_frame, text="Telefone", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky='w', pady=(0, 5))
        self.entry_telefone = tk.Entry(form_frame, font=('Arial', 11), width=20)
        self.entry_telefone.grid(row=row+1, column=0, sticky='w', pady=(0, 10))
        
        tk.Label(form_frame, text="Turma *", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=1, sticky='w', padx=(20, 0), pady=(0, 5))
        self.turma_cadastro_var = tk.StringVar()
        self.turma_cadastro_combo = ttk.Combobox(form_frame, textvariable=self.turma_cadastro_var, state="readonly", width=25)
        self.turma_cadastro_combo.grid(row=row+1, column=1, columnspan=2, sticky='ew', padx=(20, 0), pady=(0, 10))
        
        # Linha 4: Mensalidade e Status
        row += 2
        tk.Label(form_frame, text="Valor da Mensalidade *", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky='w', pady=(0, 5))
        self.entry_mensalidade = tk.Entry(form_frame, font=('Arial', 11), width=15)
        self.entry_mensalidade.grid(row=row+1, column=0, sticky='w', pady=(0, 10))
        
        tk.Label(form_frame, text="Status", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=1, sticky='w', padx=(20, 0), pady=(0, 5))
        self.status_var = tk.StringVar(value="Ativo")
        status_combo = ttk.Combobox(form_frame, textvariable=self.status_var, values=["Ativo", "Inativo"], state="readonly", width=12)
        status_combo.grid(row=row+1, column=1, sticky='w', padx=(20, 0), pady=(0, 10))
        
        # Linha 5: Endereço
        row += 2
        tk.Label(form_frame, text="Endereço", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky='w', pady=(0, 5))
        self.entry_endereco = tk.Entry(form_frame, font=('Arial', 11), width=60)
        self.entry_endereco.grid(row=row+1, column=0, columnspan=3, sticky='ew', pady=(0, 10))
        
        # Configurar grid
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(2, weight=1)

    def criar_secao_responsaveis(self):
        """Cria seção de responsáveis"""
        
        resp_frame = tk.LabelFrame(
            self.scrollable_frame,
            text=" 👨‍👩‍👧‍👦 Responsáveis ",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        resp_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Lista de responsáveis
        self.responsaveis_list = []
        
        # Frame para responsáveis dinâmicos
        self.responsaveis_frame = tk.Frame(resp_frame, bg='white')
        self.responsaveis_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # Botão para adicionar responsável
        tk.Button(
            resp_frame,
            text="➕ Adicionar Responsável",
            command=self.adicionar_responsavel,
            font=('Arial', 10, 'bold'),
            bg='#28a745',
            fg='white',
            padx=15,
            pady=8,
            relief='flat'
        ).pack(pady=(0, 15))

    def criar_botoes_cadastro(self):
        """Cria botões de ação do cadastro - COM BOTÕES VISÍVEIS"""
        
        btn_frame = tk.Frame(self.scrollable_frame, bg='white')
        btn_frame.pack(fill=tk.X, padx=20, pady=(20, 30))
        
        # ID do aluno (oculto, para edição)
        self.aluno_id_var = tk.StringVar()
        
        # === BOTÕES PRINCIPAIS ===
        # Botão Salvar
        self.btn_salvar = tk.Button(
            btn_frame,
            text="💾 Salvar Aluno",
            command=self.salvar_aluno,
            font=('Arial', 12, 'bold'),
            bg='#28a745',
            fg='white',
            padx=25,
            pady=12,
            relief='flat',
            cursor='hand2'
        )
        self.btn_salvar.pack(side=tk.LEFT, padx=(0, 15))
        
        # Botão Limpar
        tk.Button(
            btn_frame,
            text="🔄 Limpar Formulário",
            command=self.limpar_formulario,
            font=('Arial', 12, 'bold'),
            bg='#6c757d',
            fg='white',
            padx=25,
            pady=12,
            relief='flat'
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        # Botão Cancelar
        tk.Button(
            btn_frame,
            text="❌ Cancelar",
            command=self.cancelar_cadastro,
            font=('Arial', 12, 'bold'),
            bg='#dc3545',
            fg='white',
            padx=25,
            pady=12,
            relief='flat'
        ).pack(side=tk.LEFT)

    def inicializar_variaveis_form(self):
        """Inicializa variáveis do formulário"""
        self.responsaveis_list = []
        self.adicionar_responsavel()  # Adiciona primeiro responsável

    def limpar_placeholder(self, event):
        """Remove placeholder do campo de data"""
        if event.widget.get() == "DD/MM/AAAA":
            event.widget.delete(0, tk.END)

    def adicionar_responsavel(self):
        """Adiciona campo para novo responsável"""
        
        index = len(self.responsaveis_list)
        
        # Frame para este responsável
        resp_item_frame = tk.LabelFrame(
            self.responsaveis_frame,
            text=f" Responsável {index + 1} ",
            font=('Arial', 10, 'bold'),
            bg='white'
        )
        resp_item_frame.pack(fill=tk.X, pady=(0, 10))
        
        form_resp = tk.Frame(resp_item_frame, bg='white')
        form_resp.pack(fill=tk.X, padx=15, pady=10)
        
        # Campos do responsável
        tk.Label(form_resp, text="Nome:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', pady=(0, 5))
        entry_nome = tk.Entry(form_resp, font=('Arial', 11), width=30)
        entry_nome.grid(row=1, column=0, sticky='ew', pady=(0, 10), padx=(0, 10))
        
        tk.Label(form_resp, text="Telefone:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=1, sticky='w', pady=(0, 5))
        entry_telefone = tk.Entry(form_resp, font=('Arial', 11), width=20)
        entry_telefone.grid(row=1, column=1, sticky='ew', pady=(0, 10), padx=(0, 10))
        
        tk.Label(form_resp, text="Parentesco:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=2, sticky='w', pady=(0, 5))
        parentesco_var = tk.StringVar(value="Pai")
        parentesco_combo = ttk.Combobox(form_resp, textvariable=parentesco_var, 
                                      values=["Pai", "Mãe", "Avô", "Avó", "Tio", "Tia", "Responsável"], 
                                      state="readonly", width=15)
        parentesco_combo.grid(row=1, column=2, sticky='ew', pady=(0, 10), padx=(0, 10))
        
        # Checkbox principal
        principal_var = tk.BooleanVar(value=(index == 0))
        principal_check = tk.Checkbutton(form_resp, text="Principal", variable=principal_var, 
                                       font=('Arial', 10), bg='white')
        principal_check.grid(row=1, column=3, sticky='w', padx=(10, 0))
        
        # Botão remover (só se não for o primeiro)
        if index > 0:
            tk.Button(
                form_resp,
                text="🗑️",
                command=lambda idx=index: self.remover_responsavel(idx),
                font=('Arial', 8),
                bg='#dc3545',
                fg='white',
                width=3,
                relief='flat'
            ).grid(row=1, column=4, padx=(10, 0))
        
        form_resp.columnconfigure(0, weight=2)
        form_resp.columnconfigure(1, weight=1)
        form_resp.columnconfigure(2, weight=1)
        
        # Salvar referências
        responsavel_data = {
            'frame': resp_item_frame,
            'nome': entry_nome,
            'telefone': entry_telefone,
            'parentesco': parentesco_var,
            'principal': principal_var
        }
        
        self.responsaveis_list.append(responsavel_data)

    def remover_responsavel(self, index):
        """Remove responsável pelo índice"""
        if index < len(self.responsaveis_list) and len(self.responsaveis_list) > 1:
            # Destruir frame
            self.responsaveis_list[index]['frame'].destroy()
            
            # Remover da lista
            self.responsaveis_list.pop(index)
            
            # Recriar lista (para atualizar índices)
            self.recriar_responsaveis()

    def recriar_responsaveis(self):
        """Recria a lista de responsáveis com índices corretos"""
        # Salvar dados atuais
        dados_temp = []
        for resp in self.responsaveis_list:
            if resp['frame'].winfo_exists():
                dados_temp.append({
                    'nome': resp['nome'].get(),
                    'telefone': resp['telefone'].get(),
                    'parentesco': resp['parentesco'].get(),
                    'principal': resp['principal'].get()
                })
        
        # Limpar tudo
        for widget in self.responsaveis_frame.winfo_children():
            widget.destroy()
        
        self.responsaveis_list = []
        
        # Recriar com dados salvos
        for dados in dados_temp:
            self.adicionar_responsavel()
            resp = self.responsaveis_list[-1]
            resp['nome'].insert(0, dados['nome'])
            resp['telefone'].insert(0, dados['telefone'])
            resp['parentesco'].set(dados['parentesco'])
            resp['principal'].set(dados['principal'])

    def carregar_dados(self):
        """Carrega dados iniciais"""
        try:
            print("👥 Carregando dados de alunos...")
            
            # Carregar alunos
            self.alunos_data = self.aluno_service.listar_alunos()
            
            # Carregar turmas
            self.turmas_data = self.aluno_service.listar_turmas()
            
            # Atualizar combos
            turma_values = ["Todas"] + [t['display'] for t in self.turmas_data]
            self.turma_combo['values'] = turma_values
            
            turma_cadastro_values = [t['display'] for t in self.turmas_data]
            self.turma_cadastro_combo['values'] = turma_cadastro_values
            
            # Atualizar lista
            self.atualizar_lista_alunos()
            
            print(f"✅ {len(self.alunos_data)} alunos e {len(self.turmas_data)} turmas carregados")
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar dados:\n{e}")

    def atualizar_lista_alunos(self):
        """Atualiza a lista de alunos na árvore"""
        
        # Limpar árvore
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Inserir dados
        for aluno in self.alunos_data:
            try:
                tag = 'ativo' if aluno.get('status', '').lower() == 'ativo' else 'inativo'
                
                self.tree.insert('', tk.END, values=(
                    aluno.get('id', ''),
                    aluno.get('nome', ''),
                    aluno.get('cpf', 'N/I'),
                    aluno.get('idade', 0),
                    f"{aluno.get('turma_nome', '')} - {aluno.get('turma_serie', '')}",
                    format_currency(aluno.get('valor_mensalidade', 0)),
                    aluno.get('responsavel_principal', 'N/I'),
                    aluno.get('status', '')
                ), tags=(tag,))
            except Exception as e:
                print(f"⚠️ Erro ao inserir aluno {aluno.get('nome', '')}: {e}")

    def filtrar_alunos(self):
        """Filtra alunos por turma"""
        try:
            turma_filtro = self.turma_var.get()
            
            if turma_filtro == "Todas":
                self.atualizar_lista_alunos()
                return
            
            # Limpar árvore
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Filtrar e inserir
            for aluno in self.alunos_data:
                turma_completa = f"{aluno.get('turma_nome', '')} - {aluno.get('turma_serie', '')}"
                
                if turma_filtro in turma_completa:
                    tag = 'ativo' if aluno.get('status', '').lower() == 'ativo' else 'inativo'
                    
                    self.tree.insert('', tk.END, values=(
                        aluno.get('id', ''),
                        aluno.get('nome', ''),
                        aluno.get('cpf', 'N/I'),
                        aluno.get('idade', 0),
                        turma_completa,
                        format_currency(aluno.get('valor_mensalidade', 0)),
                        aluno.get('responsavel_principal', 'N/I'),
                        aluno.get('status', '')
                    ), tags=(tag,))
            
        except Exception as e:
            print(f"❌ Erro ao filtrar: {e}")

    def limpar_filtros(self):
        """Limpa filtros aplicados"""
        self.turma_var.set("Todas")
        self.atualizar_lista_alunos()

    def novo_aluno(self):
        """Prepara formulário para novo aluno"""
        self.limpar_formulario()
        self.notebook.select(1)  # Vai para aba cadastro

    def editar_aluno(self):
        """Edita aluno selecionado - CORRIGIDO"""
        try:
            selection = self.tree.selection()
            if not selection:
                messagebox.showwarning("Atenção", "Selecione um aluno para editar")
                return
            
            # Obter ID do aluno selecionado
            item = self.tree.item(selection[0])
            aluno_id = item['values'][0]
            
            if not aluno_id:
                messagebox.showerror("Erro", "ID do aluno inválido")
                return
            
            # Buscar dados completos do aluno
            aluno_completo = self.aluno_service.buscar_aluno_por_id(aluno_id)
            
            if not aluno_completo:
                messagebox.showerror("Erro", "Aluno não encontrado")
                return
            
            # Preencher formulário - CORRIGIDO
            self.preencher_formulario_edicao(aluno_completo)
            
            # Ir para aba de cadastro
            self.notebook.select(1)
            
        except Exception as e:
            print(f"❌ Erro ao editar aluno: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar dados do aluno:\n{e}")

    def preencher_formulario_edicao(self, aluno):
        """Preenche formulário com dados do aluno - CORRIGIDO"""
        try:
            # Limpar formulário primeiro
            self.limpar_formulario()
            
            # ID do aluno (para edição)
            self.aluno_id_var.set(str(aluno.get('id', '')))
            
            # Dados básicos
            self.entry_nome.insert(0, aluno.get('nome', ''))
            self.entry_cpf.insert(0, aluno.get('cpf', ''))
            
            # Data de nascimento - CORRIGIDA a formatação
            data_nasc = aluno.get('data_nascimento', '')
            if data_nasc:
                try:
                    # Se estiver no formato YYYY-MM-DD, converter para DD/MM/YYYY
                    if isinstance(data_nasc, str) and len(data_nasc) == 10 and data_nasc.count('-') == 2:
                        partes = data_nasc.split('-')
                        data_formatada = f"{partes[2]}/{partes[1]}/{partes[0]}"
                        self.entry_data_nasc.delete(0, tk.END)
                        self.entry_data_nasc.insert(0, data_formatada)
                    else:
                        self.entry_data_nasc.delete(0, tk.END)
                        self.entry_data_nasc.insert(0, str(data_nasc))
                except:
                    self.entry_data_nasc.delete(0, tk.END)
                    self.entry_data_nasc.insert(0, str(data_nasc))
            
            # Outros campos
            self.sexo_var.set(aluno.get('sexo', 'Masculino'))
            self.entry_nacionalidade.delete(0, tk.END)
            self.entry_nacionalidade.insert(0, aluno.get('nacionalidade', 'Brasileira'))
            self.entry_telefone.insert(0, aluno.get('telefone', ''))
            self.entry_endereco.insert(0, aluno.get('endereco', ''))
            self.status_var.set(aluno.get('status', 'Ativo'))
            
            # Mensalidade - CORRIGIDA formatação
            valor_mensalidade = aluno.get('valor_mensalidade', 0)
            try:
                self.entry_mensalidade.insert(0, f"{float(valor_mensalidade):.2f}")
            except:
                self.entry_mensalidade.insert(0, "0.00")
            
            # Turma - CORRIGIDA seleção
            turma_id = aluno.get('turma_id', '')
            if turma_id:
                for turma in self.turmas_data:
                    if turma['id'] == turma_id:
                        self.turma_cadastro_var.set(turma['display'])
                        break
            
            # Responsáveis - CORRIGIDO
            responsaveis = aluno.get('responsaveis', [])
            
            # Limpar responsáveis atuais
            for widget in self.responsaveis_frame.winfo_children():
                widget.destroy()
            self.responsaveis_list = []
            
            # Adicionar responsáveis do aluno
            if responsaveis:
                for resp in responsaveis:
                    self.adicionar_responsavel()
                    resp_widget = self.responsaveis_list[-1]
                    
                    resp_widget['nome'].insert(0, resp.get('nome', ''))
                    resp_widget['telefone'].insert(0, resp.get('telefone', ''))
                    resp_widget['parentesco'].set(resp.get('parentesco', 'Pai'))
                    resp_widget['principal'].set(resp.get('principal', False))
            else:
                # Se não há responsáveis, adicionar um vazio
                self.adicionar_responsavel()
            
            print(f"✅ Formulário preenchido para edição do aluno: {aluno.get('nome', '')}")
            
        except Exception as e:
            print(f"❌ Erro ao preencher formulário: {e}")
            messagebox.showerror("Erro", f"Erro ao preencher formulário:\n{e}")

    def salvar_aluno(self):
        """Salva aluno (novo ou editado) - FUNÇÃO PRINCIPAL"""
        try:
            print("💾 Iniciando salvamento do aluno...")
            
            # Validar campos obrigatórios
            if not self.entry_nome.get().strip():
                messagebox.showerror("Erro", "Nome é obrigatório")
                return
            
            if not self.entry_data_nasc.get().strip() or self.entry_data_nasc.get() == "DD/MM/AAAA":
                messagebox.showerror("Erro", "Data de nascimento é obrigatória")
                return
            
            if not self.turma_cadastro_var.get():
                messagebox.showerror("Erro", "Turma é obrigatória")
                return
            
            if not self.entry_mensalidade.get().strip():
                messagebox.showerror("Erro", "Valor da mensalidade é obrigatório")
                return
            
            # Validar responsáveis
            responsaveis_validos = []
            for resp in self.responsaveis_list:
                nome = resp['nome'].get().strip()
                telefone = resp['telefone'].get().strip()
                
                if nome or telefone:  # Se tem pelo menos nome ou telefone
                    if not nome:
                        messagebox.showerror("Erro", "Nome do responsável é obrigatório")
                        return
                    if not telefone:
                        messagebox.showerror("Erro", "Telefone do responsável é obrigatório")
                        return
                    
                    responsaveis_validos.append({
                        'nome': nome,
                        'telefone': telefone,
                        'parentesco': resp['parentesco'].get(),
                        'principal': resp['principal'].get()
                    })
            
            if not responsaveis_validos:
                messagebox.showerror("Erro", "Pelo menos um responsável é obrigatório")
                return
            
            # Processar data de nascimento
            data_nasc_str = self.entry_data_nasc.get().strip()
            try:
                # Converter DD/MM/YYYY para YYYY-MM-DD
                if '/' in data_nasc_str:
                    partes = data_nasc_str.split('/')
                    if len(partes) == 3:
                        data_nasc_db = f"{partes[2]}-{partes[1]:0>2}-{partes[0]:0>2}"
                    else:
                        raise ValueError("Formato inválido")
                else:
                    data_nasc_db = data_nasc_str
                
                # Validar data
                datetime.strptime(data_nasc_db, '%Y-%m-%d')
                
            except:
                messagebox.showerror("Erro", "Data de nascimento inválida. Use DD/MM/AAAA")
                return
            
            # Processar valor da mensalidade
            try:
                valor_mensalidade = float(self.entry_mensalidade.get().replace(',', '.'))
                if valor_mensalidade < 0:
                    raise ValueError("Valor não pode ser negativo")
            except:
                messagebox.showerror("Erro", "Valor da mensalidade inválido")
                return
            
            # Buscar ID da turma
            turma_display = self.turma_cadastro_var.get()
            turma_id = None
            
            for turma in self.turmas_data:
                if turma['display'] == turma_display:
                    turma_id = turma['id']
                    break
            
            if not turma_id:
                messagebox.showerror("Erro", "Turma selecionada é inválida")
                return
            
            # Montar dados do aluno
            aluno_data = {
                'nome': self.entry_nome.get().strip(),
                'data_nascimento': data_nasc_db,
                'cpf': self.entry_cpf.get().strip(),
                'sexo': self.sexo_var.get(),
                'nacionalidade': self.entry_nacionalidade.get().strip() or 'Brasileira',
                'telefone': self.entry_telefone.get().strip(),
                'endereco': self.entry_endereco.get().strip(),
                'turma_id': turma_id,
                'status': self.status_var.get(),
                'valor_mensalidade': valor_mensalidade
            }
            
            # Se é edição, incluir ID
            aluno_id = self.aluno_id_var.get()
            if aluno_id:
                aluno_data['id'] = int(aluno_id)
            
            print(f"📊 Dados validados: {aluno_data['nome']}")
            
            # Salvar aluno
            resultado = self.aluno_service.salvar_aluno(aluno_data, responsaveis_validos)
            
            if resultado['success']:
                acao = "atualizado" if aluno_id else "cadastrado"
                messagebox.showinfo("Sucesso", f"✅ Aluno {acao} com sucesso!")
                
                print(f"✅ Aluno salvo: {aluno_data['nome']}")
                
                # Limpar formulário e recarregar dados
                self.limpar_formulario()
                self.carregar_dados()
                
                # Voltar para aba de lista
                self.notebook.select(0)
                
            else:
                messagebox.showerror("Erro", f"❌ Erro ao salvar aluno:\n{resultado['error']}")
                print(f"❌ Erro no salvamento: {resultado['error']}")
                
        except Exception as e:
            print(f"❌ Erro crítico ao salvar aluno: {e}")
            messagebox.showerror("Erro", f"Erro inesperado ao salvar:\n{e}")

    def limpar_formulario(self):
        """Limpa todos os campos do formulário"""
        
        # ID do aluno
        self.aluno_id_var.set('')
        
        # Campos de texto
        self.entry_nome.delete(0, tk.END)
        self.entry_cpf.delete(0, tk.END)
        self.entry_data_nasc.delete(0, tk.END)
        self.entry_data_nasc.insert(0, "DD/MM/AAAA")
        self.entry_nacionalidade.delete(0, tk.END)
        self.entry_nacionalidade.insert(0, "Brasileira")
        self.entry_telefone.delete(0, tk.END)
        self.entry_endereco.delete(0, tk.END)
        self.entry_mensalidade.delete(0, tk.END)
        
        # Combos
        self.sexo_var.set("Masculino")
        self.turma_cadastro_var.set("")
        self.status_var.set("Ativo")
        
        # Responsáveis
        for widget in self.responsaveis_frame.winfo_children():
            widget.destroy()
        
        self.responsaveis_list = []
        self.adicionar_responsavel()

    def cancelar_cadastro(self):
        """Cancela cadastro e volta para lista"""
        if messagebox.askyesno("Cancelar", "Deseja cancelar? Dados não salvos serão perdidos."):
            self.limpar_formulario()
            self.notebook.select(0)

    def excluir_aluno(self):
        """Exclui aluno selecionado"""
        try:
            selection = self.tree.selection()
            if not selection:
                messagebox.showwarning("Atenção", "Selecione um aluno para excluir")
                return
            
            # Obter dados do aluno
            item = self.tree.item(selection[0])
            aluno_id = item['values'][0]
            aluno_nome = item['values'][1]
            
            # Confirmar exclusão
            if not messagebox.askyesno("Confirmar Exclusão", 
                f"Deseja realmente excluir o aluno:\n\n{aluno_nome}\n\nEsta ação não pode ser desfeita!"):
                return
            
            # Excluir aluno
            resultado = self.aluno_service.excluir_aluno(aluno_id)
            
            if resultado['success']:
                messagebox.showinfo("Sucesso", "✅ Aluno excluído com sucesso!")
                self.carregar_dados()
            else:
                messagebox.showerror("Erro", f"❌ Erro ao excluir aluno:\n{resultado['error']}")
                
        except Exception as e:
            print(f"❌ Erro ao excluir aluno: {e}")
            messagebox.showerror("Erro", f"Erro ao excluir aluno:\n{e}")

    def ver_historico(self):
        """Mostra histórico financeiro do aluno"""
        try:
            selection = self.tree.selection()
            if not selection:
                messagebox.showwarning("Atenção", "Selecione um aluno para ver o histórico")
                return
            
            item = self.tree.item(selection[0])
            aluno_id = item['values'][0]
            aluno_nome = item['values'][1]
            
            # Buscar histórico
            historico = self.aluno_service.buscar_historico_financeiro(aluno_id)
            
            # Criar janela de histórico
            self.mostrar_janela_historico(aluno_nome, historico)
            
        except Exception as e:
            print(f"❌ Erro ao buscar histórico: {e}")
            messagebox.showerror("Erro", f"Erro ao buscar histórico:\n{e}")

    def mostrar_janela_historico(self, aluno_nome, historico):
        """Mostra janela com histórico financeiro"""
        
        janela = tk.Toplevel(self.parent_frame)
        janela.title(f"📊 Histórico Financeiro - {aluno_nome}")
        janela.geometry("800x600")
        janela.transient(self.parent_frame.winfo_toplevel())
        
        # Cabeçalho
        header = tk.Frame(janela, bg='#2c3e50')
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text=f"📊 Histórico Financeiro - {aluno_nome}",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack(pady=15)
        
        # Lista de histórico
        frame_lista = tk.Frame(janela)
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # TreeView
        columns = ('mes', 'valor_orig', 'desconto', 'multa', 'valor_final', 'vencimento', 'pagamento', 'status')
        tree = ttk.Treeview(frame_lista, columns=columns, show='headings', height=15)
        
        # Configurar colunas
        headers = {
            'mes': 'Mês/Ano',
            'valor_orig': 'Valor Original',
            'desconto': 'Desconto',
            'multa': 'Multa',
            'valor_final': 'Valor Final',
            'vencimento': 'Vencimento',
            'pagamento': 'Pagamento',
            'status': 'Status'
        }
        
        for col, header_text in headers.items():
            tree.heading(col, text=header_text)
            tree.column(col, width=100, minwidth=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Inserir dados
        for item in historico:
            tree.insert('', tk.END, values=(
                item.get('mes_referencia', ''),
                format_currency(item.get('valor_original', 0)),
                format_currency(item.get('desconto_aplicado', 0)),
                format_currency(item.get('multa_aplicada', 0)),
                format_currency(item.get('valor_final', 0)),
                format_date(item.get('data_vencimento')),
                format_date(item.get('data_pagamento')) if item.get('data_pagamento') else '-',
                item.get('status', '')
            ))
        
        # Botão fechar
        tk.Button(
            janela,
            text="❌ Fechar",
            command=janela.destroy,
            font=('Arial', 12, 'bold'),
            bg='#dc3545',
            fg='white',
            padx=20,
            pady=10
        ).pack(pady=(0, 20))

    def mostrar_erro(self, mensagem):
        """Mostra tela de erro"""
        error_frame = tk.Frame(self.parent_frame, bg='white')
        error_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            error_frame,
            text="⚠️ Erro no Módulo de Alunos",
            font=('Arial', 18, 'bold'),
            bg='white',
            fg='#e74c3c'
        ).pack(pady=(100, 20))
        
        tk.Label(
            error_frame,
            text=mensagem,
            font=('Arial', 12),
            bg='white',
            fg='#6c757d',
            wraplength=600
        ).pack(pady=10)