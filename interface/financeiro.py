import tkinter as tk
from tkinter import ttk, messagebox
from services.financeiro_service import FinanceiroService
from utils.formatters import format_date, format_currency
from datetime import date, datetime
import calendar

class FinanceiroInterface:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.parent_frame.configure(bg='white')
        self.financeiro_service = FinanceiroService()
        
        try:
            self.create_interface()
            self.aplicar_filtros()
        except Exception as e:
            print(f"Erro ao criar interface financeira: {e}")
            self.show_error_interface(str(e))
    
    def show_error_interface(self, error_msg):
        """Interface de erro"""
        error_frame = tk.Frame(self.parent_frame, bg='white')
        error_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            error_frame,
            text="⚠️ Erro na Interface Financeira",
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
    
    def create_interface(self):
        """Cria interface completa do financeiro"""
        # Container principal
        main_container = tk.Frame(self.parent_frame, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(
            main_container,
            text="💰 Controle Financeiro",
            font=('Arial', 24, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 30))
        
        # Cards de estatísticas
        self.create_stats_cards(main_container)
        
        # Container para filtros e tabela
        content_frame = tk.Frame(main_container, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Filtros
        self.create_filtros_section(content_frame)
        
        # Mensalidades
        self.create_mensalidades_section(content_frame)
    
    def create_stats_cards(self, parent):
        """Cria cards com estatísticas financeiras"""
        stats_frame = tk.Frame(parent, bg='white')
        stats_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Obter estatísticas
        stats = self.financeiro_service.obter_estatisticas_financeiras()
        
        cards_data = [
            {
                'title': 'Receita do Mês',
                'value': format_currency(stats.get('receita_mes', 0)),
                'color': '#28a745',
                'icon': '💰'
            },
            {
                'title': 'Inadimplentes',
                'value': str(stats.get('total_inadimplentes', 0)),
                'color': '#dc3545',
                'icon': '⚠️'
            },
            {
                'title': 'Em Atraso',
                'value': format_currency(stats.get('valor_em_atraso', 0)),
                'color': '#fd7e14',
                'icon': '📅'
            }
        ]
        
        for i, card_data in enumerate(cards_data):
            card = tk.Frame(stats_frame, bg=card_data['color'], relief='flat', bd=0)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10) if i < len(cards_data)-1 else 0)
            
            # Conteúdo do card
            content = tk.Frame(card, bg=card_data['color'])
            content.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
            
            tk.Label(
                content,
                text=card_data['icon'],
                font=('Arial', 24),
                bg=card_data['color'],
                fg='white'
            ).pack()
            
            tk.Label(
                content,
                text=card_data['title'],
                font=('Arial', 11, 'bold'),
                bg=card_data['color'],
                fg='white'
            ).pack()
            
            tk.Label(
                content,
                text=card_data['value'],
                font=('Arial', 16, 'bold'),
                bg=card_data['color'],
                fg='white'
            ).pack()
    
    def create_filtros_section(self, parent):
        """Seção de filtros"""
        filtros_frame = tk.LabelFrame(
            parent,
            text="  🔍 Filtros  ",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        filtros_frame.pack(fill=tk.X, pady=(0, 20))
        
        filter_content = tk.Frame(filtros_frame, bg='white')
        filter_content.pack(fill=tk.X, padx=20, pady=15)
        
        # Primeira linha de filtros
        row1 = tk.Frame(filter_content, bg='white')
        row1.pack(fill=tk.X, pady=(0, 10))
        
        # Status
        tk.Label(row1, text="Status:", font=('Arial', 10, 'bold'),
                bg='white', fg='#2c3e50').pack(side=tk.LEFT)
        
        self.status_var = tk.StringVar(value="Todos")
        status_combo = ttk.Combobox(row1, textvariable=self.status_var, 
                                   values=['Todos', 'Pendente', 'Pago', 'Atrasado'], 
                                   width=12, state='readonly')
        status_combo.pack(side=tk.LEFT, padx=(10, 20))
        
        # Mês/Ano
        tk.Label(row1, text="Mês/Ano:", font=('Arial', 10, 'bold'),
                bg='white', fg='#2c3e50').pack(side=tk.LEFT)
        
        self.mes_ano_var = tk.StringVar(value="Todos")
        mes_ano_values = self.gerar_opcoes_mes_ano()
        mes_ano_combo = ttk.Combobox(row1, textvariable=self.mes_ano_var,
                                    values=mes_ano_values, width=12, state='readonly')
        mes_ano_combo.pack(side=tk.LEFT, padx=(10, 20))
        
        # Turma
        tk.Label(row1, text="Turma:", font=('Arial', 10, 'bold'),
                bg='white', fg='#2c3e50').pack(side=tk.LEFT)
        
        self.turma_var = tk.StringVar(value="Todas")
        self.turma_combo = ttk.Combobox(row1, textvariable=self.turma_var,
                                       width=20, state='readonly')
        self.turma_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Botões
        btn_frame = tk.Frame(filter_content, bg='white')
        btn_frame.pack(fill=tk.X)
        
        filtrar_btn = tk.Button(
            btn_frame, text="🔍 Aplicar Filtros", command=self.aplicar_filtros,
            font=('Arial', 11, 'bold'), bg='#007bff',
            fg='white', padx=20, pady=8, relief='flat', cursor='hand2'
        )
        filtrar_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        limpar_btn = tk.Button(
            btn_frame, text="🔄 Limpar Filtros", command=self.limpar_filtros,
            font=('Arial', 11, 'bold'), bg='#6c757d',
            fg='white', padx=20, pady=8, relief='flat', cursor='hand2'
        )
        limpar_btn.pack(side=tk.LEFT)
        
        # Carregar turmas
        self.carregar_turmas_filtro()
    
    def create_mensalidades_section(self, parent):
        """Seção de mensalidades com botão de pagamento"""
        mensalidades_frame = tk.LabelFrame(
            parent,
            text="  📋 Mensalidades  ",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        mensalidades_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        table_content = tk.Frame(mensalidades_frame, bg='white')
        table_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Treeview
        columns = ('ID', 'Aluno', 'Turma', 'Mês/Ano', 'Valor', 'Vencimento', 'Pagamento', 'Status')
        self.tree = ttk.Treeview(table_content, columns=columns, show='headings', height=15)
        
        # Configurar colunas
        column_widths = {'ID': 50, 'Aluno': 150, 'Turma': 120, 'Mês/Ano': 80, 
                        'Valor': 100, 'Vencimento': 100, 'Pagamento': 100, 'Status': 100}
        
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
        action_frame = tk.Frame(mensalidades_frame, bg='white')
        action_frame.pack(fill=tk.X, padx=20, pady=(10, 15))
        
        separator = tk.Frame(action_frame, height=2, bg='#dee2e6')
        separator.pack(fill=tk.X, pady=(0, 15))
        
        # Botão principal para registrar pagamento
        registrar_btn = tk.Button(
            action_frame, 
            text="💳 Registrar Pagamento", 
            command=self.registrar_pagamento,
            font=('Arial', 12, 'bold'), 
            bg='#28a745',
            fg='white', 
            padx=25, 
            pady=10, 
            relief='flat', 
            cursor='hand2'
        )
        registrar_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # Outros botões
        cancelar_btn = tk.Button(
            action_frame, 
            text="❌ Cancelar Pagamento", 
            command=self.cancelar_pagamento,
            font=('Arial', 11, 'bold'), 
            bg='#dc3545',
            fg='white', 
            padx=20, 
            pady=8, 
            relief='flat', 
            cursor='hand2'
        )
        cancelar_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        atualizar_btn = tk.Button(
            action_frame, 
            text="🔄 Atualizar", 
            command=self.aplicar_filtros,
            font=('Arial', 11, 'bold'), 
            bg='#6c757d',
            fg='white', 
            padx=20, 
            pady=8, 
            relief='flat', 
            cursor='hand2'
        )
        atualizar_btn.pack(side=tk.LEFT)
        
        # Bind duplo clique para abrir pagamento
        self.tree.bind('<Double-1>', lambda e: self.registrar_pagamento())
    
    def gerar_opcoes_mes_ano(self):
        """Gera opções de mês/ano para o filtro"""
        opcoes = ["Todos"]
        ano_atual = date.today().year
        
        # Adicionar meses do ano atual e anterior
        for ano in [ano_atual - 1, ano_atual, ano_atual + 1]:
            for mes in range(1, 13):
                opcoes.append(f"{ano}-{mes:02d}")
        
        return opcoes
    
    def carregar_turmas_filtro(self):
        """Carrega turmas no filtro"""
        try:
            turmas = self.financeiro_service.listar_turmas()
            valores = ["Todas"] + [turma['display'] for turma in turmas]
            self.turma_combo['values'] = valores
            self.turmas_map = {turma['display']: turma['id'] for turma in turmas}
            self.turmas_map["Todas"] = None
        except Exception as e:
            print(f"Erro ao carregar turmas para filtro: {e}")
    
    def aplicar_filtros(self):
        """Aplica filtros e atualiza tabela"""
        try:
            filtros = {}
            
            # Status
            if self.status_var.get() != "Todos":
                filtros['status'] = self.status_var.get()
            
            # Mês/Ano
            if self.mes_ano_var.get() != "Todos":
                filtros['mes_ano'] = self.mes_ano_var.get()
            
            # Turma
            if self.turma_var.get() != "Todas":
                filtros['turma_id'] = self.turmas_map.get(self.turma_var.get())
            
            # Buscar mensalidades
            mensalidades = self.financeiro_service.listar_mensalidades(filtros)
            
            # Limpar tabela
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Preencher tabela
            for msg in mensalidades:
                status_display = self.formatar_status_display(msg['status'], msg['status_calculado'])
                
                valores = (
                    msg['id'],
                    msg['aluno_nome'][:20] + "..." if len(msg['aluno_nome']) > 20 else msg['aluno_nome'],
                    f"{msg['turma_nome']} - {msg['turma_serie']}",
                    msg['mes_referencia'].replace('-', '/'),
                    format_currency(msg['valor_final']),
                    format_date(msg['data_vencimento']),
                    format_date(msg['data_pagamento']) if msg['data_pagamento'] else '-',
                    status_display
                )
                
                # Definir tag baseada no status
                tag = ''
                if 'Pago' in status_display:
                    tag = 'pago'
                elif 'Atrasado' in status_display:
                    tag = 'atrasado'
                elif 'Pendente' in status_display:
                    tag = 'pendente'
                
                self.tree.insert('', tk.END, values=valores, tags=(tag,))
            
            # Configurar cores das tags
            self.tree.tag_configure('pago', background='#d4edda')
            self.tree.tag_configure('atrasado', background='#f8d7da')
            self.tree.tag_configure('pendente', background='#fff3cd')
            
            print(f"✅ {len(mensalidades)} mensalidades carregadas")
            
        except Exception as e:
            print(f"Erro ao aplicar filtros: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar mensalidades: {str(e)}")
    
    def formatar_status_display(self, status_db, status_calculado):
        """Formata status para exibição"""
        if status_db == 'Pago':
            return '✅ Pago'
        elif status_calculado == 'Atrasado' or status_db == 'Atrasado':
            return '🔴 Atrasado'
        else:
            return '🟡 Pendente'
    
    def limpar_filtros(self):
        """Limpa todos os filtros"""
        self.status_var.set("Todos")
        self.mes_ano_var.set("Todos")
        self.turma_var.set("Todas")
        self.aplicar_filtros()
    
    def registrar_pagamento(self):
        """Abre dialog para registrar pagamento com desconto e multa"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma mensalidade para registrar o pagamento!")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        # Verificar se já está pago
        status = str(values[7]).lower()
        if 'pago' in status or '✅' in status:
            messagebox.showinfo("Informação", "Esta mensalidade já está paga!")
            return
        
        try:
            # Buscar dados completos da mensalidade
            mensalidade_id = values[0]
            mensalidade_data = self.financeiro_service.buscar_mensalidade_por_id(mensalidade_id)
            
            if not mensalidade_data:
                messagebox.showerror("Erro", "Mensalidade não encontrada!")
                return
            
            # Importar e abrir dialog
            from interface.pagamento_dialog import PagamentoDialog
            
            def callback_pagamento(dados_pagamento):
                """Callback executado quando pagamento é confirmado"""
                resultado = self.financeiro_service.processar_pagamento(dados_pagamento)
                
                if resultado['success']:
                    messagebox.showinfo("Sucesso", "✅ Pagamento registrado com sucesso!")
                    self.aplicar_filtros()  # Recarregar dados
                else:
                    messagebox.showerror("Erro", f"❌ Erro ao processar pagamento:\n{resultado['error']}")
            
            # Abrir dialog
            PagamentoDialog(self.parent_frame, mensalidade_data, callback_pagamento)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir registro de pagamento:\n{str(e)}")
    
    def cancelar_pagamento(self):
        """Cancela um pagamento já registrado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma mensalidade!")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        # Verificar se está pago
        status = str(values[7]).lower()
        if 'pago' not in status and '✅' not in status:
            messagebox.showinfo("Informação", "Esta mensalidade não está paga!")
            return
        
        mensalidade_id = values[0]
        aluno_nome = values[1]
        mes_ano = values[3]
        
        if messagebox.askyesno("Confirmar", f"Cancelar pagamento de {aluno_nome}\nreferente a {mes_ano}?"):
            resultado = self.financeiro_service.cancelar_pagamento(mensalidade_id)
            
            if resultado['success']:
                messagebox.showinfo("Sucesso", "✅ Pagamento cancelado!")
                self.aplicar_filtros()
            else:
                messagebox.showerror("Erro", f"❌ Erro: {resultado['error']}")
