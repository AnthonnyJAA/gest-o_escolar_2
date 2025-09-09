import tkinter as tk
from tkinter import ttk, messagebox
from interface.turmas import TurmasInterface
from interface.alunos import AlunosInterface
from interface.financeiro import FinanceiroInterface
from interface.dashboard import DashboardInterface
from interface.configuracoes import ConfiguracoesInterface

class SistemaGestaoEscolar:
    def __init__(self):
        self.root = tk.Tk()
        self.root.app_instance = self 
        self.sidebar_collapsed = False
        self.setup_window()
        self.create_interface()
    
    def setup_window(self):
        self.root.title("Sistema de Gestão Escolar")
        self.root.geometry("1600x900")
        self.root.configure(bg='white')
        
        # Centralizar janela
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        self.root.geometry(f"1600x900+{x}+{y}")
        
        # Interceptar fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_interface(self):
        # Header
        self.header_frame = tk.Frame(self.root, bg='#2c3e50', height=70)
        self.header_frame.pack(fill=tk.X)
        self.header_frame.pack_propagate(False)
        
        # Layout do header
        header_content = tk.Frame(self.header_frame, bg='#2c3e50')
        header_content.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Botão toggle menu
        self.toggle_btn = tk.Button(
            header_content, text="☰", command=self.toggle_sidebar,
            font=('Arial', 16, 'bold'), bg='#34495e', fg='white',
            relief='flat', bd=0, padx=15, pady=8, cursor='hand2'
        )
        self.toggle_btn.pack(side=tk.LEFT, pady=15)
        
        # Título
        title_label = tk.Label(
            header_content, text="💰 Sistema de Gestão Escolar",
            font=('Arial', 18, 'bold'), fg='white', bg='#2c3e50'
        )
        title_label.pack(side=tk.LEFT, pady=20, padx=(20, 0))
        
        # Data atual
        from datetime import datetime
        data_atual = datetime.now().strftime("%d/%m/%Y - %H:%M")
        data_label = tk.Label(
            header_content, text=f"📅 {data_atual}",
            font=('Arial', 12), fg='#bdc3c7', bg='#2c3e50'
        )
        data_label.pack(side=tk.RIGHT, pady=25)
        
        # Container principal
        self.main_container = tk.Frame(self.root, bg='white')
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Menu lateral
        self.create_sidebar()
        
        # Área de conteúdo
        self.content_frame = tk.Frame(self.main_container, bg='white', bd=1, relief='solid')
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(15, 0))
        
        # Mostrar dashboard inicial
        self.show_dashboard()
    
    def create_sidebar(self):
        self.sidebar = tk.Frame(self.main_container, bg='#343a40', width=250)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        # Container interno do sidebar
        self.sidebar_content = tk.Frame(self.sidebar, bg='#343a40')
        self.sidebar_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título do menu
        self.menu_title = tk.Label(
            self.sidebar_content, text="MENU PRINCIPAL",
            font=('Arial', 12, 'bold'), fg='#bdc3c7', bg='#343a40'
        )
        self.menu_title.pack(pady=(10, 30))
        
        # Botões do menu
        menu_items = [
            ("📊", "Dashboard", self.show_dashboard, '#3498db'),
            ("🏫", "Turmas", self.show_turmas, '#e67e22'),
            ("👥", "Alunos", self.show_alunos, '#27ae60'),
            ("💰", "Financeiro", self.show_financeiro, '#e74c3c'),
            ("⚙️", "Configurações", self.show_config, '#9b59b6')
        ]
        
        self.menu_buttons = {}
        for icon, text, command, color in menu_items:
            btn_frame = tk.Frame(self.sidebar_content, bg='#343a40')
            btn_frame.pack(fill=tk.X, pady=2)
            
            btn = tk.Button(
                btn_frame, text=f"{icon}  {text}", command=command,
                font=('Arial', 11, 'bold'), anchor='w',
                bg='#343a40', fg='white', relief='flat', bd=0,
                padx=20, pady=12, cursor='hand2'
            )
            btn.pack(fill=tk.X)
            
            # Criar versão colapsada
            btn_collapsed = tk.Button(
                btn_frame, text=icon, command=command,
                font=('Arial', 14, 'bold'), bg='#343a40', fg='white',
                relief='flat', bd=0, padx=20, pady=12, cursor='hand2'
            )
            
            # Efeitos hover
            def on_enter(e, button=btn, btn_color=color):
                if button != self.current_button:
                    button.config(bg=btn_color)
            
            def on_leave(e, button=btn):
                if button != self.current_button:
                    button.config(bg='#343a40')
            
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
            btn_collapsed.bind('<Enter>', on_enter)
            btn_collapsed.bind('<Leave>', on_leave)
            
            self.menu_buttons[text] = {
                'button': btn, 'button_collapsed': btn_collapsed,
                'frame': btn_frame, 'color': color
            }
        
        # Marcar dashboard como ativo inicialmente
        self.current_button = self.menu_buttons["Dashboard"]['button']
        self.current_button.config(bg='#3498db')
        
        # Rodapé do menu
        self.footer_frame = tk.Frame(self.sidebar, bg='#2c3e50')
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.footer_label = tk.Label(
            self.footer_frame, text="💰 Gestão Escolar v2.0\nSistema Financeiro",
            font=('Arial', 8), fg='#7f8c8d', bg='#2c3e50', justify=tk.CENTER
        )
        self.footer_label.pack(pady=15)
    
    def toggle_sidebar(self):
        """Alternar entre menu expandido e colapsado"""
        self.sidebar_collapsed = not self.sidebar_collapsed
        
        if self.sidebar_collapsed:
            self.sidebar.config(width=80)
            self.menu_title.pack_forget()
            self.footer_label.config(text="💰\nv2.0")
            
            for item in self.menu_buttons.values():
                item['button'].pack_forget()
                item['button_collapsed'].pack(fill=tk.X, pady=2)
        else:
            self.sidebar.config(width=250)
            self.menu_title.pack(pady=(10, 30))
            self.footer_label.config(text="💰 Gestão Escolar v2.0\nSistema Financeiro")
            
            for item in self.menu_buttons.values():
                item['button_collapsed'].pack_forget()
                item['button'].pack(fill=tk.X)
        
        self.sidebar.update_idletasks()
    
    def set_active_button(self, button_name):
        """Define o botão ativo no menu"""
        for name, item in self.menu_buttons.items():
            item['button'].config(bg='#343a40')
            item['button_collapsed'].config(bg='#343a40')
        
        if self.sidebar_collapsed:
            self.current_button = self.menu_buttons[button_name]['button_collapsed']
        else:
            self.current_button = self.menu_buttons[button_name]['button']
        
        self.current_button.config(bg=self.menu_buttons[button_name]['color'])
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        self.clear_content()
        self.set_active_button("Dashboard")
        try:
            DashboardInterface(self.content_frame)
        except Exception as e:
            self.show_dashboard_fallback()
    
    def show_dashboard_fallback(self):
        """Dashboard básico"""
        error_frame = tk.Frame(self.content_frame, bg='white')
        error_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(error_frame, text="📊 Dashboard", font=('Arial', 20, 'bold'),
                bg='white', fg='#2c3e50').pack(pady=(50, 20))
        
        tk.Label(error_frame, text="Dashboard básico carregado com sucesso!",
                font=('Arial', 12), bg='white', fg='#27ae60').pack(pady=20)
    
    def show_turmas(self):
        self.clear_content()
        self.set_active_button("Turmas")
        TurmasInterface(self.content_frame)
    
    def show_alunos(self):
        self.clear_content()
        self.set_active_button("Alunos")
        AlunosInterface(self.content_frame)
    
    def show_financeiro(self):
        self.clear_content()
        self.set_active_button("Financeiro")
        FinanceiroInterface(self.content_frame)
    
    def show_config(self):
        self.clear_content()
        self.set_active_button("Configurações")
        ConfiguracoesInterface(self.content_frame)
    
    def on_closing(self):
        if messagebox.askokcancel("Sair", "Deseja sair do sistema?"):
            self.root.destroy()
    
    def run(self):
        self.root.mainloop()
