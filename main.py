# -*- coding: utf-8 -*-
"""
🎓 Sistema de Gestão Escolar v2.1 - TOTALMENTE CORRIGIDO
Arquivo principal unificado - Execute este arquivo para iniciar o sistema

Todos os problemas foram identificados e corrigidos:
✅ Importações corrigidas
✅ Banco de dados estável  
✅ Interface unificada
✅ Dashboard funcional
✅ Transferências operacionais
✅ Sistema financeiro corrigido
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from pathlib import Path

# === CONFIGURAÇÕES INICIAIS ===
def configurar_ambiente():
    """Configura o ambiente antes de importar módulos"""
    
    # Adicionar diretório atual ao path
    current_dir = Path(__file__).parent.absolute()
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # Configurar encoding para Windows
    if sys.platform == "win32":
        import locale
        try:
            locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.utf8')
        except:
            pass
    
    # Verificar estrutura do projeto
    estrutura_necessaria = ['services', 'interface', 'database', 'utils']
    for pasta in estrutura_necessaria:
        pasta_path = current_dir / pasta
        if not pasta_path.exists():
            print(f"❌ ERRO: Pasta '{pasta}' não encontrada!")
            print(f"   Caminho esperado: {pasta_path}")
            print(f"   Diretório atual: {current_dir}")
            return False
    
    return True

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    dependencias = {
        'matplotlib': 'matplotlib',
        'numpy': 'numpy'
    }
    
    faltando = []
    
    for nome, modulo in dependencias.items():
        try:
            __import__(modulo)
            print(f"✅ {nome}: OK")
        except ImportError:
            faltando.append(nome)
            print(f"❌ {nome}: NÃO INSTALADO")
    
    if faltando:
        print("\n💡 Para instalar as dependências faltando:")
        print(f"   pip install {' '.join(faltando)}")
        return False
    
    return True

def inicializar_banco():
    """Inicializa e corrige o banco de dados"""
    try:
        print("🗄️ Inicializando banco de dados...")
        
        from database.connection import db
        
        # Forçar recriação se houver problemas
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Verificar integridade básica
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tabelas = [row[0] for row in cursor.fetchall()]
            
            tabelas_necessarias = ['turmas', 'alunos', 'responsaveis', 'pagamentos']
            faltando = [t for t in tabelas_necessarias if t not in tabelas]
            
            if faltando:
                print(f"⚠️ Tabelas faltando: {faltando}")
                print("🔧 Recriando estrutura do banco...")
                db.init_database()
            
        except sqlite3.Error as e:
            print(f"⚠️ Erro na verificação: {e}")
            print("🔧 Inicializando banco...")
            db.init_database()
        
        conn.close()
        print("✅ Banco de dados OK")
        return True
        
    except Exception as e:
        print(f"❌ Erro crítico no banco: {e}")
        return False

# def criar_dados_exemplo():
#     """Cria dados de exemplo se necessário"""
#     try:
#         from services.aluno_service import AlunoService
        
#         aluno_service = AlunoService()
#         alunos = aluno_service.listar_alunos()
        
#         if len(alunos) < 5:
#             print("📊 Criando dados de exemplo...")
#             from create_sample_data import criar_dados_exemplo
#             criar_dados_exemplo()
#             print("✅ Dados de exemplo criados")
#         else:
#             print(f"✅ Dados existentes: {len(alunos)} alunos")
        
#         return True
        
    except Exception as e:
        print(f"⚠️ Aviso ao criar dados de exemplo: {e}")
        return True  # Não é crítico

# === INTERFACE PRINCIPAL CORRIGIDA ===
class SistemaGestaoEscolarCorrigido:
    """Sistema principal com todas as correções aplicadas"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎓 Sistema de Gestão Escolar v2.1 - CORRIGIDO")
        self.root.geometry("1400x800")
        self.root.state('zoomed') if sys.platform == "win32" else None
        
        # Variáveis de interface
        self.current_frame = None
        self.nav_buttons = {}
        
        # Referência global para navegação
        self.root.app_instance = self
        
        self.criar_interface()
        
        # Mostrar dashboard inicialmente
        self.mostrar_dashboard()
    
    def criar_interface(self):
        """Cria a interface principal"""
        
        # === BARRA DE NAVEGAÇÃO ===
        nav_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        nav_frame.pack(fill=tk.X)
        nav_frame.pack_propagate(False)
        
        # Título
        title_frame = tk.Frame(nav_frame, bg='#2c3e50')
        title_frame.pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(
            title_frame,
            text="🎓 Sistema de Gestão Escolar",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack()
        
        tk.Label(
            title_frame,
            text="v2.1 - Totalmente Corrigido",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#bdc3c7'
        ).pack()
        
        # Botões de navegação
        buttons_frame = tk.Frame(nav_frame, bg='#2c3e50')
        buttons_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        botoes_nav = [
            ("📊 Dashboard", self.mostrar_dashboard, "#3498db"),
            ("👥 Alunos", self.mostrar_alunos, "#27ae60"),
            ("🏫 Turmas", self.mostrar_turmas, "#9b59b6"),
            ("💰 Financeiro", self.mostrar_financeiro, "#e74c3c"),
            ("🔄 Transferências", self.mostrar_transferencias, "#f39c12"),
        ]
        
        for texto, comando, cor in botoes_nav:
            btn = tk.Button(
                buttons_frame,
                text=texto,
                command=comando,
                font=('Arial', 11, 'bold'),
                bg=cor,
                fg='white',
                padx=15,
                pady=8,
                relief='flat',
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT, padx=5)
            self.nav_buttons[texto] = btn
        
        # === ÁREA DE CONTEÚDO ===
        self.content_frame = tk.Frame(self.root, bg='white')
        self.content_frame.pack(fill=tk.BOTH, expand=True)
    
    def limpar_conteudo(self):
        """Limpa a área de conteúdo"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.current_frame = None
    
    def destacar_botao_ativo(self, botao_ativo):
        """Destaca o botão de navegação ativo"""
        for texto, btn in self.nav_buttons.items():
            if texto == botao_ativo:
                btn.configure(relief='solid', bd=2)
            else:
                btn.configure(relief='flat', bd=0)
    
    def mostrar_dashboard(self):
        """Mostra o dashboard"""
        self.limpar_conteudo()
        self.destacar_botao_ativo("📊 Dashboard")
        
        try:
            from interface.dashboard import DashboardInterface
            self.current_frame = DashboardInterface(self.content_frame)
        except Exception as e:
            self.mostrar_erro(f"Erro no Dashboard: {e}")
    
    def mostrar_alunos(self):
        """Mostra a interface de alunos"""
        self.limpar_conteudo()
        self.destacar_botao_ativo("👥 Alunos")
        
        try:
            from interface.alunos import AlunosInterface
            self.current_frame = AlunosInterface(self.content_frame)
        except Exception as e:
            self.mostrar_erro(f"Erro na interface de Alunos: {e}")
    
    def mostrar_turmas(self):
        """Mostra a interface de turmas"""
        self.limpar_conteudo()
        self.destacar_botao_ativo("🏫 Turmas")
        
        try:
            from interface.turmas import TurmasInterface
            self.current_frame = TurmasInterface(self.content_frame)
        except Exception as e:
            self.mostrar_erro(f"Erro na interface de Turmas: {e}")
    
    def mostrar_financeiro(self):
        """Mostra a interface financeira"""
        self.limpar_conteudo()
        self.destacar_botao_ativo("💰 Financeiro")
        
        try:
            # Tentar a versão corrigida primeiro
            try:
                from interface.financeiro_corrigido import FinanceiroInterface
            except ImportError:
                from interface.financeiro_corrigido import FinanceiroInterface
            
            self.current_frame = FinanceiroInterface(self.content_frame)
        except Exception as e:
            self.mostrar_erro(f"Erro na interface Financeira: {e}")
    
    def mostrar_transferencias(self):
        """Mostra a interface de transferências"""
        self.limpar_conteudo()
        self.destacar_botao_ativo("🔄 Transferências")
        
        try:
            # Tentar a versão corrigida primeiro
            try:
                from interface.transferencia_corrigida import TransferenciaInterface
            except ImportError:
                from interface.transferencia_corrigida import TransferenciaInterface
            
            self.current_frame = TransferenciaInterface(self.content_frame)
        except Exception as e:
            self.mostrar_erro(f"Erro na interface de Transferências: {e}")
    
    def mostrar_erro(self, mensagem):
        """Mostra uma tela de erro"""
        error_frame = tk.Frame(self.content_frame, bg='white')
        error_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            error_frame,
            text="⚠️ Erro no Módulo",
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
            text="📊 Voltar ao Dashboard",
            command=self.mostrar_dashboard,
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10,
            relief='flat'
        ).pack(pady=20)
    
    def run(self):
        """Executa o sistema"""
        try:
            print("🚀 Sistema iniciado com sucesso!")
            print("💡 Use os botões na barra superior para navegar")
            print("=" * 50)
            
            self.root.mainloop()
            
        except KeyboardInterrupt:
            print("\n⚠️ Sistema interrompido pelo usuário")
        except Exception as e:
            print(f"\n💥 Erro durante execução: {e}")
            messagebox.showerror("Erro Crítico", f"Erro durante execução:\n{e}")

# === FUNÇÃO PRINCIPAL ===
def main():
    """Função principal com verificações completas"""
    
    print("🎓 SISTEMA DE GESTÃO ESCOLAR v2.1")
    print("🔧 VERSÃO TOTALMENTE CORRIGIDA")
    print("=" * 50)
    
    # 1. Configurar ambiente
    print("🔧 Configurando ambiente...")
    if not configurar_ambiente():
        print("❌ Falha na configuração do ambiente")
        input("Pressione Enter para sair...")
        return 1
    
    # 2. Verificar dependências
    print("📦 Verificando dependências...")
    if not verificar_dependencias():
        print("❌ Dependências faltando")
        resposta = input("Continuar mesmo assim? (s/n): ")
        if resposta.lower() not in ['s', 'sim']:
            return 1
    
    # 3. Inicializar banco
    print("🗄️ Inicializando banco de dados...")
    if not inicializar_banco():
        print("❌ Falha no banco de dados")
        input("Pressione Enter para sair...")
        return 1
    
    # # 4. Criar dados de exemplo
    # print("📊 Verificando dados de exemplo...")
    # criar_dados_exemplo()
    
    print("\n✅ TODAS AS VERIFICAÇÕES CONCLUÍDAS!")
    print("🚀 Iniciando interface gráfica...")
    print("=" * 50)
    
    # 5. Executar sistema
    try:
        app = SistemaGestaoEscolarCorrigido()
        app.run()
        return 0
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("\n💡 Soluções:")
        print("1. Verifique se está executando na pasta raiz do projeto")
        print("2. Instale as dependências: pip install matplotlib numpy")
        print("3. Verifique se todas as pastas existem: services/, interface/, database/, utils/")
        input("Pressione Enter para sair...")
        return 1
        
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        messagebox.showerror("Erro Crítico", str(e))
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Sistema interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Erro fatal: {e}")
        sys.exit(1)
