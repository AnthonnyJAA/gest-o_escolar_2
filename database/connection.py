import sqlite3
import os
from pathlib import Path

class DatabaseConnection:
    def __init__(self, db_name="escola.db"):
        """Inicializa conexão com banco corrigido"""
        self.db_path = Path(__file__).parent / db_name
        self.init_database()
    
    def get_connection(self):
        """Retorna conexão com o banco"""
        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco: {e}")
            raise
    
    def init_database(self):
        """Cria todas as tabelas com estrutura corrigida"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            print("🔄 Inicializando estrutura do banco...")
            
            # === TABELA TURMAS (apenas dados acadêmicos) ===
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS turmas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    serie TEXT NOT NULL,
                    ano_letivo TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # === TABELA ALUNOS (com dados financeiros individuais) ===
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alunos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    data_nascimento DATE NOT NULL,
                    cpf TEXT,
                    sexo TEXT,
                    nacionalidade TEXT DEFAULT 'Brasileira',
                    telefone TEXT,
                    endereco TEXT,
                    turma_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'Ativo',
                    valor_mensalidade REAL NOT NULL DEFAULT 0,
                    desconto_fixo REAL DEFAULT 0,
                    multa_por_dia REAL DEFAULT 0,
                    dias_carencia_multa INTEGER DEFAULT 30,
                    data_matricula DATE DEFAULT (date('now')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (turma_id) REFERENCES turmas (id)
                )
            """)
            
            # === TABELA RESPONSÁVEIS ===
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS responsaveis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aluno_id INTEGER NOT NULL,
                    nome TEXT NOT NULL,
                    telefone TEXT NOT NULL,
                    parentesco TEXT NOT NULL,
                    principal BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (aluno_id) REFERENCES alunos (id) ON DELETE CASCADE
                )
            """)
            
            # === TABELA PAGAMENTOS ===
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pagamentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aluno_id INTEGER NOT NULL,
                    mes_referencia TEXT NOT NULL,
                    valor_original REAL NOT NULL,
                    desconto_aplicado REAL DEFAULT 0,
                    multa_aplicada REAL DEFAULT 0,
                    valor_final REAL NOT NULL,
                    data_vencimento DATE NOT NULL,
                    data_pagamento DATE,
                    status TEXT DEFAULT 'Pendente',
                    pode_receber_multa BOOLEAN DEFAULT 1,
                    observacoes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (aluno_id) REFERENCES alunos (id)
                )
            """)
            
            # === RECRIAR TABELA HISTÓRICO DE TRANSFERÊNCIAS CORRIGIDA ===
            # Primeiro, drop se existe (para corrigir problemas)
            cursor.execute("DROP TABLE IF EXISTS historico_transferencias")
            
            # Criar nova tabela com estrutura correta
            cursor.execute("""
                CREATE TABLE historico_transferencias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aluno_id INTEGER NOT NULL,
                    turma_origem_id INTEGER,
                    turma_destino_id INTEGER,
                    motivo TEXT NOT NULL DEFAULT 'Transferência',
                    observacoes TEXT,
                    data_transferencia TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    tipo_transferencia TEXT DEFAULT 'TRANSFERENCIA',
                    usuario TEXT DEFAULT 'Sistema',
                    FOREIGN KEY (aluno_id) REFERENCES alunos (id),
                    FOREIGN KEY (turma_origem_id) REFERENCES turmas (id),
                    FOREIGN KEY (turma_destino_id) REFERENCES turmas (id)
                )
            """)
            
            # === TABELA CONFIGURAÇÕES ===
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuracoes (
                    id INTEGER PRIMARY KEY,
                    chave TEXT UNIQUE NOT NULL,
                    valor TEXT NOT NULL,
                    descricao TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # === APLICAR MIGRAÇÕES ===
            self._aplicar_migracoes(cursor)
            
            # === INSERIR DADOS INICIAIS SE NECESSÁRIO ===
            self._inserir_dados_iniciais(cursor)
            
            conn.commit()
            print("✅ Banco de dados inicializado com sucesso!")
            
        except sqlite3.Error as e:
            conn.rollback()
            print(f"❌ Erro ao inicializar banco: {e}")
            raise
        finally:
            conn.close()
    
    def _aplicar_migracoes(self, cursor):
        """Aplica migrações necessárias"""
        try:
            # Verificar se existe coluna valor_mensalidade em alunos
            cursor.execute("PRAGMA table_info(alunos)")
            colunas = [col[1] for col in cursor.fetchall()]
            
            colunas_necessarias = [
                'valor_mensalidade',
                'desconto_fixo', 
                'multa_por_dia',
                'dias_carencia_multa',
                'data_matricula'
            ]
            
            for coluna in colunas_necessarias:
                if coluna not in colunas:
                    if coluna == 'valor_mensalidade':
                        cursor.execute(f"ALTER TABLE alunos ADD COLUMN {coluna} REAL NOT NULL DEFAULT 0")
                    elif coluna in ['desconto_fixo', 'multa_por_dia']:
                        cursor.execute(f"ALTER TABLE alunos ADD COLUMN {coluna} REAL DEFAULT 0")
                    elif coluna == 'dias_carencia_multa':
                        cursor.execute(f"ALTER TABLE alunos ADD COLUMN {coluna} INTEGER DEFAULT 30")
                    elif coluna == 'data_matricula':
                        cursor.execute(f"ALTER TABLE alunos ADD COLUMN {coluna} DATE DEFAULT (date('now'))")
                    
                    print(f"✅ Coluna {coluna} adicionada à tabela alunos")
            
        except sqlite3.Error as e:
            print(f"⚠️ Aviso durante migração: {e}")
    
    def _inserir_dados_iniciais(self, cursor):
        """Insere dados iniciais se necessário"""
        try:
            # Verificar se existem turmas
            cursor.execute("SELECT COUNT(*) FROM turmas")
            if cursor.fetchone()[0] == 0:
                print("📋 Inserindo turmas iniciais...")
                
                turmas_iniciais = [
                    ("1º Ano A", "1º Ano", "2025"),
                    ("1º Ano B", "1º Ano", "2025"),
                    ("2º Ano A", "2º Ano", "2025"),
                    ("2º Ano B", "2º Ano", "2025"),
                    ("3º Ano A", "3º Ano", "2025"),
                    ("3º Ano B", "3º Ano", "2025"),
                    ("Pré-escola", "Infantil", "2025")
                ]
                
                cursor.executemany("""
                    INSERT INTO turmas (nome, serie, ano_letivo) 
                    VALUES (?, ?, ?)
                """, turmas_iniciais)
                
                print(f"✅ {len(turmas_iniciais)} turmas inseridas")
                
        except sqlite3.Error as e:
            print(f"⚠️ Erro ao inserir dados iniciais: {e}")

# Instância global do banco
db = DatabaseConnection()

# Função para backup do banco
def criar_backup():
    """Cria backup do banco de dados"""
    try:
        import shutil
        from datetime import datetime
        
        source = db.db_path
        backup_name = f"escola_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        backup_path = db.db_path.parent / backup_name
        
        shutil.copy2(source, backup_path)
        print(f"✅ Backup criado: {backup_name}")
        return True
        
    except Exception as e:
        print(f"⚠️ Erro ao criar backup: {e}")
        return False

# Função para resetar tabela específica
def reset_transferencias_table():
    """Reseta tabela de transferências se houver problemas"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Drop e recria tabela
        cursor.execute("DROP TABLE IF EXISTS historico_transferencias")
        
        cursor.execute("""
            CREATE TABLE historico_transferencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER NOT NULL,
                turma_origem_id INTEGER,
                turma_destino_id INTEGER,
                motivo TEXT NOT NULL DEFAULT 'Transferência',
                observacoes TEXT,
                data_transferencia TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                tipo_transferencia TEXT DEFAULT 'TRANSFERENCIA',
                usuario TEXT DEFAULT 'Sistema',
                FOREIGN KEY (aluno_id) REFERENCES alunos (id),
                FOREIGN KEY (turma_origem_id) REFERENCES turmas (id),
                FOREIGN KEY (turma_destino_id) REFERENCES turmas (id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Tabela de transferências resetada com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao resetar tabela: {e}")
        return False