import tkinter as tk
from tkinter import ttk
from services.dashboard_service import DashboardService
from utils.formatters import format_currency
from datetime import datetime

class DashboardInterface:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.parent_frame.configure(bg='white')
        self.dashboard_service = DashboardService()
        self.create_interface()
        self.carregar_dados()
    
    def create_interface(self):
        """Cria a interface do dashboard"""
        # Container principal
        main_container = tk.Frame(self.parent_frame, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_frame = tk.Frame(main_container, bg='white')
        title_frame.pack(fill=tk.X, pady=(0, 30))
        
        tk.Label(
            title_frame,
            text="📊 Dashboard",
            font=('Arial', 24, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(side=tk.LEFT)
        
        # Data atual
        data_atual = datetime.now().strftime("%d/%m/%Y")
        tk.Label(
            title_frame,
            text=f"📅 {data_atual}",
            font=('Arial', 12),
            bg='white',
            fg='#6c757d'
        ).pack(side=tk.RIGHT)
        
        # Cards de estatísticas
        self.create_stats_cards(main_container)
        
        # Seção de resumo
        self.create_summary_section(main_container)
        
        # Ações rápidas
        self.create_quick_actions(main_container)
    
    def create_stats_cards(self, parent):
        """Cria cards de estatísticas"""
        stats_frame = tk.Frame(parent, bg='white')
        stats_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Obter estatísticas
        stats = self.dashboard_service.obter_estatisticas_gerais()
        
        # Card 1: Total de Alunos
        self.create_stat_card(
            stats_frame, "👥", str(stats['total_alunos']), 
            "Alunos Ativos", "#3498db", 0, 0
        )
        
        # Card 2: Total de Turmas
        self.create_stat_card(
            stats_frame, "🏫", str(stats['total_turmas']), 
            "Turmas Ativas", "#9b59b6", 0, 1
        )
        
        # Card 3: Receita do Mês
        self.create_stat_card(
            stats_frame, "💰", format_currency(stats['receita_mes']), 
            "Receita do Mês", "#27ae60", 0, 2
        )
        
        # Card 4: Mensalidades Pendentes
        self.create_stat_card(
            stats_frame, "⏳", str(stats['pendentes']), 
            "Mensalidades Pendentes", "#f39c12", 0, 3
        )
        
        # Card 5: Mensalidades Atrasadas
        self.create_stat_card(
            stats_frame, "🔴", str(stats['atrasadas']), 
            "Mensalidades Atrasadas", "#e74c3c", 1, 0
        )
        
        # Card 6: Taxa de Inadimplência
        inadimplencia = 0
        if stats['total_alunos'] > 0:
            inadimplencia = round((stats['atrasadas'] / stats['total_alunos']) * 100, 1)
        
        self.create_stat_card(
            stats_frame, "📈", f"{inadimplencia}%", 
            "Taxa Inadimplência", "#e67e22", 1, 1
        )
        
        # Configurar grid
        for i in range(4):
            stats_frame.columnconfigure(i, weight=1)
    
    def create_stat_card(self, parent, icon, value, label, color, row, col):
        """Cria um card de estatística"""
        card = tk.Frame(parent, bg=color, relief='flat', bd=0)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='ew', ipady=20)
        
        # Container interno
        card_content = tk.Frame(card, bg=color)
        card_content.pack(expand=True)
        
        # Ícone
        tk.Label(
            card_content, text=icon, font=('Arial', 24), 
            bg=color, fg='white'
        ).pack(pady=(10, 5))
        
        # Valor
        tk.Label(
            card_content, text=value, font=('Arial', 18, 'bold'), 
            bg=color, fg='white'
        ).pack()
        
        # Label
        tk.Label(
            card_content, text=label, font=('Arial', 10), 
            bg=color, fg='white', wraplength=120
        ).pack(pady=(5, 10))
    
    def create_summary_section(self, parent):
        """Cria seção de resumo"""
        summary_frame = tk.LabelFrame(
            parent,
            text="  📋 Resumo Geral  ",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        summary_frame.pack(fill=tk.X, pady=(0, 30))
        
        summary_content = tk.Frame(summary_frame, bg='white')
        summary_content.pack(fill=tk.X, padx=20, pady=15)
        
        # Obter resumos
        resumos = self.dashboard_service.obter_resumos()
        
        # Lista de informações
        info_items = [
            ("📚 Turmas com mais alunos:", resumos.get('turma_popular', 'N/A')),
            ("💰 Valor total em aberto:", format_currency(resumos.get('valor_aberto', 0))),
            ("📅 Próximo vencimento:", resumos.get('proximo_vencimento', 'N/A')),
            ("🎯 Meta de receita mensal:", format_currency(resumos.get('meta_mensal', 0))),
            ("📊 Status do sistema:", "✅ Online e Operacional"),
        ]
        
        for i, (label, value) in enumerate(info_items):
            item_frame = tk.Frame(summary_content, bg='white')
            item_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(
                item_frame, text=label, font=('Arial', 11, 'bold'),
                bg='white', fg='#2c3e50'
            ).pack(side=tk.LEFT)
            
            tk.Label(
                item_frame, text=value, font=('Arial', 11),
                bg='white', fg='#27ae60'
            ).pack(side=tk.RIGHT)
    
    def create_quick_actions(self, parent):
        """Cria seção de ações rápidas"""
        actions_frame = tk.LabelFrame(
            parent,
            text="  ⚡ Ações Rápidas  ",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        actions_frame.pack(fill=tk.X)
        
        actions_content = tk.Frame(actions_frame, bg='white')
        actions_content.pack(fill=tk.X, padx=20, pady=15)
        
        # Botões de ação
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
                font=('Arial', 11, 'bold'), bg=color, fg='white',
                padx=20, pady=10, relief='flat', cursor='hand2',
                width=15
            )
            btn.grid(row=i//2, column=i%2, padx=10, pady=5, sticky='ew')
        
        # Configurar grid
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
    
    def carregar_dados(self):
        """Carrega os dados iniciais"""
        try:
            # Os dados já são carregados na criação dos cards
            print("✅ Dashboard carregado com sucesso!")
        except Exception as e:
            print(f"Erro ao carregar dashboard: {e}")
    
    def atualizar_dashboard(self):
        """Atualiza os dados do dashboard"""
        # Limpar interface atual
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Recriar interface
        self.create_interface()
        self.carregar_dados()
        
        print("🔄 Dashboard atualizado!")
    
    def ir_para_alunos(self):
        """Navega para a tela de alunos"""
        # Encontrar a janela principal e chamar show_alunos
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
