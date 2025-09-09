import tkinter as tk
from tkinter import ttk, messagebox
from services.configuracao_service import ConfiguracaoService
from datetime import datetime

class ConfiguracoesInterface:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.parent_frame.configure(bg='white')
        self.config_service = ConfiguracaoService()
        self.create_interface()
    
    def create_interface(self):
        """Cria interface básica de configurações"""
        # Container principal
        main_container = tk.Frame(self.parent_frame, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Título
        tk.Label(
            main_container,
            text="⚙️ Configurações do Sistema",
            font=('Arial', 24, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(pady=(0, 30))
        
        # Seção Escola
        self.create_escola_section(main_container)
        
        # Seção Sistema
        self.create_sistema_section(main_container)
    
    def create_escola_section(self, parent):
        """Seção de configurações da escola"""
        escola_frame = tk.LabelFrame(
            parent,
            text="  🏫 Dados da Escola  ",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        escola_frame.pack(fill=tk.X, pady=(0, 30))
        
        content = tk.Frame(escola_frame, bg='white')
        content.pack(fill=tk.X, padx=20, pady=15)
        
        # Campos da escola
        fields = [
            ("Nome da Escola:", "escola_nome"),
            ("CNPJ:", "escola_cnpj"),
            ("Endereço:", "escola_endereco"),
            ("Telefone:", "escola_telefone"),
            ("Email:", "escola_email")
        ]
        
        self.escola_vars = {}
        
        for i, (label, field) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2
            
            tk.Label(content, text=label, font=('Arial', 10, 'bold'),
                    bg='white', fg='#2c3e50').grid(row=row, column=col, 
                    sticky='w', padx=(0, 10), pady=8)
            
            var = tk.StringVar()
            entry = tk.Entry(content, textvariable=var, width=30,
                           font=('Arial', 10), relief='solid', bd=1)
            entry.grid(row=row, column=col+1, sticky='w', 
                      padx=(0, 30), pady=8, ipady=5)
            
            self.escola_vars[field] = var
        
        # Botão salvar
        tk.Button(
            content, text="💾 Salvar Configurações da Escola",
            command=self.salvar_escola, bg='#27ae60', fg='white',
            font=('Arial', 11, 'bold'), padx=20, pady=8,
            relief='flat', cursor='hand2'
        ).grid(row=len(fields)//2 + 1, column=0, columnspan=4, pady=15)
        
        # Carregar dados existentes
        self.carregar_dados_escola()
    
    def create_sistema_section(self, parent):
        """Seção de informações do sistema"""
        sistema_frame = tk.LabelFrame(
            parent,
            text="  💻 Informações do Sistema  ",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        sistema_frame.pack(fill=tk.X)
        
        content = tk.Frame(sistema_frame, bg='white')
        content.pack(fill=tk.X, padx=20, pady=15)
        
        # Informações do sistema
        info_items = [
            ("📅 Data/Hora:", datetime.now().strftime('%d/%m/%Y - %H:%M:%S')),
            ("💻 Versão:", "Sistema de Gestão Escolar v2.0"),
            ("🗃️ Banco de Dados:", "SQLite Local"),
            ("🔒 Status:", "Online e Operacional"),
        ]
        
        for i, (label, value) in enumerate(info_items):
            tk.Label(content, text=label, font=('Arial', 11, 'bold'),
                    bg='white', fg='#2c3e50').grid(row=i, column=0, 
                    sticky='w', pady=5)
            
            tk.Label(content, text=value, font=('Arial', 11),
                    bg='white', fg='#27ae60').grid(row=i, column=1, 
                    sticky='w', padx=(20, 0), pady=5)
        
        # Botões de ação
        buttons_frame = tk.Frame(content, bg='white')
        buttons_frame.grid(row=len(info_items), column=0, columnspan=2, pady=20)
        
        tk.Button(
            buttons_frame, text="🔄 Atualizar Dados", command=self.atualizar_dados,
            bg='#3498db', fg='white', font=('Arial', 10, 'bold'),
            padx=15, pady=8, relief='flat', cursor='hand2'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            buttons_frame, text="ℹ️ Sobre o Sistema", command=self.mostrar_sobre,
            bg='#9b59b6', fg='white', font=('Arial', 10, 'bold'),
            padx=15, pady=8, relief='flat', cursor='hand2'
        ).pack(side=tk.LEFT)
    
    def carregar_dados_escola(self):
        """Carrega dados salvos da escola"""
        try:
            # Definir valores padrão
            defaults = {
                'escola_nome': 'Escola Exemplo',
                'escola_cnpj': '12.345.678/0001-90',
                'escola_endereco': 'Rua da Educação, 123',
                'escola_telefone': '(11) 3333-4444',
                'escola_email': 'contato@escola.edu.br'
            }
            
            for field, var in self.escola_vars.items():
                valor = self.config_service.obter_configuracao(field, defaults.get(field, ''))
                var.set(valor)
                
        except Exception as e:
            print(f"Erro ao carregar dados da escola: {e}")
    
    def salvar_escola(self):
        """Salva configurações da escola"""
        try:
            dados = {}
            for field, var in self.escola_vars.items():
                valor = var.get().strip()
                if valor:
                    self.config_service.salvar_configuracao(field, valor)
                    dados[field] = valor
            
            messagebox.showinfo("Sucesso", "✅ Configurações da escola salvas com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"❌ Erro ao salvar configurações: {str(e)}")
    
    def atualizar_dados(self):
        """Atualiza informações na tela"""
        messagebox.showinfo("Atualizado", "✅ Dados atualizados com sucesso!")
        self.create_interface()  # Recriar interface
    
    def mostrar_sobre(self):
        """Mostra informações sobre o sistema"""
        sobre_texto = """
🎓 Sistema de Gestão Escolar v2.0

📚 Funcionalidades:
• Gestão completa de alunos e turmas
• Controle financeiro manual
• Dashboard com estatísticas
• Relatórios de inadimplência
• Interface moderna e intuitiva

💻 Tecnologia:
• Python 3.7+
• Tkinter (Interface Gráfica)
• SQLite (Banco de Dados)

👨‍💻 Desenvolvido com ❤️ em Python
        """
        
        messagebox.showinfo("Sobre o Sistema", sobre_texto)
