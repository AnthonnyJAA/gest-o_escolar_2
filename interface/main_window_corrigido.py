import tkinter as tk
from tkinter import ttk, messagebox
from interface.dashboard import DashboardInterface
from interface.alunos import AlunosInterface
from interface.turmas import TurmasInterface
from interface.financeiro_corrigido import FinanceiroInterface
from interface.transferencia_corrigida import TransferenciaAvancadaInterface
from database.connection import db
import sys

class SistemaGestaoEscolarCorrigido:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Gestão Escolar v2.1 - CORRIGIDO")
        self.root.state('zoomed')  # Maximizar janela no Windows
        self.root.configure(bg='#f0f0f0')
        
        # Configurar fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Armazenar referência da aplicação na raiz para navegação
        self.root.app_instance = self
        
        # Inicializar database
        try:
            db.init_database()
            print("✅ Banco de dados inicializado")
        except Exception as e:
            messagebox.showerror("Erro no Banco de Dados", 
                               f"Erro ao inicializar banco de dados:\n{str(e)}")
            sys.exit(1)
        
        # Criar interface
        self.create_interface()

    def create_interface(self):
        """Cria a interface principal"""
        # Frame principal
        self.main_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Barra de navegação
        self.create_navbar()

        # Área de conteúdo
        self.content_frame = tk.Frame(self.main_frame, bg='white')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Mostrar dashboard por padrão
        self.current_interface = None
        self.show_dashboard()

    def create_navbar(self):
        """Cria barra de navegação"""
        navbar = tk.Frame(self.main_frame, bg='#2c3e50', height=80)
        navbar.pack(fill=tk.X, padx=10, pady=(10, 10))
        navbar.pack_propagate(False)

        # Container superior - título e versão
        top_container = tk.Frame(navbar, bg='#2c3e50')
        top_container.pack(fill=tk.X, padx=15, pady=(8, 0))

        tk.Label(
            top_container,
            text="🎓 Sistema de Gestão Escolar v2.1 - CORRIGIDO",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack(side=tk.LEFT)

        tk.Label(
            top_container,
            text="✅ Transferências + Pagamentos Funcionando",
            font=('Arial', 11, 'bold'),
            bg='#2c3e50',
            fg='#28a745'
        ).pack(side=tk.RIGHT)

        # Container para botões (centralizado)
        buttons_container = tk.Frame(navbar, bg='#2c3e50')
        buttons_container.pack(expand=True)

        # Lista de botões com ícones e cores
        buttons_config = [
            ("🏠 Dashboard", self.show_dashboard, "#3498db"),
            ("👥 Alunos", self.show_alunos, "#e74c3c"),
            ("🏫 Turmas", self.show_turmas, "#f39c12"),
            ("💰 Financeiro", self.show_financeiro, "#27ae60"),
            ("🔄 Transferências", self.show_transferencias, "#9b59b6"),
            ("⚙️ Config", self.show_configuracoes, "#34495e")
        ]

        self.navbar_buttons = {}
        
        for i, (text, command, color) in enumerate(buttons_config):
            btn = tk.Button(
                buttons_container,
                text=text,
                command=command,
                font=('Arial', 11, 'bold'),
                bg=color,
                fg='white',
                relief='flat',
                padx=20,
                pady=10,
                cursor='hand2',
                border=0
            )
            btn.pack(side=tk.LEFT, padx=5, pady=10)
            
            # Efeitos hover
            btn.bind("<Enter>", lambda e, b=btn, c=color: self.on_button_hover(b, c))
            btn.bind("<Leave>", lambda e, b=btn, c=color: self.on_button_leave(b, c))
            
            # Armazenar referência
            self.navbar_buttons[text] = btn

        # Botão de sair
        exit_btn = tk.Button(
            navbar,
            text="❌",
            command=self.on_closing,
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            relief='flat',
            padx=12,
            pady=8,
            cursor='hand2'
        )
        exit_btn.pack(side=tk.RIGHT, padx=15, pady=15)
        
        exit_btn.bind("<Enter>", lambda e: exit_btn.config(bg='#c0392b'))
        exit_btn.bind("<Leave>", lambda e: exit_btn.config(bg='#e74c3c'))

    def on_button_hover(self, button, original_color):
        """Efeito hover nos botões"""
        hover_colors = {
            "#3498db": "#2980b9",
            "#e74c3c": "#c0392b", 
            "#f39c12": "#d68910",
            "#27ae60": "#229954",
            "#9b59b6": "#8e44ad",
            "#34495e": "#2c3e50"
        }
        button.config(bg=hover_colors.get(original_color, original_color))

    def on_button_leave(self, button, original_color):
        """Efeito quando sai do hover"""
        button.config(bg=original_color)

    def clear_content(self):
        """Limpa o conteúdo atual"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.current_interface = None

    def update_navbar_selection(self, selected_button):
        """Atualiza a seleção na barra de navegação"""
        colors = {
            "🏠 Dashboard": "#3498db",
            "👥 Alunos": "#e74c3c", 
            "🏫 Turmas": "#f39c12",
            "💰 Financeiro": "#27ae60",
            "🔄 Transferências": "#9b59b6",
            "⚙️ Config": "#34495e"
        }
        
        for btn_text, btn in self.navbar_buttons.items():
            if btn_text == selected_button:
                selected_colors = {
                    "#3498db": "#2980b9",
                    "#e74c3c": "#c0392b",
                    "#f39c12": "#d68910", 
                    "#27ae60": "#229954",
                    "#9b59b6": "#8e44ad",
                    "#34495e": "#2c3e50"
                }
                btn.config(bg=selected_colors.get(colors[btn_text], colors[btn_text]),
                          relief='sunken')
            else:
                btn.config(bg=colors[btn_text], relief='flat')

    def show_dashboard(self):
        """Mostra o dashboard"""
        try:
            self.clear_content()
            self.update_navbar_selection("🏠 Dashboard")
            
            self.current_interface = DashboardInterface(self.content_frame)
            print("✅ Dashboard carregado")
            
        except Exception as e:
            print(f"❌ Erro ao carregar dashboard: {e}")
            self.show_error("Erro ao carregar Dashboard", str(e))

    def show_alunos(self):
        """Mostra interface de alunos"""
        try:
            self.clear_content()
            self.update_navbar_selection("👥 Alunos")
            
            self.current_interface = AlunosInterface(self.content_frame)
            print("✅ Interface de Alunos carregada")
            
        except Exception as e:
            print(f"❌ Erro ao carregar alunos: {e}")
            self.show_error("Erro ao carregar Alunos", str(e))

    def show_turmas(self):
        """Mostra interface de turmas"""
        try:
            self.clear_content()
            self.update_navbar_selection("🏫 Turmas")
            
            self.current_interface = TurmasInterface(self.content_frame)
            print("✅ Interface de Turmas carregada")
            
        except Exception as e:
            print(f"❌ Erro ao carregar turmas: {e}")
            self.show_error("Erro ao carregar Turmas", str(e))

    def show_financeiro(self):
        """Mostra interface financeiro CORRIGIDA"""
        try:
            self.clear_content()
            self.update_navbar_selection("💰 Financeiro")
            
            # Mostrar loading
            loading_frame = tk.Frame(self.content_frame, bg='white')
            loading_frame.pack(fill=tk.BOTH, expand=True)
            
            loading_label = tk.Label(
                loading_frame,
                text="💰 Carregando Sistema Financeiro Avançado...\n🔄 Nova lógica de pagamentos",
                font=('Arial', 16),
                bg='white',
                fg='#27ae60',
                justify='center'
            )
            loading_label.pack(expand=True)
            self.root.update()
            
            # Remover loading
            loading_frame.destroy()
            
            # Carregar interface corrigida
            self.current_interface = FinanceiroInterface(self.content_frame)
            print("✅ Interface Financeiro CORRIGIDA carregada")
            
        except Exception as e:
            print(f"❌ Erro ao carregar financeiro: {e}")
            self.show_error("Erro ao carregar Financeiro", str(e))

    def show_transferencias(self):
        """Mostra interface de transferências CORRIGIDA"""
        try:
            self.clear_content()
            self.update_navbar_selection("🔄 Transferências")
            
            # Mostrar loading
            loading_frame = tk.Frame(self.content_frame, bg='white')
            loading_frame.pack(fill=tk.BOTH, expand=True)
            
            loading_label = tk.Label(
                loading_frame,
                text="🔄 Carregando Sistema de Transferências...\n✅ Erro de importação corrigido",
                font=('Arial', 16),
                bg='white',
                fg='#9b59b6',
                justify='center'
            )
            loading_label.pack(expand=True)
            self.root.update()
            
            # Remover loading
            loading_frame.destroy()
            
            # Carregar interface corrigida
            self.current_interface = TransferenciaAvancadaInterface(self.content_frame)
            print("✅ Interface de Transferências CORRIGIDA carregada")
            
        except Exception as e:
            print(f"❌ Erro ao carregar transferências: {e}")
            self.show_error("Erro ao carregar Transferências", str(e))

    def show_configuracoes(self):
        """Mostra configurações do sistema"""
        try:
            self.clear_content()
            self.update_navbar_selection("⚙️ Config")
            
            # Interface de configurações básica
            config_frame = tk.Frame(self.content_frame, bg='white')
            config_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Cabeçalho
            header_frame = tk.Frame(config_frame, bg='white')
            header_frame.pack(fill=tk.X, pady=(0, 20))
            
            tk.Label(
                header_frame,
                text="⚙️ Configurações do Sistema",
                font=('Arial', 20, 'bold'),
                bg='white',
                fg='#2c3e50'
            ).pack(side=tk.LEFT)
            
            # Informações do sistema
            info_frame = tk.LabelFrame(config_frame, text="📋 Informações do Sistema", font=('Arial', 12, 'bold'), bg='white')
            info_frame.pack(fill=tk.X, pady=(0, 20))
            
            info_text = """
🎓 Sistema de Gestão Escolar v2.1 - CORRIGIDO

✅ CORREÇÕES IMPLEMENTADAS:
• Erro de transferências resolvido
• Campos de pagamento habilitados
• Nova lógica: Original - Desconto + Multa + Outros
• Carregamento de turmas e alunos funcionando

💰 NOVOS RECURSOS FINANCEIROS:
• Multa manual (você define o valor)
• Campo "Outros" para cobranças extras  
• Cálculo em tempo real
• Relatórios detalhados

🔄 TRANSFERÊNCIAS FUNCIONANDO:
• Carregamento automático de turmas
• Lista de alunos com seleção múltipla
• Validações completas
• Histórico detalhado

📊 STATUS: SISTEMA 100% FUNCIONAL
            """
            
            tk.Label(
                info_frame,
                text=info_text.strip(),
                font=('Arial', 10),
                bg='white',
                fg='#2c3e50',
                justify='left'
            ).pack(padx=20, pady=15, anchor='w')
            
            # Ações
            actions_frame = tk.LabelFrame(config_frame, text="🛠️ Ações do Sistema", font=('Arial', 12, 'bold'), bg='white')
            actions_frame.pack(fill=tk.X, pady=(0, 20))
            
            buttons_frame = tk.Frame(actions_frame, bg='white')
            buttons_frame.pack(fill=tk.X, padx=20, pady=15)
            
            tk.Button(
                buttons_frame,
                text="🧪 Testar Financeiro",
                command=self.show_financeiro,
                font=('Arial', 11, 'bold'),
                bg='#27ae60',
                fg='white',
                padx=20,
                pady=8,
                relief='flat'
            ).pack(side=tk.LEFT, padx=(0, 10))
            
            tk.Button(
                buttons_frame,
                text="🧪 Testar Transferências",
                command=self.show_transferencias,
                font=('Arial', 11, 'bold'),
                bg='#9b59b6',
                fg='white',
                padx=20,
                pady=8,
                relief='flat'
            ).pack(side=tk.LEFT, padx=10)
            
            tk.Button(
                buttons_frame,
                text="🏠 Voltar ao Dashboard",
                command=self.show_dashboard,
                font=('Arial', 11, 'bold'),
                bg='#3498db',
                fg='white',
                padx=20,
                pady=8,
                relief='flat'
            ).pack(side=tk.RIGHT)
            
            print("✅ Configurações carregadas")
            
        except Exception as e:
            print(f"❌ Erro ao carregar configurações: {e}")
            self.show_error("Erro ao carregar Configurações", str(e))

    def show_error(self, title, message):
        """Mostra tela de erro"""
        self.clear_content()
        
        error_frame = tk.Frame(self.content_frame, bg='white')
        error_frame.pack(fill=tk.BOTH, expand=True)
        
        center_frame = tk.Frame(error_frame, bg='white')
        center_frame.pack(expand=True)
        
        tk.Label(
            center_frame,
            text="⚠️ Erro no Sistema",
            font=('Arial', 20, 'bold'),
            bg='white',
            fg='#e74c3c'
        ).pack(pady=(50, 20))
        
        tk.Label(
            center_frame,
            text=title,
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(pady=(0, 10))
        
        tk.Label(
            center_frame,
            text=message,
            font=('Arial', 12),
            bg='white',
            fg='#6c757d',
            wraplength=600,
            justify='center'
        ).pack(pady=(0, 30))
        
        actions_frame = tk.Frame(center_frame, bg='white')
        actions_frame.pack()
        
        tk.Button(
            actions_frame,
            text="🏠 Dashboard",
            command=self.show_dashboard,
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10,
            relief='flat',
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            actions_frame,
            text="⚙️ Configurações",
            command=self.show_configuracoes,
            font=('Arial', 12, 'bold'),
            bg='#34495e',
            fg='white',
            padx=20,
            pady=10,
            relief='flat',
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)

    def on_closing(self):
        """Callback para fechamento da janela"""
        resposta = messagebox.askyesno(
            "Confirmar Saída",
            "Deseja realmente sair do Sistema?\n\nTodas as alterações já foram salvas."
        )
        
        if resposta:
            print("👋 Encerrando Sistema de Gestão Escolar...")
            
            try:
                db.close_connection()
                print("✅ Conexão com banco fechada")
            except:
                pass
            
            self.root.destroy()

    def run(self):
        """Executa a aplicação"""
        print("🚀 Iniciando interface gráfica corrigida...")
        
        self.center_window()
        
        # Mostrar mensagem de boas-vindas
        messagebox.showinfo(
            "Sistema Corrigido!",
            "🎉 SISTEMA DE GESTÃO ESCOLAR v2.1\n\n"
            "✅ CORREÇÕES APLICADAS:\n"
            "• Financeiro: Campos habilitados\n"
            "• Transferências: Carregamento corrigido\n"
            "• Nova lógica de pagamentos funcionando\n\n"
            "🎯 TESTE AGORA:\n"
            "• Clique em '💰 Financeiro' para nova lógica\n"
            "• Clique em '🔄 Transferências' para teste\n\n"
            "🚀 Sistema pronto para uso!"
        )
        
        self.root.mainloop()

    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width // 2) - (1400 // 2)
        y = (screen_height // 2) - (900 // 2)
        
        self.root.geometry(f"1400x900+{x}+{y}")

if __name__ == "__main__":
    try:
        app = SistemaGestaoEscolarCorrigido()
        app.run()
    except Exception as e:
        print(f"💥 Erro crítico na aplicação: {e}")
        messagebox.showerror("Erro Crítico", f"Erro ao iniciar aplicação:\n{str(e)}")
        sys.exit(1)