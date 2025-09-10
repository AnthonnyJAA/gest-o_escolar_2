import tkinter as tk
from tkinter import ttk, messagebox
from services.config_financeira_service import ConfigFinanceiraService
from utils.formatters import format_currency
from datetime import datetime, date

class ConfigFinanceiraInterface:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.parent_frame.configure(bg='white')
        self.config_service = ConfigFinanceiraService()
        self.create_interface()
        self.carregar_configuracoes()
    
    def create_interface(self):
        """Cria interface de configurações financeiras"""
        # Container principal com scroll
        main_container = tk.Frame(self.parent_frame, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(
            main_container,
            text="⚙️ Configurações Financeiras",
            font=('Arial', 24, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 30))
        
        # Seção Desconto
        self.create_desconto_section(main_container)
        
        # Seção Multa
        self.create_multa_section(main_container)
        
        # Preview de cálculos
        self.create_preview_section(main_container)
        
        # Botões de ação
        self.create_action_buttons(main_container)
    
    def create_desconto_section(self, parent):
        """Seção configuração de desconto"""
        desc_frame = tk.LabelFrame(
            parent,
            text="  💰 Configurações de Desconto  ",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#27ae60',
            bd=2,
            relief='groove'
        )
        desc_frame.pack(fill=tk.X, pady=(0, 20))
        
        content = tk.Frame(desc_frame, bg='white')
        content.pack(fill=tk.X, padx=20, pady=15)
        
        # Valor do desconto
        tk.Label(content, text="Valor do Desconto por Pontualidade:", 
                font=('Arial', 11, 'bold'), bg='white', fg='#2c3e50').grid(row=0, column=0, sticky='w', pady=5)
        
        desc_frame_inner = tk.Frame(content, bg='white')
        desc_frame_inner.grid(row=0, column=1, sticky='w', padx=(10, 0))
        
        tk.Label(desc_frame_inner, text="R$", font=('Arial', 11, 'bold'), bg='white').pack(side=tk.LEFT)
        
        self.desconto_var = tk.StringVar()
        desc_entry = tk.Entry(desc_frame_inner, textvariable=self.desconto_var, width=10,
                             font=('Arial', 11), relief='solid', bd=1)
        desc_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(desc_frame_inner, text="(valor fixo em reais)", 
                font=('Arial', 9), bg='white', fg='#6c757d').pack(side=tk.LEFT, padx=5)
        
        # Dias limite para desconto
        tk.Label(content, text="Prazo para Desconto:", 
                font=('Arial', 11, 'bold'), bg='white', fg='#2c3e50').grid(row=1, column=0, sticky='w', pady=5)
        
        prazo_frame = tk.Frame(content, bg='white')
        prazo_frame.grid(row=1, column=1, sticky='w', padx=(10, 0))
        
        self.dias_desconto_var = tk.StringVar()
        dias_entry = tk.Entry(prazo_frame, textvariable=self.dias_desconto_var, width=5,
                             font=('Arial', 11), relief='solid', bd=1)
        dias_entry.pack(side=tk.LEFT)
        
        tk.Label(prazo_frame, text="dias antes do vencimento", 
                font=('Arial', 11), bg='white').pack(side=tk.LEFT, padx=5)
        
        # Explicação
        explicacao = tk.Label(
            content, 
            text="ℹ️ O desconto será aplicado apenas se o pagamento for feito dentro do prazo especificado.",
            font=('Arial', 9), bg='white', fg='#17a2b8',
            wraplength=600
        )
        explicacao.grid(row=2, column=0, columnspan=2, sticky='w', pady=(10, 0))
    
    def create_multa_section(self, parent):
        """Seção configuração de multa"""
        multa_frame = tk.LabelFrame(
            parent,
            text="  ⚠️ Configurações de Multa  ",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#e74c3c',
            bd=2,
            relief='groove'
        )
        multa_frame.pack(fill=tk.X, pady=(0, 20))
        
        content = tk.Frame(multa_frame, bg='white')
        content.pack(fill=tk.X, padx=20, pady=15)
        
        # Valor da multa por dia
        tk.Label(content, text="Multa por Dia de Atraso:", 
                font=('Arial', 11, 'bold'), bg='white', fg='#2c3e50').grid(row=0, column=0, sticky='w', pady=5)
        
        multa_frame_inner = tk.Frame(content, bg='white')
        multa_frame_inner.grid(row=0, column=1, sticky='w', padx=(10, 0))
        
        tk.Label(multa_frame_inner, text="R$", font=('Arial', 11, 'bold'), bg='white').pack(side=tk.LEFT)
        
        self.multa_var = tk.StringVar()
        multa_entry = tk.Entry(multa_frame_inner, textvariable=self.multa_var, width=10,
                              font=('Arial', 11), relief='solid', bd=1)
        multa_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(multa_frame_inner, text="por dia", 
                font=('Arial', 11), bg='white').pack(side=tk.LEFT, padx=5)
        
        # Período de carência
        tk.Label(content, text="Período de Carência:", 
                font=('Arial', 11, 'bold'), bg='white', fg='#2c3e50').grid(row=1, column=0, sticky='w', pady=5)
        
        carencia_frame = tk.Frame(content, bg='white')
        carencia_frame.grid(row=1, column=1, sticky='w', padx=(10, 0))
        
        self.carencia_var = tk.StringVar()
        carencia_entry = tk.Entry(carencia_frame, textvariable=self.carencia_var, width=5,
                                 font=('Arial', 11), relief='solid', bd=1)
        carencia_entry.pack(side=tk.LEFT)
        
        tk.Label(carencia_frame, text="dias após o vencimento", 
                font=('Arial', 11), bg='white').pack(side=tk.LEFT, padx=5)
        
        # Explicação
        explicacao = tk.Label(
            content, 
            text="ℹ️ A multa só será aplicada após o período de carência. Mensalidades de meses anteriores à matrícula nunca recebem multa.",
            font=('Arial', 9), bg='white', fg='#17a2b8',
            wraplength=600
        )
        explicacao.grid(row=2, column=0, columnspan=2, sticky='w', pady=(10, 0))
    
    def create_preview_section(self, parent):
        """Seção de preview dos cálculos"""
        preview_frame = tk.LabelFrame(
            parent,
            text="  📊 Preview de Cálculos  ",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#6f42c1',
            bd=2,
            relief='groove'
        )
        preview_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.preview_content = tk.Frame(preview_frame, bg='white')
        self.preview_content.pack(fill=tk.X, padx=20, pady=15)
        
        # Botão para atualizar preview
        tk.Button(
            self.preview_content, text="🔄 Atualizar Preview", command=self.atualizar_preview,
            bg='#6f42c1', fg='white', font=('Arial', 10, 'bold'),
            padx=15, pady=8, relief='flat', cursor='hand2'
        ).pack(anchor='center', pady=10)
        
        # Área do preview
        self.preview_text = tk.Text(self.preview_content, height=8, font=('Courier', 9),
                                   bg='#f8f9fa', relief='solid', bd=1)
        self.preview_text.pack(fill=tk.X, pady=10)
        
        # Scrollbar para preview
        preview_scroll = ttk.Scrollbar(self.preview_content, orient='vertical', command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scroll.set)
    
    def create_action_buttons(self, parent):
        """Botões de ação"""
        buttons_frame = tk.Frame(parent, bg='white')
        buttons_frame.pack(fill=tk.X, pady=20)
        
        # Separador
        separator = tk.Frame(buttons_frame, height=2, bg='#dee2e6')
        separator.pack(fill=tk.X, pady=(0, 20))
        
        # Botões
        btn_container = tk.Frame(buttons_frame, bg='white')
        btn_container.pack()
        
        tk.Button(
            btn_container, text="💾 Salvar Configurações", command=self.salvar_configuracoes,
            bg='#28a745', fg='white', font=('Arial', 12, 'bold'),
            padx=25, pady=10, relief='flat', cursor='hand2'
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Button(
            btn_container, text="🔄 Recalcular Mensalidades", command=self.recalcular_mensalidades,
            bg='#17a2b8', fg='white', font=('Arial', 12, 'bold'),
            padx=25, pady=10, relief='flat', cursor='hand2'
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Button(
            btn_container, text="↩️ Restaurar Padrão", command=self.restaurar_padrao,
            bg='#6c757d', fg='white', font=('Arial', 12, 'bold'),
            padx=25, pady=10, relief='flat', cursor='hand2'
        ).pack(side=tk.LEFT)
    
    def carregar_configuracoes(self):
        """Carrega configurações atuais"""
        try:
            config = self.config_service.obter_configuracoes()
            
            self.desconto_var.set(str(config['desconto_pontualidade']))
            self.dias_desconto_var.set(str(config['dias_limite_desconto']))
            self.multa_var.set(str(config['multa_por_dia']))
            self.carencia_var.set(str(config['dias_carencia_multa']))
            
            self.atualizar_preview()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar configurações: {str(e)}")
    
    def salvar_configuracoes(self):
        """Salva as configurações"""
        try:
            # Validar valores
            desconto = float(self.desconto_var.get().replace(',', '.'))
            dias_desconto = int(self.dias_desconto_var.get())
            multa = float(self.multa_var.get().replace(',', '.'))
            carencia = int(self.carencia_var.get())
            
            if desconto < 0 or multa < 0:
                messagebox.showerror("Erro", "Valores não podem ser negativos!")
                return
            
            if dias_desconto < 0 or carencia < 0:
                messagebox.showerror("Erro", "Dias não podem ser negativos!")
                return
            
            # Salvar
            config_data = {
                'desconto_pontualidade': desconto,
                'dias_limite_desconto': dias_desconto,
                'multa_por_dia': multa,
                'dias_carencia_multa': carencia,
                'descricao': f'Configurações atualizadas em {datetime.now().strftime("%d/%m/%Y às %H:%M")}'
            }
            
            resultado = self.config_service.salvar_configuracoes(config_data)
            
            if resultado['success']:
                messagebox.showinfo("Sucesso", "✅ Configurações salvas com sucesso!")
                self.atualizar_preview()
            else:
                messagebox.showerror("Erro", f"❌ Erro ao salvar: {resultado['error']}")
                
        except ValueError:
            messagebox.showerror("Erro", "❌ Por favor, insira valores numéricos válidos!")
        except Exception as e:
            messagebox.showerror("Erro", f"❌ Erro inesperado: {str(e)}")
    
    def recalcular_mensalidades(self):
        """Recalcula todas as mensalidades"""
        if messagebox.askyesno("Confirmar", 
                              "⚠️ Isso irá recalcular o status de todas as mensalidades não pagas.\n"
                              "Deseja continuar?"):
            try:
                from services.mensalidade_service import MensalidadeService
                mensalidade_service = MensalidadeService()
                resultado = mensalidade_service.recalcular_todas_mensalidades()
                
                if resultado['success']:
                    messagebox.showinfo("Sucesso", 
                                      f"✅ {resultado['atualizadas']} mensalidades recalculadas!")
                else:
                    messagebox.showerror("Erro", f"❌ Erro: {resultado['error']}")
                    
            except Exception as e:
                messagebox.showerror("Erro", f"❌ Erro: {str(e)}")
    
    def restaurar_padrao(self):
        """Restaura configurações padrão"""
        if messagebox.askyesno("Confirmar", "Restaurar configurações padrão?"):
            self.desconto_var.set("10.0")
            self.dias_desconto_var.set("5")
            self.multa_var.set("2.0")
            self.carencia_var.set("30")
            self.atualizar_preview()
    
    def atualizar_preview(self):
        """Atualiza preview de cálculos"""
        try:
            # Limpar preview
            self.preview_text.delete(1.0, tk.END)
            
            # Valores atuais
            desconto = float(self.desconto_var.get().replace(',', '.')) if self.desconto_var.get() else 0
            dias_desc = int(self.dias_desconto_var.get()) if self.dias_desconto_var.get() else 0
            multa = float(self.multa_var.get().replace(',', '.')) if self.multa_var.get() else 0
            carencia = int(self.carencia_var.get()) if self.carencia_var.get() else 0
            
            # Exemplo com mensalidade de R$ 100
            valor_exemplo = 100.00
            
            preview = f"PREVIEW DE CÁLCULOS (Mensalidade: R$ {valor_exemplo:.2f})\n"
            preview += "=" * 60 + "\n\n"
            
            preview += "💰 DESCONTO POR PONTUALIDADE:\n"
            if desconto > 0:
                preview += f"   • Valor do desconto: R$ {desconto:.2f}\n"
                preview += f"   • Válido até {dias_desc} dias antes do vencimento\n"
                preview += f"   • Valor final: R$ {valor_exemplo - desconto:.2f}\n"
            else:
                preview += "   • Desconto desabilitado\n"
            
            preview += "\n⚠️ MULTA POR ATRASO:\n"
            if multa > 0:
                preview += f"   • Multa por dia: R$ {multa:.2f}\n"
                preview += f"   • Carência: {carencia} dias\n"
                preview += f"   • Exemplo 40 dias atraso: R$ {valor_exemplo + (10 * multa):.2f}\n"
                preview += f"     (10 dias de multa = {carencia} + 10)\n"
            else:
                preview += "   • Multa desabilitada\n"
            
            preview += "\n📅 REGRAS ESPECIAIS:\n"
            preview += "   • Mensalidades anteriores à matrícula: SEM multa\n"
            preview += "   • Mensalidades posteriores à matrícula: COM multa\n"
            preview += "   • Desconto válido para todas as mensalidades\n"
            
            self.preview_text.insert(1.0, preview)
            
        except Exception as e:
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, f"Erro ao calcular preview: {str(e)}")
