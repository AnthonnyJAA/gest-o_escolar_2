import tkinter as tk
from tkinter import ttk, messagebox
from services.dashboard_service import DashboardService
from utils.formatters import format_currency
from datetime import datetime
import matplotlib
matplotlib.use('TkAgg')  # Configurar backend antes de importar pyplot
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

# Configurar estilo do matplotlib
plt.style.use('default')
plt.rcParams['font.size'] = 9
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['axes.labelsize'] = 9
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8

class DashboardInterface:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.parent_frame.configure(bg='white')
        self.dashboard_service = DashboardService()
        self.graficos_canvas = {}  # Armazenar referências dos canvas
        
        try:
            self.create_interface()
            self.carregar_dados()
        except Exception as e:
            print(f"Erro ao criar interface do dashboard: {e}")
            self.create_error_interface(str(e))

    def create_error_interface(self, error_msg):
        """Interface de erro simplificada"""
        error_frame = tk.Frame(self.parent_frame, bg='white')
        error_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            error_frame,
            text="⚠️ Erro no Dashboard",
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
        """Cria a interface do dashboard com gráficos interativos"""
        # Container principal com scroll
        canvas = tk.Canvas(self.parent_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.parent_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='white')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel para scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Container principal dentro do scroll
        main_container = tk.Frame(self.scrollable_frame, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título do dashboard
        self.create_header(main_container)

        # Cards de estatísticas (mais compactos)
        self.create_stats_cards(main_container)

        # Área dos gráficos
        self.create_charts_area(main_container)

        # Área de ações rápidas (mais compacta)
        self.create_quick_actions(main_container)

    def create_header(self, parent):
        """Cria o cabeçalho do dashboard"""
        header_frame = tk.Frame(parent, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # Título
        tk.Label(
            header_frame,
            text="📊 Dashboard Interativo",
            font=('Arial', 24, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(side=tk.LEFT)

        # Data atual e botão de atualização
        controls_frame = tk.Frame(header_frame, bg='white')
        controls_frame.pack(side=tk.RIGHT)

        data_atual = datetime.now().strftime("%d/%m/%Y - %H:%M")
        tk.Label(
            controls_frame,
            text=f"📅 {data_atual}",
            font=('Arial', 11),
            bg='white',
            fg='#6c757d'
        ).pack(side=tk.TOP, anchor='e')

        # Botão de atualização
        tk.Button(
            controls_frame,
            text="🔄 Atualizar",
            command=self.atualizar_dashboard,
            font=('Arial', 10, 'bold'),
            bg='#007bff',
            fg='white',
            padx=15,
            pady=5,
            relief='flat',
            cursor='hand2'
        ).pack(side=tk.TOP, anchor='e', pady=(5, 0))

    def create_stats_cards(self, parent):
        """Cria cards de estatísticas mais compactos"""
        stats_frame = tk.Frame(parent, bg='white')
        stats_frame.pack(fill=tk.X, pady=(0, 20))

        # Configurar grid
        for i in range(5):
            stats_frame.columnconfigure(i, weight=1)

    def create_stat_card(self, parent, icon, value, label, color, row, col):
        """Cria um card de estatística compacto"""
        card = tk.Frame(parent, bg=color, relief='flat', bd=0)
        card.grid(row=row, column=col, padx=8, pady=8, sticky='ew', ipady=15)

        # Container interno
        card_content = tk.Frame(card, bg=color)
        card_content.pack(expand=True)

        # Ícone
        tk.Label(
            card_content, text=icon, font=('Arial', 20),
            bg=color, fg='white'
        ).pack(pady=(8, 3))

        # Valor
        tk.Label(
            card_content, text=value, font=('Arial', 16, 'bold'),
            bg=color, fg='white'
        ).pack()

        # Label
        tk.Label(
            card_content, text=label, font=('Arial', 9),
            bg=color, fg='white', wraplength=100
        ).pack(pady=(3, 8))

    def create_charts_area(self, parent):
        """Cria área dos gráficos interativos"""
        charts_frame = tk.LabelFrame(
            parent,
            text=" 📈 Gráficos Interativos ",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        charts_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        charts_content = tk.Frame(charts_frame, bg='white')
        charts_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Grid para os gráficos (2x3)
        # Linha 1: Status das Mensalidades (pizza) + Receita Mensal (barras)
        self.create_chart_status_mensalidades(charts_content, 0, 0)
        self.create_chart_receita_mensal(charts_content, 0, 1)

        # Linha 2: Alunos por Turma (barras) + Evolução Inadimplência (linha)
        self.create_chart_alunos_turma(charts_content, 1, 0)
        self.create_chart_inadimplencia(charts_content, 1, 1)

        # Linha 3: Top Inadimplentes (barras horizontais) + Resumo Financeiro
        self.create_chart_top_inadimplentes(charts_content, 2, 0)
        self.create_resumo_financeiro(charts_content, 2, 1)

        # Configurar grid
        for i in range(2):
            charts_content.columnconfigure(i, weight=1)

    def create_chart_status_mensalidades(self, parent, row, col):
        """Gráfico de pizza - Status das mensalidades"""
        chart_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        chart_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')

        # Título
        tk.Label(
            chart_frame,
            text="📊 Status das Mensalidades",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(pady=(10, 5))

        # Figura matplotlib
        fig = Figure(figsize=(5, 4), dpi=80, facecolor='white')
        ax = fig.add_subplot(111)

        # Canvas
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        # Armazenar referências
        self.graficos_canvas['status_mensalidades'] = {
            'fig': fig,
            'ax': ax,
            'canvas': canvas
        }

    def create_chart_receita_mensal(self, parent, row, col):
        """Gráfico de barras - Receita mensal"""
        chart_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        chart_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')

        tk.Label(
            chart_frame,
            text="💰 Receita Mensal (6 meses)",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(pady=(10, 5))

        fig = Figure(figsize=(5, 4), dpi=80, facecolor='white')
        ax = fig.add_subplot(111)

        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        self.graficos_canvas['receita_mensal'] = {
            'fig': fig,
            'ax': ax,
            'canvas': canvas
        }

    def create_chart_alunos_turma(self, parent, row, col):
        """Gráfico de barras - Alunos por turma"""
        chart_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        chart_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')

        tk.Label(
            chart_frame,
            text="👥 Alunos por Turma",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(pady=(10, 5))

        fig = Figure(figsize=(5, 4), dpi=80, facecolor='white')
        ax = fig.add_subplot(111)

        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        self.graficos_canvas['alunos_turma'] = {
            'fig': fig,
            'ax': ax,
            'canvas': canvas
        }

    def create_chart_inadimplencia(self, parent, row, col):
        """Gráfico de linha - Evolução da inadimplência"""
        chart_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        chart_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')

        tk.Label(
            chart_frame,
            text="📈 Evolução da Inadimplência",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(pady=(10, 5))

        fig = Figure(figsize=(5, 4), dpi=80, facecolor='white')
        ax = fig.add_subplot(111)

        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        self.graficos_canvas['inadimplencia'] = {
            'fig': fig,
            'ax': ax,
            'canvas': canvas
        }

    def create_chart_top_inadimplentes(self, parent, row, col):
        """Gráfico de barras horizontais - Top inadimplentes"""
        chart_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        chart_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')

        tk.Label(
            chart_frame,
            text="🔴 Top 5 Turmas Inadimplentes",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(pady=(10, 5))

        fig = Figure(figsize=(5, 4), dpi=80, facecolor='white')
        ax = fig.add_subplot(111)

        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        self.graficos_canvas['top_inadimplentes'] = {
            'fig': fig,
            'ax': ax,
            'canvas': canvas
        }

    def create_resumo_financeiro(self, parent, row, col):
        """Card de resumo financeiro"""
        resumo_frame = tk.Frame(parent, bg='#f8f9fa', relief='solid', bd=1)
        resumo_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')

        tk.Label(
            resumo_frame,
            text="💼 Resumo Financeiro",
            font=('Arial', 12, 'bold'),
            bg='#f8f9fa',
            fg='#2c3e50'
        ).pack(pady=(15, 10))

        # Container para os dados
        self.resumo_content = tk.Frame(resumo_frame, bg='#f8f9fa')
        self.resumo_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def carregar_dados(self):
        """Carrega todos os dados e atualiza os gráficos"""
        try:
            print("🔄 Carregando dados do dashboard...")

            # Carregar estatísticas gerais para os cards
            stats = self.dashboard_service.obter_estatisticas_gerais()
            self.atualizar_stats_cards(stats)

            # Carregar e plotar cada gráfico
            self.plotar_grafico_status_mensalidades()
            self.plotar_grafico_receita_mensal()
            self.plotar_grafico_alunos_turma()
            self.plotar_grafico_inadimplencia()
            self.plotar_grafico_top_inadimplentes()
            self.atualizar_resumo_financeiro()

            print("✅ Dashboard carregado com sucesso!")

        except Exception as e:
            print(f"❌ Erro ao carregar dados do dashboard: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar dashboard: {str(e)}")

    def atualizar_stats_cards(self, stats):
        """Atualiza os cards de estatísticas"""
        try:
            # Criar stats cards se não existirem
            stats_frame = None
            for widget in self.scrollable_frame.winfo_children():
                if isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Frame) and len(child.winfo_children()) > 0:
                            # Procurar pelo frame de stats
                            first_child = child.winfo_children()[0]
                            if hasattr(first_child, 'winfo_children'):
                                stats_frame = child
                                break

            # Se não encontrou, criar
            if not stats_frame:
                # Encontrar o container principal
                main_container = None
                for widget in self.scrollable_frame.winfo_children():
                    if isinstance(widget, tk.Frame):
                        main_container = widget
                        break

                if main_container:
                    stats_frame = tk.Frame(main_container, bg='white')
                    stats_frame.pack(fill=tk.X, pady=(0, 20), after=main_container.winfo_children()[0])

                    # Configurar grid
                    for i in range(5):
                        stats_frame.columnconfigure(i, weight=1)

            if stats_frame:
                # Limpar cards existentes
                for widget in stats_frame.winfo_children():
                    widget.destroy()

                # Criar novos cards
                cards_data = [
                    ("👥", str(stats.get('total_alunos', 0)), "Alunos Ativos", "#3498db"),
                    ("🏫", str(stats.get('total_turmas', 0)), "Turmas", "#9b59b6"),
                    ("💰", format_currency(stats.get('receita_mes', 0)), "Receita do Mês", "#27ae60"),
                    ("⏳", str(stats.get('pendentes', 0)), "Pendentes", "#f39c12"),
                    ("🔴", str(stats.get('atrasadas', 0)), "Atrasadas", "#e74c3c")
                ]

                for i, (icon, value, label, color) in enumerate(cards_data):
                    self.create_stat_card(stats_frame, icon, value, label, color, 0, i)

        except Exception as e:
            print(f"Erro ao atualizar stats cards: {e}")

    def plotar_grafico_status_mensalidades(self):
        """Plota gráfico de pizza do status das mensalidades"""
        try:
            dados = self.dashboard_service.obter_dados_grafico_status_mensalidades()
            
            if 'status_mensalidades' in self.graficos_canvas and dados['labels']:
                graf = self.graficos_canvas['status_mensalidades']
                ax = graf['ax']
                ax.clear()

                # Criar gráfico de pizza
                wedges, texts, autotexts = ax.pie(
                    dados['valores'], 
                    labels=dados['labels'],
                    colors=dados['cores'],
                    autopct='%1.1f%%',
                    startangle=90,
                    textprops={'fontsize': 9}
                )

                ax.set_title('Status das Mensalidades', fontsize=11, fontweight='bold', pad=20)
                
                # Melhorar aparência
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')

                graf['canvas'].draw()

        except Exception as e:
            print(f"Erro ao plotar gráfico de status das mensalidades: {e}")

    def plotar_grafico_receita_mensal(self):
        """Plota gráfico de barras da receita mensal"""
        try:
            dados = self.dashboard_service.obter_dados_grafico_receita_mensal()
            
            if 'receita_mensal' in self.graficos_canvas and dados['labels']:
                graf = self.graficos_canvas['receita_mensal']
                ax = graf['ax']
                ax.clear()

                # Criar gráfico de barras
                bars = ax.bar(dados['labels'], dados['valores'], color=dados['cor'], alpha=0.8)
                
                ax.set_title('Receita Mensal (Últimos 6 meses)', fontsize=11, fontweight='bold', pad=20)
                ax.set_ylabel('Receita (R$)', fontsize=10)
                
                # Rotacionar labels do eixo X
                ax.set_xticklabels(dados['labels'], rotation=45, ha='right')
                
                # Adicionar valores nas barras
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                               f'R$ {height:.0f}',
                               ha='center', va='bottom', fontsize=8)

                # Ajustar layout
                graf['fig'].tight_layout()
                graf['canvas'].draw()

        except Exception as e:
            print(f"Erro ao plotar gráfico de receita mensal: {e}")

    def plotar_grafico_alunos_turma(self):
        """Plota gráfico de barras dos alunos por turma"""
        try:
            dados = self.dashboard_service.obter_dados_grafico_alunos_por_turma()
            
            if 'alunos_turma' in self.graficos_canvas and dados['labels']:
                graf = self.graficos_canvas['alunos_turma']
                ax = graf['ax']
                ax.clear()

                # Truncar labels muito longos
                labels_truncados = [label[:15] + '...' if len(label) > 15 else label for label in dados['labels']]

                bars = ax.bar(labels_truncados, dados['valores'], color=dados['cor'], alpha=0.8)
                
                ax.set_title('Alunos por Turma', fontsize=11, fontweight='bold', pad=20)
                ax.set_ylabel('Número de Alunos', fontsize=10)
                
                ax.set_xticklabels(labels_truncados, rotation=45, ha='right')
                
                # Adicionar valores nas barras
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                               f'{int(height)}',
                               ha='center', va='bottom', fontsize=9)

                graf['fig'].tight_layout()
                graf['canvas'].draw()

        except Exception as e:
            print(f"Erro ao plotar gráfico de alunos por turma: {e}")

    def plotar_grafico_inadimplencia(self):
        """Plota gráfico de linha da evolução da inadimplência"""
        try:
            dados = self.dashboard_service.obter_dados_grafico_inadimplencia()
            
            if 'inadimplencia' in self.graficos_canvas and dados['labels']:
                graf = self.graficos_canvas['inadimplencia']
                ax = graf['ax']
                ax.clear()

                # Criar gráfico de linha
                line = ax.plot(dados['labels'], dados['valores'], 
                             color=dados['cor'], linewidth=3, marker='o', markersize=6)
                
                ax.set_title('Evolução da Inadimplência', fontsize=11, fontweight='bold', pad=20)
                ax.set_ylabel('Nº de Inadimplentes', fontsize=10)
                
                ax.set_xticklabels(dados['labels'], rotation=45, ha='right')
                
                # Adicionar grid
                ax.grid(True, alpha=0.3)
                
                # Adicionar valores nos pontos
                for i, value in enumerate(dados['valores']):
                    ax.text(i, value + 0.1, f'{int(value)}',
                           ha='center', va='bottom', fontsize=9)

                graf['fig'].tight_layout()
                graf['canvas'].draw()

        except Exception as e:
            print(f"Erro ao plotar gráfico de inadimplência: {e}")

    def plotar_grafico_top_inadimplentes(self):
        """Plota gráfico de barras horizontais dos top inadimplentes"""
        try:
            dados = self.dashboard_service.obter_dados_grafico_top_inadimplentes()
            
            if 'top_inadimplentes' in self.graficos_canvas and dados['labels']:
                graf = self.graficos_canvas['top_inadimplentes']
                ax = graf['ax']
                ax.clear()

                # Truncar labels
                labels_truncados = [label[:20] + '...' if len(label) > 20 else label for label in dados['labels']]

                # Criar gráfico de barras horizontais
                bars = ax.barh(labels_truncados, dados['valores'], color=dados['cor'], alpha=0.8)
                
                ax.set_title('Top 5 Turmas com Inadimplentes', fontsize=11, fontweight='bold', pad=20)
                ax.set_xlabel('Nº de Inadimplentes', fontsize=10)
                
                # Adicionar valores nas barras
                for bar in bars:
                    width = bar.get_width()
                    if width > 0:
                        ax.text(width, bar.get_y() + bar.get_height()/2.,
                               f'{int(width)}',
                               ha='left', va='center', fontsize=9, 
                               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

                graf['fig'].tight_layout()
                graf['canvas'].draw()

        except Exception as e:
            print(f"Erro ao plotar gráfico de top inadimplentes: {e}")

    def atualizar_resumo_financeiro(self):
        """Atualiza o card de resumo financeiro"""
        try:
            dados = self.dashboard_service.obter_resumo_financeiro_atual()
            
            # Limpar conteúdo anterior
            for widget in self.resumo_content.winfo_children():
                widget.destroy()

            # Dados do resumo
            items = [
                ("💰 Receita do Ano:", format_currency(dados.get('receita_ano', 0))),
                ("⚠️ Total Inadimplentes:", str(dados.get('total_inadimplentes', 0))),
                ("📊 Mensalidade Média:", format_currency(dados.get('valor_medio_mensalidade', 0)))
            ]

            for i, (label, value) in enumerate(items):
                item_frame = tk.Frame(self.resumo_content, bg='#f8f9fa')
                item_frame.pack(fill=tk.X, pady=8)

                tk.Label(
                    item_frame, text=label, font=('Arial', 10, 'bold'),
                    bg='#f8f9fa', fg='#2c3e50'
                ).pack(side=tk.LEFT)

                tk.Label(
                    item_frame, text=value, font=('Arial', 10),
                    bg='#f8f9fa', fg='#27ae60'
                ).pack(side=tk.RIGHT)

        except Exception as e:
            print(f"Erro ao atualizar resumo financeiro: {e}")

    def create_quick_actions(self, parent):
        """Cria seção de ações rápidas mais compacta"""
        actions_frame = tk.LabelFrame(
            parent,
            text=" ⚡ Ações Rápidas ",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        actions_frame.pack(fill=tk.X, pady=(0, 20))

        actions_content = tk.Frame(actions_frame, bg='white')
        actions_content.pack(fill=tk.X, padx=20, pady=10)

        # Botões de ação em linha
        buttons = [
            ("👥 Cadastrar Aluno", self.ir_para_alunos, "#27ae60"),
            ("🏫 Nova Turma", self.ir_para_turmas, "#3498db"),
            ("💰 Ver Financeiro", self.ir_para_financeiro, "#e74c3c"),
            ("🔄 Atualizar Dados", self.atualizar_dashboard, "#9b59b6")
        ]

        button_frame = tk.Frame(actions_content, bg='white')
        button_frame.pack()

        for i, (text, command, color) in enumerate(buttons):
            btn = tk.Button(
                button_frame, text=text, command=command,
                font=('Arial', 10, 'bold'), bg=color, fg='white',
                padx=15, pady=8, relief='flat', cursor='hand2',
                width=12
            )
            btn.pack(side=tk.LEFT, padx=5)

    def atualizar_dashboard(self):
        """Atualiza todos os dados do dashboard"""
        try:
            print("🔄 Atualizando dashboard...")
            
            # Atualizar timestamp no header
            for widget in self.scrollable_frame.winfo_children():
                if isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Frame):
                            for grandchild in child.winfo_children():
                                if isinstance(grandchild, tk.Frame):
                                    for label in grandchild.winfo_children():
                                        if isinstance(label, tk.Label) and "📅" in label.cget("text"):
                                            data_atual = datetime.now().strftime("%d/%m/%Y - %H:%M")
                                            label.config(text=f"📅 {data_atual}")
                                            break

            # Recarregar todos os dados
            self.carregar_dados()
            
            print("✅ Dashboard atualizado!")
            
        except Exception as e:
            print(f"❌ Erro ao atualizar dashboard: {e}")
            messagebox.showerror("Erro", f"Erro ao atualizar dashboard: {str(e)}")

    def ir_para_alunos(self):
        """Navega para a tela de alunos"""
        try:
            root = self.parent_frame.winfo_toplevel()
            if hasattr(root, 'app_instance'):
                root.app_instance.show_alunos()
        except:
            print("Navegação para alunos não disponível")

    def ir_para_turmas(self):
        """Navega para a tela de turmas"""
        try:
            root = self.parent_frame.winfo_toplevel()
            if hasattr(root, 'app_instance'):
                root.app_instance.show_turmas()
        except:
            print("Navegação para turmas não disponível")

    def ir_para_financeiro(self):
        """Navega para a tela financeiro"""
        try:
            root = self.parent_frame.winfo_toplevel()
            if hasattr(root, 'app_instance'):
                root.app_instance.show_financeiro()
        except:
            print("Navegação para financeiro não disponível")