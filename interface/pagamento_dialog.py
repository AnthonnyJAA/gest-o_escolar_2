import tkinter as tk
from tkinter import ttk, messagebox
from utils.formatters import format_currency, format_date
from utils.input_formatters import CurrencyEntry
from datetime import date, datetime

class PagamentoDialog:
    def __init__(self, parent, mensalidade_data, callback=None):
        self.parent = parent
        self.mensalidade_data = mensalidade_data
        self.callback = callback
        self.resultado = None
        
        self.create_dialog()
    
    def create_dialog(self):
        """Cria dialog de registro de pagamento"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("💳 Registrar Pagamento")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg='white')
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Centralizar
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        # Header
        header = tk.Frame(self.dialog, bg='#28a745', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header, text="💳 Registrar Pagamento",
            font=('Arial', 18, 'bold'), fg='white', bg='#28a745'
        ).pack(expand=True)
        
        # Conteúdo principal
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Informações da mensalidade
        self.create_info_section(main_frame)
        
        # Seção de pagamento
        self.create_payment_section(main_frame)
        
        # Resumo
        self.create_summary_section(main_frame)
        
        # Botões
        self.create_buttons(main_frame)
        
        # Calcular valores iniciais
        self.calcular_valores()
        
        # Focar na data de pagamento
        self.data_pagamento_entry.focus_set()
    
    def create_info_section(self, parent):
        """Seção com informações da mensalidade"""
        info_frame = tk.LabelFrame(
            parent, text="📋 Informações da Mensalidade", 
            font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50'
        )
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        content = tk.Frame(info_frame, bg='white')
        content.pack(fill=tk.X, padx=15, pady=10)
        
        # Informações em duas colunas
        tk.Label(content, text="Aluno:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', pady=3)
        tk.Label(content, text=self.mensalidade_data.get('aluno_nome', ''), font=('Arial', 10), bg='white').grid(row=0, column=1, sticky='w', pady=3, padx=(10, 0))
        
        tk.Label(content, text="Mês/Ano:", font=('Arial', 10, 'bold'), bg='white').grid(row=1, column=0, sticky='w', pady=3)
        tk.Label(content, text=self.mensalidade_data.get('mes_referencia', '').replace('-', '/'), font=('Arial', 10), bg='white').grid(row=1, column=1, sticky='w', pady=3, padx=(10, 0))
        
        tk.Label(content, text="Vencimento:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=2, sticky='w', pady=3, padx=(20, 0))
        tk.Label(content, text=format_date(self.mensalidade_data.get('data_vencimento', '')), font=('Arial', 10), bg='white').grid(row=0, column=3, sticky='w', pady=3, padx=(10, 0))
        
        tk.Label(content, text="Valor Original:", font=('Arial', 10, 'bold'), bg='white').grid(row=1, column=2, sticky='w', pady=3, padx=(20, 0))
        tk.Label(content, text=format_currency(self.mensalidade_data.get('valor_original', 0)), font=('Arial', 10), bg='white').grid(row=1, column=3, sticky='w', pady=3, padx=(10, 0))
    
    def create_payment_section(self, parent):
        """Seção de dados do pagamento"""
        payment_frame = tk.LabelFrame(
            parent, text="💳 Dados do Pagamento", 
            font=('Arial', 12, 'bold'), bg='white', fg='#007bff'
        )
        payment_frame.pack(fill=tk.X, pady=(0, 20))
        
        content = tk.Frame(payment_frame, bg='white')
        content.pack(fill=tk.X, padx=15, pady=15)
        
        # Data do pagamento
        tk.Label(content, text="Data do Pagamento *:", 
                font=('Arial', 11, 'bold'), bg='white').grid(row=0, column=0, sticky='w', pady=10)
        
        self.data_pagamento_var = tk.StringVar(value=date.today().strftime('%d/%m/%Y'))
        self.data_pagamento_entry = tk.Entry(content, textvariable=self.data_pagamento_var, 
                                            width=12, font=('Arial', 11))
        self.data_pagamento_entry.grid(row=0, column=1, sticky='w', pady=10, padx=(10, 20))
        self.data_pagamento_entry.bind('<KeyRelease>', self.on_date_change)
        
        # Desconto
        tk.Label(content, text="Desconto (R$):", 
                font=('Arial', 11, 'bold'), bg='white').grid(row=0, column=2, sticky='w', pady=10, padx=(20, 0))
        
        self.desconto_var = tk.StringVar(value="0,00")
        self.desconto_entry = CurrencyEntry(content, self.desconto_var, 
                                           width=10, font=('Arial', 11), bg='white')
        self.desconto_entry.grid(row=0, column=3, sticky='w', pady=10, padx=(10, 0))
        self.desconto_entry.entry.bind('<KeyRelease>', lambda e: self.calcular_valores())
        
        # Multa (calculada automaticamente)
        tk.Label(content, text="Multa por Atraso:", 
                font=('Arial', 11, 'bold'), bg='white').grid(row=1, column=0, sticky='w', pady=10)
        
        self.multa_display = tk.Label(content, text="R$ 0,00", 
                                     font=('Arial', 11), bg='white', fg='#dc3545')
        self.multa_display.grid(row=1, column=1, sticky='w', pady=10, padx=(10, 20))
        
        # Observações
        tk.Label(content, text="Observações:", 
                font=('Arial', 11, 'bold'), bg='white').grid(row=2, column=0, sticky='nw', pady=10)
        
        self.observacoes_var = tk.StringVar()
        obs_entry = tk.Entry(content, textvariable=self.observacoes_var, 
                            width=40, font=('Arial', 11))
        obs_entry.grid(row=2, column=1, columnspan=3, sticky='ew', pady=10, padx=(10, 0))
        
        content.columnconfigure(3, weight=1)
    
    def create_summary_section(self, parent):
        """Seção de resumo do pagamento"""
        summary_frame = tk.LabelFrame(
            parent, text="📊 Resumo do Pagamento", 
            font=('Arial', 12, 'bold'), bg='white', fg='#28a745'
        )
        summary_frame.pack(fill=tk.X, pady=(0, 20))
        
        content = tk.Frame(summary_frame, bg='#f8f9fa')
        content.pack(fill=tk.X, padx=15, pady=15, ipady=10)
        
        # Resumo em formato tabular
        tk.Label(content, text="Valor Original:", font=('Arial', 11), bg='#f8f9fa').grid(row=0, column=0, sticky='w', pady=2)
        self.resumo_original = tk.Label(content, text="R$ 0,00", font=('Arial', 11, 'bold'), bg='#f8f9fa')
        self.resumo_original.grid(row=0, column=1, sticky='e', pady=2, padx=(20, 0))
        
        tk.Label(content, text="(-) Desconto:", font=('Arial', 11), bg='#f8f9fa', fg='#28a745').grid(row=1, column=0, sticky='w', pady=2)
        self.resumo_desconto = tk.Label(content, text="R$ 0,00", font=('Arial', 11, 'bold'), bg='#f8f9fa', fg='#28a745')
        self.resumo_desconto.grid(row=1, column=1, sticky='e', pady=2, padx=(20, 0))
        
        tk.Label(content, text="(+) Multa:", font=('Arial', 11), bg='#f8f9fa', fg='#dc3545').grid(row=2, column=0, sticky='w', pady=2)
        self.resumo_multa = tk.Label(content, text="R$ 0,00", font=('Arial', 11, 'bold'), bg='#f8f9fa', fg='#dc3545')
        self.resumo_multa.grid(row=2, column=1, sticky='e', pady=2, padx=(20, 0))
        
        # Linha separadora
        separator = tk.Frame(content, height=1, bg='#dee2e6')
        separator.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(5, 5))
        
        tk.Label(content, text="VALOR A PAGAR:", font=('Arial', 12, 'bold'), bg='#f8f9fa').grid(row=4, column=0, sticky='w', pady=5)
        self.resumo_final = tk.Label(content, text="R$ 0,00", font=('Arial', 14, 'bold'), bg='#f8f9fa', fg='#007bff')
        self.resumo_final.grid(row=4, column=1, sticky='e', pady=5, padx=(20, 0))
        
        content.columnconfigure(1, weight=1)
    
    def create_buttons(self, parent):
        """Botões de ação com melhor destaque"""
        btn_frame = tk.Frame(parent, bg='white')
        btn_frame.pack(fill=tk.X, pady=20)
        
        # Separador
        separator = tk.Frame(btn_frame, height=2, bg='#dee2e6')
        separator.pack(fill=tk.X, pady=(0, 15))
        
        # Botão confirmar - PRINCIPAL
        self.confirmar_btn = tk.Button(
            btn_frame, 
            text="💾 CONFIRMAR PAGAMENTO", 
            command=self.confirmar_pagamento,
            bg='#28a745', 
            fg='white', 
            font=('Arial', 14, 'bold'),
            padx=30, 
            pady=15, 
            relief='flat', 
            cursor='hand2',
            activebackground='#218838'
        )
        self.confirmar_btn.pack(side=tk.LEFT, padx=(0, 20))
        
        # Botão cancelar
        cancelar_btn = tk.Button(
            btn_frame, 
            text="❌ Cancelar", 
            command=self.cancelar,
            bg='#6c757d', 
            fg='white', 
            font=('Arial', 12, 'bold'),
            padx=25, 
            pady=12, 
            relief='flat', 
            cursor='hand2',
            activebackground='#5a6268'
        )
        cancelar_btn.pack(side=tk.LEFT)
        
        # === MELHORAR ATALHOS DE TECLADO ===
        
        # Enter para confirmar (múltiplas variações)
        self.dialog.bind('<Return>', self.confirmar_com_enter)
        self.dialog.bind('<KP_Enter>', self.confirmar_com_enter)
        
        # Ctrl+Enter para confirmar
        self.dialog.bind('<Control-Return>', self.confirmar_com_enter)
        
        # Escape para cancelar
        self.dialog.bind('<Escape>', lambda e: self.cancelar())
        
        # F12 para confirmar
        self.dialog.bind('<F12>', self.confirmar_com_enter)
        
        # Bind Enter em todos os campos
        self.data_pagamento_entry.bind('<Return>', self.confirmar_com_enter)
        self.desconto_entry.entry.bind('<Return>', self.confirmar_com_enter)
    
    def confirmar_com_enter(self, event=None):
        """Permite confirmar com Enter"""
        self.confirmar_pagamento()
    
    def on_date_change(self, event=None):
        """Recalcula valores quando data muda"""
        self.calcular_valores()
    
    def calcular_valores(self):
        """Calcula multa e valores finais"""
        try:
            # Valor original
            valor_original = float(self.mensalidade_data.get('valor_original', 0))
            
            # Desconto
            desconto = self.desconto_entry.get_float_value()
            
            # Calcular multa baseada no atraso
            multa = self.calcular_multa()
            
            # Valor final
            valor_final = valor_original - desconto + multa
            
            # Atualizar displays
            self.multa_display.config(text=format_currency(multa))
            
            # Atualizar resumo
            self.resumo_original.config(text=format_currency(valor_original))
            self.resumo_desconto.config(text=format_currency(desconto))
            self.resumo_multa.config(text=format_currency(multa))
            self.resumo_final.config(text=format_currency(valor_final))
            
        except Exception as e:
            print(f"Erro ao calcular valores: {e}")
    
    def calcular_multa(self):
        """Calcula multa baseada no atraso"""
        try:
            # Data de vencimento
            data_vencimento_str = self.mensalidade_data.get('data_vencimento', '')
            if not data_vencimento_str:
                return 0
            
            data_vencimento = datetime.strptime(data_vencimento_str, '%Y-%m-%d').date()
            
            # Data de pagamento
            data_pagamento_str = self.data_pagamento_var.get()
            if not data_pagamento_str:
                return 0
            
            try:
                data_pagamento = datetime.strptime(data_pagamento_str, '%d/%m/%Y').date()
            except:
                return 0
            
            # Calcular dias de atraso
            dias_atraso = (data_pagamento - data_vencimento).days
            
            if dias_atraso <= 0:
                return 0  # Sem atraso
            
            # Multa: 2% do valor + R$ 1,00 por dia (configurável)
            valor_original = float(self.mensalidade_data.get('valor_original', 0))
            
            multa_percentual = valor_original * 0.02  # 2%
            multa_diaria = dias_atraso * 1.00  # R$ 1,00 por dia
            
            multa_total = multa_percentual + multa_diaria
            
            return max(0, multa_total)
            
        except Exception as e:
            print(f"Erro ao calcular multa: {e}")
            return 0
    
    def confirmar_pagamento(self):
        """Confirma o pagamento com melhor validação"""
        try:
            # Desabilitar botão para evitar cliques duplos
            self.confirmar_btn.config(text="⏳ Processando...", state='disabled')
            
            # Validações
            if not self.data_pagamento_var.get().strip():
                messagebox.showerror("Erro", "Data de pagamento é obrigatória!")
                self.confirmar_btn.config(text="💾 CONFIRMAR PAGAMENTO", state='normal')
                return
            
            # Validar formato da data
            try:
                datetime.strptime(self.data_pagamento_var.get(), '%d/%m/%Y')
            except ValueError:
                messagebox.showerror("Erro", "Data inválida! Use o formato dd/mm/aaaa")
                self.confirmar_btn.config(text="💾 CONFIRMAR PAGAMENTO", state='normal')
                return
            
            # Preparar dados do pagamento
            dados_pagamento = {
                'mensalidade_id': self.mensalidade_data.get('id'),
                'data_pagamento': self.data_pagamento_var.get(),
                'desconto_aplicado': self.desconto_entry.get_float_value(),
                'multa_aplicada': self.calcular_multa(),
                'observacoes': self.observacoes_var.get().strip()
            }
            
            # Calcular valor final
            valor_original = float(self.mensalidade_data.get('valor_original', 0))
            valor_final = valor_original - dados_pagamento['desconto_aplicado'] + dados_pagamento['multa_aplicada']
            dados_pagamento['valor_final'] = valor_final
            
            # Confirmar com usuário se houver desconto ou multa
            msg_confirmacao = f"Confirmar pagamento:\n\nAluno: {self.mensalidade_data.get('aluno_nome', '')}"
            msg_confirmacao += f"\nMês/Ano: {self.mensalidade_data.get('mes_referencia', '').replace('-', '/')}"
            msg_confirmacao += f"\nValor Original: R$ {valor_original:.2f}"
            
            if dados_pagamento['desconto_aplicado'] > 0:
                msg_confirmacao += f"\nDesconto: -R$ {dados_pagamento['desconto_aplicado']:.2f}"
            
            if dados_pagamento['multa_aplicada'] > 0:
                msg_confirmacao += f"\nMulta: +R$ {dados_pagamento['multa_aplicada']:.2f}"
            
            msg_confirmacao += f"\n\nVALOR FINAL: R$ {valor_final:.2f}"
            
            if not messagebox.askyesno("Confirmar Pagamento", msg_confirmacao):
                self.confirmar_btn.config(text="💾 CONFIRMAR PAGAMENTO", state='normal')
                return
            
            self.resultado = dados_pagamento
            
            if self.callback:
                self.callback(dados_pagamento)
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar pagamento:\n{str(e)}")
            self.confirmar_btn.config(text="💾 CONFIRMAR PAGAMENTO", state='normal')
    
    def cancelar(self):
        """Cancela o dialog"""
        self.resultado = None
        self.dialog.destroy()
