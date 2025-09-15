import tkinter as tk
from tkinter import ttk, messagebox
from services.transferencia_service import TransferenciaService
from utils.formatters import format_date, format_currency
from datetime import datetime, date
import csv
import os

class TransferenciaInterface:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.transferencia_service = TransferenciaService()
        
        # Variáveis de controle
        self.turma_origem_var = tk.StringVar()
        self.turma_destino_var = tk.StringVar()
        self.motivo_var = tk.StringVar()
        self.observacoes_var = tk.StringVar()
        self.alunos_selecionados = {}  # {aluno_id: checkbox_var}
        
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

        # Bind mousewheel
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

        # Estatísticas rápidas
        self.create_stats_section(main_container)

        # Painel de transferência
        self.create_transfer_section(main_container)

        # Histórico de transferências
        self.create_history_section(main_container)

    def create_header(self, parent):
        """Cria o cabeçalho"""
        header_frame = tk.Frame(parent, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # Título
        tk.Label(
            header_frame,
            text="🔄 Sistema de Transferência de Alunos",
            font=('Arial', 24, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(side=tk.LEFT)

        # Botões de ação
        buttons_frame = tk.Frame(header_frame, bg='white')
        buttons_frame.pack(side=tk.RIGHT)

        # Botão de relatório
        tk.Button(
            buttons_frame,
            text="📊 Gerar Relatório",
            command=self.gerar_relatorio,
            font=('Arial', 11, 'bold'),
            bg='#17a2b8',
            fg='white',
            padx=15,
            pady=8,
            relief='flat',
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Botão de atualizar
        tk.Button(
            buttons_frame,
            text="🔄 Atualizar",
            command=self.atualizar_dados,
            font=('Arial', 11, 'bold'),
            bg='#28a745',
            fg='white',
            padx=15,
            pady=8,
            relief='flat',
            cursor='hand2'
        ).pack(side=tk.LEFT)

    def create_stats_section(self, parent):
        """Cria seção de estatísticas"""
        stats_frame = tk.LabelFrame(
            parent,
            text=" 📊 Estatísticas de Transferências ",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        stats_frame.pack(fill=tk.X, pady=(0, 20))

        # Container interno
        stats_container = tk.Frame(stats_frame, bg='white')
        stats_container.pack(fill=tk.X, padx=20, pady=15)

        # Grid de estatísticas
        self.stats_widgets = {}
        stats_data = [
            ("📊", "0", "Total de Transferências", "#3498db"),
            ("📅", "0", "Transferências este Mês", "#e74c3c"),
            ("🗓️", "0", "Transferências este Ano", "#f39c12"),
            ("📈", "N/A", "Turma que Mais Recebe", "#27ae60"),
            ("📉", "N/A", "Turma que Mais Perde", "#e67e22")
        ]

        for i, (icon, value, label, color) in enumerate(stats_data):
            self.create_stat_widget(stats_container, icon, value, label, color, i)

    def create_stat_widget(self, parent, icon, value, label, color, index):
        """Cria widget de estatística"""
        # Frame para cada stat
        stat_frame = tk.Frame(parent, bg=color, bd=1, relief='solid')
        stat_frame.grid(row=index//3, column=index%3, padx=8, pady=8, sticky='ew')

        # Configurar grid
        parent.columnconfigure(index%3, weight=1)

        # Container interno
        inner_frame = tk.Frame(stat_frame, bg=color)
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Ícone
        tk.Label(
            inner_frame, text=icon, font=('Arial', 16),
            bg=color, fg='white'
        ).pack(side=tk.LEFT)

        # Textos
        text_frame = tk.Frame(inner_frame, bg=color)
        text_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Valor
        value_label = tk.Label(
            text_frame, text=value, font=('Arial', 14, 'bold'),
            bg=color, fg='white', anchor='e'
        )
        value_label.pack(anchor='e')

        # Label
        tk.Label(
            text_frame, text=label, font=('Arial', 9),
            bg=color, fg='white', anchor='e'
        ).pack(anchor='e')

        # Armazenar referência para atualização
        self.stats_widgets[label] = value_label

    def create_transfer_section(self, parent):
        """Cria seção principal de transferência"""
        transfer_frame = tk.LabelFrame(
            parent,
            text=" 🔄 Painel de Transferências ",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        transfer_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Container principal
        main_transfer_container = tk.Frame(transfer_frame, bg='white')
        main_transfer_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Dividir em duas colunas
        left_column = tk.Frame(main_transfer_container, bg='white')
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right_column = tk.Frame(main_transfer_container, bg='white')
        right_column.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        # === COLUNA ESQUERDA: Seleção e Lista ===
        self.create_selection_panel(left_column)
        self.create_students_list(left_column)

        # === COLUNA DIREITA: Painel de Transferência ===
        self.create_transfer_panel(right_column)

    def create_selection_panel(self, parent):
        """Cria painel de seleção de turmas"""
        selection_frame = tk.LabelFrame(
            parent,
            text=" 🎯 Seleção de Turmas ",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg='#34495e'
        )
        selection_frame.pack(fill=tk.X, pady=(0, 15))

        selection_container = tk.Frame(selection_frame, bg='white')
        selection_container.pack(fill=tk.X, padx=15, pady=10)

        # Turma de origem
        origem_frame = tk.Frame(selection_container, bg='white')
        origem_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            origem_frame, text="Turma de Origem:", font=('Arial', 10, 'bold'),
            bg='white', fg='#2c3e50'
        ).pack(anchor='w')

        self.turma_origem_combo = ttk.Combobox(
            origem_frame,
            textvariable=self.turma_origem_var,
            state='readonly',
            font=('Arial', 10),
            width=50
        )
        self.turma_origem_combo.pack(fill=tk.X, pady=(5, 0))
        self.turma_origem_combo.bind('<<ComboboxSelected>>', self.on_turma_origem_selected)

        # Botão para carregar alunos
        tk.Button(
            origem_frame,
            text="📋 Carregar Alunos da Turma",
            command=self.carregar_alunos_turma,
            font=('Arial', 10, 'bold'),
            bg='#007bff',
            fg='white',
            padx=12,
            pady=6,
            relief='flat',
            cursor='hand2'
        ).pack(pady=(10, 0))

    def create_students_list(self, parent):
        """Cria lista de alunos"""
        list_frame = tk.LabelFrame(
            parent,
            text=" 👥 Alunos da Turma ",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg='#34495e'
        )
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Toolbar da lista
        toolbar = tk.Frame(list_frame, bg='white')
        toolbar.pack(fill=tk.X, padx=15, pady=(10, 5))

        # Botões de seleção
        tk.Button(
            toolbar, text="☑️ Selecionar Todos", command=self.selecionar_todos,
            font=('Arial', 9), bg='#28a745', fg='white', padx=10, pady=4,
            relief='flat', cursor='hand2'
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            toolbar, text="☐ Limpar Seleção", command=self.limpar_selecao,
            font=('Arial', 9), bg='#6c757d', fg='white', padx=10, pady=4,
            relief='flat', cursor='hand2'
        ).pack(side=tk.LEFT)

        # Label de contador
        self.contador_label = tk.Label(
            toolbar, text="0 alunos selecionados", font=('Arial', 9),
            bg='white', fg='#6c757d'
        )
        self.contador_label.pack(side=tk.RIGHT)

        # Frame da lista com scroll
        list_container = tk.Frame(list_frame, bg='white')
        list_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 15))

        # Canvas e scrollbar para a lista
        self.list_canvas = tk.Canvas(list_container, bg='white', highlightthickness=1, highlightcolor='#ddd')
        list_scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.list_canvas.yview)
        self.students_frame = tk.Frame(self.list_canvas, bg='white')

        self.students_frame.bind(
            "<Configure>",
            lambda e: self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all"))
        )

        self.list_canvas.create_window((0, 0), window=self.students_frame, anchor="nw")
        self.list_canvas.configure(yscrollcommand=list_scrollbar.set)

        self.list_canvas.pack(side="left", fill="both", expand=True)
        list_scrollbar.pack(side="right", fill="y")

    def create_transfer_panel(self, parent):
        """Cria painel de transferência"""
        transfer_panel = tk.LabelFrame(
            parent,
            text=" ➡️ Executar Transferência ",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg='#34495e',
            width=350
        )
        transfer_panel.pack(fill=tk.Y, expand=True)
        transfer_panel.pack_propagate(False)  # Manter largura fixa

        panel_container = tk.Frame(transfer_panel, bg='white')
        panel_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Turma de destino
        tk.Label(
            panel_container, text="🎯 Turma de Destino:", font=('Arial', 10, 'bold'),
            bg='white', fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 5))

        self.turma_destino_combo = ttk.Combobox(
            panel_container,
            textvariable=self.turma_destino_var,
            state='readonly',
            font=('Arial', 10),
            width=35
        )
        self.turma_destino_combo.pack(fill=tk.X, pady=(0, 15))

        # Motivo da transferência
        tk.Label(
            panel_container, text="📝 Motivo da Transferência:", font=('Arial', 10, 'bold'),
            bg='white', fg='#2c3e50'
        ).pack(anchor='w', pady=(0, 5))

        motivos_frame = tk.Frame(panel_container, bg='white')
        motivos_frame.pack(fill=tk.X, pady=(0, 15))

        # Combobox com motivos pré-definidos
        self.motivo_combo = ttk.Combobox(
            motivos_frame,
            textvariable=self.motivo_var,
            font=('Arial', 10),
            width=35,
            values=[
                "Promoção para próxima série",
                "Mudança de turno",
                "Remanejamento de turma",
                "Solicitação dos pais",
                "Adequação pedagógica",
                "Transferência administrativa",
                "Outros"
            ]
        )
        self.motivo_combo.pack(fill=tk.X)
        self.motivo_combo.set("Promoção para próxima série")

        # Observações
        tk.Label(
            panel_container, text="💭 Observações Adicionais:", font=('Arial', 10, 'bold'),
            bg='white', fg='#2c3e50'
        ).pack(anchor='w', pady=(15, 5))

        obs_frame = tk.Frame(panel_container, bg='white')
        obs_frame.pack(fill=tk.X, pady=(0, 20))

        self.obs_text = tk.Text(
            obs_frame, height=4, font=('Arial', 9),
            bg='#f8f9fa', relief='solid', bd=1,
            wrap=tk.WORD
        )
        self.obs_text.pack(fill=tk.X)

        # Botões de ação
        buttons_frame = tk.Frame(panel_container, bg='white')
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        # Transferir selecionados
        self.btn_transferir = tk.Button(
            buttons_frame,
            text="🚀 Transferir Selecionados",
            command=self.transferir_alunos_selecionados,
            font=('Arial', 11, 'bold'),
            bg='#28a745',
            fg='white',
            padx=15,
            pady=10,
            relief='flat',
            cursor='hand2',
            state='disabled'
        )
        self.btn_transferir.pack(fill=tk.X, pady=(0, 8))

        # Simular transferência (validação)
        tk.Button(
            buttons_frame,
            text="🔍 Validar Transferência",
            command=self.validar_transferencias,
            font=('Arial', 10),
            bg='#17a2b8',
            fg='white',
            padx=15,
            pady=8,
            relief='flat',
            cursor='hand2'
        ).pack(fill=tk.X)

        # Status da transferência
        self.status_frame = tk.Frame(panel_container, bg='white')
        self.status_frame.pack(fill=tk.X, pady=(15, 0))

        self.status_label = tk.Label(
            self.status_frame, text="ℹ️ Selecione alunos e turma de destino",
            font=('Arial', 9), bg='white', fg='#6c757d',
            wraplength=300, justify='left'
        )
        self.status_label.pack(fill=tk.X)

    def create_history_section(self, parent):
        """Cria seção do histórico"""
        history_frame = tk.LabelFrame(
            parent,
            text=" 📚 Histórico de Transferências ",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            bd=2,
            relief='groove'
        )
        history_frame.pack(fill=tk.BOTH, expand=True)

        # Toolbar do histórico
        history_toolbar = tk.Frame(history_frame, bg='white')
        history_toolbar.pack(fill=tk.X, padx=20, pady=(15, 10))

        tk.Label(
            history_toolbar, text="📋 Últimas 20 transferências realizadas:",
            font=('Arial', 11, 'bold'), bg='white', fg='#34495e'
        ).pack(side=tk.LEFT)

        tk.Button(
            history_toolbar, text="🔄 Atualizar Histórico", command=self.carregar_historico,
            font=('Arial', 9), bg='#6c757d', fg='white', padx=10, pady=4,
            relief='flat', cursor='hand2'
        ).pack(side=tk.RIGHT)

        # Tabela do histórico
        history_container = tk.Frame(history_frame, bg='white')
        history_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))

        # Treeview para o histórico
        self.history_tree = ttk.Treeview(
            history_container,
            columns=('data', 'aluno', 'origem', 'destino', 'motivo'),
            show='headings',
            height=8
        )

        # Configurar colunas
        self.history_tree.heading('data', text='Data', anchor='w')
        self.history_tree.heading('aluno', text='Aluno', anchor='w')
        self.history_tree.heading('origem', text='Turma Origem', anchor='w')
        self.history_tree.heading('destino', text='Turma Destino', anchor='w')
        self.history_tree.heading('motivo', text='Motivo', anchor='w')

        self.history_tree.column('data', width=80, minwidth=80)
        self.history_tree.column('aluno', width=180, minwidth=150)
        self.history_tree.column('origem', width=150, minwidth=120)
        self.history_tree.column('destino', width=150, minwidth=120)
        self.history_tree.column('motivo', width=200, minwidth=150)

        # Scrollbar para a tabela
        history_scroll = ttk.Scrollbar(history_container, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scroll.set)

        self.history_tree.pack(side="left", fill="both", expand=True)
        history_scroll.pack(side="right", fill="y")

        # Bind para duplo clique
        self.history_tree.bind("<Double-1>", self.on_historico_double_click)

    def carregar_dados_iniciais(self):
        """Carrega dados iniciais da interface"""
        try:
            # Carregar turmas para os comboboxes
            turmas = self.transferencia_service.listar_turmas_para_filtro()
            turmas_display = [turma['display'] for turma in turmas]
            
            self.turma_origem_combo['values'] = turmas_display
            self.turma_destino_combo['values'] = turmas_display
            
            # Armazenar referência das turmas
            self.turmas_data = {turma['display']: turma for turma in turmas}
            
            # Carregar estatísticas
            self.carregar_estatisticas()
            
            # Carregar histórico
            self.carregar_historico()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados iniciais: {str(e)}")

    def on_turma_origem_selected(self, event=None):
        """Callback quando turma de origem é selecionada"""
        self.limpar_lista_alunos()
        self.atualizar_status("📋 Clique em 'Carregar Alunos da Turma' para listar os alunos")

    def carregar_alunos_turma(self):
        """Carrega alunos da turma selecionada"""
        turma_display = self.turma_origem_var.get()
        if not turma_display:
            messagebox.showwarning("Aviso", "Selecione uma turma de origem primeiro!")
            return
        
        try:
            turma_data = self.turmas_data[turma_display]
            alunos = self.transferencia_service.listar_alunos_por_turma(turma_data['id'])
            
            self.exibir_alunos(alunos)
            self.atualizar_status(f"📋 {len(alunos)} alunos carregados da turma {turma_display}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar alunos: {str(e)}")

    def exibir_alunos(self, alunos):
        """Exibe lista de alunos com checkboxes"""
        # Limpar lista anterior
        self.limpar_lista_alunos()
        
        if not alunos:
            tk.Label(
                self.students_frame, text="📭 Nenhum aluno encontrado nesta turma",
                font=('Arial', 12), bg='white', fg='#6c757d'
            ).pack(pady=20)
            return
        
        # Header da lista
        header_frame = tk.Frame(self.students_frame, bg='#f8f9fa', relief='solid', bd=1)
        header_frame.pack(fill=tk.X, padx=2, pady=(5, 0))
        
        tk.Label(header_frame, text="", width=3, bg='#f8f9fa').pack(side=tk.LEFT)  # Espaço para checkbox
        tk.Label(header_frame, text="Nome do Aluno", width=25, bg='#f8f9fa', font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        tk.Label(header_frame, text="Idade", width=6, bg='#f8f9fa', font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        tk.Label(header_frame, text="Mensalidade", width=12, bg='#f8f9fa', font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        tk.Label(header_frame, text="Responsável", width=20, bg='#f8f9fa', font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

        # Lista de alunos
        for i, aluno in enumerate(alunos):
            self.criar_item_aluno(aluno, i)

        # Atualizar contador
        self.atualizar_contador()

    def criar_item_aluno(self, aluno, index):
        """Cria item de aluno na lista"""
        # Cor de fundo alternada
        bg_color = '#f8f9fa' if index % 2 == 0 else 'white'
        
        item_frame = tk.Frame(self.students_frame, bg=bg_color, relief='solid', bd=1)
        item_frame.pack(fill=tk.X, padx=2, pady=1)
        
        # Checkbox para seleção
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(
            item_frame, variable=var, bg=bg_color,
            command=self.on_checkbox_changed
        )
        checkbox.pack(side=tk.LEFT, padx=5)
        
        # Armazenar referência
        self.alunos_selecionados[aluno['id']] = {
            'var': var,
            'data': aluno
        }
        
        # Informações do aluno
        tk.Label(item_frame, text=aluno['nome'][:30] + ('...' if len(aluno['nome']) > 30 else ''), 
                width=25, bg=bg_color, anchor='w').pack(side=tk.LEFT)
        tk.Label(item_frame, text=f"{aluno['idade']} anos", width=6, bg=bg_color).pack(side=tk.LEFT)
        tk.Label(item_frame, text=format_currency(aluno['valor_mensalidade']), width=12, bg=bg_color).pack(side=tk.LEFT)
        tk.Label(item_frame, text=aluno['responsavel_nome'][:18] + ('...' if len(aluno['responsavel_nome']) > 18 else ''), 
                width=20, bg=bg_color, anchor='w').pack(side=tk.LEFT)

    def limpar_lista_alunos(self):
        """Limpa a lista de alunos"""
        for widget in self.students_frame.winfo_children():
            widget.destroy()
        self.alunos_selecionados.clear()
        self.atualizar_contador()

    def selecionar_todos(self):
        """Seleciona todos os alunos"""
        for aluno_data in self.alunos_selecionados.values():
            aluno_data['var'].set(True)
        self.on_checkbox_changed()

    def limpar_selecao(self):
        """Limpa seleção de alunos"""
        for aluno_data in self.alunos_selecionados.values():
            aluno_data['var'].set(False)
        self.on_checkbox_changed()

    def on_checkbox_changed(self):
        """Callback quando checkbox é alterado"""
        self.atualizar_contador()
        self.atualizar_botao_transferir()

    def atualizar_contador(self):
        """Atualiza contador de alunos selecionados"""
        selecionados = sum(1 for data in self.alunos_selecionados.values() if data['var'].get())
        total = len(self.alunos_selecionados)
        self.contador_label.config(text=f"{selecionados} de {total} alunos selecionados")

    def atualizar_botao_transferir(self):
        """Atualiza estado do botão de transferir"""
        selecionados = any(data['var'].get() for data in self.alunos_selecionados.values())
        turma_destino = self.turma_destino_var.get()
        
        if selecionados and turma_destino:
            self.btn_transferir.config(state='normal')
        else:
            self.btn_transferir.config(state='disabled')

    def validar_transferencias(self):
        """Valida as transferências selecionadas"""
        alunos_selecionados = [
            aluno_id for aluno_id, data in self.alunos_selecionados.items() 
            if data['var'].get()
        ]
        
        if not alunos_selecionados:
            self.atualizar_status("⚠️ Selecione pelo menos um aluno para validar")
            return
        
        turma_destino_display = self.turma_destino_var.get()
        if not turma_destino_display:
            self.atualizar_status("⚠️ Selecione uma turma de destino")
            return
        
        try:
            turma_destino_data = self.turmas_data[turma_destino_display]
            
            problemas = []
            validos = 0
            
            for aluno_id in alunos_selecionados:
                validacao = self.transferencia_service.validar_transferencia(
                    aluno_id, turma_destino_data['id']
                )
                
                if validacao['valido']:
                    validos += 1
                else:
                    aluno_nome = self.alunos_selecionados[aluno_id]['data']['nome']
                    problemas.append(f"• {aluno_nome}: {validacao['erro']}")
            
            if problemas:
                msg = f"❌ {len(problemas)} problema(s) encontrado(s):\n\n" + "\n".join(problemas)
                if validos > 0:
                    msg += f"\n\n✅ {validos} aluno(s) podem ser transferidos normalmente"
                messagebox.showwarning("Problemas na Validação", msg)
            else:
                self.atualizar_status(f"✅ Todos os {validos} alunos podem ser transferidos com sucesso!")
                
        except Exception as e:
            self.atualizar_status(f"❌ Erro na validação: {str(e)}")

    def transferir_alunos_selecionados(self):
        """Executa a transferência dos alunos selecionados"""
        alunos_selecionados = [
            aluno_id for aluno_id, data in self.alunos_selecionados.items() 
            if data['var'].get()
        ]
        
        if not alunos_selecionados:
            messagebox.showwarning("Aviso", "Selecione pelo menos um aluno para transferir!")
            return
        
        turma_origem_display = self.turma_origem_var.get()
        turma_destino_display = self.turma_destino_var.get()
        
        if not turma_destino_display:
            messagebox.showwarning("Aviso", "Selecione uma turma de destino!")
            return
        
        # Confirmar transferência
        resposta = messagebox.askyesno(
            "Confirmar Transferência",
            f"Deseja transferir {len(alunos_selecionados)} aluno(s) da turma:\n"
            f"'{turma_origem_display}'\n\n"
            f"Para a turma:\n"
            f"'{turma_destino_display}'?\n\n"
            f"⚠️ Esta ação não pode ser desfeita!"
        )
        
        if not resposta:
            return
        
        try:
            # Obter dados das turmas
            turma_origem_data = self.turmas_data[turma_origem_display]
            turma_destino_data = self.turmas_data[turma_destino_display]
            
            # Obter motivo e observações
            motivo = self.motivo_var.get().strip()
            observacoes = self.obs_text.get("1.0", tk.END).strip()
            
            # Executar transferência em lote
            resultado = self.transferencia_service.transferir_alunos_lote(
                alunos_selecionados,
                turma_origem_data['id'],
                turma_destino_data['id'],
                motivo,
                observacoes
            )
            
            if resultado['success']:
                # Mostrar resultados
                msg = f"✅ Transferência realizada com sucesso!\n\n"
                msg += f"📊 Resultados:\n"
                msg += f"• ✅ {resultado['total_sucesso']} aluno(s) transferido(s)\n"
                
                if resultado['total_erro'] > 0:
                    msg += f"• ❌ {resultado['total_erro']} erro(s)\n\n"
                    msg += "Erros encontrados:\n"
                    for erro in resultado['transferencias_erro'][:5]:  # Mostrar até 5 erros
                        msg += f"• {erro}\n"
                
                messagebox.showinfo("Transferência Concluída", msg)
                
                # Recarregar dados
                self.carregar_alunos_turma()
                self.carregar_estatisticas()
                self.carregar_historico()
                
                # Limpar campos
                self.motivo_var.set("Promoção para próxima série")
                self.obs_text.delete("1.0", tk.END)
                
            else:
                messagebox.showerror("Erro", f"Falha na transferência: {resultado.get('error', 'Erro desconhecido')}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao executar transferência: {str(e)}")

    def carregar_estatisticas(self):
        """Carrega e atualiza estatísticas"""
        try:
            stats = self.transferencia_service.obter_estatisticas_transferencias()
            
            # Atualizar widgets de estatísticas
            stats_mapping = {
                "Total de Transferências": str(stats['total_transferencias']),
                "Transferências este Mês": str(stats['transferencias_mes']),
                "Transferências este Ano": str(stats['transferencias_ano']),
                "Turma que Mais Recebe": stats['turma_mais_recebe'][:25] + ('...' if len(stats['turma_mais_recebe']) > 25 else ''),
                "Turma que Mais Perde": stats['turma_mais_perde'][:25] + ('...' if len(stats['turma_mais_perde']) > 25 else '')
            }
            
            for label, valor in stats_mapping.items():
                if label in self.stats_widgets:
                    self.stats_widgets[label].config(text=valor)
                    
        except Exception as e:
            print(f"Erro ao carregar estatísticas: {e}")

    def carregar_historico(self):
        """Carrega histórico de transferências"""
        try:
            # Limpar tabela
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            
            # Carregar dados
            historico = self.transferencia_service.obter_historico_transferencias(20)
            
            for item in historico:
                self.history_tree.insert('', 'end', values=(
                    format_date(item['data_transferencia']),
                    item['aluno_nome'],
                    item['turma_origem'],
                    item['turma_destino'],
                    item['motivo'][:30] + ('...' if len(item['motivo']) > 30 else '')
                ))
                
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")

    def on_historico_double_click(self, event):
        """Callback para duplo clique no histórico"""
        item = self.history_tree.selection()[0] if self.history_tree.selection() else None
        if not item:
            return
        
        valores = self.history_tree.item(item, 'values')
        if valores:
            msg = f"📋 Detalhes da Transferência\n\n"
            msg += f"📅 Data: {valores[0]}\n"
            msg += f"👤 Aluno: {valores[1]}\n"
            msg += f"📤 Origem: {valores[2]}\n"
            msg += f"📥 Destino: {valores[3]}\n"
            msg += f"📝 Motivo: {valores[4]}"
            
            messagebox.showinfo("Detalhes da Transferência", msg)

    def atualizar_status(self, mensagem):
        """Atualiza mensagem de status"""
        self.status_label.config(text=mensagem)

    def atualizar_dados(self):
        """Atualiza todos os dados da interface"""
        try:
            self.carregar_dados_iniciais()
            self.atualizar_status("🔄 Dados atualizados com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar dados: {str(e)}")

    def gerar_relatorio(self):
        """Gera relatório de transferências"""
        try:
            # Diálogo para período (simplificado - últimos 30 dias)
            from datetime import timedelta
            data_fim = date.today()
            data_inicio = data_fim - timedelta(days=30)
            
            # Gerar relatório
            relatorio = self.transferencia_service.gerar_relatorio_transferencias(
                data_inicio.strftime('%Y-%m-%d'),
                data_fim.strftime('%Y-%m-%d')
            )
            
            if not relatorio:
                messagebox.showinfo("Relatório", "Nenhuma transferência encontrada no período!")
                return
            
            # Salvar como CSV
            filename = f"relatorio_transferencias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Data', 'Aluno', 'Turma Origem', 'Turma Destino', 'Motivo', 'Observações'])
                
                for item in relatorio:
                    writer.writerow([
                        format_date(item['data_transferencia']),
                        item['aluno_nome'],
                        item['turma_origem'],
                        item['turma_destino'],
                        item['motivo'],
                        item['observacoes']
                    ])
            
            messagebox.showinfo(
                "Relatório Gerado",
                f"📊 Relatório salvo como:\n{filename}\n\n"
                f"📋 Total de registros: {len(relatorio)}\n"
                f"📅 Período: {format_date(data_inicio)} a {format_date(data_fim)}"
            )
            
            # Abrir arquivo (Windows)
            try:
                os.startfile(filename)
            except:
                pass
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")