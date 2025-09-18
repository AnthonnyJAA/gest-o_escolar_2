import tkinter as tk
from tkinter import ttk, messagebox
from services.financeiro_service import FinanceiroService
from services.aluno_service import AlunoService
from utils.formatters import format_currency, format_date
from datetime import datetime, date, timedelta
import calendar

class FinanceiroInterface:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.parent_frame.configure(bg='white')
        
        self.financeiro_service = FinanceiroService()
        self.aluno_service = AlunoService()
        
        # Cache para melhor performance
        self._turmas_cache = None
        self._alunos_cache = None
        self._cache_timestamp = None
        
        # Variáveis de interface
        self.mensalidades_data = []
        self.mensalidades_filtradas = []
        self.mensalidade_selecionada = None
        
        # Variáveis de filtro avançado
        self.filtros = {
            'status': tk.StringVar(value="Todos"),
            'mes': tk.StringVar(value="Todos"),
            'ano': tk.StringVar(value="Todos"),
            'turma': tk.StringVar(value="Todas"),
            'aluno': tk.StringVar(value="Todos"),
            'valor_min': tk.StringVar(),
            'valor_max': tk.StringVar(),
            'data_inicio': tk.StringVar(),
            'data_fim': tk.StringVar()
        }
        
        # Variáveis de entrada para pagamento
        self.var_desconto = tk.StringVar()
        self.var_multa = tk.StringVar()
        self.var_outros = tk.StringVar()
        self.var_observacoes = tk.StringVar()
        
        # Widgets de entrada (para habilitar/desabilitar)
        self.entry_desconto = None
        self.entry_multa = None
        self.entry_outros = None
        self.entry_observacoes = None
        self.btn_dar_baixa = None
        
        # Estatísticas em tempo real
        self.stats_vars = {
            'total_mensalidades': tk.StringVar(value="0"),
            'valor_total': tk.StringVar(value="R$ 0,00"),
            'pendentes': tk.StringVar(value="0"),
            'atrasadas': tk.StringVar(value="0"),
            'pagas': tk.StringVar(value="0")
        }
        
        try:
            self.create_interface()
            self.carregar_dados_iniciais()
            self.setup_keyboard_shortcuts()
        except Exception as e:
            self.mostrar_erro(f"Erro ao criar interface financeira: {e}")
    
    def get_turmas_cached(self):
        """Obtém turmas com cache para performance"""
        current_time = datetime.now()
        
        # Cache por 5 minutos
        if (self._turmas_cache is None or 
            self._cache_timestamp is None or 
            (current_time - self._cache_timestamp).seconds > 300):
            
            self._turmas_cache = self.aluno_service.listar_turmas()
            self._cache_timestamp = current_time
        
        return self._turmas_cache
    
    def create_interface(self):
        """Cria interface financeira AVANÇADA com filtros melhorados"""
        
        # Container principal
        main_container = tk.Frame(self.parent_frame, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # === CABEÇALHO COM ESTATÍSTICAS ===
        self.criar_cabecalho_stats(main_container)
        
        # === ÁREA DE FILTROS AVANÇADOS ===
        self.criar_area_filtros_avancados(main_container)
        
        # === ÁREA PRINCIPAL (2 COLUNAS) ===
        content_frame = tk.Frame(main_container, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Coluna esquerda - Lista de mensalidades
        left_frame = tk.LabelFrame(
            content_frame,
            text=" 📋 Mensalidades ",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.criar_lista_mensalidades(left_frame)
        
        # Coluna direita - Gestão de pagamento
        right_frame = tk.LabelFrame(
            content_frame,
            text=" 💳 Gestão de Pagamento ",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_frame.configure(width=400)
        right_frame.pack_propagate(False)
        
        self.criar_area_pagamento(right_frame)
    
    def criar_cabecalho_stats(self, parent):
        """Cria cabeçalho com estatísticas em tempo real"""
        
        header_frame = tk.Frame(parent, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Título
        title_frame = tk.Frame(header_frame, bg='white')
        title_frame.pack(side=tk.LEFT)
        
        tk.Label(
            title_frame,
            text="💰 Gestão Financeira Avançada",
            font=('Arial', 24, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w')
        
        tk.Label(
            title_frame,
            text="Sistema com filtros avançados e análise em tempo real",
            font=('Arial', 11),
            bg='white',
            fg='#6c757d'
        ).pack(anchor='w')
        
        # Estatísticas em tempo real
        stats_frame = tk.Frame(header_frame, bg='white')
        stats_frame.pack(side=tk.RIGHT)
        
        stats_grid = tk.Frame(stats_frame, bg='white')
        stats_grid.pack()
        
        # Cards de estatísticas
        stats_configs = [
            ("📊 Total", self.stats_vars['total_mensalidades'], "#3498db"),
            ("💰 Valor Total", self.stats_vars['valor_total'], "#27ae60"),
            ("⏳ Pendentes", self.stats_vars['pendentes'], "#f39c12"),
            ("🚨 Atrasadas", self.stats_vars['atrasadas'], "#e74c3c"),
            ("✅ Pagas", self.stats_vars['pagas'], "#27ae60")
        ]
        
        for i, (label, var, color) in enumerate(stats_configs):
            row = i // 3
            col = i % 3
            
            card_frame = tk.Frame(stats_grid, bg=color, relief='raised', bd=2)
            card_frame.grid(row=row, column=col, padx=2, pady=2, sticky='ew')
            
            tk.Label(
                card_frame,
                text=label,
                font=('Arial', 9, 'bold'),
                bg=color,
                fg='white'
            ).pack(padx=8, pady=2)
            
            tk.Label(
                card_frame,
                textvariable=var,
                font=('Arial', 11, 'bold'),
                bg=color,
                fg='white'
            ).pack(padx=8, pady=2)
        
        # Botões de ação rápida
        action_frame = tk.Frame(header_frame, bg='white')
        action_frame.pack(side=tk.RIGHT, padx=(20, 0))
        
        tk.Button(
            action_frame,
            text="🔄 Atualizar",
            command=self.atualizar_tudo,
            font=('Arial', 10, 'bold'),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=5,
            relief='flat'
        ).pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        
        tk.Button(
            action_frame,
            text="📊 Relatório",
            command=self.gerar_relatorio_avancado,
            font=('Arial', 10, 'bold'),
            bg='#9b59b6',
            fg='white',
            padx=15,
            pady=5,
            relief='flat'
        ).pack(side=tk.TOP, fill=tk.X)
    
    def criar_area_filtros_avancados(self, parent):
        """Cria área de filtros avançados MELHORADA"""
        
        filters_frame = tk.LabelFrame(
            parent,
            text=" 🔍 Filtros Avançados ",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        filters_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Container para filtros
        filters_container = tk.Frame(filters_frame, bg='white')
        filters_container.pack(fill=tk.X, padx=15, pady=15)
        
        # === LINHA 1: Filtros básicos ===
        row1_frame = tk.Frame(filters_container, bg='white')
        row1_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Status
        tk.Label(row1_frame, text="Status:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', padx=(0, 5))
        status_combo = ttk.Combobox(
            row1_frame, textvariable=self.filtros['status'],
            values=["Todos", "Pendente", "Atrasado", "Pago"],
            width=12, state="readonly"
        )
        status_combo.grid(row=0, column=1, padx=(0, 20))
        status_combo.bind("<<ComboboxSelected>>", lambda e: self.aplicar_filtros())
        
        # Mês
        tk.Label(row1_frame, text="Mês:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=2, sticky='w', padx=(0, 5))
        meses = ["Todos"] + [f"{i:02d} - {calendar.month_name[i][:3]}" for i in range(1, 13)]
        mes_combo = ttk.Combobox(
            row1_frame, textvariable=self.filtros['mes'],
            values=meses, width=15, state="readonly"
        )
        mes_combo.grid(row=0, column=3, padx=(0, 20))
        mes_combo.bind("<<ComboboxSelected>>", lambda e: self.aplicar_filtros())
        
        # Ano
        tk.Label(row1_frame, text="Ano:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=4, sticky='w', padx=(0, 5))
        anos = ["Todos"] + [str(year) for year in range(2023, 2030)]
        ano_combo = ttk.Combobox(
            row1_frame, textvariable=self.filtros['ano'],
            values=anos, width=10, state="readonly"
        )
        ano_combo.grid(row=0, column=5, padx=(0, 20))
        ano_combo.bind("<<ComboboxSelected>>", lambda e: self.aplicar_filtros())
        
        # === LINHA 2: Filtros específicos ===
        row2_frame = tk.Frame(filters_container, bg='white')
        row2_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Turma
        tk.Label(row2_frame, text="Turma:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.turma_combo = ttk.Combobox(
            row2_frame, textvariable=self.filtros['turma'],
            values=["Todas"], width=20, state="readonly"
        )
        self.turma_combo.grid(row=0, column=1, padx=(0, 20))
        self.turma_combo.bind("<<ComboboxSelected>>", lambda e: self.on_turma_change())
        
        # Aluno
        tk.Label(row2_frame, text="Aluno:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=2, sticky='w', padx=(0, 5))
        self.aluno_combo = ttk.Combobox(
            row2_frame, textvariable=self.filtros['aluno'],
            values=["Todos"], width=25, state="readonly"
        )
        self.aluno_combo.grid(row=0, column=3, padx=(0, 20))
        self.aluno_combo.bind("<<ComboboxSelected>>", lambda e: self.aplicar_filtros())
        
        # === LINHA 3: Filtros de valor e data ===
        row3_frame = tk.Frame(filters_container, bg='white')
        row3_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Valor mínimo
        tk.Label(row3_frame, text="Valor Mín:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', padx=(0, 5))
        valor_min_entry = tk.Entry(row3_frame, textvariable=self.filtros['valor_min'], width=12)
        valor_min_entry.grid(row=0, column=1, padx=(0, 20))
        valor_min_entry.bind('<KeyRelease>', lambda e: self.aplicar_filtros_com_delay())
        
        # Valor máximo  
        tk.Label(row3_frame, text="Valor Máx:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=2, sticky='w', padx=(0, 5))
        valor_max_entry = tk.Entry(row3_frame, textvariable=self.filtros['valor_max'], width=12)
        valor_max_entry.grid(row=0, column=3, padx=(0, 20))
        valor_max_entry.bind('<KeyRelease>', lambda e: self.aplicar_filtros_com_delay())
        
        # Data início
        tk.Label(row3_frame, text="Data Início:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=4, sticky='w', padx=(0, 5))
        data_inicio_entry = tk.Entry(row3_frame, textvariable=self.filtros['data_inicio'], width=12)
        data_inicio_entry.grid(row=0, column=5, padx=(0, 20))
        data_inicio_entry.bind('<KeyRelease>', lambda e: self.aplicar_filtros_com_delay())
        data_inicio_entry.insert(0, "DD/MM/AAAA")
        data_inicio_entry.bind('<FocusIn>', lambda e: self.limpar_placeholder(e, "DD/MM/AAAA"))
        
        # Data fim
        tk.Label(row3_frame, text="Data Fim:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=6, sticky='w', padx=(0, 5))
        data_fim_entry = tk.Entry(row3_frame, textvariable=self.filtros['data_fim'], width=12)
        data_fim_entry.grid(row=0, column=7, padx=(0, 20))
        data_fim_entry.bind('<KeyRelease>', lambda e: self.aplicar_filtros_com_delay())
        data_fim_entry.insert(0, "DD/MM/AAAA")
        data_fim_entry.bind('<FocusIn>', lambda e: self.limpar_placeholder(e, "DD/MM/AAAA"))
        
        # === LINHA 4: Botões de ação ===
        row4_frame = tk.Frame(filters_container, bg='white')
        row4_frame.pack(fill=tk.X, pady=(10, 0))
        
        buttons_config = [
            ("🔍 Aplicar Filtros", self.aplicar_filtros, "#27ae60"),
            ("🗑️ Limpar Filtros", self.limpar_filtros, "#6c757d"),
            ("⚡ Filtros Rápidos", self.mostrar_filtros_rapidos, "#3498db"),
            ("💾 Salvar Filtros", self.salvar_filtros, "#9b59b6")
        ]
        
        for i, (texto, comando, cor) in enumerate(buttons_config):
            tk.Button(
                row4_frame,
                text=texto,
                command=comando,
                font=('Arial', 9, 'bold'),
                bg=cor,
                fg='white',
                padx=15,
                pady=5,
                relief='flat'
            ).grid(row=0, column=i, padx=(0, 10), sticky='ew')
        
        # Configurar grid weights
        for i in range(8):
            row3_frame.columnconfigure(i, weight=1)
        for i in range(4):
            row4_frame.columnconfigure(i, weight=1)
    
    def criar_lista_mensalidades(self, parent):
        """Cria lista de mensalidades otimizada"""
        
        # === TREEVIEW MELHORADA ===
        tree_frame = tk.Frame(parent, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Definir colunas com mais informações
        columns = (
            'id', 'aluno', 'turma', 'mes_ref', 'vencimento', 
            'valor_original', 'desconto', 'multa', 'valor_final', 'status', 'dias_atraso'
        )
        
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configurar colunas otimizadas
        colunas_config = {
            'id': ('ID', 40),
            'aluno': ('Aluno', 180),
            'turma': ('Turma', 120),
            'mes_ref': ('Mês/Ano', 80),
            'vencimento': ('Vencimento', 90),
            'valor_original': ('Valor Orig.', 85),
            'desconto': ('Desconto', 70),
            'multa': ('Multa', 60),
            'valor_final': ('Valor Final', 90),
            'status': ('Status', 80),
            'dias_atraso': ('Dias', 50)
        }
        
        for col, (heading, width) in colunas_config.items():
            self.tree.heading(col, text=heading, command=lambda c=col: self.ordenar_coluna(c))
            self.tree.column(col, width=width, minwidth=40)
        
        # Scrollbars otimizadas
        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Grid otimizado
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        # Bind de seleção
        self.tree.bind("<<TreeviewSelect>>", self.on_mensalidade_select)
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # Tags melhoradas com mais cores
        self.tree.tag_configure('pendente', background='#fff3cd', foreground='#856404')
        self.tree.tag_configure('atrasado', background='#f8d7da', foreground='#721c24')
        self.tree.tag_configure('pago', background='#d4edda', foreground='#155724')
        self.tree.tag_configure('muito_atrasado', background='#dc3545', foreground='white')
        
        # Indicador de carregamento
        self.loading_label = tk.Label(
            tree_frame,
            text="🔄 Carregando mensalidades...",
            font=('Arial', 12),
            bg='white',
            fg='#6c757d'
        )
    
    def criar_area_pagamento(self, right_frame):
        """Cria área de gestão de pagamento otimizada"""
        
        # Container com scroll otimizado
        canvas = tk.Canvas(right_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # === INFORMAÇÕES DA MENSALIDADE SELECIONADA ===
        info_frame = tk.LabelFrame(
            scrollable_frame,
            text=" ℹ️ Mensalidade Selecionada ",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        info_frame.pack(fill=tk.X, padx=10, pady=(10, 15))
        
        # Labels de informação com mais detalhes
        self.info_labels = {}
        info_configs = [
            ('aluno', 'Aluno: Nenhum selecionado'),
            ('turma', 'Turma: -'),
            ('mes', 'Mês/Ano: -'),
            ('vencimento', 'Vencimento: -'),
            ('status', 'Status: -'),
            ('dias_atraso', 'Dias em Atraso: -'),
            ('valor_original', 'Valor Original: R$ 0,00')
        ]
        
        for key, texto_inicial in info_configs:
            label = tk.Label(
                info_frame, 
                text=texto_inicial,
                font=('Arial', 10), 
                bg='white', 
                anchor='w'
            )
            label.pack(fill=tk.X, padx=10, pady=2)
            self.info_labels[key] = label
        
        # === CÁLCULO INTELIGENTE ===
        calculo_frame = tk.LabelFrame(
            scrollable_frame,
            text=" 🧮 Cálculo Inteligente: Original - Desconto + Multa + Outros ",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#27ae60'
        )
        calculo_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        # Valor original com destaque
        valor_frame = tk.Frame(calculo_frame, bg='white')
        valor_frame.pack(fill=tk.X, padx=10, pady=(10, 15))
        
        tk.Label(valor_frame, text="💰 Valor Original:", font=('Arial', 10, 'bold'), bg='white').pack(side=tk.LEFT)
        self.lbl_valor_original = tk.Label(valor_frame, text="R$ 0,00", 
                                          font=('Arial', 14, 'bold'), bg='white', fg='#2c3e50')
        self.lbl_valor_original.pack(side=tk.RIGHT)
        
        # Campos de entrada otimizados
        campos_config = [
            ('desconto', '💸 Desconto (R$):', '#e74c3c'),
            ('multa', '🚨 Multa (R$):', '#f39c12'),
            ('outros', '➕ Outros (R$):', '#3498db')
        ]
        
        for field, label, color in campos_config:
            field_frame = tk.Frame(calculo_frame, bg='white')
            field_frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(field_frame, text=label, font=('Arial', 10, 'bold'), 
                    bg='white', fg=color).pack(anchor='w')
            
            entry = tk.Entry(field_frame, textvariable=getattr(self, f'var_{field}'), 
                           font=('Arial', 11), width=20, state='disabled')
            entry.pack(anchor='w', pady=(2, 0))
            entry.bind('<KeyRelease>', self.calcular_valor_final)
            entry.bind('<FocusOut>', self.validar_valor_numerico)
            
            setattr(self, f'entry_{field}', entry)
        
        # Separador visual
        separator = tk.Frame(calculo_frame, bg='#27ae60', height=2)
        separator.pack(fill=tk.X, padx=10, pady=10)
        
        # Valor final com destaque
        final_frame = tk.Frame(calculo_frame, bg='#f8f9fa', relief='solid', bd=1)
        final_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        tk.Label(final_frame, text="💳 VALOR FINAL:", font=('Arial', 12, 'bold'), 
                bg='#f8f9fa', fg='#2c3e50').pack(anchor='w', padx=10, pady=(10, 5))
        self.lbl_valor_final = tk.Label(final_frame, text="R$ 0,00", 
                                       font=('Arial', 16, 'bold'), bg='#f8f9fa', fg='#27ae60')
        self.lbl_valor_final.pack(anchor='w', padx=10, pady=(0, 10))
        
        # === OBSERVAÇÕES MELHORADAS ===
        obs_frame = tk.LabelFrame(
            scrollable_frame,
            text=" 📝 Observações do Pagamento ",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        obs_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        self.entry_observacoes = tk.Text(obs_frame, height=3, wrap=tk.WORD, 
                                        font=('Arial', 10), state='disabled')
        self.entry_observacoes.pack(fill=tk.X, padx=10, pady=10)
        
        # === BOTÕES DE AÇÃO PRINCIPAL ===
        self.btn_dar_baixa = tk.Button(
            scrollable_frame,
            text="💳 CONFIRMAR PAGAMENTO",
            command=self.dar_baixa_mensalidade,
            font=('Arial', 12, 'bold'),
            bg='#28a745',
            fg='white',
            padx=20,
            pady=15,
            relief='flat',
            cursor='hand2',
            state='disabled'
        )
        self.btn_dar_baixa.pack(fill=tk.X, padx=10, pady=(10, 15))
        
        # === BOTÕES SECUNDÁRIOS MELHORADOS ===
        buttons_frame = tk.Frame(scrollable_frame, bg='white')
        buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 20))
        
        secondary_buttons = [
            ("🧮 Calcular Multa", self.calcular_multa_automatica, "#f39c12"),
            ("💸 Aplicar Desconto", self.aplicar_desconto_rapido, "#e74c3c"),
            ("❌ Cancelar", self.cancelar_selecao, "#6c757d")
        ]
        
        for i, (texto, comando, cor) in enumerate(secondary_buttons):
            btn = tk.Button(
                buttons_frame,
                text=texto,
                command=comando,
                font=('Arial', 9, 'bold'),
                bg=cor,
                fg='white',
                padx=10,
                pady=6,
                relief='flat'
            )
            btn.grid(row=0, column=i, padx=(0, 5), sticky='ew')
        
        # Configurar grid
        for i in range(3):
            buttons_frame.columnconfigure(i, weight=1)
    
    # === MÉTODOS DE FILTRO AVANÇADO ===
    
    def carregar_dados_iniciais(self):
        """Carrega dados iniciais com cache"""
        try:
            print("💰 Carregando dados financeiros...")
            
            # Carregar mensalidades
            self.mensalidades_data = self.financeiro_service.listar_mensalidades()
            self.mensalidades_filtradas = self.mensalidades_data.copy()
            
            # Carregar dados para filtros
            self.atualizar_combos_filtros()
            
            # Atualizar interface
            self.atualizar_tree()
            self.atualizar_estatisticas()
            
            print(f"✅ {len(self.mensalidades_data)} mensalidades carregadas")
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados iniciais: {e}")
            self.mostrar_erro(f"Erro ao carregar dados: {e}")
    
    def atualizar_combos_filtros(self):
        """Atualiza combos de filtros com dados atuais"""
        try:
            # Turmas
            turmas = self.get_turmas_cached()
            turma_values = ["Todas"] + [t['display'] for t in turmas]
            self.turma_combo['values'] = turma_values
            
            # Anos únicos das mensalidades
            anos = set()
            for m in self.mensalidades_data:
                if m.get('mes_referencia'):
                    ano = m['mes_referencia'].split('-')[0]
                    anos.add(ano)
            
            ano_values = ["Todos"] + sorted(list(anos), reverse=True)
            
            # Atualizar combos de ano se diferentes dos valores atuais
            current_anos = list(self.filtros['ano'].get() for _ in range(1))
            if set(ano_values) != set(current_anos):
                # Encontrar o combo de ano e atualizar
                for widget in self.parent_frame.winfo_children():
                    if hasattr(widget, 'winfo_children'):
                        self._update_combo_recursive(widget, 'ano', ano_values)
            
        except Exception as e:
            print(f"⚠️ Erro ao atualizar combos: {e}")
    
    def _update_combo_recursive(self, parent, combo_name, values):
        """Atualiza combo recursivamente"""
        for widget in parent.winfo_children():
            if isinstance(widget, ttk.Combobox):
                if hasattr(widget, 'textvariable') and widget['textvariable'] == str(self.filtros.get(combo_name)):
                    widget['values'] = values
            elif hasattr(widget, 'winfo_children'):
                self._update_combo_recursive(widget, combo_name, values)
    
    def on_turma_change(self):
        """Atualiza combo de alunos quando turma muda"""
        try:
            turma_selecionada = self.filtros['turma'].get()
            
            if turma_selecionada == "Todas":
                # Todos os alunos
                alunos_únicos = set()
                for m in self.mensalidades_data:
                    alunos_únicos.add(m.get('aluno_nome', ''))
                aluno_values = ["Todos"] + sorted(list(alunos_únicos))
            else:
                # Alunos da turma específica
                alunos_únicos = set()
                for m in self.mensalidades_data:
                    if turma_selecionada in m.get('turma_nome', ''):
                        alunos_únicos.add(m.get('aluno_nome', ''))
                aluno_values = ["Todos"] + sorted(list(alunos_únicos))
            
            self.aluno_combo['values'] = aluno_values
            self.filtros['aluno'].set("Todos")
            
            self.aplicar_filtros()
            
        except Exception as e:
            print(f"❌ Erro ao atualizar alunos por turma: {e}")
    
    def aplicar_filtros(self):
        """Aplica todos os filtros selecionados"""
        try:
            print("🔍 Aplicando filtros avançados...")
            
            dados_filtrados = self.mensalidades_data.copy()
            
            # Filtro por status
            status = self.filtros['status'].get()
            if status != "Todos":
                dados_filtrados = [m for m in dados_filtrados 
                                 if status.lower() in m.get('status', '').lower()]
            
            # Filtro por mês
            mes = self.filtros['mes'].get()
            if mes != "Todos":
                mes_num = mes.split(' - ')[0] if ' - ' in mes else mes
                dados_filtrados = [m for m in dados_filtrados 
                                 if m.get('mes_referencia', '').split('-')[1] == mes_num]
            
            # Filtro por ano
            ano = self.filtros['ano'].get()
            if ano != "Todos":
                dados_filtrados = [m for m in dados_filtrados 
                                 if m.get('mes_referencia', '').split('-')[0] == ano]
            
            # Filtro por turma
            turma = self.filtros['turma'].get()
            if turma != "Todas":
                dados_filtrados = [m for m in dados_filtrados 
                                 if turma in m.get('turma_nome', '')]
            
            # Filtro por aluno
            aluno = self.filtros['aluno'].get()
            if aluno != "Todos":
                dados_filtrados = [m for m in dados_filtrados 
                                 if aluno in m.get('aluno_nome', '')]
            
            # Filtro por valor mínimo
            valor_min = self.filtros['valor_min'].get()
            if valor_min:
                try:
                    valor_min_float = float(valor_min.replace(',', '.'))
                    dados_filtrados = [m for m in dados_filtrados 
                                     if m.get('valor_final', 0) >= valor_min_float]
                except ValueError:
                    pass
            
            # Filtro por valor máximo
            valor_max = self.filtros['valor_max'].get()
            if valor_max:
                try:
                    valor_max_float = float(valor_max.replace(',', '.'))
                    dados_filtrados = [m for m in dados_filtrados 
                                     if m.get('valor_final', 0) <= valor_max_float]
                except ValueError:
                    pass
            
            # Filtro por data início
            data_inicio = self.filtros['data_inicio'].get()
            if data_inicio and data_inicio != "DD/MM/AAAA":
                try:
                    data_inicio_obj = self.parse_date_filter(data_inicio)
                    if data_inicio_obj:
                        dados_filtrados = [m for m in dados_filtrados 
                                         if self.parse_date_filter(m.get('data_vencimento', '')) >= data_inicio_obj]
                except:
                    pass
            
            # Filtro por data fim
            data_fim = self.filtros['data_fim'].get()
            if data_fim and data_fim != "DD/MM/AAAA":
                try:
                    data_fim_obj = self.parse_date_filter(data_fim)
                    if data_fim_obj:
                        dados_filtrados = [m for m in dados_filtrados 
                                         if self.parse_date_filter(m.get('data_vencimento', '')) <= data_fim_obj]
                except:
                    pass
            
            self.mensalidades_filtradas = dados_filtrados
            
            # Atualizar interface
            self.atualizar_tree()
            self.atualizar_estatisticas()
            
            print(f"✅ Filtros aplicados: {len(dados_filtrados)}/{len(self.mensalidades_data)} mensalidades")
            
        except Exception as e:
            print(f"❌ Erro ao aplicar filtros: {e}")
            messagebox.showerror("Erro", f"Erro ao aplicar filtros:\n{e}")
    
    def aplicar_filtros_com_delay(self):
        """Aplica filtros com delay para evitar múltiplas execuções"""
        # Cancelar timer anterior se existir
        if hasattr(self, '_filter_timer'):
            self.parent_frame.after_cancel(self._filter_timer)
        
        # Agendar aplicação de filtros em 500ms
        self._filter_timer = self.parent_frame.after(500, self.aplicar_filtros)
    
    def parse_date_filter(self, date_str):
        """Converte string de data para objeto date"""
        try:
            if not date_str:
                return None
            
            # Se já é formato YYYY-MM-DD
            if len(date_str) == 10 and date_str.count('-') == 2:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Se é formato DD/MM/YYYY
            if '/' in date_str:
                parts = date_str.split('/')
                if len(parts) == 3:
                    return date(int(parts[2]), int(parts[1]), int(parts[0]))
            
            return None
        except:
            return None
    
    def limpar_filtros(self):
        """Limpa todos os filtros"""
        try:
            # Reset filtros
            self.filtros['status'].set("Todos")
            self.filtros['mes'].set("Todos")
            self.filtros['ano'].set("Todos")
            self.filtros['turma'].set("Todas")
            self.filtros['aluno'].set("Todos")
            self.filtros['valor_min'].set("")
            self.filtros['valor_max'].set("")
            self.filtros['data_inicio'].set("DD/MM/AAAA")
            self.filtros['data_fim'].set("DD/MM/AAAA")
            
            # Recarregar todos os dados
            self.mensalidades_filtradas = self.mensalidades_data.copy()
            self.atualizar_tree()
            self.atualizar_estatisticas()
            
            print("🗑️ Filtros limpos")
            
        except Exception as e:
            print(f"❌ Erro ao limpar filtros: {e}")
    
    def mostrar_filtros_rapidos(self):
        """Mostra menu de filtros rápidos"""
        try:
            popup = tk.Toplevel(self.parent_frame)
            popup.title("⚡ Filtros Rápidos")
            popup.geometry("300x400")
            popup.transient(self.parent_frame.winfo_toplevel())
            popup.grab_set()
            
            # Centralizar popup
            popup.update_idletasks()
            x = self.parent_frame.winfo_rootx() + 50
            y = self.parent_frame.winfo_rooty() + 50
            popup.geometry(f"+{x}+{y}")
            
            tk.Label(
                popup,
                text="⚡ Filtros Rápidos",
                font=('Arial', 16, 'bold'),
                pady=20
            ).pack()
            
            filtros_rapidos = [
                ("🚨 Mensalidades Atrasadas", lambda: self.aplicar_filtro_rapido('status', 'Atrasado')),
                ("⏳ Vencendo Hoje", lambda: self.aplicar_filtro_rapido('vencimento', 'hoje')),
                ("📅 Vencendo Esta Semana", lambda: self.aplicar_filtro_rapido('vencimento', 'semana')),
                ("💰 Valores Altos (>R$ 800)", lambda: self.aplicar_filtro_rapido('valor', 'alto')),
                ("💸 Valores Baixos (<R$ 500)", lambda: self.aplicar_filtro_rapido('valor', 'baixo')),
                ("📆 Mês Atual", lambda: self.aplicar_filtro_rapido('mes', 'atual')),
                ("🎯 Mês Anterior", lambda: self.aplicar_filtro_rapido('mes', 'anterior'))
            ]
            
            for texto, comando in filtros_rapidos:
                tk.Button(
                    popup,
                    text=texto,
                    command=lambda cmd=comando: [cmd(), popup.destroy()],
                    font=('Arial', 11),
                    width=25,
                    pady=8,
                    relief='flat',
                    bg='#f8f9fa',
                    activebackground='#e9ecef'
                ).pack(pady=5, padx=20)
            
            tk.Button(
                popup,
                text="❌ Fechar",
                command=popup.destroy,
                font=('Arial', 11, 'bold'),
                bg='#6c757d',
                fg='white',
                pady=8,
                relief='flat'
            ).pack(pady=20)
            
        except Exception as e:
            print(f"❌ Erro ao mostrar filtros rápidos: {e}")
    
    def aplicar_filtro_rapido(self, tipo, valor):
        """Aplica filtro rápido específico"""
        try:
            self.limpar_filtros()
            
            if tipo == 'status':
                self.filtros['status'].set(valor)
            
            elif tipo == 'vencimento':
                hoje = date.today()
                if valor == 'hoje':
                    self.filtros['data_inicio'].set(hoje.strftime('%d/%m/%Y'))
                    self.filtros['data_fim'].set(hoje.strftime('%d/%m/%Y'))
                elif valor == 'semana':
                    fim_semana = hoje + timedelta(days=7)
                    self.filtros['data_inicio'].set(hoje.strftime('%d/%m/%Y'))
                    self.filtros['data_fim'].set(fim_semana.strftime('%d/%m/%Y'))
            
            elif tipo == 'valor':
                if valor == 'alto':
                    self.filtros['valor_min'].set("800")
                elif valor == 'baixo':
                    self.filtros['valor_max'].set("500")
            
            elif tipo == 'mes':
                hoje = date.today()
                if valor == 'atual':
                    self.filtros['mes'].set(f"{hoje.month:02d} - {calendar.month_name[hoje.month][:3]}")
                elif valor == 'anterior':
                    mes_ant = hoje.replace(day=1) - timedelta(days=1)
                    self.filtros['mes'].set(f"{mes_ant.month:02d} - {calendar.month_name[mes_ant.month][:3]}")
            
            self.aplicar_filtros()
            
        except Exception as e:
            print(f"❌ Erro ao aplicar filtro rápido: {e}")
    
    def salvar_filtros(self):
        """Salva filtros atuais como favoritos"""
        # Implementar salvamento de filtros em arquivo ou banco
        messagebox.showinfo("Info", "Funcionalidade de salvar filtros será implementada em breve")
    
    # === MÉTODOS DE INTERFACE MELHORADOS ===
    
    def atualizar_tree(self):
        """Atualiza a árvore com dados filtrados"""
        try:
            # Mostrar indicador de carregamento
            self.loading_label.place(relx=0.5, rely=0.5, anchor='center')
            self.parent_frame.update()
            
            # Limpar árvore
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Inserir dados filtrados
            for mensalidade in self.mensalidades_filtradas:
                # Calcular dias de atraso
                dias_atraso = self.calcular_dias_atraso(mensalidade.get('data_vencimento'))
                
                # Determinar tag baseada no status e dias de atraso
                status = mensalidade.get('status', '').lower()
                tag = 'pendente'
                
                if 'pago' in status:
                    tag = 'pago'
                elif 'atrasado' in status or dias_atraso > 0:
                    tag = 'muito_atrasado' if dias_atraso > 30 else 'atrasado'
                
                # Inserir item
                self.tree.insert('', tk.END, values=(
                    mensalidade.get('id', ''),
                    mensalidade.get('aluno_nome', ''),
                    mensalidade.get('turma_nome', ''),
                    mensalidade.get('mes_referencia', ''),
                    format_date(mensalidade.get('data_vencimento')),
                    format_currency(mensalidade.get('valor_original', 0)),
                    format_currency(mensalidade.get('desconto_aplicado', 0)),
                    format_currency(mensalidade.get('multa_aplicada', 0)),
                    format_currency(mensalidade.get('valor_final', 0)),
                    mensalidade.get('status', ''),
                    dias_atraso if dias_atraso > 0 else ''
                ), tags=(tag,))
            
            # Remover indicador de carregamento
            self.loading_label.place_forget()
            
        except Exception as e:
            self.loading_label.place_forget()
            print(f"❌ Erro ao atualizar tree: {e}")
    
    def atualizar_estatisticas(self):
        """Atualiza estatísticas em tempo real"""
        try:
            dados = self.mensalidades_filtradas
            
            # Contadores
            total = len(dados)
            pendentes = len([m for m in dados if 'pendente' in m.get('status', '').lower()])
            atrasadas = len([m for m in dados if 'atrasado' in m.get('status', '').lower() 
                           or self.calcular_dias_atraso(m.get('data_vencimento')) > 0])
            pagas = len([m for m in dados if 'pago' in m.get('status', '').lower()])
            
            # Valor total
            valor_total = sum(m.get('valor_final', 0) for m in dados)
            
            # Atualizar variáveis
            self.stats_vars['total_mensalidades'].set(str(total))
            self.stats_vars['valor_total'].set(format_currency(valor_total))
            self.stats_vars['pendentes'].set(str(pendentes))
            self.stats_vars['atrasadas'].set(str(atrasadas))
            self.stats_vars['pagas'].set(str(pagas))
            
        except Exception as e:
            print(f"❌ Erro ao atualizar estatísticas: {e}")
    
    def calcular_dias_atraso(self, data_vencimento):
        """Calcula dias de atraso"""
        try:
            if not data_vencimento:
                return 0
            
            if isinstance(data_vencimento, str):
                venc_date = datetime.strptime(data_vencimento, '%Y-%m-%d').date()
            else:
                venc_date = data_vencimento
            
            hoje = date.today()
            delta = hoje - venc_date
            
            return max(0, delta.days)
            
        except:
            return 0
    
    def ordenar_coluna(self, col):
        """Ordena dados por coluna"""
        try:
            reverse = getattr(self, f'_sort_{col}_reverse', False)
            
            # Mapear colunas para campos de dados
            col_mapping = {
                'id': 'id',
                'aluno': 'aluno_nome', 
                'turma': 'turma_nome',
                'mes_ref': 'mes_referencia',
                'vencimento': 'data_vencimento',
                'valor_original': 'valor_original',
                'valor_final': 'valor_final',
                'status': 'status'
            }
            
            field = col_mapping.get(col, col)
            
            # Ordenar dados filtrados
            if field in ['valor_original', 'valor_final']:
                self.mensalidades_filtradas.sort(
                    key=lambda x: x.get(field, 0), reverse=reverse
                )
            else:
                self.mensalidades_filtradas.sort(
                    key=lambda x: str(x.get(field, '')), reverse=reverse
                )
            
            # Atualizar tree
            self.atualizar_tree()
            
            # Toggle reverse para próxima ordenação
            setattr(self, f'_sort_{col}_reverse', not reverse)
            
        except Exception as e:
            print(f"❌ Erro ao ordenar por {col}: {e}")
    
    def on_double_click(self, event):
        """Ação no duplo clique"""
        try:
            item = self.tree.selection()[0]
            values = self.tree.item(item)['values']
            
            if values and values[9] != 'Pago':  # Se não está pago
                # Auto-selecionar para pagamento
                self.on_mensalidade_select(event)
                # Focar no campo de desconto
                if self.entry_desconto['state'] == 'normal':
                    self.entry_desconto.focus()
            
        except:
            pass
    
    # === MÉTODOS DE PAGAMENTO MELHORADOS ===
    
    def on_mensalidade_select(self, event):
        """Quando uma mensalidade é selecionada - VERSÃO MELHORADA"""
        try:
            selection = self.tree.selection()
            if not selection:
                return
            
            # Obter dados da linha selecionada
            item = self.tree.item(selection[0])
            values = item['values']
            
            if not values:
                return
            
            # Encontrar mensalidade completa nos dados filtrados
            mensalidade_id = values[0]
            
            self.mensalidade_selecionada = None
            for mensalidade in self.mensalidades_filtradas:
                if str(mensalidade.get('id')) == str(mensalidade_id):
                    self.mensalidade_selecionada = mensalidade
                    break
            
            if not self.mensalidade_selecionada:
                return
            
            # Atualizar informações detalhadas
            self.atualizar_informacoes_detalhadas()
            
            # HABILITAR campos se não estiver paga
            if self.mensalidade_selecionada.get('status', '').lower() != 'pago':
                self.habilitar_campos()
            else:
                self.desabilitar_campos()
                messagebox.showinfo("Mensalidade Paga", 
                    f"Esta mensalidade de {self.mensalidade_selecionada.get('aluno_nome')} já foi paga em {format_date(self.mensalidade_selecionada.get('data_pagamento'))}")
            
        except Exception as e:
            print(f"❌ Erro na seleção: {e}")
            messagebox.showerror("Erro", f"Erro ao selecionar mensalidade:\n{e}")
    
    def atualizar_informacoes_detalhadas(self):
        """Atualiza as informações da mensalidade selecionada com mais detalhes"""
        if not self.mensalidade_selecionada:
            return
        
        m = self.mensalidade_selecionada
        
        # Atualizar labels com mais informações
        self.info_labels['aluno'].config(text=f"Aluno: {m.get('aluno_nome', '')}")
        self.info_labels['turma'].config(text=f"Turma: {m.get('turma_nome', '')}")
        self.info_labels['mes'].config(text=f"Mês/Ano: {m.get('mes_referencia', '')}")
        self.info_labels['vencimento'].config(text=f"Vencimento: {format_date(m.get('data_vencimento'))}")
        
        # Status com cor e dias de atraso
        status = m.get('status', '')
        dias_atraso = self.calcular_dias_atraso(m.get('data_vencimento'))
        
        cor = '#28a745' if 'pago' in status.lower() else '#dc3545' if dias_atraso > 0 else '#ffc107'
        self.info_labels['status'].config(text=f"Status: {status}", fg=cor)
        
        if dias_atraso > 0:
            self.info_labels['dias_atraso'].config(
                text=f"Dias em Atraso: {dias_atraso}",
                fg='#dc3545'
            )
        else:
            self.info_labels['dias_atraso'].config(text="Dias em Atraso: -", fg='black')
        
        # Valor original
        valor_original = m.get('valor_original', 0)
        self.lbl_valor_original.config(text=format_currency(valor_original))
        
        # Preencher campos com valores atuais
        self.var_desconto.set(str(m.get('desconto_aplicado', 0)))
        self.var_multa.set(str(m.get('multa_aplicada', 0)))
        self.var_outros.set('0')  # Sempre 0 inicialmente
        
        # Observações no campo de texto
        obs_text = m.get('observacoes', '')
        self.entry_observacoes.config(state='normal')
        self.entry_observacoes.delete(1.0, tk.END)
        self.entry_observacoes.insert(1.0, obs_text)
        if self.entry_observacoes['state'] != 'normal':
            self.entry_observacoes.config(state='disabled')
        
        # Calcular valor final inicial
        self.calcular_valor_final()
    
    def habilitar_campos(self):
        """Habilita campos para edição - VERSÃO MELHORADA"""
        self.entry_desconto.config(state='normal', bg='white')
        self.entry_multa.config(state='normal', bg='white')
        self.entry_outros.config(state='normal', bg='white')
        self.entry_observacoes.config(state='normal', bg='white')
        self.btn_dar_baixa.config(state='normal')
        
        # Auto-calcular multa se em atraso
        dias_atraso = self.calcular_dias_atraso(self.mensalidade_selecionada.get('data_vencimento'))
        if dias_atraso > 0 and float(self.var_multa.get() or 0) == 0:
            self.calcular_multa_automatica()
        
        print("✅ Campos habilitados para edição")
    
    def desabilitar_campos(self):
        """Desabilita campos"""
        self.entry_desconto.config(state='disabled', bg='#f8f9fa')
        self.entry_multa.config(state='disabled', bg='#f8f9fa')
        self.entry_outros.config(state='disabled', bg='#f8f9fa')
        self.entry_observacoes.config(state='disabled', bg='#f8f9fa')
        self.btn_dar_baixa.config(state='disabled')
    
    def calcular_valor_final(self, event=None):
        """Calcula valor final usando nova lógica com validação"""
        try:
            if not self.mensalidade_selecionada:
                return
            
            # Obter valores
            valor_original = float(self.mensalidade_selecionada.get('valor_original', 0))
            
            try:
                desconto = float(self.var_desconto.get().replace(',', '.') or 0)
            except:
                desconto = 0
            
            try:
                multa = float(self.var_multa.get().replace(',', '.') or 0)
            except:
                multa = 0
            
            try:
                outros = float(self.var_outros.get().replace(',', '.') or 0)
            except:
                outros = 0
            
            # Validações
            if desconto > valor_original:
                desconto = valor_original
                self.var_desconto.set(f"{desconto:.2f}")
            
            # Nova lógica: Original - Desconto + Multa + Outros
            valor_final = valor_original - desconto + multa + outros
            
            # Não pode ser negativo
            valor_final = max(0, valor_final)
            
            # Atualizar label com cor baseada no valor
            cor = '#27ae60' if valor_final <= valor_original else '#e74c3c'
            self.lbl_valor_final.config(text=format_currency(valor_final), fg=cor)
            
        except Exception as e:
            print(f"⚠️ Erro no cálculo: {e}")
    
    def validar_valor_numerico(self, event):
        """Valida se valor inserido é numérico"""
        try:
            widget = event.widget
            valor = widget.get()
            
            if valor and not valor.replace(',', '.').replace('.', '').isdigit():
                # Remover caracteres não numéricos
                valor_limpo = ''.join(c for c in valor if c.isdigit() or c in '.,')
                widget.delete(0, tk.END)
                widget.insert(0, valor_limpo)
                
        except:
            pass
    
    def calcular_multa_automatica(self):
        """Calcula multa automaticamente baseada nos dias de atraso"""
        try:
            if not self.mensalidade_selecionada:
                return
            
            dias_atraso = self.calcular_dias_atraso(self.mensalidade_selecionada.get('data_vencimento'))
            
            if dias_atraso <= 0:
                messagebox.showinfo("Info", "Esta mensalidade não está em atraso")
                return
            
            # Fórmula: 2% do valor original + R$ 1 por dia
            valor_original = float(self.mensalidade_selecionada.get('valor_original', 0))
            multa_percentual = valor_original * 0.02  # 2%
            multa_diaria = dias_atraso * 1.0  # R$ 1 por dia
            
            multa_total = multa_percentual + multa_diaria
            
            self.var_multa.set(f"{multa_total:.2f}")
            self.calcular_valor_final()
            
            messagebox.showinfo(
                "Multa Calculada",
                f"Multa automática aplicada:\n\n"
                f"• {dias_atraso} dias de atraso\n"
                f"• 2% do valor: {format_currency(multa_percentual)}\n"
                f"• R$ 1,00 por dia: {format_currency(multa_diaria)}\n"
                f"• Total: {format_currency(multa_total)}"
            )
            
        except Exception as e:
            print(f"❌ Erro ao calcular multa: {e}")
            messagebox.showerror("Erro", f"Erro ao calcular multa:\n{e}")
    
    def aplicar_desconto_rapido(self):
        """Aplica desconto rápido com opções pré-definidas"""
        try:
            if not self.mensalidade_selecionada:
                messagebox.showwarning("Atenção", "Selecione uma mensalidade")
                return
            
            valor_original = float(self.mensalidade_selecionada.get('valor_original', 0))
            
            popup = tk.Toplevel(self.parent_frame)
            popup.title("💸 Desconto Rápido")
            popup.geometry("300x350")
            popup.transient(self.parent_frame.winfo_toplevel())
            popup.grab_set()
            
            # Centralizar
            popup.update_idletasks()
            x = self.parent_frame.winfo_rootx() + 100
            y = self.parent_frame.winfo_rooty() + 100
            popup.geometry(f"+{x}+{y}")
            
            tk.Label(
                popup,
                text="💸 Aplicar Desconto Rápido",
                font=('Arial', 14, 'bold'),
                pady=20
            ).pack()
            
            tk.Label(
                popup,
                text=f"Valor Original: {format_currency(valor_original)}",
                font=('Arial', 12)
            ).pack()
            
            # Opções de desconto
            descontos = [
                ("5% - Pagamento à Vista", valor_original * 0.05),
                ("10% - Desconto Promocional", valor_original * 0.10),
                ("15% - Desconto Especial", valor_original * 0.15),
                ("20% - Desconto Família", valor_original * 0.20)
            ]
            
            for texto, valor_desconto in descontos:
                valor_final = valor_original - valor_desconto
                btn = tk.Button(
                    popup,
                    text=f"{texto}\n{format_currency(valor_desconto)} → {format_currency(valor_final)}",
                    command=lambda v=valor_desconto: [
                        self.var_desconto.set(f"{v:.2f}"),
                        self.calcular_valor_final(),
                        popup.destroy()
                    ],
                    font=('Arial', 10),
                    width=30,
                    pady=8
                )
                btn.pack(pady=5)
            
            tk.Button(
                popup,
                text="❌ Cancelar",
                command=popup.destroy,
                font=('Arial', 11, 'bold'),
                bg='#6c757d',
                fg='white',
                pady=8
            ).pack(pady=20)
            
        except Exception as e:
            print(f"❌ Erro no desconto rápido: {e}")
    
    def dar_baixa_mensalidade(self):
        """Processa pagamento da mensalidade - VERSÃO MELHORADA"""
        try:
            if not self.mensalidade_selecionada:
                messagebox.showwarning("Atenção", "Nenhuma mensalidade selecionada")
                return
            
            # Obter valores com validação
            try:
                desconto = float(self.var_desconto.get().replace(',', '.') or 0)
                multa = float(self.var_multa.get().replace(',', '.') or 0)
                outros = float(self.var_outros.get().replace(',', '.') or 0)
            except ValueError:
                messagebox.showerror("Erro", "Valores inválidos nos campos numéricos.\nUse apenas números.")
                return
            
            valor_original = float(self.mensalidade_selecionada.get('valor_original', 0))
            valor_final = valor_original - desconto + multa + outros
            valor_final = max(0, valor_final)
            
            # Observações do campo de texto
            observacoes = self.entry_observacoes.get("1.0", tk.END).strip()
            
            # Validações adicionais
            if desconto > valor_original:
                if not messagebox.askyesno("Atenção", 
                    f"Desconto ({format_currency(desconto)}) é maior que o valor original ({format_currency(valor_original)}).\n\nContinuar mesmo assim?"):
                    return
            
            if valor_final == 0:
                if not messagebox.askyesno("Atenção", 
                    "O valor final ficou R$ 0,00.\n\nConfirmar pagamento sem valor?"):
                    return
            
            # Confirmar operação com detalhes
            confirmacao = f"""
CONFIRMAR PAGAMENTO DETALHADO

👤 Aluno: {self.mensalidade_selecionada.get('aluno_nome')}
🏫 Turma: {self.mensalidade_selecionada.get('turma_nome')}
📅 Mês/Ano: {self.mensalidade_selecionada.get('mes_referencia')}
📆 Vencimento: {format_date(self.mensalidade_selecionada.get('data_vencimento'))}

💰 CÁLCULO DETALHADO:
• Valor Original: {format_currency(valor_original)}
• Desconto: -{format_currency(desconto)}
• Multa: +{format_currency(multa)}
• Outros: +{format_currency(outros)}
{'=' * 35}
• VALOR FINAL: {format_currency(valor_final)}

📝 Observações: {observacoes or 'Nenhuma'}

🔄 Data do Pagamento: {date.today().strftime('%d/%m/%Y')}

Confirmar este pagamento?
            """
            
            if not messagebox.askyesno("Confirmar Pagamento", confirmacao.strip()):
                return
            
            # Processar pagamento
            resultado = self.financeiro_service.processar_pagamento(
                self.mensalidade_selecionada.get('id'),
                valor_final,
                desconto,
                multa,
                observacoes
            )
            
            if resultado['success']:
                messagebox.showinfo(
                    "Pagamento Processado", 
                    f"✅ Pagamento processado com sucesso!\n\n"
                    f"👤 Aluno: {self.mensalidade_selecionada.get('aluno_nome')}\n"
                    f"💰 Valor Pago: {format_currency(valor_final)}\n"
                    f"📅 Data: {date.today().strftime('%d/%m/%Y')}"
                )
                
                # Atualizar interface
                self.atualizar_tudo()
                self.cancelar_selecao()
                
                # Focar no próximo pendente
                self.focar_proximo_pendente()
                
            else:
                messagebox.showerror("Erro", f"❌ Erro ao processar pagamento:\n{resultado['error']}")
                
        except Exception as e:
            print(f"❌ Erro ao dar baixa: {e}")
            messagebox.showerror("Erro", f"Erro ao processar pagamento:\n{e}")
    
    def focar_proximo_pendente(self):
        """Foca automaticamente na próxima mensalidade pendente"""
        try:
            for item in self.tree.get_children():
                values = self.tree.item(item)['values']
                if len(values) >= 10:
                    status = values[9].lower()
                    if 'pendente' in status or 'atrasado' in status:
                        self.tree.selection_set(item)
                        self.tree.focus(item)
                        self.tree.see(item)
                        # Simular evento de seleção
                        fake_event = type('Event', (), {})()
                        self.on_mensalidade_select(fake_event)
                        break
        except Exception as e:
            print(f"⚠️ Erro ao focar próximo pendente: {e}")
    
    def cancelar_selecao(self):
        """Cancela seleção atual com limpeza completa"""
        try:
            self.tree.selection_remove(self.tree.selection())
            self.mensalidade_selecionada = None
            
            # Limpar informações
            for key, label in self.info_labels.items():
                if key == 'aluno':
                    label.config(text="Aluno: Nenhum selecionado", fg='black')
                elif key == 'status':
                    label.config(text="Status: -", fg='black')
                elif key == 'dias_atraso':
                    label.config(text="Dias em Atraso: -", fg='black')
                else:
                    label.config(text=f"{key.replace('_', ' ').title()}: -", fg='black')
            
            self.lbl_valor_original.config(text="R$ 0,00")
            self.lbl_valor_final.config(text="R$ 0,00", fg='black')
            
            # Limpar campos
            self.var_desconto.set('')
            self.var_multa.set('')
            self.var_outros.set('')
            
            # Limpar observações
            self.entry_observacoes.config(state='normal')
            self.entry_observacoes.delete(1.0, tk.END)
            self.entry_observacoes.config(state='disabled')
            
            # Desabilitar campos
            self.desabilitar_campos()
            
        except Exception as e:
            print(f"❌ Erro ao cancelar seleção: {e}")
    
    def atualizar_tudo(self):
        """Atualiza todos os dados e interface"""
        try:
            # Recarregar dados
            self.carregar_dados_iniciais()
            
            # Cancelar seleção
            self.cancelar_selecao()
            
            print("🔄 Interface atualizada completamente")
            
        except Exception as e:
            print(f"❌ Erro ao atualizar tudo: {e}")
            messagebox.showerror("Erro", f"Erro ao atualizar dados:\n{e}")
    
    def gerar_relatorio_avancado(self):
        """Gera relatório avançado baseado nos filtros atuais"""
        try:
            if not self.mensalidades_filtradas:
                messagebox.showwarning("Atenção", "Nenhuma mensalidade encontrada com os filtros atuais")
                return
            
            # Criar janela de relatório
            relatorio = tk.Toplevel(self.parent_frame)
            relatorio.title("📊 Relatório Financeiro Avançado")
            relatorio.geometry("900x700")
            relatorio.transient(self.parent_frame.winfo_toplevel())
            
            # Cabeçalho
            header = tk.Frame(relatorio, bg='#2c3e50')
            header.pack(fill=tk.X)
            
            tk.Label(
                header,
                text="📊 Relatório Financeiro Detalhado",
                font=('Arial', 18, 'bold'),
                bg='#2c3e50',
                fg='white'
            ).pack(pady=15)
            
            # Resumo executivo
            resumo_frame = tk.LabelFrame(relatorio, text="Resumo Executivo", font=('Arial', 12, 'bold'))
            resumo_frame.pack(fill=tk.X, padx=20, pady=10)
            
            dados = self.mensalidades_filtradas
            total_valor = sum(m.get('valor_final', 0) for m in dados)
            valor_pago = sum(m.get('valor_final', 0) for m in dados if 'pago' in m.get('status', '').lower())
            valor_pendente = total_valor - valor_pago
            
            resumo_text = f"""
📊 RESUMO GERAL:
• Total de Mensalidades: {len(dados)}
• Valor Total: {format_currency(total_valor)}
• Valor Arrecadado: {format_currency(valor_pago)}
• Valor Pendente: {format_currency(valor_pendente)}
• Taxa de Inadimplência: {((valor_pendente/total_valor)*100) if total_valor > 0 else 0:.1f}%

📈 DISTRIBUIÇÃO POR STATUS:
• Pagas: {len([m for m in dados if 'pago' in m.get('status', '').lower()])}
• Pendentes: {len([m for m in dados if 'pendente' in m.get('status', '').lower()])}
• Atrasadas: {len([m for m in dados if 'atrasado' in m.get('status', '').lower()])}
            """
            
            tk.Label(resumo_frame, text=resumo_text.strip(), font=('Arial', 10), 
                    justify=tk.LEFT, bg='white').pack(padx=10, pady=10)
            
            # Botão de exportar (futuro)
            tk.Button(
                relatorio,
                text="💾 Exportar Relatório",
                command=lambda: messagebox.showinfo("Info", "Exportação será implementada em breve"),
                font=('Arial', 12, 'bold'),
                bg='#27ae60',
                fg='white',
                padx=20,
                pady=10
            ).pack(pady=20)
            
        except Exception as e:
            print(f"❌ Erro ao gerar relatório: {e}")
            messagebox.showerror("Erro", f"Erro ao gerar relatório:\n{e}")
    
    def limpar_placeholder(self, event, placeholder_text):
        """Remove placeholder do campo"""
        if event.widget.get() == placeholder_text:
            event.widget.delete(0, tk.END)
    
    def setup_keyboard_shortcuts(self):
        """Configura atalhos de teclado otimizados"""
        try:
            # Bind Enter para processar pagamento
            def processar_com_enter(event):
                if self.btn_dar_baixa['state'] == 'normal':
                    self.dar_baixa_mensalidade()
            
            # Aplicar bind em campos
            if hasattr(self, 'entry_desconto'):
                self.entry_desconto.bind('<Return>', processar_com_enter)
                self.entry_multa.bind('<Return>', processar_com_enter)
                self.entry_outros.bind('<Return>', processar_com_enter)
            
            # Bind ESC para cancelar
            def cancelar_com_esc(event):
                self.cancelar_selecao()
            
            # Bind F5 para atualizar
            def atualizar_com_f5(event):
                self.atualizar_tudo()
            
            # Bind Ctrl+F para focar nos filtros
            def focar_filtros(event):
                # Focar no primeiro combo de filtros
                try:
                    for widget in self.parent_frame.winfo_children():
                        if isinstance(widget, ttk.Combobox):
                            widget.focus()
                            break
                except:
                    pass
            
            self.parent_frame.bind('<Escape>', cancelar_com_esc)
            self.parent_frame.bind('<F5>', atualizar_com_f5)
            self.parent_frame.bind('<Control-f>', focar_filtros)
            self.parent_frame.focus_set()
            
        except Exception as e:
            print(f"⚠️ Erro ao configurar atalhos: {e}")
    
    def mostrar_erro(self, mensagem):
        """Mostra tela de erro otimizada"""
        error_frame = tk.Frame(self.parent_frame, bg='white')
        error_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            error_frame,
            text="⚠️ Erro no Módulo Financeiro",
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
        
        tk.Button(
            error_frame,
            text="🔄 Tentar Novamente",
            command=lambda: [error_frame.destroy(), self.create_interface()],
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10
        ).pack(pady=20)
