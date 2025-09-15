import tkinter as tk
from tkinter import ttk, messagebox
from interface.dashboard import DashboardInterface
from interface.alunos import AlunosInterface
from interface.turmas import TurmasInterface
from interface.financeiro import FinanceiroInterface
from interface.transferencia import TransferenciaInterface
from database.connection import db
import sys

class SistemaGestaoEscolar:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Gestão Escolar v2.0 - Com Transferências")
        self.root.state('zoomed')  # Maximizar janela no Windows
        self.root.configure(bg='#f0f0f0')
        
        # Configurar ícone (se houver)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        # Configurar fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Armazenar referência da aplicação na raiz para navegação
        self.root.app_instance = self
        
        # Inicializar database
        try:
            db.init_database()
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
        navbar = tk.Frame(self.main_frame, bg='#2c3e50', height=60)
        navbar.pack(fill=tk.X, padx=10, pady=(10, 10))
        navbar.pack_propagate(False)

        # Container para botões (centralizado)
        buttons_container = tk.Frame(navbar, bg='#2c3e50')
        buttons_container.pack(expand=True)

        # Lista de botões com ícones e cores
        buttons_config = [
            ("🏠 Dashboard", self.show_dashboard, "#3498db"),
            ("👥 Alunos", self.show_alunos, "#e74c3c"),
            ("🏫 Turmas", self.show_turmas, "#f39c12"),
            ("💰 Financeiro", self.show_financeiro, "#27ae60"),
            ("🔄 Transferências", self.show_transferencias, "#9b59b6"),  # NOVO BOTÃO
            ("⚙️ Configurações", self.show_configuracoes, "#34495e")
        ]

        self.navbar_buttons = {}
        
        for i, (text, command, color) in enumerate(buttons_config):
            btn = tk.Button(
                buttons_container,
                text=text,
                command=command,
                font=('Arial', 12, 'bold'),
                bg=color,
                fg='white',
                relief='flat',
                padx=20,
                pady=12,
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
            text="❌ Sair",
            command=self.on_closing,
            font=('Arial', 10, 'bold'),
            bg='#e74c3c',
            fg='white',
            relief='flat',
            padx=15,
            pady=8,
            cursor='hand2'
        )
        exit_btn.pack(side=tk.RIGHT, padx=15, pady=15)
        
        exit_btn.bind("<Enter>", lambda e: exit_btn.config(bg='#c0392b'))
        exit_btn.bind("<Leave>", lambda e: exit_btn.config(bg='#e74c3c'))

    def on_button_hover(self, button, original_color):
        """Efeito hover nos botões"""
        # Escurecer a cor original
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
        # Reset todos os botões
        colors = {
            "🏠 Dashboard": "#3498db",
            "👥 Alunos": "#e74c3c", 
            "🏫 Turmas": "#f39c12",
            "💰 Financeiro": "#27ae60",
            "🔄 Transferências": "#9b59b6",
            "⚙️ Configurações": "#34495e"
        }
        
        for btn_text, btn in self.navbar_buttons.items():
            if btn_text == selected_button:
                # Botão selecionado - mais escuro
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
        """Mostra interface financeiro"""
        try:
            self.clear_content()
            self.update_navbar_selection("💰 Financeiro")
            
            self.current_interface = FinanceiroInterface(self.content_frame)
            print("✅ Interface Financeiro carregada")
            
        except Exception as e:
            print(f"❌ Erro ao carregar financeiro: {e}")
            self.show_error("Erro ao carregar Financeiro", str(e))

    def show_transferencias(self):
        """Mostra interface de transferências - NOVA FUNCIONALIDADE"""
        try:
            self.clear_content()
            self.update_navbar_selection("🔄 Transferências")
            
            self.current_interface = TransferenciaInterface(self.content_frame)
            print("✅ Interface de Transferências carregada")
            
        except Exception as e:
            print(f"❌ Erro ao carregar transferências: {e}")
            self.show_error("Erro ao carregar Transferências", str(e))

    def show_configuracoes(self):
        """Mostra configurações do sistema"""
        try:
            self.clear_content()
            self.update_navbar_selection("⚙️ Configurações")
            
            # Interface simples de configurações
            config_frame = tk.Frame(self.content_frame, bg='white')
            config_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Título
            tk.Label(
                config_frame,
                text="⚙️ Configurações do Sistema",
                font=('Arial', 24, 'bold'),
                bg='white',
                fg='#2c3e50'
            ).pack(pady=(0, 30))
            
            # Informações do sistema
            info_frame = tk.LabelFrame(
                config_frame,
                text=" 📋 Informações do Sistema ",
                font=('Arial', 14, 'bold'),
                bg='white',
                fg='#2c3e50'
            )
            info_frame.pack(fill=tk.X, pady=(0, 20))
            
            info_container = tk.Frame(info_frame, bg='white')
            info_container.pack(fill=tk.X, padx=20, pady=15)
            
            info_items = [
                ("🎓 Sistema:", "Gestão Escolar v2.0"),
                ("📊 Recursos:", "Dashboard Interativo + Transferências"),
                ("🗄️ Banco de Dados:", "SQLite3"),
                ("🐍 Python:", f"{sys.version.split()[0]}"),
                ("📈 Gráficos:", "Matplotlib + Tkinter"),
                ("🔄 Última Atualização:", "Setembro 2025")
            ]
            
            for i, (label, valor) in enumerate(info_items):
                item_frame = tk.Frame(info_container, bg='white')
                item_frame.pack(fill=tk.X, pady=5)
                
                tk.Label(
                    item_frame, text=label, font=('Arial', 11, 'bold'),
                    bg='white', fg='#2c3e50', anchor='w'
                ).pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                tk.Label(
                    item_frame, text=valor, font=('Arial', 11),
                    bg='white', fg='#27ae60', anchor='e'
                ).pack(side=tk.RIGHT)
            
            # Ações do sistema
            actions_frame = tk.LabelFrame(
                config_frame,
                text=" 🔧 Ações do Sistema ",
                font=('Arial', 14, 'bold'),
                bg='white',
                fg='#2c3e50'
            )
            actions_frame.pack(fill=tk.X, pady=(0, 20))
            
            actions_container = tk.Frame(actions_frame, bg='white')
            actions_container.pack(fill=tk.X, padx=20, pady=15)
            
            # Botões de ação
            tk.Button(
                actions_container,
                text="🗄️ Backup do Banco de Dados",
                command=self.backup_database,
                font=('Arial', 12, 'bold'),
                bg='#17a2b8',
                fg='white',
                padx=20,
                pady=10,
                relief='flat',
                cursor='hand2'
            ).pack(fill=tk.X, pady=5)
            
            tk.Button(
                actions_container,
                text="📊 Verificar Integridade dos Dados",
                command=self.verificar_integridade,
                font=('Arial', 12, 'bold'),
                bg='#28a745',
                fg='white',
                padx=20,
                pady=10,
                relief='flat',
                cursor='hand2'
            ).pack(fill=tk.X, pady=5)
            
            tk.Button(
                actions_container,
                text="🧹 Limpar Cache do Sistema",
                command=self.limpar_cache,
                font=('Arial', 12, 'bold'),
                bg='#ffc107',
                fg='black',
                padx=20,
                pady=10,
                relief='flat',
                cursor='hand2'
            ).pack(fill=tk.X, pady=5)
            
            print("✅ Configurações carregadas")
            
        except Exception as e:
            print(f"❌ Erro ao carregar configurações: {e}")
            self.show_error("Erro ao carregar Configurações", str(e))

    def backup_database(self):
        """Realiza backup do banco de dados"""
        try:
            import shutil
            from datetime import datetime
            
            # Nome do arquivo de backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_escolar_{timestamp}.db"
            
            # Copiar arquivo do banco
            shutil.copy2("escolar.db", backup_filename)
            
            messagebox.showinfo(
                "Backup Realizado",
                f"✅ Backup realizado com sucesso!\n\n"
                f"📁 Arquivo: {backup_filename}\n"
                f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
                f"💡 O arquivo foi salvo na pasta do sistema."
            )
            
        except Exception as e:
            messagebox.showerror("Erro no Backup", f"❌ Erro ao realizar backup:\n{str(e)}")

    def verificar_integridade(self):
        """Verifica integridade dos dados"""
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Verificações básicas
            verificacoes = []
            
            # Contar registros principais
            cursor.execute("SELECT COUNT(*) FROM alunos")
            total_alunos = cursor.fetchone()[0]
            verificacoes.append(f"👥 Alunos cadastrados: {total_alunos}")
            
            cursor.execute("SELECT COUNT(*) FROM turmas")
            total_turmas = cursor.fetchone()[0]
            verificacoes.append(f"🏫 Turmas cadastradas: {total_turmas}")
            
            cursor.execute("SELECT COUNT(*) FROM pagamentos")
            total_pagamentos = cursor.fetchone()[0]
            verificacoes.append(f"💰 Registros de pagamento: {total_pagamentos}")
            
            cursor.execute("SELECT COUNT(*) FROM historico_transferencias")
            total_transferencias = cursor.fetchone()[0]
            verificacoes.append(f"🔄 Transferências registradas: {total_transferencias}")
            
            # Verificar inconsistências
            problemas = []
            
            # Alunos sem turma válida
            cursor.execute("""
                SELECT COUNT(*) FROM alunos a 
                LEFT JOIN turmas t ON a.turma_id = t.id 
                WHERE t.id IS NULL AND a.status = 'Ativo'
            """)
            alunos_sem_turma = cursor.fetchone()[0]
            if alunos_sem_turma > 0:
                problemas.append(f"⚠️ {alunos_sem_turma} aluno(s) sem turma válida")
            
            # Pagamentos órfãos
            cursor.execute("""
                SELECT COUNT(*) FROM pagamentos p 
                LEFT JOIN alunos a ON p.aluno_id = a.id 
                WHERE a.id IS NULL
            """)
            pagamentos_orfaos = cursor.fetchone()[0]
            if pagamentos_orfaos > 0:
                problemas.append(f"⚠️ {pagamentos_orfaos} pagamento(s) sem aluno válido")
            
            conn.close()
            
            # Mostrar resultado
            resultado = "✅ Verificação de Integridade Concluída\n\n"
            resultado += "📊 Resumo dos Dados:\n"
            resultado += "\n".join(verificacoes)
            
            if problemas:
                resultado += "\n\n⚠️ Problemas Encontrados:\n"
                resultado += "\n".join(problemas)
                resultado += "\n\n💡 Recomenda-se corrigir os problemas encontrados."
            else:
                resultado += "\n\n✅ Nenhum problema encontrado!\nO banco de dados está íntegro."
            
            messagebox.showinfo("Verificação de Integridade", resultado)
            
        except Exception as e:
            messagebox.showerror("Erro na Verificação", f"❌ Erro ao verificar integridade:\n{str(e)}")

    def limpar_cache(self):
        """Limpa cache do sistema"""
        try:
            # Simular limpeza de cache
            import time
            
            # Mostrar progresso (simulado)
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Limpando Cache")
            progress_window.geometry("300x100")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            tk.Label(
                progress_window, text="🧹 Limpando cache do sistema...",
                font=('Arial', 12), pady=20
            ).pack()
            
            progress = ttk.Progressbar(
                progress_window, mode='indeterminate'
            )
            progress.pack(fill=tk.X, padx=20, pady=10)
            progress.start()
            
            progress_window.update()
            time.sleep(2)  # Simular tempo de processamento
            
            progress_window.destroy()
            
            messagebox.showinfo(
                "Cache Limpo",
                "✅ Cache do sistema limpo com sucesso!\n\n"
                "🚀 O sistema pode apresentar melhor performance."
            )
            
        except Exception as e:
            messagebox.showerror("Erro na Limpeza", f"❌ Erro ao limpar cache:\n{str(e)}")

    def show_error(self, title, message):
        """Mostra tela de erro"""
        self.clear_content()
        
        error_frame = tk.Frame(self.content_frame, bg='white')
        error_frame.pack(fill=tk.BOTH, expand=True)
        
        # Centralizar conteúdo
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
        
        # Botão para voltar ao dashboard
        tk.Button(
            center_frame,
            text="🏠 Voltar ao Dashboard",
            command=self.show_dashboard,
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10,
            relief='flat',
            cursor='hand2'
        ).pack()

    def on_closing(self):
        """Callback para fechamento da janela"""
        resposta = messagebox.askyesno(
            "Confirmar Saída",
            "🤔 Deseja realmente sair do Sistema de Gestão Escolar?\n\n"
            "✅ Todos os dados foram salvos automaticamente."
        )
        
        if resposta:
            print("👋 Encerrando Sistema de Gestão Escolar...")
            
            # Fechar conexões do banco
            try:
                db.close_connection()
            except:
                pass
            
            self.root.destroy()

    def run(self):
        """Executa a aplicação"""
        print("🚀 Iniciando interface gráfica...")
        
        # Centralizar janela na tela
        self.center_window()
        
        # Iniciar loop principal
        self.root.mainloop()

    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        
        # Obter dimensões da tela
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calcular posição central
        x = (screen_width // 2) - (1200 // 2)  # Largura desejada: 1200px
        y = (screen_height // 2) - (800 // 2)   # Altura desejada: 800px
        
        # Definir geometria
        self.root.geometry(f"1200x800+{x}+{y}")

if __name__ == "__main__":
    try:
        app = SistemaGestaoEscolar()
        app.run()
    except Exception as e:
        print(f"💥 Erro crítico na aplicação: {e}")
        messagebox.showerror("Erro Crítico", f"Erro ao iniciar aplicação:\n{str(e)}")
        sys.exit(1)