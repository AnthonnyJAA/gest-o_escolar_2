import tkinter as tk
from tkinter import ttk, messagebox
from services.financeiro_service import FinanceiroService
from services.aluno_service import AlunoService
from utils.formatters import format_currency, format_date
from datetime import datetime, date
import calendar

class FinanceiroInterface:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.parent_frame.configure(bg='white')
        
        self.financeiro_service = FinanceiroService()
        self.aluno_service = AlunoService()
        
        # Variáveis de interface
        self.mensalidades_data = []
        self.mensalidade_selecionada = None
        
        # Variáveis de entrada
        self.var_desconto = tk.StringVar()
        self.var_multa = tk.StringVar()
        self.var_outros = tk.StringVar()
        self.var_observacoes = tk.StringVar()
        
        # Widgets de entrada (para habilitar/desabilitar)
        self.entry_desconto = None
        self.entry_multa = None
        self.entry_outros = None
        self.entry_observacoes = None
        self.btn_dar_baixa = None
        
        try:
            self.create_interface()
            self.carregar_mensalidades()
            self.setup_keyboard_shortcuts()
        except Exception as e:
            self.mostrar_erro(f"Erro ao criar interface financeira: {e}")
    
    def create_interface(self):
        """Cria interface financeira CORRIGIDA com botão"""
        
        # Container principal
        main_container = tk.Frame(self.parent_frame, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # === CABEÇALHO ===
        header_frame = tk.Frame(main_container, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            header_frame,
            text="💰 Gestão Financeira",
            font=('Arial', 24, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(side=tk.LEFT)
        
        # Botão de atualizar
        tk.Button(
            header_frame,
            text="🔄 Atualizar",
            command=self.carregar_mensalidades,
            font=('Arial', 10, 'bold'),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=5,
            relief='flat'
        ).pack(side=tk.RIGHT)
        
        # === ÁREA PRINCIPAL (2 COLUNAS) ===
        content_frame = tk.Frame(main_container, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Coluna esquerda - Lista de mensalidades
        left_frame = tk.LabelFrame(
            content_frame,
            text=" 📋 Mensalidades ",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.criar_lista_mensalidades(left_frame)
        
        # Coluna direita - Gestão de pagamento
        right_frame = tk.LabelFrame(
            content_frame,
            text=" 💳 Gestão de Pagamento ",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_frame.configure(width=350)
        right_frame.pack_propagate(False)
        
        self.criar_area_pagamento(right_frame)
    
    def criar_lista_mensalidades(self, parent):
        """Cria lista de mensalidades"""
        
        # === FILTROS ===
        filter_frame = tk.Frame(parent, bg='white')
        filter_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Filtro por status
        tk.Label(filter_frame, text="Status:", font=('Arial', 10, 'bold'), bg='white').pack(side=tk.LEFT)
        
        self.status_var = tk.StringVar(value="Todos")
        status_combo = ttk.Combobox(
            filter_frame, textvariable=self.status_var,
            values=["Todos", "Pendente", "Atrasado", "Pago"],
            width=12, state="readonly"
        )
        status_combo.pack(side=tk.LEFT, padx=(5, 15))
        status_combo.bind("<<ComboboxSelected>>", lambda e: self.filtrar_mensalidades())
        
        # Filtro por mês
        tk.Label(filter_frame, text="Mês:", font=('Arial', 10, 'bold'), bg='white').pack(side=tk.LEFT)
        
        meses = ["Todos"] + [f"{i:02d}" for i in range(1, 13)]
        self.mes_var = tk.StringVar(value="Todos")
        mes_combo = ttk.Combobox(
            filter_frame, textvariable=self.mes_var,
            values=meses, width=8, state="readonly"
        )
        mes_combo.pack(side=tk.LEFT, padx=(5, 15))
        mes_combo.bind("<<ComboboxSelected>>", lambda e: self.filtrar_mensalidades())
        
        # Botão de filtrar
        tk.Button(
            filter_frame,
            text="🔍 Filtrar",
            command=self.filtrar_mensalidades,
            font=('Arial', 9, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=10,
            relief='flat'
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # === TREEVIEW ===
        tree_frame = tk.Frame(parent, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        # Definir colunas
        columns = (
            'aluno', 'turma', 'mes_ref', 'vencimento', 
            'valor_original', 'desconto', 'multa', 'valor_final', 'status'
        )
        
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configurar colunas
        colunas_config = {
            'aluno': ('Aluno', 200),
            'turma': ('Turma', 120),
            'mes_ref': ('Mês/Ano', 80),
            'vencimento': ('Vencimento', 90),
            'valor_original': ('Valor Orig.', 80),
            'desconto': ('Desconto', 70),
            'multa': ('Multa', 60),
            'valor_final': ('Valor Final', 90),
            'status': ('Status', 80)
        }
        
        for col, (heading, width) in colunas_config.items():
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, minwidth=50)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Grid
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        # Bind de seleção
        self.tree.bind("<<TreeviewSelect>>", self.on_mensalidade_select)
        
        # Tags para cores
        self.tree.tag_configure('pendente', background='#fff3cd')
        self.tree.tag_configure('atrasado', background='#f8d7da')
        self.tree.tag_configure('pago', background='#d4edda')
    
    def criar_area_pagamento(self, parent):
        """Cria área de gestão de pagamento CORRIGIDA com BOTÃO"""
        
        # Container com scroll
        canvas = tk.Canvas(parent, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # === INFORMAÇÕES DA MENSALIDADE SELECIONADA ===
        info_frame = tk.LabelFrame(
            scrollable_frame,
            text=" ℹ️ Mensalidade Selecionada ",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        info_frame.pack(fill=tk.X, padx=10, pady=(10, 15))
        
        # Labels de informação (serão atualizados)
        self.lbl_aluno = tk.Label(info_frame, text="Aluno: Nenhum selecionado", 
                                 font=('Arial', 10), bg='white', anchor='w')
        self.lbl_aluno.pack(fill=tk.X, padx=10, pady=2)
        
        self.lbl_turma = tk.Label(info_frame, text="Turma: -", 
                                 font=('Arial', 10), bg='white', anchor='w')
        self.lbl_turma.pack(fill=tk.X, padx=10, pady=2)
        
        self.lbl_mes = tk.Label(info_frame, text="Mês/Ano: -", 
                               font=('Arial', 10), bg='white', anchor='w')
        self.lbl_mes.pack(fill=tk.X, padx=10, pady=2)
        
        self.lbl_vencimento = tk.Label(info_frame, text="Vencimento: -", 
                                     font=('Arial', 10), bg='white', anchor='w')
        self.lbl_vencimento.pack(fill=tk.X, padx=10, pady=2)
        
        self.lbl_status = tk.Label(info_frame, text="Status: -", 
                                  font=('Arial', 10, 'bold'), bg='white', anchor='w')
        self.lbl_status.pack(fill=tk.X, padx=10, pady=2)
        
        # === NOVA LÓGICA DE CÁLCULO ===
        calculo_frame = tk.LabelFrame(
            scrollable_frame,
            text=" 🧮 Nova Lógica: Original - Desconto + Multa + Outros ",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#27ae60'
        )
        calculo_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        # Valor original (readonly)
        tk.Label(calculo_frame, text="💰 Valor Original:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', padx=10, pady=(10, 5))
        self.lbl_valor_original = tk.Label(calculo_frame, text="R$ 0,00", 
                                          font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50')
        self.lbl_valor_original.pack(anchor='w', padx=20, pady=(0, 10))
        
        # Desconto
        tk.Label(calculo_frame, text="💸 Desconto (R$):", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', padx=10, pady=(5, 2))
        self.entry_desconto = tk.Entry(calculo_frame, textvariable=self.var_desconto, 
                                      font=('Arial', 11), width=15, state='disabled')
        self.entry_desconto.pack(anchor='w', padx=20, pady=(0, 5))
        self.entry_desconto.bind('<KeyRelease>', self.calcular_valor_final)
        
        # Multa
        tk.Label(calculo_frame, text="🚨 Multa (R$):", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', padx=10, pady=(5, 2))
        self.entry_multa = tk.Entry(calculo_frame, textvariable=self.var_multa, 
                                   font=('Arial', 11), width=15, state='disabled')
        self.entry_multa.pack(anchor='w', padx=20, pady=(0, 5))
        self.entry_multa.bind('<KeyRelease>', self.calcular_valor_final)
        
        # Outros
        tk.Label(calculo_frame, text="➕ Outros (R$):", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', padx=10, pady=(5, 2))
        self.entry_outros = tk.Entry(calculo_frame, textvariable=self.var_outros, 
                                    font=('Arial', 11), width=15, state='disabled')
        self.entry_outros.pack(anchor='w', padx=20, pady=(0, 10))
        self.entry_outros.bind('<KeyRelease>', self.calcular_valor_final)
        
        # Separador
        tk.Label(calculo_frame, text="=" * 25, font=('Arial', 12, 'bold'), bg='white', fg='#27ae60').pack(padx=10, pady=5)
        
        # Valor final
        tk.Label(calculo_frame, text="💳 VALOR FINAL:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', padx=10, pady=(5, 2))
        self.lbl_valor_final = tk.Label(calculo_frame, text="R$ 0,00", 
                                       font=('Arial', 14, 'bold'), bg='white', fg='#27ae60')
        self.lbl_valor_final.pack(anchor='w', padx=20, pady=(0, 15))
        
        # === OBSERVAÇÕES ===
        obs_frame = tk.LabelFrame(
            scrollable_frame,
            text=" 📝 Observações ",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        obs_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        self.entry_observacoes = tk.Entry(obs_frame, textvariable=self.var_observacoes, 
                                         font=('Arial', 10), width=35, state='disabled')
        self.entry_observacoes.pack(fill=tk.X, padx=10, pady=10)
        
        # === BOTÃO DE AÇÃO PRINCIPAL ===
        self.btn_dar_baixa = tk.Button(
            scrollable_frame,
            text="💳 DAR BAIXA NA MENSALIDADE",
            command=self.dar_baixa_mensalidade,
            font=('Arial', 12, 'bold'),
            bg='#28a745',
            fg='white',
            padx=20,
            pady=15,
            relief='flat',
            cursor='hand2',
            state='disabled'
        )
        self.btn_dar_baixa.pack(fill=tk.X, padx=10, pady=(10, 15))
        
        # === BOTÕES SECUNDÁRIOS ===
        buttons_frame = tk.Frame(scrollable_frame, bg='white')
        buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 20))
        
        # Botão Cancelar
        tk.Button(
            buttons_frame,
            text="❌ Cancelar Seleção",
            command=self.cancelar_selecao,
            font=('Arial', 10),
            bg='#6c757d',
            fg='white',
            padx=15,
            pady=8,
            relief='flat'
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Botão Relatório
        tk.Button(
            buttons_frame,
            text="📊 Relatório",
            command=self.gerar_relatorio,
            font=('Arial', 10),
            bg='#17a2b8',
            fg='white',
            padx=15,
            pady=8,
            relief='flat'
        ).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
    
    def carregar_mensalidades(self):
        """Carrega lista de mensalidades"""
        try:
            print("💰 Carregando mensalidades...")
            
            # Obter mensalidades do serviço
            self.mensalidades_data = self.financeiro_service.listar_mensalidades()
            
            print(f"✅ {len(self.mensalidades_data)} mensalidades carregadas")
            
            # Atualizar árvore
            self.atualizar_tree()
            
        except Exception as e:
            print(f"❌ Erro ao carregar mensalidades: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar mensalidades:\n{e}")
    
    def atualizar_tree(self):
        """Atualiza a árvore com os dados"""
        
        # Limpar árvore
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Inserir dados
        for mensalidade in self.mensalidades_data:
            # Determinar tag baseada no status
            status = mensalidade.get('status', '').lower()
            tag = ''
            if 'pendente' in status:
                tag = 'pendente'
            elif 'atrasado' in status:
                tag = 'atrasado'
            elif 'pago' in status:
                tag = 'pago'
            
            # Inserir item
            self.tree.insert('', tk.END, values=(
                mensalidade.get('aluno_nome', ''),
                mensalidade.get('turma_nome', ''),
                mensalidade.get('mes_referencia', ''),
                format_date(mensalidade.get('data_vencimento')),
                format_currency(mensalidade.get('valor_original', 0)),
                format_currency(mensalidade.get('desconto_aplicado', 0)),
                format_currency(mensalidade.get('multa_aplicada', 0)),
                format_currency(mensalidade.get('valor_final', 0)),
                mensalidade.get('status', '')
            ), tags=(tag,))
    
    def filtrar_mensalidades(self):
        """Filtra mensalidades por status e mês"""
        try:
            status_filtro = self.status_var.get()
            mes_filtro = self.mes_var.get()
            
            # Limpar árvore
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Filtrar dados
            dados_filtrados = self.mensalidades_data
            
            if status_filtro != "Todos":
                dados_filtrados = [m for m in dados_filtrados 
                                  if status_filtro.lower() in m.get('status', '').lower()]
            
            if mes_filtro != "Todos":
                dados_filtrados = [m for m in dados_filtrados 
                                  if m.get('mes_referencia', '').split('-')[1] == mes_filtro]
            
            # Inserir dados filtrados
            for mensalidade in dados_filtrados:
                status = mensalidade.get('status', '').lower()
                tag = ''
                if 'pendente' in status:
                    tag = 'pendente'
                elif 'atrasado' in status:
                    tag = 'atrasado'
                elif 'pago' in status:
                    tag = 'pago'
                
                self.tree.insert('', tk.END, values=(
                    mensalidade.get('aluno_nome', ''),
                    mensalidade.get('turma_nome', ''),
                    mensalidade.get('mes_referencia', ''),
                    format_date(mensalidade.get('data_vencimento')),
                    format_currency(mensalidade.get('valor_original', 0)),
                    format_currency(mensalidade.get('desconto_aplicado', 0)),
                    format_currency(mensalidade.get('multa_aplicada', 0)),
                    format_currency(mensalidade.get('valor_final', 0)),
                    mensalidade.get('status', '')
                ), tags=(tag,))
            
            print(f"🔍 Filtro aplicado: {len(dados_filtrados)} mensalidades")
            
        except Exception as e:
            print(f"❌ Erro ao filtrar: {e}")
    
    def on_mensalidade_select(self, event):
        """Quando uma mensalidade é selecionada - CORRIGIDO"""
        try:
            selection = self.tree.selection()
            if not selection:
                return
            
            # Obter dados da linha selecionada
            item = self.tree.item(selection[0])
            values = item['values']
            
            if not values:
                return
            
            # Encontrar mensalidade completa nos dados
            aluno_nome = values[0]
            mes_ref = values[2]
            
            self.mensalidade_selecionada = None
            for mensalidade in self.mensalidades_data:
                if (mensalidade.get('aluno_nome') == aluno_nome and 
                    mensalidade.get('mes_referencia') == mes_ref):
                    self.mensalidade_selecionada = mensalidade
                    break
            
            if not self.mensalidade_selecionada:
                return
            
            # Atualizar informações
            self.atualizar_informacoes_mensalidade()
            
            # HABILITAR campos se não estiver paga
            if self.mensalidade_selecionada.get('status', '').lower() != 'pago':
                self.habilitar_campos()
            else:
                self.desabilitar_campos()
                messagebox.showinfo("Mensalidade Paga", "Esta mensalidade já foi paga.")
            
        except Exception as e:
            print(f"❌ Erro na seleção: {e}")
            messagebox.showerror("Erro", f"Erro ao selecionar mensalidade:\n{e}")
    
    def atualizar_informacoes_mensalidade(self):
        """Atualiza as informações da mensalidade selecionada"""
        if not self.mensalidade_selecionada:
            return
        
        m = self.mensalidade_selecionada
        
        # Atualizar labels
        self.lbl_aluno.config(text=f"Aluno: {m.get('aluno_nome', '')}")
        self.lbl_turma.config(text=f"Turma: {m.get('turma_nome', '')}")
        self.lbl_mes.config(text=f"Mês/Ano: {m.get('mes_referencia', '')}")
        self.lbl_vencimento.config(text=f"Vencimento: {format_date(m.get('data_vencimento'))}")
        
        # Status com cor
        status = m.get('status', '')
        cor = '#28a745' if 'pago' in status.lower() else '#dc3545' if 'atrasado' in status.lower() else '#ffc107'
        self.lbl_status.config(text=f"Status: {status}", fg=cor)
        
        # Valor original
        valor_original = m.get('valor_original', 0)
        self.lbl_valor_original.config(text=format_currency(valor_original))
        
        # Preencher campos com valores atuais
        self.var_desconto.set(str(m.get('desconto_aplicado', 0)))
        self.var_multa.set(str(m.get('multa_aplicada', 0)))
        self.var_outros.set('0')  # Sempre 0 inicialmente
        self.var_observacoes.set(m.get('observacoes', ''))
        
        # Calcular valor final inicial
        self.calcular_valor_final()
    
    def habilitar_campos(self):
        """Habilita campos para edição - CORRIGIDO"""
        self.entry_desconto.config(state='normal')
        self.entry_multa.config(state='normal')
        self.entry_outros.config(state='normal')
        self.entry_observacoes.config(state='normal')
        self.btn_dar_baixa.config(state='normal')
        
        print("✅ Campos habilitados para edição")
    
    def desabilitar_campos(self):
        """Desabilita campos"""
        self.entry_desconto.config(state='disabled')
        self.entry_multa.config(state='disabled')
        self.entry_outros.config(state='disabled')
        self.entry_observacoes.config(state='disabled')
        self.btn_dar_baixa.config(state='disabled')
    
    def calcular_valor_final(self, event=None):
        """Calcula valor final usando NOVA LÓGICA"""
        try:
            if not self.mensalidade_selecionada:
                return
            
            # Obter valores
            valor_original = float(self.mensalidade_selecionada.get('valor_original', 0))
            
            try:
                desconto = float(self.var_desconto.get() or 0)
            except:
                desconto = 0
            
            try:
                multa = float(self.var_multa.get() or 0)
            except:
                multa = 0
            
            try:
                outros = float(self.var_outros.get() or 0)
            except:
                outros = 0
            
            # NOVA LÓGICA: Original - Desconto + Multa + Outros
            valor_final = valor_original - desconto + multa + outros
            
            # Não pode ser negativo
            valor_final = max(0, valor_final)
            
            # Atualizar label
            self.lbl_valor_final.config(text=format_currency(valor_final))
            
        except Exception as e:
            print(f"⚠️ Erro no cálculo: {e}")
    
    def dar_baixa_mensalidade(self):
        """Processa pagamento da mensalidade - CORRIGIDO"""
        try:
            if not self.mensalidade_selecionada:
                messagebox.showwarning("Atenção", "Nenhuma mensalidade selecionada")
                return
            
            # Obter valores
            try:
                desconto = float(self.var_desconto.get().replace(',', '.') or 0)
                multa = float(self.var_multa.get().replace(',', '.') or 0)
                outros = float(self.var_outros.get().replace(',', '.') or 0)
            except ValueError:
                messagebox.showerror("Erro", "Valores inválidos nos campos numéricos")
                return
            
            valor_original = float(self.mensalidade_selecionada.get('valor_original', 0))
            valor_final = valor_original - desconto + multa + outros
            valor_final = max(0, valor_final)
            
            observacoes = self.var_observacoes.get()
            
            # Confirmar operação
            mensagem = f"""
CONFIRMAR PAGAMENTO

Aluno: {self.mensalidade_selecionada.get('aluno_nome')}
Mês/Ano: {self.mensalidade_selecionada.get('mes_referencia')}

💰 CÁLCULO:
Valor Original: {format_currency(valor_original)}
Desconto: -{format_currency(desconto)}
Multa: +{format_currency(multa)}
Outros: +{format_currency(outros)}
{'=' * 25}
VALOR FINAL: {format_currency(valor_final)}

Observações: {observacoes or 'Nenhuma'}

Confirmar pagamento?
            """
            
            if not messagebox.askyesno("Confirmar Pagamento", mensagem.strip()):
                return
            
            # Processar pagamento
            resultado = self.financeiro_service.processar_pagamento(
                self.mensalidade_selecionada.get('id'),
                valor_final,
                desconto,
                multa,
                observacoes
            )
            
            if resultado['success']:
                messagebox.showinfo("Sucesso", "✅ Pagamento processado com sucesso!")
                
                # Recarregar dados
                self.carregar_mensalidades()
                self.cancelar_selecao()
                
                # Focar no próximo pendente
                self.focar_proximo_pendente()
                
            else:
                messagebox.showerror("Erro", f"❌ Erro ao processar pagamento:\n{resultado['error']}")
                
        except Exception as e:
            print(f"❌ Erro ao dar baixa: {e}")
            messagebox.showerror("Erro", f"Erro ao processar pagamento:\n{e}")
    
    def focar_proximo_pendente(self):
        """Foca automaticamente na próxima mensalidade pendente"""
        try:
            # Buscar próxima mensalidade pendente/atrasada
            for item in self.tree.get_children():
                values = self.tree.item(item)['values']
                if len(values) >= 9:
                    status = values[8].lower()
                    if 'pendente' in status or 'atrasado' in status:
                        self.tree.selection_set(item)
                        self.tree.focus(item)
                        self.tree.see(item)
                        # Simular evento de seleção
                        fake_event = type('Event', (), {})()
                        self.on_mensalidade_select(fake_event)
                        break
        except Exception as e:
            print(f"⚠️ Erro ao focar próximo pendente: {e}")
    
    def cancelar_selecao(self):
        """Cancela seleção atual"""
        self.tree.selection_remove(self.tree.selection())
        self.mensalidade_selecionada = None
        
        # Limpar informações
        self.lbl_aluno.config(text="Aluno: Nenhum selecionado")
        self.lbl_turma.config(text="Turma: -")
        self.lbl_mes.config(text="Mês/Ano: -")
        self.lbl_vencimento.config(text="Vencimento: -")
        self.lbl_status.config(text="Status: -", fg='black')
        self.lbl_valor_original.config(text="R$ 0,00")
        self.lbl_valor_final.config(text="R$ 0,00")
        
        # Limpar campos
        self.var_desconto.set('')
        self.var_multa.set('')
        self.var_outros.set('')
        self.var_observacoes.set('')
        
        # Desabilitar campos
        self.desabilitar_campos()
    
    def gerar_relatorio(self):
        """Gera relatório financeiro"""
        messagebox.showinfo("Relatório", "Funcionalidade em desenvolvimento")
    
    def setup_keyboard_shortcuts(self):
        """Configura atalhos de teclado"""
        # Bind Enter para processar pagamento quando campos estão habilitados
        def processar_com_enter(event):
            if self.btn_dar_baixa['state'] == 'normal':
                self.dar_baixa_mensalidade()
        
        # Aplicar bind em todos os campos
        self.entry_desconto.bind('<Return>', processar_com_enter)
        self.entry_multa.bind('<Return>', processar_com_enter)
        self.entry_outros.bind('<Return>', processar_com_enter)
        self.entry_observacoes.bind('<Return>', processar_com_enter)
        
        # Bind ESC para cancelar seleção
        def cancelar_com_esc(event):
            self.cancelar_selecao()
        
        self.parent_frame.bind('<Escape>', cancelar_com_esc)
        self.parent_frame.focus_set()  # Para receber eventos de teclado
    
    def mostrar_erro(self, mensagem):
        """Mostra tela de erro"""
        error_frame = tk.Frame(self.parent_frame, bg='white')
        error_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            error_frame,
            text="⚠️ Erro no Módulo Financeiro",
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
