import tkinter as tk
from tkinter import ttk, messagebox
from services.financeiro_service import FinanceiroService
from utils.formatters import format_date, format_currency
from datetime import datetime
import csv
import os

class FinanceiroInterface:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.financeiro_service = FinanceiroService()
        
        # Variáveis de controle
        self.turma_filtro_var = tk.StringVar()
        self.status_filtro_var = tk.StringVar(value="Todos")
        self.mes_filtro_var = tk.StringVar()
        
        # Variáveis do pagamento avançado
        self.valor_original_var = tk.DoubleVar()
        self.desconto_var = tk.DoubleVar()
        self.multa_var = tk.DoubleVar()
        self.outros_var = tk.DoubleVar()
        self.valor_final_var = tk.DoubleVar()
        self.observacoes_var = tk.StringVar()
        self.detalhes_outros_var = tk.StringVar()
        
        self.pagamento_selecionado = None
        
        self.create_interface()
        self.carregar_dados_iniciais()

    def create_interface(self):
        """Cria a interface principal"""
        # Container principal com scroll
        canvas = tk.Canvas(self.parent_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.parent_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='white')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Container principal
        main_container = tk.Frame(self.scrollable_frame, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        self.create_header(main_container)

        # Container principal - 2 colunas
        content_container = tk.Frame(main_container, bg='white')
        content_container.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        # Coluna esquerda - Lista de pagamentos
        left_column = tk.Frame(content_container, bg='white')
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Coluna direita - Painel de pagamento
        right_column = tk.Frame(content_container, bg='white')
        right_column.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_column.config(width=400)

        # Criar painéis
        self.create_filters_panel(left_column)
        self.create_payments_list(left_column)
        self.create_advanced_payment_panel(right_column)

    def create_header(self, parent):
        """Cria o cabeçalho"""
        header_frame = tk.Frame(parent, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Título
        title_frame = tk.Frame(header_frame, bg='white')
        title_frame.pack(fill=tk.X)

        tk.Label(
            title_frame,
            text="💰 Gestão Financeira Avançada",
            font=('Arial', 20, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(side=tk.LEFT)

        tk.Label(
            title_frame,
            text="Nova Lógica: Valor Original - Desconto + Multa + Outros",
            font=('Arial', 10),
            bg='white',
            fg='#27ae60'
        ).pack(side=tk.RIGHT)

        # Botões de ação
        buttons_frame = tk.Frame(header_frame, bg='white')
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Button(
            buttons_frame,
            text="🔄 Atualizar",
            command=self.carregar_pagamentos,
            font=('Arial', 10, 'bold'),
            bg='#17a2b8',
            fg='white',
            padx=15,
            pady=5,
            relief='flat'
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            buttons_frame,
            text="📊 Relatório",
            command=self.gerar_relatorio,
            font=('Arial', 10, 'bold'),
            bg='#28a745',
            fg='white',
            padx=15,
            pady=5,
            relief='flat'
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            buttons_frame,
            text="📈 Estatísticas",
            command=self.mostrar_estatisticas,
            font=('Arial', 10, 'bold'),
            bg='#6610f2',
            fg='white',
            padx=15,
            pady=5,
            relief='flat'
        ).pack(side=tk.LEFT, padx=5)

    def create_filters_panel(self, parent):
        """Cria painel de filtros"""
        filters_frame = tk.LabelFrame(
            parent,
            text=" 🔍 Filtros ",
            font=('Arial', 11, 'bold'),
            bg='white'
        )
        filters_frame.pack(fill=tk.X, pady=(0, 15))

        filter_container = tk.Frame(filters_frame, bg='white')
        filter_container.pack(fill=tk.X, padx=15, pady=10)

        # Turma
        tk.Label(filter_container, text="Turma:", font=('Arial', 9, 'bold'), bg='white').grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.turma_combo = ttk.Combobox(
            filter_container, textvariable=self.turma_filtro_var,
            state='readonly', width=20
        )
        self.turma_combo.grid(row=0, column=1, padx=(0, 10), sticky='w')

        # Status
        tk.Label(filter_container, text="Status:", font=('Arial', 9, 'bold'), bg='white').grid(row=0, column=2, sticky='w', padx=(0, 5))
        status_combo = ttk.Combobox(
            filter_container, textvariable=self.status_filtro_var,
            values=["Todos", "Pendente", "Atrasado", "Pago"],
            state='readonly', width=12
        )
        status_combo.grid(row=0, column=3, padx=(0, 10), sticky='w')

        # Mês
        tk.Label(filter_container, text="Mês:", font=('Arial', 9, 'bold'), bg='white').grid(row=0, column=4, sticky='w', padx=(0, 5))
        mes_combo = ttk.Combobox(
            filter_container, textvariable=self.mes_filtro_var,
            values=["Todos", "2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06",
                   "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12"],
            state='readonly', width=10
        )
        mes_combo.grid(row=0, column=5, padx=(0, 10), sticky='w')

        # Botão aplicar
        tk.Button(
            filter_container,
            text="🔍 Aplicar",
            command=self.aplicar_filtros,
            font=('Arial', 9, 'bold'),
            bg='#007bff',
            fg='white',
            padx=10,
            pady=3,
            relief='flat'
        ).grid(row=0, column=6, padx=(10, 0))

    def create_payments_list(self, parent):
        """Cria lista de pagamentos"""
        list_frame = tk.LabelFrame(
            parent,
            text=" 📋 Lista de Pagamentos - Clique para Selecionar ",
            font=('Arial', 11, 'bold'),
            bg='white'
        )
        list_frame.pack(fill=tk.BOTH, expand=True)

        # TreeView para pagamentos
        self.payments_tree = ttk.Treeview(
            list_frame,
            columns=('aluno', 'turma', 'mes', 'original', 'desconto', 'multa', 'outros', 'final', 'vencimento', 'status'),
            show='headings',
            height=15
        )

        # Configurar colunas
        columns_config = [
            ('aluno', 'Aluno', 140),
            ('turma', 'Turma', 80),
            ('mes', 'Mês', 70),
            ('original', 'Original', 80),
            ('desconto', 'Desconto', 70),
            ('multa', 'Multa', 60),
            ('outros', 'Outros', 60),
            ('final', 'Total', 80),
            ('vencimento', 'Vencimento', 90),
            ('status', 'Status', 80)
        ]

        for col, heading, width in columns_config:
            self.payments_tree.heading(col, text=heading)
            self.payments_tree.column(col, width=width)

        # Scrollbar
        payments_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.payments_tree.yview)
        self.payments_tree.configure(yscrollcommand=payments_scrollbar.set)

        self.payments_tree.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        payments_scrollbar.pack(side="right", fill="y", pady=15)

        # Bind selection - CORRIGIDO
        self.payments_tree.bind("<<TreeviewSelect>>", self.on_payment_selected)
        self.payments_tree.bind("<Button-1>", self.on_payment_click)

    def create_advanced_payment_panel(self, parent):
        """Cria painel avançado de pagamento"""
        payment_frame = tk.LabelFrame(
            parent,
            text=" 💳 Processar Pagamento Avançado ",
            font=('Arial', 11, 'bold'),
            bg='white'
        )
        payment_frame.pack(fill=tk.BOTH, expand=True)

        # Container do painel
        panel_container = tk.Frame(payment_frame, bg='white')
        panel_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Informações do pagamento selecionado
        info_frame = tk.LabelFrame(panel_container, text="Pagamento Selecionado", bg='white')
        info_frame.pack(fill=tk.X, pady=(0, 15))

        self.info_label = tk.Label(
            info_frame,
            text="👆 Clique em uma mensalidade na lista\npara habilitar os campos de pagamento",
            font=('Arial', 10),
            bg='white',
            fg='#6c757d',
            justify='center'
        )
        self.info_label.pack(pady=10)

        # Campos de entrada
        campos_frame = tk.LabelFrame(panel_container, text="Valores do Pagamento", bg='white')
        campos_frame.pack(fill=tk.X, pady=(0, 15))

        # Valor Original
        tk.Label(campos_frame, text="💰 Valor Original (R$):", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', padx=10, pady=(10, 5))
        self.valor_original_entry = tk.Entry(
            campos_frame, textvariable=self.valor_original_var,
            font=('Arial', 12), width=20, justify='right',
            state='disabled'  # Inicialmente desabilitado
        )
        self.valor_original_entry.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Desconto - HABILITADO
        tk.Label(campos_frame, text="📉 Desconto (R$):", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', padx=10, pady=(0, 5))
        self.desconto_entry = tk.Entry(
            campos_frame, textvariable=self.desconto_var,
            font=('Arial', 12), width=20, justify='right',
            state='disabled'  # Inicialmente desabilitado
        )
        self.desconto_entry.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.desconto_entry.bind('<KeyRelease>', self.calcular_valor_final)

        # Multa Manual - HABILITADO
        tk.Label(campos_frame, text="⚠️ Multa Manual (R$):", font=('Arial', 10, 'bold'), bg='white', fg='#e74c3c').pack(anchor='w', padx=10, pady=(0, 5))
        self.multa_entry = tk.Entry(
            campos_frame, textvariable=self.multa_var,
            font=('Arial', 12), width=20, justify='right',
            state='disabled'  # Inicialmente desabilitado
        )
        self.multa_entry.pack(fill=tk.X, padx=10, pady=(0, 5))

        tk.Label(
            campos_frame,
            text="💡 Não calculado automaticamente - você define o valor",
            font=('Arial', 8),
            bg='white',
            fg='#6c757d'
        ).pack(anchor='w', padx=10, pady=(0, 10))
        self.multa_entry.bind('<KeyRelease>', self.calcular_valor_final)

        # Outros - HABILITADO
        tk.Label(campos_frame, text="📚 Outros (R$):", font=('Arial', 10, 'bold'), bg='white', fg='#17a2b8').pack(anchor='w', padx=10, pady=(0, 5))
        self.outros_entry = tk.Entry(
            campos_frame, textvariable=self.outros_var,
            font=('Arial', 12), width=20, justify='right',
            state='disabled'  # Inicialmente desabilitado
        )
        self.outros_entry.pack(fill=tk.X, padx=10, pady=(0, 5))

        tk.Label(
            campos_frame,
            text="📝 Ex: livros, uniformes, festas, materiais",
            font=('Arial', 8),
            bg='white',
            fg='#6c757d'
        ).pack(anchor='w', padx=10, pady=(0, 10))
        self.outros_entry.bind('<KeyRelease>', self.calcular_valor_final)

        # Detalhes dos outros - HABILITADO
        tk.Label(campos_frame, text="📝 Detalhes dos Outros:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', padx=10, pady=(0, 5))
        self.detalhes_outros_entry = tk.Entry(
            campos_frame, textvariable=self.detalhes_outros_var,
            font=('Arial', 10), width=20,
            state='disabled'  # Inicialmente desabilitado
        )
        self.detalhes_outros_entry.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Separador visual
        separator = tk.Frame(campos_frame, height=2, bg='#dee2e6')
        separator.pack(fill=tk.X, padx=10, pady=10)

        # Valor Final (calculado)
        valor_final_frame = tk.Frame(campos_frame, bg='#28a745', relief='solid', bd=1)
        valor_final_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Label(
            valor_final_frame,
            text="💵 TOTAL A PAGAR (R$):",
            font=('Arial', 12, 'bold'),
            bg='#28a745',
            fg='white'
        ).pack(pady=(5, 0))

        self.valor_final_label = tk.Label(
            valor_final_frame,
            text="0,00",
            font=('Arial', 16, 'bold'),
            bg='#28a745',
            fg='white'
        )
        self.valor_final_label.pack(pady=(0, 5))

        # Observações
        obs_frame = tk.LabelFrame(panel_container, text="Observações do Pagamento", bg='white')
        obs_frame.pack(fill=tk.X, pady=(0, 15))

        self.observacoes_text = tk.Text(obs_frame, height=3, font=('Arial', 10), wrap=tk.WORD, state='disabled')
        self.observacoes_text.pack(fill=tk.X, padx=10, pady=10)

        # Botão de processar - INICIALMENTE DESABILITADO
        self.process_button = tk.Button(
            panel_container,
            text="💳 DAR BAIXA / CONFIRMAR PAGAMENTO",
            command=self.processar_pagamento,
            font=('Arial', 12, 'bold'),
            bg='#6c757d',  # Cinza quando desabilitado
            fg='white',
            padx=20,
            pady=15,
            relief='flat',
            cursor='hand2',
            state='disabled'
        )
        self.process_button.pack(fill=tk.X, pady=(0, 10))

        # Resumo do cálculo
        resumo_frame = tk.LabelFrame(panel_container, text="Resumo do Cálculo", bg='white')
        resumo_frame.pack(fill=tk.X)

        self.resumo_text = tk.Text(
            resumo_frame, height=6, font=('Arial', 9),
            bg='#f8f9fa', wrap=tk.WORD, state='disabled'
        )
        self.resumo_text.pack(fill=tk.X, padx=10, pady=10)

    def carregar_dados_iniciais(self):
        """Carrega dados iniciais"""
        try:
            # Carregar turmas
            turmas = self.financeiro_service.listar_turmas()
            turmas_display = ["Todas"] + [turma['display'] for turma in turmas]
            self.turma_combo['values'] = turmas_display
            self.turma_combo.set("Todas")
            
            self.turmas_data = {"Todas": None}
            for turma in turmas:
                self.turmas_data[turma['display']] = turma
            
            # Carregar pagamentos
            self.carregar_pagamentos()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados: {str(e)}")

    def aplicar_filtros(self):
        """Aplica filtros e recarrega pagamentos"""
        self.carregar_pagamentos()

    def carregar_pagamentos(self):
        """Carrega lista de pagamentos com filtros"""
        # Limpar lista
        for item in self.payments_tree.get_children():
            self.payments_tree.delete(item)

        try:
            # Preparar filtros
            filtros = {}
            
            turma_selecionada = self.turma_filtro_var.get()
            if turma_selecionada and turma_selecionada != "Todas":
                turma_data = self.turmas_data.get(turma_selecionada)
                if turma_data:
                    filtros['turma_id'] = turma_data['id']

            status_selecionado = self.status_filtro_var.get()
            if status_selecionado and status_selecionado != "Todos":
                filtros['status'] = status_selecionado

            mes_selecionado = self.mes_filtro_var.get()
            if mes_selecionado and mes_selecionado != "Todos":
                filtros['mes_referencia'] = mes_selecionado

            # Carregar dados
            if filtros or self.status_filtro_var.get() == "Todos":
                pagamentos = self.financeiro_service.obter_relatorio_financeiro_detalhado(filtros)
            else:
                pagamentos = self.financeiro_service.obter_pagamentos_pendentes()

            # Preencher TreeView
            for pagamento in pagamentos:
                status_display = pagamento.get('status_atual', pagamento['status'])
                
                # Cores baseadas no status
                tags = []
                if status_display == 'Atrasado':
                    tags.append('atrasado')
                elif status_display == 'Pago':
                    tags.append('pago')
                else:
                    tags.append('pendente')

                # Usar um ID único para cada pagamento
                pagamento_id = pagamento.get('id', f"pag_{len(self.payments_tree.get_children())}")

                self.payments_tree.insert('', 'end', values=(
                    pagamento['aluno_nome'],
                    pagamento['turma_nome'],
                    pagamento['mes_referencia'],
                    f"{pagamento['valor_original']:.2f}",
                    f"{pagamento['desconto_aplicado']:.2f}",
                    f"{pagamento['multa_aplicada']:.2f}",
                    f"{pagamento['outros']:.2f}",
                    f"{pagamento['valor_final']:.2f}",
                    format_date(pagamento['data_vencimento']),
                    status_display
                ), tags=(str(pagamento_id),))

            # Configurar tags de cores
            self.payments_tree.tag_configure('atrasado', background='#f8d7da')
            self.payments_tree.tag_configure('pago', background='#d4edda')
            self.payments_tree.tag_configure('pendente', background='#fff3cd')

            print(f"✅ {len(pagamentos)} pagamentos carregados")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar pagamentos: {str(e)}")
            print(f"❌ Erro ao carregar pagamentos: {e}")

    def on_payment_click(self, event):
        """Callback para clique do mouse"""
        # Identificar qual item foi clicado
        item = self.payments_tree.identify('item', event.x, event.y)
        if item:
            self.payments_tree.selection_set(item)
            self.on_payment_selected()

    def on_payment_selected(self, event=None):
        """Callback quando pagamento é selecionado - CORRIGIDO"""
        selection = self.payments_tree.selection()
        if not selection:
            return

        try:
            item = selection[0]
            pagamento_id_str = self.payments_tree.item(item, 'tags')[0] if self.payments_tree.item(item, 'tags') else None
            
            if not pagamento_id_str:
                print("❌ Nenhuma tag encontrada para o item")
                return

            # Tenta converter para int, se falhar usa como string
            try:
                pagamento_id = int(pagamento_id_str)
            except ValueError:
                print(f"⚠️ ID não é numérico: {pagamento_id_str}")
                # Se não conseguir converter, usar dados da linha diretamente
                self.carregar_pagamento_da_linha(item)
                return
            
            # Carregar detalhes do pagamento pelo ID
            pagamento = self.financeiro_service.obter_detalhes_pagamento(pagamento_id)
            if not pagamento:
                print(f"❌ Pagamento ID {pagamento_id} não encontrado, usando dados da linha")
                self.carregar_pagamento_da_linha(item)
                return

            self.carregar_pagamento_completo(pagamento)

        except Exception as e:
            print(f"❌ Erro ao selecionar pagamento: {e}")
            # Fallback: carregar dados da linha
            try:
                self.carregar_pagamento_da_linha(selection[0])
            except:
                messagebox.showerror("Erro", f"Erro ao selecionar pagamento: {str(e)}")

    def carregar_pagamento_da_linha(self, item):
        """Carrega pagamento usando dados diretamente da linha da TreeView"""
        try:
            values = self.payments_tree.item(item, 'values')
            if not values or len(values) < 10:
                return

            # Criar objeto pagamento baseado nos dados da linha
            pagamento = {
                'id': 0,  # ID fictício
                'aluno_nome': values[0],
                'turma_nome': values[1], 
                'serie': '',
                'mes_referencia': values[2],
                'valor_original': float(values[3]),
                'desconto_aplicado': float(values[4]),
                'multa_aplicada': float(values[5]),
                'outros': float(values[6]),
                'valor_final': float(values[7]),
                'data_vencimento': values[8],
                'status': values[9],
                'observacoes_pagamento': '',
                'detalhes_outros': ''
            }

            self.carregar_pagamento_completo(pagamento)
            print("✅ Pagamento carregado usando dados da linha")

        except Exception as e:
            print(f"❌ Erro ao carregar pagamento da linha: {e}")

    def carregar_pagamento_completo(self, pagamento):
        """Carrega dados completos do pagamento e habilita campos"""
        try:
            self.pagamento_selecionado = pagamento

            # Atualizar painel de informações
            info_text = f"🎓 {pagamento['aluno_nome']}\n"
            info_text += f"🏫 {pagamento['turma_nome']}"
            if pagamento.get('serie'):
                info_text += f" - {pagamento['serie']}"
            info_text += f"\n📅 {pagamento['mes_referencia']}\n"
            info_text += f"⏰ Venc: {pagamento['data_vencimento']}\n"
            info_text += f"📊 Status: {pagamento['status']}"

            self.info_label.config(text=info_text, justify='left')

            # Preencher campos
            self.valor_original_var.set(pagamento['valor_original'])
            self.desconto_var.set(pagamento['desconto_aplicado'])
            self.multa_var.set(pagamento['multa_aplicada'])
            self.outros_var.set(pagamento['outros'])
            self.detalhes_outros_var.set(pagamento.get('detalhes_outros', ''))

            # HABILITAR CAMPOS - CORREÇÃO PRINCIPAL
            if pagamento['status'] != 'Pago':
                self.habilitar_campos_edicao()
            else:
                self.desabilitar_campos_edicao()

            # Preencher observações
            self.observacoes_text.config(state='normal')
            self.observacoes_text.delete(1.0, tk.END)
            self.observacoes_text.insert(1.0, pagamento.get('observacoes_pagamento', ''))
            if pagamento['status'] == 'Pago':
                self.observacoes_text.config(state='disabled')

            # Calcular valor final
            self.calcular_valor_final()

            print(f"✅ Pagamento selecionado: {pagamento['aluno_nome']} - {pagamento['mes_referencia']}")

        except Exception as e:
            print(f"❌ Erro ao carregar pagamento completo: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar dados do pagamento: {str(e)}")

    def habilitar_campos_edicao(self):
        """Habilita campos para edição quando pagamento é selecionado"""
        try:
            # Habilitar campos de entrada
            self.valor_original_entry.config(state='readonly', bg='#e9ecef')  # Só leitura
            self.desconto_entry.config(state='normal', bg='white')
            self.multa_entry.config(state='normal', bg='white')
            self.outros_entry.config(state='normal', bg='white')
            self.detalhes_outros_entry.config(state='normal', bg='white')
            
            # Habilitar campo de observações
            self.observacoes_text.config(state='normal', bg='white')
            
            # Habilitar botão de processar
            self.process_button.config(
                state='normal',
                bg='#007bff',
                text="💳 DAR BAIXA / CONFIRMAR PAGAMENTO"
            )
            
            print("✅ Campos habilitados para edição")
            
        except Exception as e:
            print(f"❌ Erro ao habilitar campos: {e}")

    def desabilitar_campos_edicao(self):
        """Desabilita campos quando não há seleção ou pagamento já está pago"""
        try:
            # Desabilitar campos de entrada
            self.valor_original_entry.config(state='disabled', bg='#f8f9fa')
            self.desconto_entry.config(state='disabled', bg='#f8f9fa')
            self.multa_entry.config(state='disabled', bg='#f8f9fa')
            self.outros_entry.config(state='disabled', bg='#f8f9fa')
            self.detalhes_outros_entry.config(state='disabled', bg='#f8f9fa')
            
            # Desabilitar campo de observações
            self.observacoes_text.config(state='disabled', bg='#f8f9fa')
            
            # Desabilitar botão de processar
            self.process_button.config(
                state='disabled',
                bg='#6c757d',
                text="💳 SELECIONE UM PAGAMENTO PRIMEIRO"
            )
            
        except Exception as e:
            print(f"❌ Erro ao desabilitar campos: {e}")

    def calcular_valor_final(self, event=None):
        """Calcula valor final em tempo real"""
        try:
            valor_original = self.valor_original_var.get() or 0
            desconto = self.desconto_var.get() or 0
            multa = self.multa_var.get() or 0
            outros = self.outros_var.get() or 0

            valor_final = max(0, valor_original - desconto + multa + outros)
            self.valor_final_label.config(text=f"{valor_final:.2f}")

            # Atualizar resumo
            self.atualizar_resumo_calculo(valor_original, desconto, multa, outros, valor_final)

        except Exception as e:
            self.valor_final_label.config(text="0,00")
            print(f"❌ Erro no cálculo: {e}")

    def atualizar_resumo_calculo(self, original, desconto, multa, outros, final):
        """Atualiza resumo do cálculo"""
        try:
            resumo = f"""
📊 RESUMO DO PAGAMENTO:

💰 Valor Original:     R$ {original:8.2f}
📉 (-) Desconto:       R$ {desconto:8.2f}
⚠️  (+) Multa Manual:   R$ {multa:8.2f}
📚 (+) Outros:         R$ {outros:8.2f}
{'='*35}
💵 TOTAL A PAGAR:      R$ {final:8.2f}

💡 Nova Lógica Aplicada:
   Total = Original - Desconto + Multa + Outros
            """

            self.resumo_text.config(state='normal')
            self.resumo_text.delete(1.0, tk.END)
            self.resumo_text.insert(1.0, resumo.strip())
            self.resumo_text.config(state='disabled')

        except Exception as e:
            print(f"❌ Erro ao atualizar resumo: {e}")

    def processar_pagamento(self):
        """Processa o pagamento com valores avançados - CORRIGIDO"""
        if not self.pagamento_selecionado:
            messagebox.showwarning("Aviso", "Selecione um pagamento primeiro!")
            return

        if self.pagamento_selecionado['status'] == 'Pago':
            messagebox.showwarning("Aviso", "Este pagamento já foi processado!")
            return

        try:
            # Obter valores dos campos
            valor_original = self.valor_original_var.get() or 0
            desconto = self.desconto_var.get() or 0
            multa = self.multa_var.get() or 0
            outros = self.outros_var.get() or 0
            valor_final = max(0, valor_original - desconto + multa + outros)

            observacoes = self.observacoes_text.get(1.0, tk.END).strip()
            detalhes_outros = self.detalhes_outros_var.get().strip()

            # Confirmação detalhada
            confirm_msg = f"""Confirmar processamento do pagamento?

🎓 Aluno: {self.pagamento_selecionado['aluno_nome']}
📅 Mês: {self.pagamento_selecionado['mes_referencia']}

💰 Valor Original: R$ {valor_original:.2f}
📉 Desconto: R$ {desconto:.2f}
⚠️ Multa: R$ {multa:.2f}
📚 Outros: R$ {outros:.2f}
💵 TOTAL: R$ {valor_final:.2f}"""

            if detalhes_outros:
                confirm_msg += f"\n📝 Detalhes Outros: {detalhes_outros}"

            if not messagebox.askyesno("Confirmar Pagamento", confirm_msg):
                return

            # Processar pagamento
            pagamento_id = self.pagamento_selecionado.get('id', 0)
            if pagamento_id == 0:
                # Se não tiver ID, tentar buscar pelo nome e mês
                messagebox.showinfo("Aviso", "Pagamento será processado com dados básicos")

            resultado = self.financeiro_service.processar_pagamento_avancado(
                pagamento_id,
                valor_original, desconto, multa, outros,
                observacoes, detalhes_outros
            )

            if resultado['success']:
                messagebox.showinfo(
                    "✅ Pagamento Processado",
                    f"Pagamento registrado com sucesso!\n\n"
                    f"💵 Valor Final: R$ {resultado['valor_final']:.2f}\n"
                    f"📊 Status: PAGO\n\n"
                    f"🎓 Aluno: {self.pagamento_selecionado['aluno_nome']}\n"
                    f"📅 Mês: {self.pagamento_selecionado['mes_referencia']}"
                )
                
                # Recarregar dados
                self.carregar_pagamentos()
                self.limpar_painel_pagamento()
            else:
                messagebox.showerror("Erro", f"Erro ao processar pagamento:\n{resultado['error']}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar pagamento:\n{str(e)}")
            print(f"❌ Erro ao processar pagamento: {e}")

    def limpar_painel_pagamento(self):
        """Limpa painel de pagamento"""
        try:
            self.pagamento_selecionado = None
            self.valor_original_var.set(0)
            self.desconto_var.set(0)
            self.multa_var.set(0)
            self.outros_var.set(0)
            self.observacoes_var.set("")
            self.detalhes_outros_var.set("")
            
            self.observacoes_text.delete(1.0, tk.END)
            self.valor_final_label.config(text="0,00")
            
            self.info_label.config(
                text="👆 Clique em uma mensalidade na lista\npara habilitar os campos de pagamento",
                justify='center'
            )
            
            self.resumo_text.config(state='normal')
            self.resumo_text.delete(1.0, tk.END)
            self.resumo_text.config(state='disabled')

            # Desabilitar campos
            self.desabilitar_campos_edicao()
            
        except Exception as e:
            print(f"❌ Erro ao limpar painel: {e}")

    def gerar_relatorio(self):
        """Gera relatório CSV detalhado"""
        try:
            # Preparar filtros atuais
            filtros = {}
            
            turma_selecionada = self.turma_filtro_var.get()
            if turma_selecionada and turma_selecionada != "Todas":
                turma_data = self.turmas_data.get(turma_selecionada)
                if turma_data:
                    filtros['turma_id'] = turma_data['id']

            status_selecionado = self.status_filtro_var.get()
            if status_selecionado and status_selecionado != "Todos":
                filtros['status'] = status_selecionado

            # Obter dados
            dados = self.financeiro_service.obter_relatorio_financeiro_detalhado(filtros)
            
            if not dados:
                messagebox.showwarning("Aviso", "Não há dados para gerar relatório!")
                return

            # Nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"relatorio_financeiro_avancado_{timestamp}.csv"

            # Salvar CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'Aluno', 'Turma', 'Série', 'Mês Referência',
                    'Valor Original', 'Desconto', 'Multa', 'Outros', 'Valor Final',
                    'Data Vencimento', 'Data Pagamento', 'Status',
                    'Observações', 'Detalhes Outros'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for item in dados:
                    writer.writerow({
                        'Aluno': item['aluno_nome'],
                        'Turma': item['turma_nome'],
                        'Série': item['serie'],
                        'Mês Referência': item['mes_referencia'],
                        'Valor Original': item['valor_original'],
                        'Desconto': item['desconto_aplicado'],
                        'Multa': item['multa_aplicada'],
                        'Outros': item['outros'],
                        'Valor Final': item['valor_final'],
                        'Data Vencimento': item['data_vencimento'],
                        'Data Pagamento': item['data_pagamento'] or '',
                        'Status': item['status_atual'],
                        'Observações': item['observacoes_pagamento'],
                        'Detalhes Outros': item['detalhes_outros']
                    })

            messagebox.showinfo(
                "Relatório Gerado",
                f"✅ Relatório salvo como:\n{filename}\n\n"
                f"📊 Total de registros: {len(dados)}"
            )

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")

    def mostrar_estatisticas(self):
        """Mostra estatísticas avançadas"""
        try:
            stats = self.financeiro_service.obter_estatisticas_avancadas()
            
            if not stats:
                messagebox.showwarning("Aviso", "Não há dados para estatísticas!")
                return

            # Janela de estatísticas
            stats_window = tk.Toplevel(self.parent_frame)
            stats_window.title("📈 Estatísticas Financeiras Avançadas")
            stats_window.geometry("500x400")
            stats_window.transient(self.parent_frame.winfo_toplevel())
            
            # Texto das estatísticas
            stats_text = tk.Text(stats_window, font=('Arial', 10), wrap=tk.WORD)
            stats_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Formatar estatísticas
            texto = "📊 ESTATÍSTICAS FINANCEIRAS AVANÇADAS\n"
            texto += "=" * 50 + "\n\n"
            
            if 'pagamentos_realizados' in stats:
                p = stats['pagamentos_realizados']
                texto += "✅ PAGAMENTOS REALIZADOS:\n"
                texto += f"   📈 Quantidade: {p['quantidade']}\n"
                texto += f"   💰 Valor Original: R$ {p['valor_original']:.2f}\n"
                texto += f"   📉 Total Descontos: R$ {p['total_descontos']:.2f}\n"
                texto += f"   ⚠️ Total Multas: R$ {p['total_multas']:.2f}\n"
                texto += f"   📚 Total Outros: R$ {p['total_outros']:.2f}\n"
                texto += f"   💵 Valor Final: R$ {p['valor_final']:.2f}\n\n"
            
            if 'pagamentos_pendentes' in stats:
                p = stats['pagamentos_pendentes']
                texto += "⏳ PAGAMENTOS PENDENTES:\n"
                texto += f"   📈 Quantidade: {p['quantidade']}\n"
                texto += f"   💰 Valor Total: R$ {p['valor_total']:.2f}\n\n"
            
            if 'componentes' in stats:
                c = stats['componentes']
                texto += "📊 ANÁLISE DE COMPONENTES:\n"
                texto += f"   ⚠️ Multa Média: R$ {c['multa_media']:.2f}\n"
                texto += f"   ⚠️ Multa Máxima: R$ {c['multa_maxima']:.2f}\n"
                texto += f"   📚 Outros Médio: R$ {c['outros_medio']:.2f}\n"
                texto += f"   📚 Outros Máximo: R$ {c['outros_maximo']:.2f}\n"
                texto += f"   📉 Desconto Médio: R$ {c['desconto_medio']:.2f}\n"
            
            stats_text.insert(1.0, texto)
            stats_text.config(state='disabled')

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao obter estatísticas: {str(e)}")