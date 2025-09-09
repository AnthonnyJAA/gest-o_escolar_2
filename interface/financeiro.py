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
        """Cria a interface simplificada do financeiro"""
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
        self.create_simple_cards(main_container)
        
        # Tabela de mensalidades
        self.create_simple_table(main_container)
        
        # Ações
        self.create_action_buttons(main_container)
    
    def create_simple_cards(self, parent):
        """Cria cards simples de resumo"""
        cards_frame = tk.Frame(parent, bg='white')
        cards_frame.pack(fill=tk.X, pady=(0, 20))
        
        try:
            # Obter estatísticas básicas
            stats = self.financeiro_service.obter_estatisticas_financeiras()
            
            # Card 1: Receita do Mês
            self.create_simple_card(
                cards_frame, "💰 Receita do Mês", 
                format_currency(stats.get('receita_mes', 0)), "#27ae60", 0, 0
            )
            
            # Card 2: Mensalidades Pagas
            self.create_simple_card(
                cards_frame, "✅ Pagas", 
                str(stats.get('total_pagos', 0)), "#2ecc71", 0, 1
            )
            
            # Card 3: Mensalidades Pendentes
            self.create_simple_card(
                cards_frame, "⏳ Pendentes", 
                str(stats.get('total_pendentes', 0)), "#3498db", 0, 2
            )
            
            # Card 4: Mensalidades Atrasadas
            self.create_simple_card(
                cards_frame, "🔴 Atrasadas", 
                str(stats.get('total_atrasados', 0)), "#e74c3c", 0, 3
            )
            
        except Exception as e:
            print(f"Erro ao carregar estatísticas: {e}")
            # Cards com valores padrão
            self.create_simple_card(cards_frame, "💰 Receita", "R$ 0,00", "#27ae60", 0, 0)
            self.create_simple_card(cards_frame, "✅ Pagas", "0", "#2ecc71", 0, 1)
            self.create_simple_card(cards_frame, "⏳ Pendentes", "0", "#3498db", 0, 2)
            self.create_simple_card(cards_frame, "🔴 Atrasadas", "0", "#e74c3c", 0, 3)
        
        # Configurar grid
        for i in range(4):
            cards_frame.columnconfigure(i, weight=1)
    
    def create_simple_card(self, parent, title, value, color, row, col):
        """Cria um card simples"""
        card = tk.Frame(parent, bg=color, relief='raised', bd=2)
        card.grid(row=row, column=col, padx=5, pady=5, sticky='ew', ipady=15)
        
        tk.Label(card, text=title, font=('Arial', 10, 'bold'), 
                bg=color, fg='white').pack(pady=5)
        tk.Label(card, text=value, font=('Arial', 14, 'bold'), 
                bg=color, fg='white').pack(pady=5)
    
    def create_simple_table(self, parent):
        """Cria tabela simples de mensalidades"""
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
        columns = ('ID', 'Aluno', 'Turma', 'Mês/Ano', 'Valor', 'Vencimento', 'Status')
        self.tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=12)
        
        # Configurar colunas
        column_widths = {
            'ID': 50, 'Aluno': 200, 'Turma': 120, 'Mês/Ano': 80, 
            'Valor': 100, 'Vencimento': 100, 'Status': 100
        }
        
        for col in columns:
            self.tree.heading(col, text=col, anchor='center')
            self.tree.column(col, width=column_widths[col], anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_container, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Posicionar
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Configurar cores
        self.tree.tag_configure('pago', background='#d5f4e6')
        self.tree.tag_configure('pendente', background='#fff3cd')
        self.tree.tag_configure('atrasado', background='#f8d7da')
        
        # Bind duplo clique
        self.tree.bind('<Double-1>', lambda e: self.registrar_pagamento())
    
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
            buttons_frame, text="🔄 Atualizar", 
            command=self.carregar_mensalidades,
            bg='#3498db', fg='white', font=('Arial', 10, 'bold'),
            padx=15, pady=8, relief='flat', cursor='hand2'
        ).pack(side=tk.LEFT)
    
    def carregar_dados_iniciais(self):
        """Carrega dados iniciais"""
        try:
            print("📋 Carregando mensalidades...")
            self.carregar_mensalidades()
            print("✅ Dados carregados com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
    
    def carregar_mensalidades(self):
        """Carrega mensalidades na tabela"""
        try:
            # Limpar tabela
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Carregar mensalidades
            mensalidades = self.financeiro_service.listar_mensalidades()
            
            print(f"📋 Carregando {len(mensalidades)} mensalidades...")
            
            for m in mensalidades:
                # Determinar status e cor
                status = m.get('status_calculado', m.get('status', 'Pendente'))
                
                if status == 'Pago':
                    tag = 'pago'
                    status_display = '✅ Pago'
                elif status == 'Atrasado':
                    tag = 'atrasado' 
                    status_display = '🔴 Atrasado'
                else:
                    tag = 'pendente'
                    status_display = '⏳ Pendente'
                
                valores = (
                    m.get('id', ''),
                    m.get('aluno_nome', '')[:25] + "..." if len(m.get('aluno_nome', '')) > 25 else m.get('aluno_nome', ''),
                    f"{m.get('turma_nome', '')} - {m.get('turma_serie', '')}",
                    m.get('mes_referencia', ''),
                    format_currency(m.get('valor_final', 0)),
                    format_date(m.get('data_vencimento', '')),
                    status_display
                )
                
                self.tree.insert('', tk.END, values=valores, tags=(tag,))
            
            # Atualizar cards
            self.update_cards()
            
            print(f"✅ {len(mensalidades)} mensalidades carregadas")
            
        except Exception as e:
            print(f"❌ Erro ao carregar mensalidades: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar mensalidades:\n{str(e)}")
    
    def update_cards(self):
        """Atualiza os cards com novos dados"""
        try:
            # Recriar apenas os cards
            for widget in self.parent_frame.winfo_children():
                if hasattr(widget, 'winfo_children'):
                    for child in widget.winfo_children():
                        if child.winfo_class() == 'Frame' and len(child.winfo_children()) == 4:
                            # É provavelmente o frame dos cards, atualizar
                            self.create_simple_cards(widget)
                            break
        except Exception as e:
            print(f"Erro ao atualizar cards: {e}")
    
    def registrar_pagamento(self):
        """Registra pagamento simples"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma mensalidade!")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        if '✅ Pago' in str(values[6]):
            messagebox.showinfo("Informação", "Mensalidade já está paga!")
            return
        
        # Janela simples de confirmação
        if messagebox.askyesno("Confirmar Pagamento", 
                              f"Confirmar pagamento de {values[4]} do aluno {values[1]}?"):
            
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
                    messagebox.showinfo("Sucesso", "Pagamento registrado!")
                    self.carregar_mensalidades()
                else:
                    messagebox.showerror("Erro", f"Erro: {resultado['error']}")
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")
    
    def cancelar_pagamento(self):
        """Cancela pagamento"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma mensalidade!")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        if '✅ Pago' not in str(values[6]):
            messagebox.showinfo("Informação", "Mensalidade não está paga!")
            return
        
        if messagebox.askyesno("Confirmar", 
                              f"Cancelar pagamento de {values[4]} do aluno {values[1]}?"):
            
            try:
                resultado = self.financeiro_service.cancelar_pagamento(values[0])
                
                if resultado['success']:
                    messagebox.showinfo("Sucesso", "Pagamento cancelado!")
                    self.carregar_mensalidades()
                else:
                    messagebox.showerror("Erro", f"Erro: {resultado['error']}")
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")
    
    def mostrar_inadimplentes(self):
        """Mostra lista de inadimplentes"""
        try:
            inadimplentes = self.financeiro_service.buscar_inadimplentes()
            
            # Criar janela
            inad_window = tk.Toplevel()
            inad_window.title("📋 Relatório de Inadimplência")
            inad_window.geometry("800x500")
            inad_window.configure(bg='white')
            
            tk.Label(
                inad_window, text=f"📋 Relatório de Inadimplência - {len(inadimplentes)} alunos",
                font=('Arial', 14, 'bold'), bg='white', fg='#e74c3c'
            ).pack(pady=20)
            
            if not inadimplentes:
                tk.Label(
                    inad_window, text="✅ Parabéns! Não há inadimplentes!",
                    font=('Arial', 12), bg='white', fg='#27ae60'
                ).pack(expand=True)
            else:
                # Lista simples
                text_area = tk.Text(inad_window, height=20, font=('Courier', 10))
                text_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
                
                text_area.insert(tk.END, "ALUNO                    TURMA              VALOR DEVIDO    TEL. RESPONSÁVEL\n")
                text_area.insert(tk.END, "-" * 80 + "\n")
                
                total_devido = 0
                for inad in inadimplentes:
                    linha = f"{inad['aluno_nome'][:20]:<20} {inad['turma_nome'][:15]:<15} {format_currency(inad['valor_total_devido']):<12} {inad['responsavel_telefone']:<15}\n"
                    text_area.insert(tk.END, linha)
                    total_devido += inad['valor_total_devido']
                
                text_area.insert(tk.END, "\n" + "-" * 80 + "\n")
                text_area.insert(tk.END, f"TOTAL EM ATRASO: {format_currency(total_devido)}\n")
                
                text_area.config(state=tk.DISABLED)
            
            tk.Button(
                inad_window, text="Fechar", command=inad_window.destroy,
                bg='#6c757d', fg='white', font=('Arial', 11, 'bold'),
                padx=20, pady=8
            ).pack(pady=20)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar inadimplentes: {str(e)}")
