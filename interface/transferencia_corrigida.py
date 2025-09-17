import tkinter as tk
from tkinter import ttk, messagebox
from services.transferencia_service import TransferenciaService
from services.aluno_service import AlunoService
from utils.formatters import format_date
from datetime import datetime

class TransferenciaInterface:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.parent_frame.configure(bg='white')
        
        try:
            self.transferencia_service = TransferenciaService()
            self.aluno_service = AlunoService()
        except Exception as e:
            print(f"❌ Erro ao inicializar serviços: {e}")
            self.mostrar_erro(f"Erro ao inicializar serviços: {e}")
            return
        
        # Variáveis
        self.turmas_data = []
        self.alunos_turma_origem = []
        self.alunos_selecionados = []
        
        try:
            self.create_interface()
            self.carregar_turmas()
        except Exception as e:
            print(f"❌ Erro ao criar interface: {e}")
            self.mostrar_erro(f"Erro ao criar interface: {e}")

    def create_interface(self):
        """Cria interface de transferências"""
        
        # Container principal
        main_container = tk.Frame(self.parent_frame, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # === CABEÇALHO ===
        header_frame = tk.Frame(main_container, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            header_frame,
            text="🔄 Sistema de Transferências",
            font=('Arial', 24, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(side=tk.LEFT)
        
        # Botão de atualizar
        tk.Button(
            header_frame,
            text="🔄 Atualizar",
            command=self.carregar_turmas,
            font=('Arial', 10, 'bold'),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=5,
            relief='flat'
        ).pack(side=tk.RIGHT)
        
        # === ÁREA PRINCIPAL ===
        content_frame = tk.Frame(main_container, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Coluna esquerda - Seleção
        left_frame = tk.Frame(content_frame, bg='white')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.criar_secao_selecao(left_frame)
        
        # Coluna direita - Ações
        right_frame = tk.Frame(content_frame, bg='white')
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_frame.configure(width=350)
        right_frame.pack_propagate(False)
        
        self.criar_secao_acoes(right_frame)

    def criar_secao_selecao(self, parent):
        """Cria seção de seleção de turmas e alunos"""
        
        # === SELEÇÃO DE TURMAS ===
        turmas_frame = tk.LabelFrame(
            parent,
            text=" 🎯 Seleção de Turmas ",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        turmas_frame.pack(fill=tk.X, pady=(0, 10))
        
        turmas_content = tk.Frame(turmas_frame, bg='white')
        turmas_content.pack(fill=tk.X, padx=15, pady=15)
        
        # Turma de origem
        tk.Label(turmas_content, text="📤 Turma de Origem:", font=('Arial', 11, 'bold'), bg='white').pack(anchor='w', pady=(0, 5))
        
        self.turma_origem_var = tk.StringVar()
        self.turma_origem_combo = ttk.Combobox(
            turmas_content, textvariable=self.turma_origem_var,
            state="readonly", width=40
        )
        self.turma_origem_combo.pack(fill=tk.X, pady=(0, 10))
        self.turma_origem_combo.bind("<<ComboboxSelected>>", self.on_turma_origem_change)
        
        # Botão carregar alunos
        tk.Button(
            turmas_content,
            text="📋 Carregar Alunos da Turma",
            command=self.carregar_alunos_turma,
            font=('Arial', 10, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=15,
            pady=8,
            relief='flat'
        ).pack(pady=(0, 15))
        
        # Turma de destino
        tk.Label(turmas_content, text="📥 Turma de Destino:", font=('Arial', 11, 'bold'), bg='white').pack(anchor='w', pady=(0, 5))
        
        self.turma_destino_var = tk.StringVar()
        self.turma_destino_combo = ttk.Combobox(
            turmas_content, textvariable=self.turma_destino_var,
            state="readonly", width=40
        )
        self.turma_destino_combo.pack(fill=tk.X)
        
        # === SELEÇÃO DE ALUNOS ===
        alunos_frame = tk.LabelFrame(
            parent,
            text=" 👥 Seleção de Alunos ",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        alunos_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Controles de seleção
        controles_frame = tk.Frame(alunos_frame, bg='white')
        controles_frame.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        tk.Button(
            controles_frame,
            text="☑️ Selecionar Todos",
            command=self.selecionar_todos,
            font=('Arial', 9, 'bold'),
            bg='#007bff',
            fg='white',
            padx=10,
            relief='flat'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            controles_frame,
            text="☐ Limpar Seleção",
            command=self.limpar_selecao,
            font=('Arial', 9, 'bold'),
            bg='#6c757d',
            fg='white',
            padx=10,
            relief='flat'
        ).pack(side=tk.LEFT)
        
        # Contador de selecionados
        self.lbl_selecionados = tk.Label(
            controles_frame,
            text="Selecionados: 0",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        self.lbl_selecionados.pack(side=tk.RIGHT)
        
        # Lista de alunos com checkboxes
        lista_frame = tk.Frame(alunos_frame, bg='white')
        lista_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Frame com scroll
        canvas = tk.Canvas(lista_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(lista_frame, orient="vertical", command=canvas.yview)
        self.scrollable_alunos = tk.Frame(canvas, bg='white')
        
        self.scrollable_alunos.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_alunos, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Inicializar lista vazia
        self.checkboxes_alunos = []

    def criar_secao_acoes(self, parent):
        """Cria seção de ações de transferência"""
        
        # === INFORMAÇÕES ===
        info_frame = tk.LabelFrame(
            parent,
            text=" ℹ️ Informações ",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        info_frame.pack(fill=tk.X, padx=10, pady=(10, 15))
        
        info_content = tk.Frame(info_frame, bg='white')
        info_content.pack(fill=tk.X, padx=10, pady=10)
        
        self.lbl_info = tk.Label(
            info_content,
            text="Selecione uma turma de origem\npara começar",
            font=('Arial', 10),
            bg='white',
            fg='#6c757d',
            justify=tk.LEFT
        )
        self.lbl_info.pack(fill=tk.X)
        
        # === CONFIGURAÇÕES DE TRANSFERÊNCIA ===
        config_frame = tk.LabelFrame(
            parent,
            text=" ⚙️ Configurações ",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        config_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        config_content = tk.Frame(config_frame, bg='white')
        config_content.pack(fill=tk.X, padx=10, pady=10)
        
        # Motivo
        tk.Label(config_content, text="📝 Motivo:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(0, 5))
        
        self.motivo_var = tk.StringVar(value="Remanejamento de turma")
        motivo_combo = ttk.Combobox(
            config_content, textvariable=self.motivo_var,
            values=[
                "Remanejamento de turma",
                "Promoção para próxima série",
                "Mudança de turno",
                "Solicitação dos pais",
                "Adequação pedagógica",
                "Transferência administrativa",
                "Outros"
            ],
            width=25
        )
        motivo_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Observações
        tk.Label(config_content, text="💭 Observações:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(0, 5))
        
        self.entry_observacoes = tk.Text(config_content, height=3, wrap=tk.WORD, font=('Arial', 10))
        self.entry_observacoes.pack(fill=tk.X, pady=(0, 10))
        
        # === AÇÕES ===
        acoes_frame = tk.LabelFrame(
            parent,
            text=" 🚀 Executar Transferência ",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        acoes_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        acoes_content = tk.Frame(acoes_frame, bg='white')
        acoes_content.pack(fill=tk.X, padx=10, pady=15)
        
        # Botão validar
        self.btn_validar = tk.Button(
            acoes_content,
            text="🔍 Validar Transferência",
            command=self.validar_transferencia,
            font=('Arial', 10, 'bold'),
            bg='#17a2b8',
            fg='white',
            padx=15,
            pady=8,
            relief='flat',
            state='disabled'
        )
        self.btn_validar.pack(fill=tk.X, pady=(0, 10))
        
        # Botão transferir
        self.btn_transferir = tk.Button(
            acoes_content,
            text="🚀 Transferir Selecionados",
            command=self.executar_transferencia,
            font=('Arial', 11, 'bold'),
            bg='#28a745',
            fg='white',
            padx=15,
            pady=12,
            relief='flat',
            state='disabled'
        )
        self.btn_transferir.pack(fill=tk.X)
        
        # === HISTÓRICO RECENTE ===
        historico_frame = tk.LabelFrame(
            parent,
            text=" 📚 Histórico Recente ",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        historico_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(15, 10))
        
        # Lista de histórico
        self.lista_historico = tk.Listbox(
            historico_frame,
            font=('Arial', 9),
            height=8,
            selectmode=tk.SINGLE
        )
        self.lista_historico.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def carregar_turmas(self):
        """Carrega lista de turmas"""
        try:
            print("🔄 Carregando turmas para transferência...")
            
            # Usar o serviço correto
            self.turmas_data = self.aluno_service.listar_turmas()
            
            if not self.turmas_data:
                print("⚠️ Nenhuma turma encontrada")
                self.atualizar_info("Nenhuma turma cadastrada\nno sistema")
                return
            
            # Atualizar combos
            turma_values = [turma['display'] for turma in self.turmas_data]
            
            self.turma_origem_combo['values'] = turma_values
            self.turma_destino_combo['values'] = turma_values
            
            # Limpar seleções
            self.turma_origem_var.set('')
            self.turma_destino_var.set('')
            
            # Atualizar informações
            self.atualizar_info(f"{len(self.turmas_data)} turmas carregadas\nSelecione a turma de origem")
            
            # Carregar histórico
            self.carregar_historico()
            
            print(f"✅ {len(self.turmas_data)} turmas carregadas")
            
        except Exception as e:
            print(f"❌ Erro ao carregar turmas: {e}")
            self.atualizar_info(f"Erro ao carregar turmas:\n{str(e)}")

    def on_turma_origem_change(self, event=None):
        """Quando turma de origem muda"""
        try:
            turma_origem = self.turma_origem_var.get()
            if not turma_origem:
                return
            
            # Encontrar turma
            turma_origem_obj = None
            for turma in self.turmas_data:
                if turma['display'] == turma_origem:
                    turma_origem_obj = turma
                    break
            
            if turma_origem_obj:
                self.atualizar_info(f"Turma selecionada:\n{turma_origem}\n\nClique em 'Carregar Alunos'")
                
                # Habilitar botão de carregar
                self.habilitar_controles(False)
            
        except Exception as e:
            print(f"❌ Erro ao selecionar turma origem: {e}")

    def carregar_alunos_turma(self):
        """Carrega alunos da turma selecionada"""
        try:
            turma_origem = self.turma_origem_var.get()
            if not turma_origem:
                messagebox.showwarning("Atenção", "Selecione uma turma de origem")
                return
            
            # Encontrar ID da turma
            turma_id = None
            for turma in self.turmas_data:
                if turma['display'] == turma_origem:
                    turma_id = turma['id']
                    break
            
            if not turma_id:
                messagebox.showerror("Erro", "Turma não encontrada")
                return
            
            print(f"📋 Carregando alunos da turma ID: {turma_id}")
            
            # Carregar alunos
            self.alunos_turma_origem = self.aluno_service.buscar_alunos_por_turma(turma_id)
            
            if not self.alunos_turma_origem:
                messagebox.showinfo("Informação", "Nenhum aluno encontrado nesta turma")
                self.atualizar_info("Turma selecionada não possui\nalunos ativos")
                return
            
            # Atualizar interface
            self.criar_lista_alunos()
            self.atualizar_info(f"{len(self.alunos_turma_origem)} alunos carregados\nSelecione os alunos e\na turma de destino")
            
            # Habilitar controles
            self.habilitar_controles(True)
            
            print(f"✅ {len(self.alunos_turma_origem)} alunos carregados")
            
        except Exception as e:
            print(f"❌ Erro ao carregar alunos: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar alunos:\n{e}")

    def criar_lista_alunos(self):
        """Cria lista de alunos com checkboxes"""
        
        # Limpar lista anterior
        for widget in self.scrollable_alunos.winfo_children():
            widget.destroy()
        
        self.checkboxes_alunos = []
        
        # Criar checkbox para cada aluno
        for i, aluno in enumerate(self.alunos_turma_origem):
            
            # Frame para o aluno
            aluno_frame = tk.Frame(self.scrollable_alunos, bg='white', relief='solid', bd=1)
            aluno_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Variável do checkbox
            var_checkbox = tk.BooleanVar()
            
            # Checkbox
            checkbox = tk.Checkbutton(
                aluno_frame,
                variable=var_checkbox,
                bg='white',
                command=self.atualizar_contador_selecionados
            )
            checkbox.pack(side=tk.LEFT, padx=(10, 5), pady=8)
            
            # Informações do aluno
            info_frame = tk.Frame(aluno_frame, bg='white')
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10), pady=5)
            
            # Nome
            tk.Label(
                info_frame,
                text=aluno.get('nome', ''),
                font=('Arial', 11, 'bold'),
                bg='white',
                fg='#2c3e50'
            ).pack(anchor='w')
            
            # Detalhes
            detalhes = f"ID: {aluno.get('id', '')} | Idade: {aluno.get('idade', 0)} anos"
            if aluno.get('valor_mensalidade'):
                detalhes += f" | Mensalidade: R$ {aluno.get('valor_mensalidade', 0):.2f}"
            
            tk.Label(
                info_frame,
                text=detalhes,
                font=('Arial', 9),
                bg='white',
                fg='#6c757d'
            ).pack(anchor='w')
            
            # Salvar referências
            self.checkboxes_alunos.append({
                'aluno': aluno,
                'var': var_checkbox,
                'frame': aluno_frame
            })

    def selecionar_todos(self):
        """Seleciona todos os alunos"""
        for item in self.checkboxes_alunos:
            item['var'].set(True)
        
        self.atualizar_contador_selecionados()

    def limpar_selecao(self):
        """Limpa seleção de todos os alunos"""
        for item in self.checkboxes_alunos:
            item['var'].set(False)
        
        self.atualizar_contador_selecionados()

    def atualizar_contador_selecionados(self):
        """Atualiza contador de alunos selecionados"""
        try:
            selecionados = 0
            for item in self.checkboxes_alunos:
                if item['var'].get():
                    selecionados += 1
            
            self.lbl_selecionados.config(text=f"Selecionados: {selecionados}")
            
            # Atualizar estado dos botões
            has_selection = selecionados > 0
            has_destino = bool(self.turma_destino_var.get())
            
            self.btn_validar.config(state='normal' if has_selection and has_destino else 'disabled')
            self.btn_transferir.config(state='normal' if has_selection and has_destino else 'disabled')
            
        except Exception as e:
            print(f"❌ Erro ao atualizar contador: {e}")

    def validar_transferencia(self):
        """Valida transferência antes de executar - CORRIGIDO"""
        try:
            # Obter seleções
            alunos_selecionados = []
            for item in self.checkboxes_alunos:
                if item['var'].get():
                    alunos_selecionados.append(item['aluno'])
            
            if not alunos_selecionados:
                messagebox.showwarning("Atenção", "Selecione pelo menos um aluno")
                return
            
            turma_destino = self.turma_destino_var.get()
            if not turma_destino:
                messagebox.showwarning("Atenção", "Selecione a turma de destino")
                return
            
            # Encontrar IDs das turmas
            turma_origem_id = None
            turma_destino_id = None
            
            turma_origem = self.turma_origem_var.get()
            
            for turma in self.turmas_data:
                if turma['display'] == turma_origem:
                    turma_origem_id = turma['id']
                if turma['display'] == turma_destino:
                    turma_destino_id = turma['id']
            
            # Validar cada aluno
            problemas_gerais = []
            
            if turma_destino == turma_origem:
                problemas_gerais.append("• Turma de destino deve ser diferente da origem")
            
            problemas_alunos = []
            for aluno in alunos_selecionados:
                validacao = self.transferencia_service.validar_transferencia(
                    aluno['id'], turma_origem_id, turma_destino_id
                )
                
                if not validacao['success']:
                    for problema in validacao['problemas']:
                        problemas_alunos.append(f"• {aluno['nome']}: {problema}")
            
            # Mostrar resultado
            todos_problemas = problemas_gerais + problemas_alunos
            
            if todos_problemas:
                messagebox.showerror("❌ Problemas Encontrados", "\n".join(todos_problemas))
            else:
                messagebox.showinfo("✅ Validação OK", 
                    f"Transferência validada com sucesso!\n\n"
                    f"• {len(alunos_selecionados)} aluno(s) selecionado(s)\n"
                    f"• Turma destino: {turma_destino}\n"
                    f"• Motivo: {self.motivo_var.get()}\n\n"
                    f"Clique em 'Transferir' para executar.")
            
        except Exception as e:
            print(f"❌ Erro na validação: {e}")
            messagebox.showerror("Erro", f"Erro na validação:\n{e}")

    def executar_transferencia(self):
        """Executa transferência dos alunos selecionados - VERSÃO FINAL CORRIGIDA"""
        try:
            print("🚀 Iniciando processo de transferência...")
            
            # Obter seleções
            alunos_selecionados = []
            for item in self.checkboxes_alunos:
                if item['var'].get():
                    alunos_selecionados.append(item['aluno'])
            
            if not alunos_selecionados:
                messagebox.showwarning("Atenção", "Selecione pelo menos um aluno")
                return
            
            turma_destino = self.turma_destino_var.get()
            if not turma_destino:
                messagebox.showwarning("Atenção", "Selecione a turma de destino")
                return
            
            # Encontrar IDs das turmas
            turma_origem_id = None
            turma_destino_id = None
            
            turma_origem = self.turma_origem_var.get()
            
            for turma in self.turmas_data:
                if turma['display'] == turma_origem:
                    turma_origem_id = turma['id']
                if turma['display'] == turma_destino:
                    turma_destino_id = turma['id']
            
            if not turma_origem_id or not turma_destino_id:
                messagebox.showerror("Erro", "Erro ao identificar turmas")
                return
            
            print(f"📊 Transferindo {len(alunos_selecionados)} aluno(s)")
            print(f"📤 Turma origem ID: {turma_origem_id}")
            print(f"📥 Turma destino ID: {turma_destino_id}")
            
            # Confirmar operação
            confirmacao = f"""
    🔄 CONFIRMAR TRANSFERÊNCIA

    📤 De: {turma_origem}
    📥 Para: {turma_destino}

    👥 Alunos selecionados: {len(alunos_selecionados)}
    {chr(10).join([f"   • {aluno['nome']}" for aluno in alunos_selecionados[:5]])}
    {"   • ..." if len(alunos_selecionados) > 5 else ""}

    📝 Motivo: {self.motivo_var.get()}

    ⚠️ Esta operação não pode ser desfeita!

    Deseja continuar?
            """
            
            if not messagebox.askyesno("Confirmar Transferência", confirmacao.strip()):
                return
            
            # Executar transferências
            sucessos = 0
            erros = []
            
            motivo = self.motivo_var.get() or "Transferência"
            observacoes = self.entry_observacoes.get("1.0", tk.END).strip()
            
            print(f"📝 Motivo: {motivo}")
            print(f"💭 Observações: {observacoes}")
            
            for i, aluno in enumerate(alunos_selecionados):
                try:
                    print(f"🔄 Transferindo {i+1}/{len(alunos_selecionados)}: {aluno['nome']} (ID: {aluno['id']})")
                    
                    # Usar o serviço corrigido
                    resultado = self.transferencia_service.transferir_aluno(
                        aluno['id'], 
                        turma_origem_id, 
                        turma_destino_id,
                        motivo,
                        observacoes
                    )
                    
                    if resultado['success']:
                        sucessos += 1
                        print(f"✅ {aluno.get('nome', '')} transferido com sucesso")
                    else:
                        erros.append(f"• {aluno.get('nome', '')}: {resultado.get('error', 'Erro desconhecido')}")
                        print(f"❌ Erro ao transferir {aluno.get('nome', '')}: {resultado.get('error', '')}")
                    
                    # Pequena pausa para não sobrecarregar o banco
                    import time
                    time.sleep(0.1)
                        
                except Exception as e:
                    erros.append(f"• {aluno.get('nome', '')}: {str(e)}")
                    print(f"❌ Exceção ao transferir {aluno.get('nome', '')}: {e}")
            
            # Mostrar resultado final
            print(f"📊 Resultado: {sucessos} sucessos, {len(erros)} erros")
            
            if sucessos > 0:
                mensagem_final = f"✅ {sucessos} aluno(s) transferido(s) com sucesso!"
                if erros:
                    mensagem_final += f"\n\n❌ Erros encontrados:\n" + "\n".join(erros)
                
                messagebox.showinfo("Transferência Concluída", mensagem_final)
                
                # Recarregar dados
                print("🔄 Recarregando interface...")
                self.carregar_turmas()
                self.limpar_selecao()
                
                # Limpar turma origem para forçar nova seleção
                self.turma_origem_var.set('')
                self.alunos_turma_origem = []
                
                # Limpar lista de alunos
                for widget in self.scrollable_alunos.winfo_children():
                    widget.destroy()
                self.checkboxes_alunos = []
                
                self.habilitar_controles(False)
                self.atualizar_info("Transferência concluída!\nSelecione nova turma de origem")
                
                print("✅ Interface atualizada!")
                
            else:
                messagebox.showerror("Erro na Transferência", 
                    "❌ Nenhuma transferência foi concluída.\n\nErros encontrados:\n\n" + "\n".join(erros))
                print("❌ Nenhuma transferência concluída")
                
        except Exception as e:
            print(f"❌ Erro crítico na transferência: {e}")
            messagebox.showerror("Erro Crítico", f"Erro crítico durante a transferência:\n\n{str(e)}\n\nConsulte o console para mais detalhes.")


    def transferir_aluno_simples(self, aluno_id, turma_origem_id, turma_destino_id, motivo, observacoes):
        """Executa transferência simples de aluno"""
        try:
            from database.connection import db
            
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Atualizar turma do aluno
            cursor.execute("""
                UPDATE alunos 
                SET turma_id = ?
                WHERE id = ?
            """, (turma_destino_id, aluno_id))
            
            # Registrar no histórico
            cursor.execute("""
                INSERT INTO historico_transferencias 
                (aluno_id, turma_origem_id, turma_destino_id, motivo, observacoes, tipo_transferencia)
                VALUES (?, ?, ?, ?, ?, 'TRANSFERENCIA')
            """, (aluno_id, turma_origem_id, turma_destino_id, motivo, observacoes))
            
            conn.commit()
            conn.close()
            
            return {'success': True}
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return {'success': False, 'error': str(e)}

    def carregar_historico(self):
        """Carrega histórico recente de transferências - CORRIGIDO"""
        try:
            # Usar o serviço corrigido
            historico = self.transferencia_service.obter_historico_transferencias(10)
            
            # Limpar lista
            self.lista_historico.delete(0, tk.END)
            
            # Inserir histórico
            for item in historico:
                try:
                    from utils.formatters import format_date
                    data = format_date(item['data_transferencia']) if item['data_transferencia'] else "N/A"
                    texto = f"{data} - {item['aluno_nome']} ({item['turma_origem']} → {item['turma_destino']})"
                    self.lista_historico.insert(tk.END, texto)
                except Exception as e:
                    print(f"⚠️ Erro ao formatar item do histórico: {e}")
                    texto = f"{item['aluno_nome']} - Transferência registrada"
                    self.lista_historico.insert(tk.END, texto)
            
        except Exception as e:
            print(f"❌ Erro ao carregar histórico: {e}")
            # Inserir mensagem de erro na lista
            self.lista_historico.delete(0, tk.END)
            self.lista_historico.insert(tk.END, "Erro ao carregar histórico")

    def habilitar_controles(self, habilitar):
        """Habilita/desabilita controles de transferência"""
        estado = 'normal' if habilitar else 'disabled'
        
        # Atualizar contador
        self.atualizar_contador_selecionados()

    def atualizar_info(self, texto):
        """Atualiza informações na interface"""
        self.lbl_info.config(text=texto)

    def mostrar_erro(self, mensagem):
        """Mostra tela de erro"""
        error_frame = tk.Frame(self.parent_frame, bg='white')
        error_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            error_frame,
            text="⚠️ Erro no Módulo de Transferências",
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
