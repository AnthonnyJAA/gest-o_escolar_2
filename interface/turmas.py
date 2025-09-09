import tkinter as tk
from tkinter import ttk, messagebox
from services.turma_service import TurmaService
from utils.formatters import format_currency, validate_number

class TurmasInterface:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.turma_service = TurmaService()
        self.turma_editando = None
        self.create_interface()
        self.carregar_turmas()
    
    def create_interface(self):
        """Cria a interface completa de turmas"""
        # Título
        title_frame = tk.Frame(self.parent_frame, bg='white')
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            title_frame,
            text="Gestão de Turmas",
            font=('Arial', 20, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(pady=15)
        
        # Container principal com scroll
        main_container = tk.Frame(self.parent_frame, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Criar formulário de cadastro
        self.create_form(main_container)
        
        # Criar tabela de turmas
        self.create_table(main_container)
    
    def create_form(self, parent):
        """Cria o formulário de cadastro/edição"""
        # Frame do formulário
        form_frame = tk.LabelFrame(
            parent,
            text="Cadastrar/Editar Turma",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=20,
            pady=15
        )
        form_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Grid para organizar campos
        fields_frame = tk.Frame(form_frame, bg='white')
        fields_frame.pack(fill=tk.X)
        
        # Linha 1 - Dados básicos
        row1 = tk.Frame(fields_frame, bg='white')
        row1.pack(fill=tk.X, pady=5)
        
        # Nome da Turma
        tk.Label(row1, text="Nome da Turma*:", bg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.nome_var = tk.StringVar()
        self.nome_entry = tk.Entry(row1, textvariable=self.nome_var, width=20, font=('Arial', 10))
        self.nome_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # Série
        tk.Label(row1, text="Série/Ano*:", bg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.serie_var = tk.StringVar()
        self.serie_entry = tk.Entry(row1, textvariable=self.serie_var, width=15, font=('Arial', 10))
        self.serie_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # Ano Letivo  
        tk.Label(row1, text="Ano Letivo*:", bg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.ano_var = tk.StringVar(value="2025")
        self.ano_entry = tk.Entry(row1, textvariable=self.ano_var, width=10, font=('Arial', 10))
        self.ano_entry.pack(side=tk.LEFT)
        
        # Linha 2 - Configurações financeiras
        row2 = tk.Frame(fields_frame, bg='white')  
        row2.pack(fill=tk.X, pady=10)
        
        # Valor Mensalidade
        tk.Label(row2, text="Valor Mensalidade (R$)*:", bg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.valor_var = tk.StringVar()
        self.valor_entry = tk.Entry(row2, textvariable=self.valor_var, width=15, font=('Arial', 10))
        self.valor_entry.pack(side=tk.LEFT, padx=(0, 20))
        self.valor_entry.bind('<FocusOut>', self.format_valor)
        
        # Dia Vencimento
        tk.Label(row2, text="Dia Vencimento:", bg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.dia_venc_var = tk.StringVar(value="10")
        self.dia_venc_entry = tk.Entry(row2, textvariable=self.dia_venc_var, width=8, font=('Arial', 10))
        self.dia_venc_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # Dia Limite Desconto
        tk.Label(row2, text="Dia Limite Desconto:", bg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.dia_desc_var = tk.StringVar(value="5")
        self.dia_desc_entry = tk.Entry(row2, textvariable=self.dia_desc_var, width=8, font=('Arial', 10))
        self.dia_desc_entry.pack(side=tk.LEFT)
        
        # Linha 3 - Percentuais
        row3 = tk.Frame(fields_frame, bg='white')
        row3.pack(fill=tk.X, pady=5)
        
        # % Desconto
        tk.Label(row3, text="% Desconto:", bg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.desc_var = tk.StringVar(value="0")
        self.desc_entry = tk.Entry(row3, textvariable=self.desc_var, width=10, font=('Arial', 10))
        self.desc_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # % Multa
        tk.Label(row3, text="% Multa:", bg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.multa_var = tk.StringVar(value="0")
        self.multa_entry = tk.Entry(row3, textvariable=self.multa_var, width=10, font=('Arial', 10))
        self.multa_entry.pack(side=tk.LEFT)
        
        # Botões de ação
        buttons_frame = tk.Frame(form_frame, bg='white')
        buttons_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.salvar_btn = tk.Button(
            buttons_frame,
            text="💾 Salvar Turma",
            command=self.salvar_turma,
            bg='#27ae60',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor='hand2'
        )
        self.salvar_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            buttons_frame,
            text="🔄 Limpar",
            command=self.limpar_formulario,
            bg='#95a5a6',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancelar_btn = tk.Button(
            buttons_frame,
            text="❌ Cancelar",
            command=self.cancelar_edicao,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor='hand2'
        )
        self.cancelar_btn.pack(side=tk.LEFT)
        self.cancelar_btn.pack_forget()  # Inicialmente oculto
    
    def create_table(self, parent):
        """Cria a tabela de turmas"""
        # Frame da tabela
        table_frame = tk.LabelFrame(
            parent,
            text="Turmas Cadastradas",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=20,
            pady=15
        )
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Frame para a treeview e scrollbar
        tree_frame = tk.Frame(table_frame, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configurar colunas
        columns = ('ID', 'Nome', 'Série', 'Ano', 'Mensalidade', 'Venc.', 'Desc.', '% Desc', '% Multa', 'Alunos')
        
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)
        
        # Configurar cabeçalhos e larguras
        column_widths = {'ID': 50, 'Nome': 150, 'Série': 100, 'Ano': 80, 'Mensalidade': 120, 
                        'Venc.': 60, 'Desc.': 60, '% Desc': 80, '% Multa': 80, 'Alunos': 80}
        
        for col in columns:
            self.tree.heading(col, text=col, anchor='center')
            self.tree.column(col, width=column_widths[col], anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Posicionar elementos
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Botões de ação da tabela
        action_frame = tk.Frame(table_frame, bg='white')
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(
            action_frame,
            text="✏️ Editar",
            command=self.editar_turma,
            bg='#3498db',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            action_frame,
            text="🗑️ Excluir",
            command=self.excluir_turma,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            action_frame,
            text="🔄 Atualizar",
            command=self.carregar_turmas,
            bg='#17a2b8',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT)
        
        # Bind para duplo clique
        self.tree.bind('<Double-1>', lambda e: self.editar_turma())
    
    def format_valor(self, event=None):
        """Formata o valor enquanto o usuário digita"""
        try:
            valor = self.valor_var.get().replace('R$', '').replace('.', '').replace(',', '.')
            if valor and validate_number(valor):
                formatted = format_currency(float(valor))
                self.valor_var.set(formatted)
        except:
            pass
    
    def validar_formulario(self):
        """Valida os dados do formulário"""
        erros = []
        
        if not self.nome_var.get().strip():
            erros.append("Nome da turma é obrigatório")
        
        if not self.serie_var.get().strip():
            erros.append("Série é obrigatória")
            
        if not self.ano_var.get().strip():
            erros.append("Ano letivo é obrigatório")
        
        valor_str = self.valor_var.get().replace('R$', '').replace('.', '').replace(',', '.')
        if not valor_str or not validate_number(valor_str):
            erros.append("Valor da mensalidade deve ser um número válido")
        
        try:
            dia_venc = int(self.dia_venc_var.get())
            if dia_venc < 1 or dia_venc > 31:
                erros.append("Dia de vencimento deve ser entre 1 e 31")
        except:
            erros.append("Dia de vencimento deve ser um número válido")
        
        try:
            dia_desc = int(self.dia_desc_var.get())
            if dia_desc < 1 or dia_desc > 31:
                erros.append("Dia limite de desconto deve ser entre 1 e 31")
        except:
            erros.append("Dia limite de desconto deve ser um número válido")
        
        return erros
    
    def salvar_turma(self):
        """Salva ou atualiza uma turma"""
        erros = self.validar_formulario()
        if erros:
            messagebox.showerror("Erro de Validação", "\n".join(erros))
            return
        
        try:
            # Preparar dados
            valor_str = self.valor_var.get().replace('R$', '').replace('.', '').replace(',', '.')
            
            turma_data = {
                'nome': self.nome_var.get().strip(),
                'serie': self.serie_var.get().strip(),
                'ano_letivo': self.ano_var.get().strip(),
                'valor_mensalidade': float(valor_str),
                'dia_vencimento': int(self.dia_venc_var.get()),
                'dia_limite_desconto': int(self.dia_desc_var.get()),
                'percentual_desconto': float(self.desc_var.get() or 0),
                'percentual_multa': float(self.multa_var.get() or 0)
            }
            
            # Se está editando, incluir o ID
            if self.turma_editando:
                turma_data['id'] = self.turma_editando
            
            # Salvar
            resultado = self.turma_service.salvar_turma(turma_data)
            
            if resultado['success']:
                acao = "atualizada" if self.turma_editando else "cadastrada"
                messagebox.showinfo("Sucesso", f"Turma {acao} com sucesso!")
                self.limpar_formulario()
                self.cancelar_edicao()
                self.carregar_turmas()
            else:
                messagebox.showerror("Erro", f"Erro ao salvar turma: {resultado['error']}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")
    
    def editar_turma(self):
        """Carrega uma turma para edição"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma turma para editar!")
            return
        
        # Obter ID da turma selecionada
        item = self.tree.item(selection[0])
        turma_id = item['values'][0]
        
        # Buscar dados da turma
        turma = self.turma_service.buscar_turma_por_id(turma_id)
        if not turma:
            messagebox.showerror("Erro", "Turma não encontrada!")
            return
        
        # Preencher formulário
        self.nome_var.set(turma['nome'])
        self.serie_var.set(turma['serie'])
        self.ano_var.set(turma['ano_letivo'])
        self.valor_var.set(format_currency(turma['valor_mensalidade']))
        self.dia_venc_var.set(str(turma['dia_vencimento']))
        self.dia_desc_var.set(str(turma['dia_limite_desconto']))
        self.desc_var.set(str(turma['percentual_desconto']))
        self.multa_var.set(str(turma['percentual_multa']))
        
        # Ativar modo edição
        self.turma_editando = turma_id
        self.salvar_btn.config(text="💾 Atualizar Turma")
        self.cancelar_btn.pack(side=tk.LEFT)
    
    def cancelar_edicao(self):
        """Cancela a edição e volta ao modo de cadastro"""
        self.turma_editando = None
        self.salvar_btn.config(text="💾 Salvar Turma")
        self.cancelar_btn.pack_forget()
        self.limpar_formulario()
    
    def excluir_turma(self):
        """Exclui uma turma selecionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma turma para excluir!")
            return
        
        # Obter dados da turma
        item = self.tree.item(selection[0])
        turma_id = item['values'][0]
        turma_nome = item['values'][1]
        
        # Confirmar exclusão
        if not messagebox.askyesno(
            "Confirmar Exclusão", 
            f"Tem certeza que deseja excluir a turma '{turma_nome}'?\n\nEsta ação não pode ser desfeita!"
        ):
            return
        
        # Excluir
        resultado = self.turma_service.excluir_turma(turma_id)
        
        if resultado['success']:
            messagebox.showinfo("Sucesso", "Turma excluída com sucesso!")
            self.carregar_turmas()
        else:
            messagebox.showerror("Erro", resultado['error'])
    
    def limpar_formulario(self):
        """Limpa todos os campos do formulário"""
        self.nome_var.set("")
        self.serie_var.set("")
        self.ano_var.set("2025")
        self.valor_var.set("")
        self.dia_venc_var.set("10")
        self.dia_desc_var.set("5")
        self.desc_var.set("0")
        self.multa_var.set("0")
        
        # Focar no primeiro campo
        self.nome_entry.focus()
    
    def carregar_turmas(self):
        """Carrega e exibe todas as turmas na tabela"""
        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Carregar turmas
        turmas = self.turma_service.listar_turmas()
        
        for turma in turmas:
            valores = (
                turma['id'],
                turma['nome'],
                turma['serie'],
                turma['ano_letivo'],
                format_currency(turma['valor_mensalidade']),
                turma['dia_vencimento'],
                turma['dia_limite_desconto'],
                f"{turma['percentual_desconto']}%",
                f"{turma['percentual_multa']}%",
                turma['total_alunos']
            )
            self.tree.insert('', tk.END, values=valores)
        
        print(f"✅ {len(turmas)} turmas carregadas!")
