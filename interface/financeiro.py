import tkinter as tk
from tkinter import ttk, messagebox
from services.financeiro_service import FinanceiroService
from utils.formatters import format_currency, format_date, parse_date, validate_date
from datetime import datetime, date
import re

class FinanceiroInterface:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.parent_frame.configure(bg='white')
        
        # Inicializar serviço com tratamento de erro
        try:
            self.financeiro_service = FinanceiroService()
            print("✅ FinanceiroService inicializado")
            self.create_interface()
            self.carregar_dados_iniciais()
        except Exception as e:
            print(f"❌ Erro ao inicializar financeiro: {e}")
            self.create_error_interface(str(e))
    
    def create_error_interface(self, error_msg):
        """Cria interface de erro"""
        error_frame = tk.Frame(self.parent_frame, bg='white')
        error_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            error_frame,
            text="⚠️ Erro no Módulo Financeiro",
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
            self.financeiro_service = FinanceiroService()
            self.create_interface()
            self.carregar_dados_iniciais()
        except Exception as e:
            self.create_error_interface(str(e))
    
    def create_interface(self):
        """Cria a interface completa do financeiro COM FILTROS"""
        # Container principal
        main_container = tk.Frame(self.parent_frame, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_frame = tk.Frame(main_container, bg='white')
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            title_frame,
            text="💰 Controle Financeiro",
            font=('Arial', 24, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(side=tk.LEFT)
        
        # Data atual
        data_atual = datetime.now().strftime("%d/%m/%Y - %H:%M")
        tk.Label(
            title_frame,
            text=f"📅 {data_atual}",
            font=('Arial', 12),
            bg='white',
            fg='#6c757d'
        ).pack(side=tk.RIGHT)
        
        # Cards de resumo
        self.create_cards_with_filters(main_container)
        
        # Seção de Filtros
        self.create_filter_section(main_container)
        
        # Tabela de mensalidades
        self.create_table_with_filters(main_container)
        
        # Ações
        self.create_action_buttons(main_container)
    
    def create_cards_with_filters(self, parent):
        """Cria cards de resumo que atualizam com filtros"""
        self.cards_frame = tk.Frame(parent, bg='white')
        self.cards_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.update_cards()
    
    def update_cards(self):
        """Atualiza cards com estatísticas"""
        # Limpar cards existentes
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        
        try:
            # Obter estatísticas baseadas nos filtros atuais
            filtros = self.get_current_filters()
            stats = self.financeiro_service.obter_estatisticas_financeiras()
            
            # Card 1: Receita do Mês
            self.create_card(
                self.cards_frame, "💰 Receita do Mês", 
                format_currency(stats.get('receita_mes', 0)), "#27ae60", 0, 0
            )
            
            # Card 2: Mensalidades Pagas
            self.create_card(
                self.cards_frame, "✅ Pagas", 
                str(stats.get('total_pagos', 0)), "#2ecc71", 0, 1
            )
            
            # Card 3: Mensalidades Pendentes
            self.create_card(
                self.cards_frame, "⏳ Pendentes", 
                str(stats.get('total_pendentes', 0)), "#3498db", 0, 2
            )
            
            # Card 4: Mensalidades Atrasadas
            self.create_card(
                self.cards_frame, "🔴 Atrasadas", 
                str(stats.get('total_atrasados', 0)), "#e74c3c", 0, 3
            )
            
            # Card 5: Valor em Aberto
            self.create_card(
                self.cards_frame, "💸 Em Aberto", 
                format_currency(stats.get('valor_pendente', 0) + stats.get('valor_atraso', 0)), "#f39c12", 0, 4
            )
            
        except Exception as e:
            print(f"Erro ao carregar estatísticas: {e}")
            # Cards com valores padrão
            self.create_card(self.cards_frame, "💰 Receita", "R$ 0,00", "#27ae60", 0, 0)
            self.create_card(self.cards_frame, "✅ Pagas", "0", "#2ecc71", 0, 1)
            self.create_card(self.cards_frame, "⏳ Pendentes", "0", "#3498db", 0, 2)
            self.create_card(self.cards_frame, "🔴 Atrasadas", "0", "#e74c3c", 0, 3)
        
        # Configurar grid
        for i in range(5):
            self.cards_frame.columnconfigure(i, weight=1)
    
    def create_card(self, parent, title, value, color, row, col):
        """Cria um card de estatística"""
        card = tk.Frame(parent, bg=color, relief='raised', bd=2)
        card.grid(row=row, column=col, padx=5, pady=5, sticky='ew', ipady=15)
        
        tk.Label(card, text=title, font=('Arial', 9, 'bold'), 
                bg=color, fg='white').pack(pady=3)
        tk.Label(card, text=value, font=('Arial', 12, 'bold'), 
                bg=color, fg='white').pack(pady=3)
    
    def create_filter_section(self, parent):
        """Cria seção de filtros avançados"""
        filter_frame = tk.LabelFrame(
            parent,
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
        
        # Linha 1: Status e Turma
        row1_frame = tk.Frame(filter_content, bg='white')
        row1_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Filtro por Status
        tk.Label(row1_frame, text="Status:", 
                font=('Arial', 10, 'bold'),
                bg='white', 
                fg='#2c3e50').pack(side=tk.LEFT)
        
        self.filtro_status_var = tk.StringVar(value="Todos")
        self.filtro_status_combo = ttk.Combobox(
            row1_frame, textvariable=self.filtro_status_var, 
            values=['Todos', 'Pendente', 'Pago', 'Atrasado'],
            width=12, state='readonly'
        )
        self.filtro_status_combo.pack(side=tk.LEFT, padx=(10, 20))
        
        # Filtro por Turma
        tk.Label(row1_frame, text="Turma:", 
                font=('Arial', 10, 'bold'),
                bg='white', 
                fg='#2c3e50').pack(side=tk.LEFT)
        
        self.filtro_turma_var = tk.StringVar(value="Todas")
        self.filtro_turma_combo = ttk.Combobox(
            row1_frame, textvariable=self.filtro_turma_var, 
            width=25, state='readonly'
        )
        self.filtro_turma_combo.pack(side=tk.LEFT, padx=(10, 20))
        
        # Linha 2: Período
        row2_frame = tk.Frame(filter_content, bg='white')
        row2_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Filtro por Mês/Ano
        tk.Label(row2_frame, text="Mês/Ano:", 
                font=('Arial', 10, 'bold'),
                bg='white', 
                fg='#2c3e50').pack(side=tk.LEFT)
        
        self.filtro_mes_var = tk.StringVar(value="Todos")
        self.filtro_mes_combo = ttk.Combobox(
            row2_frame, textvariable=self.filtro_mes_var, 
            width=12, state='readonly'
        )
        self.filtro_mes_combo.pack(side=tk.LEFT, padx=(10, 20))
        
        # Filtro por Aluno (busca)
        tk.Label(row2_frame, text="Aluno:", 
                font=('Arial', 10, 'bold'),
                bg='white', 
                fg='#2c3e50').pack(side=tk.LEFT)
        
        self.filtro_aluno_var = tk.StringVar()
        aluno_entry = tk.Entry(row2_frame, textvariable=self.filtro_aluno_var, 
                              width=20, font=('Arial', 10))
        aluno_entry.pack(side=tk.LEFT, padx=(10, 20))
        aluno_entry.bind('<KeyRelease>', lambda e: self.aplicar_filtros())
        
        # Linha 3: Botões de Filtro
        row3_frame = tk.Frame(filter_content, bg='white')
        row3_frame.pack(fill=tk.X)
        
        tk.Button(
            row3_frame, text="🔍 Aplicar Filtros", command=self.aplicar_filtros,
            font=('Arial', 10, 'bold'), bg='#007bff',
            fg='white', padx=15, pady=5, relief='flat', cursor='hand2'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            row3_frame, text="🔄 Limpar Filtros", command=self.limpar_filtros,
            font=('Arial', 10, 'bold'), bg='#6c757d',
            fg='white', padx=15, pady=5, relief='flat', cursor='hand2'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Contador de resultados
        self.resultado_label = tk.Label(
            row3_frame, text="", font=('Arial', 10),
            bg='white', fg='#17a2b8'
        )
        self.resultado_label.pack(side=tk.RIGHT)
        
        # Carregar dados dos filtros
        self.carregar_dados_filtros()
    
    def carregar_dados_filtros(self):
        """Carrega dados para os filtros"""
        try:
            # Carregar turmas
            turmas = self.financeiro_service.listar_turmas()
            valores_turmas = ["Todas"] + [turma['display'] for turma in turmas]
            self.filtro_turma_combo['values'] = valores_turmas
            
            # Carregar meses (últimos 12 meses + atual)
            hoje = date.today()
            meses = ["Todos"]
            
            for i in range(12):
                if i == 0:
                    mes_ano = hoje.strftime("%Y-%m")
                    display = hoje.strftime("Atual (%m/%Y)")
                else:
                    data_mes = date(hoje.year, hoje.month, 1)
                    # Calcular mês anterior
                    if data_mes.month == 1:
                        data_mes = date(data_mes.year - 1, 12, 1)
                    else:
                        data_mes = date(data_mes.year, data_mes.month - 1, 1)
                    
                    for _ in range(i - 1):
                        if data_mes.month == 1:
                            data_mes = date(data_mes.year - 1, 12, 1)
                        else:
                            data_mes = date(data_mes.year, data_mes.month - 1, 1)
                    
                    mes_ano = data_mes.strftime("%Y-%m")
                    display = data_mes.strftime("%m/%Y")
                
                meses.append(f"{display}|{mes_ano}")
            
            self.filtro_mes_combo['values'] = meses
            
        except Exception as e:
            print(f"Erro ao carregar dados dos filtros: {e}")
    
    def create_table_with_filters(self, parent):
        """Cria tabela que responde aos filtros"""
        table_frame = tk.LabelFrame(
            parent,
            text="  📋 Mensalidades  ",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Container da tabela
        tree_container = tk.Frame(table_frame, bg='white')
        tree_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview
        columns = ('ID', 'Aluno', 'Turma', 'Mês/Ano', 'Valor', 'Vencimento', 'Pagamento', 'Status')
        self.tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=12)
        
        # Configurar colunas
        column_widths = {
            'ID': 50, 'Aluno': 180, 'Turma': 120, 'Mês/Ano': 80, 
            'Valor': 100, 'Vencimento': 100, 'Pagamento': 100, 'Status': 100
        }
        
        for col in columns:
            self.tree.heading(col, text=col, anchor='center')
            self.tree.column(col, width=column_widths[col], anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Posicionar
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Configurar cores por status
        self.tree.tag_configure('pago', background='#d5f4e6')
        self.tree.tag_configure('pendente', background='#fff3cd')
        self.tree.tag_configure('atrasado', background='#f8d7da')
        
        # Bind duplo clique
        self.tree.bind('<Double-1>', lambda e: self.registrar_pagamento())
        
        # Bind mudança de seleção
        self.tree.bind('<<TreeviewSelect>>', self.on_select_mensalidade)
    
    def on_select_mensalidade(self, event=None):
        """Evento quando seleciona uma mensalidade"""
        # Pode ser usado para mostrar detalhes ou habilitar botões
        pass
    
    def get_current_filters(self):
        """Obtém filtros atuais"""
        filtros = {}
        
        # Filtro de status
        status = self.filtro_status_var.get()
        if status and status != 'Todos':
            filtros['status'] = status
        
        # Filtro de turma
        turma = self.filtro_turma_var.get()
        if turma and turma != 'Todas':
            # Encontrar ID da turma
            try:
                turmas = self.financeiro_service.listar_turmas()
                for t in turmas:
                    if t['display'] == turma:
                        filtros['turma_id'] = t['id']
                        break
            except:
                pass
        
        # Filtro de mês
        mes = self.filtro_mes_var.get()
        if mes and mes != 'Todos' and '|' in mes:
            mes_ano = mes.split('|')[1]
            filtros['mes_ano'] = mes_ano
        
        # Filtro de aluno (busca por nome)
        aluno = self.filtro_aluno_var.get().strip()
        if aluno:
            filtros['aluno_nome'] = aluno
        
        return filtros
    
    def aplicar_filtros(self):
        """Aplica filtros e recarrega dados"""
        try:
            filtros = self.get_current_filters()
            self.carregar_mensalidades(filtros)
            self.update_cards()
        except Exception as e:
            print(f"Erro ao aplicar filtros: {e}")
            messagebox.showerror("Erro", f"Erro ao aplicar filtros: {str(e)}")
    
    def limpar_filtros(self):
        """Limpa todos os filtros"""
        self.filtro_status_var.set("Todos")
        self.filtro_turma_var.set("Todas")
        self.filtro_mes_var.set("Todos")
        self.filtro_aluno_var.set("")
        self.aplicar_filtros()
    
    def create_action_buttons(self, parent):
        """Cria botões de ação"""
        action_frame = tk.Frame(parent, bg='white')
        action_frame.pack(fill=tk.X)
        
        # Separador
        separator = tk.Frame(action_frame, height=2, bg='#dee2e6')
        separator.pack(fill=tk.X, pady=(0, 15))
        
        # Título
        tk.Label(
            action_frame, text="⚡ Ações Rápidas", 
            font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50'
        ).pack(pady=(0, 10))
        
        # Botões
        buttons_frame = tk.Frame(action_frame, bg='white')
        buttons_frame.pack()
        
        tk.Button(
            buttons_frame, text="💳 Registrar Pagamento", 
            command=self.registrar_pagamento,
            bg='#27ae60', fg='white', font=('Arial', 10, 'bold'),
            padx=15, pady=8, relief='flat', cursor='hand2'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            buttons_frame, text="❌ Cancelar Pagamento", 
            command=self.cancelar_pagamento,
            bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'),
            padx=15, pady=8, relief='flat', cursor='hand2'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            buttons_frame, text="📊 Inadimplentes", 
            command=self.mostrar_inadimplentes,
            bg='#e67e22', fg='white', font=('Arial', 10, 'bold'),
            padx=15, pady=8, relief='flat', cursor='hand2'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            buttons_frame, text="📄 Exportar", 
            command=self.exportar_dados,
            bg='#6f42c1', fg='white', font=('Arial', 10, 'bold'),
            padx=15, pady=8, relief='flat', cursor='hand2'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            buttons_frame, text="🔄 Atualizar", 
            command=self.carregar_dados_iniciais,
            bg='#3498db', fg='white', font=('Arial', 10, 'bold'),
            padx=15, pady=8, relief='flat', cursor='hand2'
        ).pack(side=tk.LEFT)
    
    def carregar_dados_iniciais(self):
        """Carrega dados iniciais"""
        try:
            print("📋 Carregando mensalidades...")
            self.carregar_mensalidades()
            self.update_cards()
            print("✅ Dados carregados com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
    
    def carregar_mensalidades(self, filtros=None):
        """Carrega mensalidades na tabela com filtros aplicados"""
        try:
            # Limpar tabela
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Carregar mensalidades com filtros
            mensalidades = self.financeiro_service.listar_mensalidades(filtros)
            
            # Aplicar filtro de nome do aluno (client-side)
            if filtros and filtros.get('aluno_nome'):
                nome_filtro = filtros['aluno_nome'].lower()
                mensalidades = [m for m in mensalidades if nome_filtro in m.get('aluno_nome', '').lower()]
            
            print(f"📋 Carregando {len(mensalidades)} mensalidades...")
            
            contador_status = {'Pendente': 0, 'Pago': 0, 'Atrasado': 0}
            
            for m in mensalidades:
                # Determinar status e cor
                status = m.get('status_calculado', m.get('status', 'Pendente'))
                contador_status[status] = contador_status.get(status, 0) + 1
                
                if status == 'Pago':
                    tag = 'pago'
                    status_display = '✅ Pago'
                elif status == 'Atrasado':
                    tag = 'atrasado' 
                    status_display = '🔴 Atrasado'
                else:
                    tag = 'pendente'
                    status_display = '⏳ Pendente'
                
                # Formatar dados para exibição
                valores = (
                    m.get('id', ''),
                    m.get('aluno_nome', '')[:20] + "..." if len(m.get('aluno_nome', '')) > 20 else m.get('aluno_nome', ''),
                    f"{m.get('turma_nome', '')} - {m.get('turma_serie', '')}"[:15] + "..." if len(f"{m.get('turma_nome', '')} - {m.get('turma_serie', '')}") > 15 else f"{m.get('turma_nome', '')} - {m.get('turma_serie', '')}",
                    m.get('mes_referencia', '').replace('-', '/') if m.get('mes_referencia') else '',
                    format_currency(m.get('valor_final', 0)),
                    format_date(m.get('data_vencimento', '')),
                    format_date(m.get('data_pagamento', '')) if m.get('data_pagamento') else '-',
                    status_display
                )
                
                self.tree.insert('', tk.END, values=valores, tags=(tag,))
            
            # Atualizar contador de resultados
            total = len(mensalidades)
            resultado_text = f"📊 {total} mensalidades"
            if total > 0:
                detalhes = []
                for status, count in contador_status.items():
                    if count > 0:
                        detalhes.append(f"{count} {status.lower()}")
                if detalhes:
                    resultado_text += f" ({', '.join(detalhes)})"
            
            self.resultado_label.config(text=resultado_text)
            
            print(f"✅ {len(mensalidades)} mensalidades carregadas")
            
        except Exception as e:
            print(f"❌ Erro ao carregar mensalidades: {e}")
            self.resultado_label.config(text="❌ Erro ao carregar dados")
            messagebox.showerror("Erro", f"Erro ao carregar mensalidades:\n{str(e)}")
    
    def registrar_pagamento(self):
        """Registra pagamento simples"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma mensalidade!")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        if '✅ Pago' in str(values[7]):
            messagebox.showinfo("Informação", "Mensalidade já está paga!")
            return
        
        # Janela simples de confirmação
        if messagebox.askyesno("Confirmar Pagamento", 
                              f"Confirmar pagamento de {values[4]} do aluno {values[1]}?\n"
                              f"Mês: {values[3]}\n"
                              f"Vencimento: {values[5]}"):
            
            try:
                resultado = self.financeiro_service.registrar_pagamento(
                    values[0],  # ID
                    date.today().strftime('%Y-%m-%d'),  # Data de hoje
                    None,  # Valor padrão
                    0,  # Sem desconto
                    0,  # Sem multa
                    "Pagamento registrado manualmente"
                )
                
                if resultado['success']:
                    messagebox.showinfo("Sucesso", "✅ Pagamento registrado!")
                    self.aplicar_filtros()  # Recarregar com filtros
                else:
                    messagebox.showerror("Erro", f"❌ Erro: {resultado['error']}")
                    
            except Exception as e:
                messagebox.showerror("Erro", f"❌ Erro inesperado: {str(e)}")
    
    def cancelar_pagamento(self):
        """Cancela pagamento"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma mensalidade!")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        if '✅ Pago' not in str(values[7]):
            messagebox.showinfo("Informação", "Mensalidade não está paga!")
            return
        
        if messagebox.askyesno("Confirmar", 
                              f"Cancelar pagamento de {values[4]} do aluno {values[1]}?\n"
                              f"Mês: {values[3]}"):
            
            try:
                resultado = self.financeiro_service.cancelar_pagamento(values[0])
                
                if resultado['success']:
                    messagebox.showinfo("Sucesso", "✅ Pagamento cancelado!")
                    self.aplicar_filtros()  # Recarregar com filtros
                else:
                    messagebox.showerror("Erro", f"❌ Erro: {resultado['error']}")
                    
            except Exception as e:
                messagebox.showerror("Erro", f"❌ Erro inesperado: {str(e)}")
    
    def mostrar_inadimplentes(self):
        """Mostra lista de inadimplentes"""
        try:
            inadimplentes = self.financeiro_service.buscar_inadimplentes()
            
            # Criar janela
            inad_window = tk.Toplevel()
            inad_window.title("📋 Relatório de Inadimplência")
            inad_window.geometry("900x600")
            inad_window.configure(bg='white')
            
            tk.Label(
                inad_window, text=f"📋 Relatório de Inadimplência - {len(inadimplentes)} aluno(s)",
                font=('Arial', 14, 'bold'), bg='white', fg='#e74c3c'
            ).pack(pady=20)
            
            if not inadimplentes:
                tk.Label(
                    inad_window, text="✅ Parabéns! Não há inadimplentes!",
                    font=('Arial', 12), bg='white', fg='#27ae60'
                ).pack(expand=True)
            else:
                # Criar treeview para inadimplentes
                tree_frame = tk.Frame(inad_window, bg='white')
                tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
                
                columns = ('Aluno', 'Turma', 'Mensalidades', 'Valor Devido', 'Telefone')
                inad_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
                
                # Configurar colunas
                inad_tree.heading('Aluno', text='Aluno')
                inad_tree.heading('Turma', text='Turma')
                inad_tree.heading('Mensalidades', text='Mens. Atrasadas')
                inad_tree.heading('Valor Devido', text='Valor Devido')
                inad_tree.heading('Telefone', text='Telefone')
                
                inad_tree.column('Aluno', width=200)
                inad_tree.column('Turma', width=150)
                inad_tree.column('Mensalidades', width=120)
                inad_tree.column('Valor Devido', width=120)
                inad_tree.column('Telefone', width=120)
                
                # Scrollbar
                inad_scroll = ttk.Scrollbar(tree_frame, orient='vertical', command=inad_tree.yview)
                inad_tree.configure(yscrollcommand=inad_scroll.set)
                
                inad_tree.pack(side='left', fill='both', expand=True)
                inad_scroll.pack(side='right', fill='y')
                
                # Adicionar dados
                total_devido = 0
                for inad in inadimplentes:
                    valores = (
                        inad['aluno_nome'],
                        inad['turma_nome'],
                        str(inad['mensalidades_atrasadas']),
                        format_currency(inad['valor_total_devido']),
                        inad['responsavel_telefone']
                    )
                    inad_tree.insert('', tk.END, values=valores)
                    total_devido += inad['valor_total_devido']
                
                # Total
                total_frame = tk.Frame(inad_window, bg='white')
                total_frame.pack(fill=tk.X, padx=20, pady=10)
                
                tk.Label(
                    total_frame, 
                    text=f"💰 Total em atraso: {format_currency(total_devido)}",
                    font=('Arial', 12, 'bold'), bg='white', fg='#e74c3c'
                ).pack()
            
            tk.Button(
                inad_window, text="Fechar", command=inad_window.destroy,
                bg='#6c757d', fg='white', font=('Arial', 11, 'bold'),
                padx=20, pady=8
            ).pack(pady=20)
            
        except Exception as e:
            messagebox.showerror("Erro", f"❌ Erro ao buscar inadimplentes: {str(e)}")
    
    def exportar_dados(self):
        """Exporta dados filtrados para CSV"""
        try:
            filtros = self.get_current_filters()
            mensalidades = self.financeiro_service.listar_mensalidades(filtros)
            
            if not mensalidades:
                messagebox.showwarning("Aviso", "Nenhum dado para exportar!")
                return
            
            # Criar nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mensalidades_{timestamp}.csv"
            
            # Exportar usando execute_python
            from services.export_service import ExportService
            export_service = ExportService()
            resultado = export_service.exportar_mensalidades_csv(mensalidades, filename)
            
            if resultado['success']:
                messagebox.showinfo("Sucesso", f"✅ Dados exportados para: {filename}")
            else:
                messagebox.showerror("Erro", f"❌ Erro na exportação: {resultado['error']}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"❌ Erro ao exportar: {str(e)}")