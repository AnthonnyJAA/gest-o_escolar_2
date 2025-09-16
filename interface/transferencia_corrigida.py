import tkinter as tk
from tkinter import ttk, messagebox
from services.transferencia_service import TransferenciaAvancadaService
from services.aluno_service import AlunoService  
from services.turma_service import TurmaService
from utils.formatters import format_date, format_currency
from datetime import datetime

class TransferenciaAvancadaInterface:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.transferencia_service = TransferenciaAvancadaService()
        self.aluno_service = AlunoService()
        self.turma_service = TurmaService()
        
        # Variáveis de controle
        self.turma_origem_var = tk.StringVar()
        self.turma_destino_var = tk.StringVar()
        self.motivo_var = tk.StringVar()
        self.tipo_operacao_var = tk.StringVar(value="TRANSFERENCIA")
        self.alunos_selecionados = []
        
        # Dados carregados
        self.turmas_data = {}
        self.alunos_origem_data = []
        
        self.create_interface()
        self.carregar_dados_iniciais()

    def create_interface(self):
        """Cria a interface principal avançada"""
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

        # Seletor de tipo de operação
        self.create_operation_selector(main_container)

        # Painel principal de transferência
        self.create_transfer_panel(main_container)

        # Histórico avançado
        self.create_history_panel(main_container)

    def create_header(self, parent):
        """Cria o cabeçalho"""
        header_frame = tk.Frame(parent, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # Título
        title_frame = tk.Frame(header_frame, bg='white')
        title_frame.pack(fill=tk.X)

        tk.Label(
            title_frame,
            text="🔄 Sistema de Transferências Avançadas",
            font=('Arial', 20, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(side=tk.LEFT)

        tk.Label(
            title_frame,
            text="Versão Corrigida - Carregamento de Dados OK",
            font=('Arial', 10),
            bg='white',
            fg='#28a745'
        ).pack(side=tk.RIGHT)

        # Botões
        buttons_frame = tk.Frame(header_frame, bg='white')
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Button(
            buttons_frame,
            text="🔄 Recarregar Dados",
            command=self.carregar_dados_iniciais,
            font=('Arial', 10, 'bold'),
            bg='#28a745',
            fg='white',
            padx=15,
            pady=5,
            relief='flat'
        ).pack(side=tk.RIGHT)

    def create_operation_selector(self, parent):
        """Cria seletor de tipo de operação"""
        selector_frame = tk.LabelFrame(
            parent,
            text=" Tipo de Operação ",
            font=('Arial', 12, 'bold'),
            bg='white'
        )
        selector_frame.pack(fill=tk.X, pady=(0, 20))

        operations_frame = tk.Frame(selector_frame, bg='white')
        operations_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Radiobutton(
            operations_frame,
            text="🔄 Transferência de Turma",
            variable=self.tipo_operacao_var,
            value="TRANSFERENCIA",
            font=('Arial', 11),
            bg='white',
            command=self.on_operacao_changed
        ).pack(side=tk.LEFT, padx=(0, 20))

        tk.Radiobutton(
            operations_frame,
            text="❌ Desligamento",
            variable=self.tipo_operacao_var,
            value="DESLIGAMENTO", 
            font=('Arial', 11),
            bg='white',
            command=self.on_operacao_changed
        ).pack(side=tk.LEFT)

    def create_transfer_panel(self, parent):
        """Cria painel principal de transferência"""
        transfer_frame = tk.LabelFrame(
            parent,
            text=" Painel de Transferências ",
            font=('Arial', 12, 'bold'),
            bg='white'
        )
        transfer_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Container principal
        main_container = tk.Frame(transfer_frame, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Turma de origem
        origem_frame = tk.Frame(main_container, bg='white')
        origem_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(origem_frame, text="🏫 Turma de Origem:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w')
        
        self.turma_origem_combo = ttk.Combobox(
            origem_frame,
            textvariable=self.turma_origem_var,
            state='readonly',
            font=('Arial', 10),
            width=70
        )
        self.turma_origem_combo.pack(fill=tk.X, pady=(5, 0))
        self.turma_origem_combo.bind('<<ComboboxSelected>>', self.on_turma_origem_selected)

        # Status de carregamento
        self.status_origem_label = tk.Label(
            origem_frame,
            text="🔄 Carregando turmas...",
            font=('Arial', 9),
            bg='white',
            fg='#6c757d'
        )
        self.status_origem_label.pack(anchor='w', pady=(2, 0))

        # Lista de alunos
        alunos_frame = tk.Frame(main_container, bg='white')
        alunos_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        alunos_header = tk.Frame(alunos_frame, bg='white')
        alunos_header.pack(fill=tk.X)

        tk.Label(alunos_header, text="👥 Alunos Disponíveis:", font=('Arial', 10, 'bold'), bg='white').pack(side=tk.LEFT, anchor='w')

        # Contador de alunos
        self.contador_alunos_label = tk.Label(
            alunos_header,
            text="Selecione uma turma primeiro",
            font=('Arial', 9),
            bg='white',
            fg='#6c757d'
        )
        self.contador_alunos_label.pack(side=tk.RIGHT)

        # TreeView para alunos com checkboxes
        tree_frame = tk.Frame(alunos_frame, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.alunos_tree = ttk.Treeview(
            tree_frame,
            columns=('nome', 'idade', 'mensalidade', 'status'),
            show='tree headings',  # Mostrar tree + headings para checkbox
            height=10
        )

        # Configurar colunas
        self.alunos_tree.heading('#0', text='✓', width=30)
        self.alunos_tree.heading('nome', text='Nome')
        self.alunos_tree.heading('idade', text='Idade')  
        self.alunos_tree.heading('mensalidade', text='Mensalidade')
        self.alunos_tree.heading('status', text='Status')

        self.alunos_tree.column('#0', width=30, minwidth=30)
        self.alunos_tree.column('nome', width=250)
        self.alunos_tree.column('idade', width=80)
        self.alunos_tree.column('mensalidade', width=100)
        self.alunos_tree.column('status', width=80)

        scrollbar_alunos = ttk.Scrollbar(tree_frame, orient="vertical", command=self.alunos_tree.yview)
        self.alunos_tree.configure(yscrollcommand=scrollbar_alunos.set)

        self.alunos_tree.pack(side="left", fill="both", expand=True)
        scrollbar_alunos.pack(side="right", fill="y")

        # Bind para seleção
        self.alunos_tree.bind("<Button-1>", self.on_aluno_click)
        self.alunos_tree.bind("<space>", self.toggle_aluno_selection)

        # Painel de destino (só para transferência)
        self.destino_frame = tk.Frame(main_container, bg='white')
        self.destino_frame.pack(fill=tk.X, pady=(15, 10))

        tk.Label(self.destino_frame, text="🎯 Turma de Destino:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w')
        
        self.turma_destino_combo = ttk.Combobox(
            self.destino_frame,
            textvariable=self.turma_destino_var,
            state='readonly',
            font=('Arial', 10),
            width=70
        )
        self.turma_destino_combo.pack(fill=tk.X, pady=(5, 0))

        self.status_destino_label = tk.Label(
            self.destino_frame,
            text="Aguardando seleção da turma de origem",
            font=('Arial', 9),
            bg='white',
            fg='#6c757d'
        )
        self.status_destino_label.pack(anchor='w', pady=(2, 0))

        # Motivo
        motivo_frame = tk.Frame(main_container, bg='white')
        motivo_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Label(motivo_frame, text="📝 Motivo:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w')
        
        motivos = [
            "Transferência de turma",
            "Mudança de turno", 
            "Solicitação dos pais",
            "Adequação pedagógica",
            "Mudança de nível",
            "Reorganização de classes",
            "Outros"
        ]
        
        self.motivo_combo = ttk.Combobox(
            motivo_frame,
            textvariable=self.motivo_var,
            values=motivos,
            font=('Arial', 10),
            width=70
        )
        self.motivo_combo.pack(fill=tk.X, pady=(5, 0))
        self.motivo_combo.set(motivos[0])

        # Painel de resumo
        resumo_frame = tk.LabelFrame(main_container, text="📋 Resumo da Operação", bg='white')
        resumo_frame.pack(fill=tk.X, pady=(15, 0))

        self.resumo_label = tk.Label(
            resumo_frame,
            text="Selecione os alunos e configure a transferência",
            font=('Arial', 10),
            bg='white',
            fg='#6c757d',
            justify='left'
        )
        self.resumo_label.pack(padx=15, pady=10, anchor='w')

        # Botões
        buttons_frame = tk.Frame(main_container, bg='white')
        buttons_frame.pack(fill=tk.X, pady=(15, 0))

        # Botão de seleção rápida
        tk.Button(
            buttons_frame,
            text="☑️ Selecionar Todos",
            command=self.selecionar_todos_alunos,
            font=('Arial', 10),
            bg='#17a2b8',
            fg='white',
            padx=15,
            pady=8,
            relief='flat'
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            buttons_frame,
            text="☐ Limpar Seleção",
            command=self.limpar_selecao_alunos,
            font=('Arial', 10),
            bg='#6c757d',
            fg='white',
            padx=15,
            pady=8,
            relief='flat'
        ).pack(side=tk.LEFT)

        # Botão principal
        self.execute_button = tk.Button(
            buttons_frame,
            text="🚀 EXECUTAR TRANSFERÊNCIA",
            command=self.executar_operacao,
            font=('Arial', 12, 'bold'),
            bg='#007bff',
            fg='white',
            padx=25,
            pady=12,
            relief='flat',
            cursor='hand2',
            state='disabled'
        )
        self.execute_button.pack(side=tk.RIGHT)

    def create_history_panel(self, parent):
        """Cria painel de histórico"""
        history_frame = tk.LabelFrame(
            parent,
            text=" 📚 Histórico de Transferências ",
            font=('Arial', 12, 'bold'),
            bg='white'
        )
        history_frame.pack(fill=tk.BOTH, expand=True)

        # TreeView para histórico
        self.history_tree = ttk.Treeview(
            history_frame,
            columns=('data', 'tipo', 'aluno', 'origem', 'destino', 'motivo'),
            show='headings',
            height=6
        )

        self.history_tree.heading('data', text='Data')
        self.history_tree.heading('tipo', text='Tipo')
        self.history_tree.heading('aluno', text='Aluno')
        self.history_tree.heading('origem', text='Origem')
        self.history_tree.heading('destino', text='Destino')
        self.history_tree.heading('motivo', text='Motivo')

        self.history_tree.column('data', width=80)
        self.history_tree.column('tipo', width=100)
        self.history_tree.column('aluno', width=150)
        self.history_tree.column('origem', width=120)
        self.history_tree.column('destino', width=120)
        self.history_tree.column('motivo', width=200)

        scrollbar_history = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar_history.set)

        self.history_tree.pack(side="left", fill="both", expand=True, padx=20, pady=15)
        scrollbar_history.pack(side="right", fill="y", pady=15)

    def carregar_dados_iniciais(self):
        """Carrega dados iniciais - CORRIGIDO"""
        try:
            print("🔄 Carregando dados das transferências...")
            
            # Atualizar status
            self.status_origem_label.config(text="🔄 Carregando turmas...", fg='#007bff')
            self.parent_frame.update_idletasks()

            # Carregar turmas usando TurmaService diretamente
            turmas = self.turma_service.listar_turmas()
            print(f"✅ {len(turmas)} turmas encontradas")

            if not turmas:
                self.status_origem_label.config(text="⚠️ Nenhuma turma encontrada", fg='#dc3545')
                messagebox.showwarning("Aviso", "Nenhuma turma encontrada!\n\nCadastre turmas primeiro na aba 'Turmas'.")
                return

            # Formatar turmas para exibição
            self.turmas_data = {}
            turmas_display = []

            for turma in turmas:
                # Contar alunos ativos na turma
                try:
                    alunos_turma = self.aluno_service.listar_alunos_por_turma(turma['id'])
                    total_alunos = len([a for a in alunos_turma if a.get('status') == 'Ativo'])
                except:
                    total_alunos = 0

                display_name = f"{turma['nome']} - {turma['serie']} ({turma['ano_letivo']}) - {total_alunos} aluno(s)"
                
                turmas_display.append(display_name)
                self.turmas_data[display_name] = {
                    'id': turma['id'],
                    'nome': turma['nome'],
                    'serie': turma['serie'],
                    'ano_letivo': turma['ano_letivo'],
                    'total_alunos': total_alunos,
                    'valor_mensalidade_padrao': turma.get('valor_mensalidade_padrao', 0)
                }

            # Atualizar combos
            self.turma_origem_combo['values'] = turmas_display
            self.turma_destino_combo['values'] = turmas_display
            
            # Limpar seleções
            self.turma_origem_var.set('')
            self.turma_destino_var.set('')

            # Atualizar status
            self.status_origem_label.config(text=f"✅ {len(turmas)} turmas carregadas", fg='#28a745')
            
            # Carregar histórico
            self.carregar_historico()
            
            print("✅ Dados carregados com sucesso!")

        except Exception as e:
            error_msg = f"Erro ao carregar dados: {str(e)}"
            print(f"❌ {error_msg}")
            self.status_origem_label.config(text="❌ Erro ao carregar turmas", fg='#dc3545')
            messagebox.showerror("Erro", error_msg)

    def on_operacao_changed(self):
        """Callback quando tipo de operação muda"""
        if self.tipo_operacao_var.get() == "DESLIGAMENTO":
            self.destino_frame.pack_forget()
            self.execute_button.config(text="❌ EXECUTAR DESLIGAMENTO")
        else:
            self.destino_frame.pack(fill=tk.X, pady=(15, 10))
            self.execute_button.config(text="🚀 EXECUTAR TRANSFERÊNCIA")

    def on_turma_origem_selected(self, event=None):
        """Callback quando turma origem é selecionada - CORRIGIDO"""
        try:
            turma_display = self.turma_origem_var.get()
            if not turma_display or turma_display not in self.turmas_data:
                return

            print(f"🔄 Carregando alunos da turma: {turma_display}")
            
            # Atualizar contador
            self.contador_alunos_label.config(text="🔄 Carregando alunos...", fg='#007bff')
            
            # Obter dados da turma
            turma_data = self.turmas_data[turma_display]
            
            # Carregar alunos da turma
            alunos = self.aluno_service.listar_alunos_por_turma(turma_data['id'])
            alunos_ativos = [a for a in alunos if a.get('status') == 'Ativo']
            
            # Limpar lista atual
            for item in self.alunos_tree.get_children():
                self.alunos_tree.delete(item)
            
            self.alunos_origem_data = []
            self.alunos_selecionados = []

            if not alunos_ativos:
                self.contador_alunos_label.config(text="⚠️ Nenhum aluno ativo nesta turma", fg='#dc3545')
                self.atualizar_resumo()
                return

            # Preencher lista de alunos
            for aluno in alunos_ativos:
                # Calcular idade aproximada
                idade = "N/A"
                if aluno.get('data_nascimento'):
                    try:
                        from datetime import datetime
                        nascimento = datetime.strptime(aluno['data_nascimento'], '%Y-%m-%d')
                        idade_anos = datetime.now().year - nascimento.year
                        idade = f"{idade_anos} anos"
                    except:
                        pass

                # Inserir na TreeView
                item_id = self.alunos_tree.insert('', 'end', 
                    text='☐',  # Checkbox vazio
                    values=(
                        aluno['nome'],
                        idade,
                        format_currency(aluno.get('valor_mensalidade', 0)),
                        aluno.get('status', 'Ativo')
                    ),
                    tags=(str(aluno['id']),)
                )
                
                self.alunos_origem_data.append({
                    'item_id': item_id,
                    'aluno_data': aluno
                })

            # Atualizar contador
            self.contador_alunos_label.config(
                text=f"✅ {len(alunos_ativos)} aluno(s) disponível(is)", 
                fg='#28a745'
            )

            # Atualizar turmas de destino (excluir a origem)
            if self.tipo_operacao_var.get() == "TRANSFERENCIA":
                self.atualizar_turmas_destino(turma_display)
            
            self.atualizar_resumo()
            print(f"✅ {len(alunos_ativos)} alunos carregados")

        except Exception as e:
            error_msg = f"Erro ao carregar alunos: {str(e)}"
            print(f"❌ {error_msg}")
            self.contador_alunos_label.config(text="❌ Erro ao carregar alunos", fg='#dc3545')
            messagebox.showerror("Erro", error_msg)

    def atualizar_turmas_destino(self, turma_origem_excluir):
        """Atualiza lista de turmas de destino excluindo a origem"""
        try:
            turmas_destino = [t for t in self.turma_origem_combo['values'] if t != turma_origem_excluir]
            self.turma_destino_combo['values'] = turmas_destino
            self.turma_destino_var.set('')
            
            self.status_destino_label.config(
                text=f"✅ {len(turmas_destino)} turmas de destino disponíveis", 
                fg='#28a745'
            )
            
        except Exception as e:
            print(f"❌ Erro ao atualizar turmas destino: {e}")

    def on_aluno_click(self, event):
        """Callback para clique em aluno"""
        item = self.alunos_tree.identify('item', event.x, event.y)
        if item:
            self.toggle_aluno_selection(item=item)

    def toggle_aluno_selection(self, event=None, item=None):
        """Alterna seleção de aluno"""
        if not item and event:
            item = self.alunos_tree.selection()[0] if self.alunos_tree.selection() else None
        
        if not item:
            return

        # Alternar checkbox
        current_text = self.alunos_tree.item(item, 'text')
        if current_text == '☐':
            self.alunos_tree.item(item, text='☑️')
            if item not in self.alunos_selecionados:
                self.alunos_selecionados.append(item)
        else:
            self.alunos_tree.item(item, text='☐')
            if item in self.alunos_selecionados:
                self.alunos_selecionados.remove(item)
        
        self.atualizar_resumo()

    def selecionar_todos_alunos(self):
        """Seleciona todos os alunos"""
        for item in self.alunos_tree.get_children():
            self.alunos_tree.item(item, text='☑️')
            if item not in self.alunos_selecionados:
                self.alunos_selecionados.append(item)
        self.atualizar_resumo()

    def limpar_selecao_alunos(self):
        """Limpa seleção de alunos"""
        for item in self.alunos_tree.get_children():
            self.alunos_tree.item(item, text='☐')
        self.alunos_selecionados = []
        self.atualizar_resumo()

    def atualizar_resumo(self):
        """Atualiza resumo da operação"""
        try:
            if not self.alunos_selecionados:
                resumo = "Selecione pelo menos um aluno para continuar"
                self.execute_button.config(state='disabled', bg='#6c757d')
            else:
                operacao = "transferir" if self.tipo_operacao_var.get() == "TRANSFERENCIA" else "desligar"
                plural = "alunos" if len(self.alunos_selecionados) > 1 else "aluno"
                
                resumo = f"📋 Pronto para {operacao} {len(self.alunos_selecionados)} {plural}:\n"
                
                # Listar alunos selecionados (máximo 3)
                count = 0
                for item_id in self.alunos_selecionados[:3]:
                    values = self.alunos_tree.item(item_id, 'values')
                    if values:
                        resumo += f"   • {values[0]}\n"
                        count += 1
                
                if len(self.alunos_selecionados) > 3:
                    resumo += f"   • ... e mais {len(self.alunos_selecionados) - 3}\n"
                
                # Verificar se pode executar
                can_execute = True
                if self.tipo_operacao_var.get() == "TRANSFERENCIA":
                    if not self.turma_destino_var.get():
                        resumo += "\n⚠️ Selecione uma turma de destino"
                        can_execute = False
                    else:
                        resumo += f"\n🎯 Destino: {self.turma_destino_var.get()}"
                
                if can_execute:
                    self.execute_button.config(state='normal', bg='#007bff')
                else:
                    self.execute_button.config(state='disabled', bg='#6c757d')

            self.resumo_label.config(text=resumo)

        except Exception as e:
            print(f"❌ Erro ao atualizar resumo: {e}")

    def carregar_historico(self):
        """Carrega histórico de transferências"""
        try:
            # Limpar histórico atual
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            
            # Obter histórico
            historico = self.transferencia_service.obter_historico_avancado(limite=15)
            
            for item in historico:
                self.history_tree.insert('', 'end', values=(
                    format_date(item['data_transferencia']),
                    item['tipo_transferencia'],
                    item['aluno_nome'],
                    item['turma_origem'] or 'N/A',
                    item['turma_destino'] or 'N/A',
                    (item['motivo'] or '')[:40] + ('...' if len(item.get('motivo', '')) > 40 else '')
                ))
                
        except Exception as e:
            print(f"❌ Erro ao carregar histórico: {e}")

    def executar_operacao(self):
        """Executa a operação selecionada"""
        if not self.alunos_selecionados:
            messagebox.showwarning("Aviso", "Selecione pelo menos um aluno!")
            return

        if self.tipo_operacao_var.get() == "TRANSFERENCIA":
            self.executar_transferencia()
        else:
            self.executar_desligamento()

    def executar_transferencia(self):
        """Executa transferência de alunos"""
        if not self.turma_destino_var.get():
            messagebox.showwarning("Aviso", "Selecione uma turma de destino!")
            return

        try:
            turma_origem_display = self.turma_origem_var.get()
            turma_destino_display = self.turma_destino_var.get()
            
            turma_origem = self.turmas_data[turma_origem_display]
            turma_destino = self.turmas_data[turma_destino_display]
            
            # Obter dados dos alunos selecionados
            alunos_para_transferir = []
            for item_id in self.alunos_selecionados:
                tags = self.alunos_tree.item(item_id, 'tags')
                if tags:
                    aluno_id = int(tags[0])
                    values = self.alunos_tree.item(item_id, 'values')
                    alunos_para_transferir.append({
                        'id': aluno_id,
                        'nome': values[0] if values else 'N/A'
                    })

            # Confirmação
            nomes_alunos = [a['nome'] for a in alunos_para_transferir]
            confirm_msg = f"""Confirmar transferência?

👥 Alunos ({len(nomes_alunos)}):
{chr(10).join(f'   • {nome}' for nome in nomes_alunos[:5])}
{f'   • ... e mais {len(nomes_alunos) - 5}' if len(nomes_alunos) > 5 else ''}

🏫 De: {turma_origem['nome']} - {turma_origem['serie']}
🎯 Para: {turma_destino['nome']} - {turma_destino['serie']}
📝 Motivo: {self.motivo_var.get()}"""

            if not messagebox.askyesno("Confirmar Transferência", confirm_msg):
                return

            # Executar transferências
            sucessos = 0
            erros = 0
            
            for aluno in alunos_para_transferir:
                try:
                    # Determinar tipo de transferência
                    if turma_origem['ano_letivo'] == turma_destino['ano_letivo']:
                        # Mesmo ano letivo
                        resultado = self.transferencia_service.transferir_aluno_mesmo_ano(
                            aluno['id'], turma_origem['id'], turma_destino['id'],
                            False, None, self.motivo_var.get(), ""
                        )
                    else:
                        # Diferente ano letivo - implementar
                        messagebox.showinfo("Info", "Transferência entre anos letivos será implementada")
                        continue
                    
                    if resultado['success']:
                        sucessos += 1
                    else:
                        erros += 1
                        print(f"❌ Erro ao transferir {aluno['nome']}: {resultado.get('error', 'Erro desconhecido')}")
                        
                except Exception as e:
                    erros += 1
                    print(f"❌ Erro ao transferir {aluno['nome']}: {str(e)}")

            # Resultado
            if sucessos > 0:
                messagebox.showinfo(
                    "Transferências Concluídas",
                    f"✅ {sucessos} aluno(s) transferido(s) com sucesso!"
                    f"{f' | ❌ {erros} erro(s)' if erros > 0 else ''}"
                )
                
                # Recarregar dados
                self.carregar_dados_iniciais()
                self.limpar_selecao_alunos()
            else:
                messagebox.showerror("Erro", f"Nenhum aluno foi transferido.\n{erros} erro(s) encontrado(s)")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao executar transferência: {str(e)}")

    def executar_desligamento(self):
        """Executa desligamento de alunos"""
        messagebox.showinfo("Em Desenvolvimento", "Funcionalidade de desligamento será implementada em breve")