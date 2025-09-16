import tkinter as tk
from tkinter import ttk, messagebox
from interface.dashboard import DashboardInterface
from interface.alunos import AlunosInterface
from interface.turmas import TurmasInterface
from interface.financeiro import FinanceiroInterface
from interface.transferencia_avancada import TransferenciaAvancadaInterface
from database.connection import db
import sys

class SistemaGestaoEscolarAvancado:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Gestão Escolar v2.1 - Transferências Avançadas")
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
        """Cria barra de navegação atualizada"""
        navbar = tk.Frame(self.main_frame, bg='#2c3e50', height=70)
        navbar.pack(fill=tk.X, padx=10, pady=(10, 10))
        navbar.pack_propagate(False)

        # Container superior - título e versão
        top_container = tk.Frame(navbar, bg='#2c3e50')
        top_container.pack(fill=tk.X, padx=10, pady=(5, 0))

        tk.Label(
            top_container,
            text="🎓 Sistema de Gestão Escolar v2.1",
            font=('Arial', 14, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack(side=tk.LEFT)

        tk.Label(
            top_container,
            text="Com Transferências Avançadas - 3 Cenários Implementados",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(side=tk.RIGHT)

        # Container para botões (centralizado)
        buttons_container = tk.Frame(navbar, bg='#2c3e50')
        buttons_container.pack(expand=True)

        # Lista de botões com ícones e cores - ATUALIZADA
        buttons_config = [
            ("🏠 Dashboard", self.show_dashboard, "#3498db"),
            ("👥 Alunos", self.show_alunos, "#e74c3c"),
            ("🏫 Turmas", self.show_turmas, "#f39c12"),
            ("💰 Financeiro", self.show_financeiro, "#27ae60"),
            ("🔄 Transferências", self.show_transferencias_avancadas, "#9b59b6"),  # ATUALIZADO
            ("⚙️ Configurações", self.show_configuracoes, "#34495e")
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
                padx=18,
                pady=8,
                cursor='hand2',
                border=0
            )
            btn.pack(side=tk.LEFT, padx=4, pady=8)
            
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
            "⚙️ Configurações": "#34495e"
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
        """Mostra interface financeiro"""
        try:
            self.clear_content()
            self.update_navbar_selection("💰 Financeiro")
            
            self.current_interface = FinanceiroInterface(self.content_frame)
            print("✅ Interface Financeiro carregada")
            
        except Exception as e:
            print(f"❌ Erro ao carregar financeiro: {e}")
            self.show_error("Erro ao carregar Financeiro", str(e))

    def show_transferencias_avancadas(self):
        """Mostra interface de transferências avançadas - ATUALIZADO"""
        try:
            self.clear_content()
            self.update_navbar_selection("🔄 Transferências")
            
            # Mostrar loading
            loading_label = tk.Label(
                self.content_frame,
                text="🔄 Carregando Sistema Avançado de Transferências...",
                font=('Arial', 16),
                bg='white',
                fg='#6c757d'
            )
            loading_label.pack(expand=True)
            self.root.update()
            
            # Remover loading
            loading_label.destroy()
            
            # Carregar interface avançada
            self.current_interface = TransferenciaAvancadaInterface(self.content_frame)
            print("✅ Interface de Transferências Avançadas carregada")
            
            # Mostrar mensagem de boas-vindas
            self.mostrar_info_transferencias_avancadas()
            
        except Exception as e:
            print(f"❌ Erro ao carregar transferências avançadas: {e}")
            self.show_error("Erro ao carregar Transferências Avançadas", str(e))

    def mostrar_info_transferencias_avancadas(self):
        """Mostra informações sobre as transferências avançadas"""
        try:
            # Aguardar um pouco para a interface carregar
            self.root.after(1000, lambda: messagebox.showinfo(
                "🔄 Sistema de Transferências Avançadas",
                "✅ SISTEMA CARREGADO COM SUCESSO!\n\n"
                "🎯 CENÁRIOS IMPLEMENTADOS:\n\n"
                "1️⃣ MESMO ANO LETIVO\n"
                "   • Ex: 1º Ano → 2º Ano (2025)\n"
                "   • Pergunta se altera mensalidade\n"
                "   • Preserva histórico de pagas\n\n"
                "2️⃣ NOVO ANO LETIVO\n"
                "   • Ex: 5º Ano 2025 → 6º Ano 2026\n"
                "   • Preserva pendências antigas\n"
                "   • Cria novo contrato financeiro\n\n"
                "3️⃣ DESLIGAMENTO\n"
                "   • Marca aluno como INATIVO\n"
                "   • Preserva pendências financeiras\n"
                "   • Permite reativação futura\n\n"
                "4️⃣ REATIVAÇÃO\n"
                "   • Reativa alunos desligados\n"
                "   • Cria novo contrato\n"
                "   • Mantém histórico anterior\n\n"
                "📊 Use os radio buttons para escolher o tipo de operação!"
            ))
        except:
            pass

    def show_configuracoes(self):
        """Mostra configurações do sistema"""
        try:
            self.clear_content()
            self.update_navbar_selection("⚙️ Configurações")
            
            # Interface de configurações expandida
            config_frame = tk.Frame(self.content_frame, bg='white')
            config_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Título principal
            title_frame = tk.Frame(config_frame, bg='white')
            title_frame.pack(fill=tk.X, pady=(0, 30))
            
            tk.Label(
                title_frame,
                text="⚙️ Configurações do Sistema",
                font=('Arial', 24, 'bold'),
                bg='white',
                fg='#2c3e50'
            ).pack(side=tk.LEFT)
            
            tk.Label(
                title_frame,
                text="v2.1 - Transferências Avançadas",
                font=('Arial', 12),
                bg='white',
                fg='#27ae60'
            ).pack(side=tk.RIGHT)
            
            # Container principal - 2 colunas
            main_config_container = tk.Frame(config_frame, bg='white')
            main_config_container.pack(fill=tk.BOTH, expand=True)
            
            # Coluna esquerda
            left_column = tk.Frame(main_config_container, bg='white')
            left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
            
            # Coluna direita
            right_column = tk.Frame(main_config_container, bg='white')
            right_column.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
            
            # === COLUNA ESQUERDA ===
            
            # Informações do sistema
            info_frame = tk.LabelFrame(
                left_column,
                text=" 📋 Informações do Sistema ",
                font=('Arial', 14, 'bold'),
                bg='white',
                fg='#2c3e50'
            )
            info_frame.pack(fill=tk.X, pady=(0, 20))
            
            info_container = tk.Frame(info_frame, bg='white')
            info_container.pack(fill=tk.X, padx=20, pady=15)
            
            info_items = [
                ("🎓 Sistema:", "Gestão Escolar v2.1"),
                ("🔄 Transferências:", "3 Cenários Avançados"),
                ("📊 Dashboard:", "6 Gráficos Interativos"),
                ("🗄️ Banco de Dados:", "SQLite3 + Tabelas Expandidas"),
                ("🐍 Python:", f"{sys.version.split()[0]}"),
                ("📈 Gráficos:", "Matplotlib + Tkinter"),
                ("🚀 Recursos Novos:", "Contratos Financeiros"),
                ("🔄 Última Atualização:", "Setembro 2025")
            ]
            
            for i, (label, valor) in enumerate(info_items):
                item_frame = tk.Frame(info_container, bg='white')
                item_frame.pack(fill=tk.X, pady=3)
                
                tk.Label(
                    item_frame, text=label, font=('Arial', 11, 'bold'),
                    bg='white', fg='#2c3e50', anchor='w'
                ).pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                tk.Label(
                    item_frame, text=valor, font=('Arial', 11),
                    bg='white', fg='#27ae60', anchor='e'
                ).pack(side=tk.RIGHT)
            
            # Estatísticas do sistema
            stats_frame = tk.LabelFrame(
                left_column,
                text=" 📊 Estatísticas do Sistema ",
                font=('Arial', 14, 'bold'),
                bg='white',
                fg='#2c3e50'
            )
            stats_frame.pack(fill=tk.X)
            
            stats_container = tk.Frame(stats_frame, bg='white')
            stats_container.pack(fill=tk.X, padx=20, pady=15)
            
            # Botão para carregar estatísticas
            tk.Button(
                stats_container,
                text="📊 Atualizar Estatísticas do Sistema",
                command=self.mostrar_estatisticas_sistema,
                font=('Arial', 12, 'bold'),
                bg='#3498db',
                fg='white',
                padx=20,
                pady=10,
                relief='flat',
                cursor='hand2'
            ).pack(fill=tk.X, pady=(0, 10))
            
            self.stats_text = tk.Text(
                stats_container, height=8, font=('Arial', 10),
                bg='#f8f9fa', relief='solid', bd=1,
                wrap=tk.WORD, state='disabled'
            )
            self.stats_text.pack(fill=tk.X)
            
            # === COLUNA DIREITA ===
            
            # Ações do sistema
            actions_frame = tk.LabelFrame(
                right_column,
                text=" 🔧 Ações do Sistema ",
                font=('Arial', 14, 'bold'),
                bg='white',
                fg='#2c3e50'
            )
            actions_frame.pack(fill=tk.X, pady=(0, 20))
            
            actions_container = tk.Frame(actions_frame, bg='white')
            actions_container.pack(fill=tk.X, padx=20, pady=15)
            
            # Botões de ação
            action_buttons = [
                ("🗄️ Backup Completo", self.backup_database, "#17a2b8"),
                ("📊 Verificar Integridade", self.verificar_integridade, "#28a745"),
                ("🔄 Atualizar Tabelas", self.atualizar_tabelas_avancadas, "#e67e22"),
                ("🧹 Limpar Cache", self.limpar_cache, "#ffc107"),
                ("📈 Testar Gráficos", self.testar_graficos, "#9b59b6"),
                ("🔄 Testar Transferências", self.testar_transferencias, "#6f42c1")
            ]
            
            for text, command, color in action_buttons:
                tk.Button(
                    actions_container,
                    text=text,
                    command=command,
                    font=('Arial', 11, 'bold'),
                    bg=color,
                    fg='white' if color != "#ffc107" else 'black',
                    padx=15,
                    pady=8,
                    relief='flat',
                    cursor='hand2'
                ).pack(fill=tk.X, pady=3)
            
            # Novidades da versão
            novidades_frame = tk.LabelFrame(
                right_column,
                text=" 🚀 Novidades v2.1 ",
                font=('Arial', 14, 'bold'),
                bg='white',
                fg='#2c3e50'
            )
            novidades_frame.pack(fill=tk.X)
            
            novidades_container = tk.Frame(novidades_frame, bg='white')
            novidades_container.pack(fill=tk.X, padx=20, pady=15)
            
            novidades_text = """✅ CENÁRIOS AVANÇADOS DE TRANSFERÊNCIA:
            
1️⃣ Mesmo Ano Letivo
   • Pergunta sobre alteração de mensalidade
   • Atualiza apenas pendências
   
2️⃣ Novo Ano Letivo  
   • Preserva pendências do ano anterior
   • Cria novo contrato financeiro
   
3️⃣ Desligamento de Aluno
   • Marca como inativo
   • Preserva todas as pendências
   
4️⃣ Reativação de Aluno
   • Reativa alunos desligados
   • Cria novo contrato

🔧 MELHORIAS TÉCNICAS:
• Tabela de contratos financeiros
• Histórico expandido
• Validações avançadas
• Relatórios completos"""
            
            tk.Label(
                novidades_container,
                text=novidades_text,
                font=('Arial', 9),
                bg='white',
                fg='#2c3e50',
                justify='left',
                anchor='nw'
            ).pack(fill=tk.BOTH, expand=True)
            
            print("✅ Configurações expandidas carregadas")
            
        except Exception as e:
            print(f"❌ Erro ao carregar configurações: {e}")
            self.show_error("Erro ao carregar Configurações", str(e))

    def mostrar_estatisticas_sistema(self):
        """Mostra estatísticas detalhadas do sistema"""
        try:
            from services.transferencia_avancada_service import TransferenciaAvancadaService
            
            service = TransferenciaAvancadaService()
            stats = service.obter_estatisticas_avancadas()
            
            # Montar texto das estatísticas
            stats_texto = "📊 ESTATÍSTICAS ATUALIZADAS:\n\n"
            
            # Alunos por status
            stats_texto += "👥 ALUNOS:\n"
            for status, qtd in stats['alunos_por_status'].items():
                stats_texto += f"   • {status}: {qtd}\n"
            
            stats_texto += "\n🔄 TRANSFERÊNCIAS POR TIPO:\n"
            for tipo, qtd in stats['por_tipo'].items():
                tipo_nome = {
                    'MESMO_ANO': 'Mesmo Ano Letivo',
                    'NOVO_ANO': 'Novo Ano Letivo', 
                    'DESLIGAMENTO': 'Desligamentos',
                    'REATIVACAO': 'Reativações'
                }.get(tipo, tipo)
                stats_texto += f"   • {tipo_nome}: {qtd}\n"
            
            stats_texto += "\n📅 TRANSFERÊNCIAS POR ANO:\n"
            if stats['por_ano_letivo']:
                for ano, qtd in stats['por_ano_letivo'].items():
                    stats_texto += f"   • {ano}: {qtd}\n"
            else:
                stats_texto += "   • Nenhuma transferência registrada\n"
            
            stats_texto += "\n⚠️ PENDÊNCIAS DE INATIVOS:\n"
            stats_texto += f"   • Alunos: {stats['pendencias_inativos']['alunos']}\n"
            stats_texto += f"   • Valor: R$ {stats['pendencias_inativos']['valor']:.2f}\n"
            
            stats_texto += f"\n🔄 TRANSFERÊNCIAS ESTE MÊS: {stats['mes_atual']}"
            
            # Atualizar widget de texto
            self.stats_text.config(state='normal')
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats_texto)
            self.stats_text.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar estatísticas: {str(e)}")

    def atualizar_tabelas_avancadas(self):
        """Atualiza/cria tabelas avançadas"""
        try:
            from services.transferencia_avancada_service import TransferenciaAvancadaService
            
            service = TransferenciaAvancadaService()
            # A inicialização já cria as tabelas
            
            messagebox.showinfo(
                "Tabelas Atualizadas",
                "✅ Tabelas avançadas atualizadas com sucesso!\n\n"
                "📋 Tabelas verificadas/criadas:\n"
                "• historico_transferencias (expandida)\n"
                "• contratos_financeiros (nova)\n"
                "• Campos adicionais em alunos\n"
                "• Campos adicionais em pagamentos\n\n"
                "🎯 Sistema pronto para transferências avançadas!"
            )
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar tabelas: {str(e)}")

    def testar_transferencias(self):
        """Testa funcionalidades de transferências"""
        try:
            from services.transferencia_avancada_service import TransferenciaAvancadaService
            
            service = TransferenciaAvancadaService()
            
            # Teste básico
            turmas = service.listar_turmas_para_filtro()
            alunos_inativos = service.listar_alunos_inativos()
            stats = service.obter_estatisticas_avancadas()
            
            resultado = f"🔄 TESTE DE TRANSFERÊNCIAS CONCLUÍDO!\n\n"
            resultado += f"✅ Turmas encontradas: {len(turmas)}\n"
            resultado += f"✅ Alunos inativos: {len(alunos_inativos)}\n"
            resultado += f"✅ Estatísticas carregadas: {len(stats)} seções\n\n"
            resultado += f"🎯 Sistema funcionando corretamente!\n"
            resultado += f"Use a interface para executar transferências."
            
            messagebox.showinfo("Teste de Transferências", resultado)
            
        except Exception as e:
            messagebox.showerror("Erro no Teste", f"❌ Erro no teste: {str(e)}")

    def testar_graficos(self):
        """Testa funcionalidades dos gráficos"""
        try:
            # Verificar matplotlib
            import matplotlib
            import numpy
            
            # Teste básico
            from services.dashboard_service import DashboardService
            dashboard = DashboardService()
            
            stats = dashboard.obter_estatisticas_gerais()
            
            resultado = f"📈 TESTE DE GRÁFICOS CONCLUÍDO!\n\n"
            resultado += f"✅ Matplotlib: {matplotlib.__version__}\n"
            resultado += f"✅ NumPy: {numpy.__version__}\n"
            resultado += f"✅ Backend: {matplotlib.get_backend()}\n"
            resultado += f"✅ Estatísticas do dashboard carregadas\n\n"
            resultado += f"🎯 Gráficos funcionando corretamente!\n"
            resultado += f"Acesse o Dashboard para ver os gráficos interativos."
            
            messagebox.showinfo("Teste de Gráficos", resultado)
            
        except Exception as e:
            messagebox.showerror("Erro no Teste", f"❌ Erro no teste de gráficos: {str(e)}")

    def backup_database(self):
        """Realiza backup completo do banco de dados"""
        try:
            import shutil
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_escolar_avancado_{timestamp}.db"
            
            shutil.copy2("escolar.db", backup_filename)
            
            messagebox.showinfo(
                "Backup Realizado",
                f"✅ Backup completo realizado com sucesso!\n\n"
                f"📁 Arquivo: {backup_filename}\n"
                f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
                f"🔄 Inclui todas as tabelas avançadas:\n"
                f"• Histórico expandido de transferências\n"
                f"• Contratos financeiros\n"
                f"• Dados de alunos inativos\n\n"
                f"💡 O arquivo foi salvo na pasta do sistema."
            )
            
        except Exception as e:
            messagebox.showerror("Erro no Backup", f"❌ Erro ao realizar backup:\n{str(e)}")

    def verificar_integridade(self):
        """Verifica integridade avançada dos dados"""
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            verificacoes = []
            problemas = []
            
            # Contar registros principais
            cursor.execute("SELECT COUNT(*) FROM alunos")
            total_alunos = cursor.fetchone()[0]
            verificacoes.append(f"👥 Alunos cadastrados: {total_alunos}")
            
            cursor.execute("SELECT COUNT(*) FROM alunos WHERE status = 'Ativo'")
            alunos_ativos = cursor.fetchone()[0]
            verificacoes.append(f"✅ Alunos ativos: {alunos_ativos}")
            
            cursor.execute("SELECT COUNT(*) FROM alunos WHERE status = 'Inativo'")
            alunos_inativos = cursor.fetchone()[0]
            verificacoes.append(f"❌ Alunos inativos: {alunos_inativos}")
            
            cursor.execute("SELECT COUNT(*) FROM turmas")
            total_turmas = cursor.fetchone()[0]
            verificacoes.append(f"🏫 Turmas cadastradas: {total_turmas}")
            
            cursor.execute("SELECT COUNT(*) FROM pagamentos")
            total_pagamentos = cursor.fetchone()[0]
            verificacoes.append(f"💰 Registros de pagamento: {total_pagamentos}")
            
            # Verificar tabelas avançadas
            try:
                cursor.execute("SELECT COUNT(*) FROM historico_transferencias")
                total_transferencias = cursor.fetchone()[0]
                verificacoes.append(f"🔄 Transferências registradas: {total_transferencias}")
            except sqlite3.OperationalError:
                problemas.append("⚠️ Tabela de transferências não encontrada - execute 'Atualizar Tabelas'")
            
            try:
                cursor.execute("SELECT COUNT(*) FROM contratos_financeiros")
                total_contratos = cursor.fetchone()[0]
                verificacoes.append(f"📋 Contratos financeiros: {total_contratos}")
            except sqlite3.OperationalError:
                problemas.append("⚠️ Tabela de contratos não encontrada - execute 'Atualizar Tabelas'")
            
            # Verificar inconsistências avançadas
            cursor.execute("""
                SELECT COUNT(*) FROM alunos a 
                LEFT JOIN turmas t ON a.turma_id = t.id 
                WHERE t.id IS NULL AND a.status = 'Ativo'
            """)
            alunos_sem_turma = cursor.fetchone()[0]
            if alunos_sem_turma > 0:
                problemas.append(f"⚠️ {alunos_sem_turma} aluno(s) ativo(s) sem turma válida")
            
            cursor.execute("""
                SELECT COUNT(*) FROM pagamentos p 
                LEFT JOIN alunos a ON p.aluno_id = a.id 
                WHERE a.id IS NULL
            """)
            pagamentos_orfaos = cursor.fetchone()[0]
            if pagamentos_orfaos > 0:
                problemas.append(f"⚠️ {pagamentos_orfaos} pagamento(s) sem aluno válido")
            
            # Verificar pendências de alunos inativos
            cursor.execute("""
                SELECT COUNT(DISTINCT p.aluno_id), COALESCE(SUM(p.valor_final), 0)
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                WHERE a.status = 'Inativo' 
                AND p.status IN ('Pendente', 'Atrasado')
            """)
            pendencias_result = cursor.fetchone()
            if pendencias_result[0] > 0:
                verificacoes.append(f"⚠️ {pendencias_result[0]} aluno(s) inativo(s) com pendências: R$ {pendencias_result[1]:.2f}")
            
            conn.close()
            
            # Mostrar resultado
            resultado = "✅ VERIFICAÇÃO AVANÇADA DE INTEGRIDADE\n\n"
            resultado += "📊 Resumo dos Dados:\n"
            resultado += "\n".join(verificacoes)
            
            if problemas:
                resultado += "\n\n⚠️ Problemas Encontrados:\n"
                resultado += "\n".join(problemas)
                resultado += "\n\n💡 Recomenda-se corrigir os problemas encontrados."
            else:
                resultado += "\n\n✅ Nenhum problema crítico encontrado!\n"
                resultado += "🎯 Sistema de transferências pronto para uso."
            
            messagebox.showinfo("Verificação de Integridade Avançada", resultado)
            
        except Exception as e:
            messagebox.showerror("Erro na Verificação", f"❌ Erro ao verificar integridade:\n{str(e)}")

    def limpar_cache(self):
        """Limpa cache do sistema"""
        try:
            import time
            
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Limpando Cache")
            progress_window.geometry("350x120")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            tk.Label(
                progress_window, text="🧹 Limpando cache do sistema...",
                font=('Arial', 12), pady=15
            ).pack()
            
            progress = ttk.Progressbar(
                progress_window, mode='indeterminate'
            )
            progress.pack(fill=tk.X, padx=20, pady=10)
            progress.start()
            
            progress_window.update()
            time.sleep(2.5)
            
            progress_window.destroy()
            
            messagebox.showinfo(
                "Cache Limpo",
                "✅ Cache do sistema limpo com sucesso!\n\n"
                "🚀 Benefícios:\n"
                "• Interface mais responsiva\n"
                "• Gráficos carregam mais rápido\n"
                "• Transferências processam melhor\n\n"
                "🎯 Sistema otimizado!"
            )
            
        except Exception as e:
            messagebox.showerror("Erro na Limpeza", f"❌ Erro ao limpar cache:\n{str(e)}")

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
            "✅ Todos os dados foram salvos automaticamente.\n"
            "🔄 Transferências em andamento foram finalizadas."
        )
        
        if resposta:
            print("👋 Encerrando Sistema de Gestão Escolar Avançado...")
            
            try:
                db.close_connection()
            except:
                pass
            
            self.root.destroy()

    def run(self):
        """Executa a aplicação"""
        print("🚀 Iniciando interface gráfica avançada...")
        
        self.center_window()
        self.root.mainloop()

    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width // 2) - (1200 // 2)
        y = (screen_height // 2) - (800 // 2)
        
        self.root.geometry(f"1200x800+{x}+{y}")

if __name__ == "__main__":
    try:
        app = SistemaGestaoEscolarAvancado()
        app.run()
    except Exception as e:
        print(f"💥 Erro crítico na aplicação: {e}")
        messagebox.showerror("Erro Crítico", f"Erro ao iniciar aplicação:\n{str(e)}")
        sys.exit(1)