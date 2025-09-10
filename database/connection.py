import sqlite3
import os
from pathlib import Path

class DatabaseConnection:
    def __init__(self, db_name="escola.db"):
        self.db_path = Path(__file__).parent / db_name
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Cria as tabelas com estrutura corrigida - Turmas apenas acadêmicas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # === MIGRAÇÃO AUTOMÁTICA ===
        print("🔄 Verificando estrutura do banco de dados...")
        self._migrar_estrutura_turmas(cursor)
        
        # Tabela TURMAS (apenas dados acadêmicos)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS turmas_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                serie TEXT NOT NULL,
                ano_letivo TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela ALUNOS (com dados financeiros individuais)
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
        
        # Tabela RESPONSÁVEIS (múltiplos por aluno)
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
        
        # Tabela PAGAMENTOS
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
        
        # Tabela CONFIGURAÇÕES
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                id INTEGER PRIMARY KEY,
                chave TEXT UNIQUE NOT NULL,
                valor TEXT NOT NULL,
                descricao TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Migrar dados para nova estrutura
        self._finalizar_migracao_turmas(cursor)
        
        conn.commit()
        conn.close()
        print("✅ Banco de dados inicializado com estrutura corrigida!")
    
    def _migrar_estrutura_turmas(self, cursor):
        """Migra estrutura da tabela turmas removendo campos financeiros"""
        try:
            # Verificar se existe tabela turmas antiga
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='turmas'")
            tabela_existe = cursor.fetchone()
            
            if tabela_existe:
                # Verificar se tem campos financeiros
                cursor.execute("PRAGMA table_info(turmas)")
                colunas = cursor.fetchall()
                colunas_nomes = [col[1] for col in colunas]
                
                if 'valor_mensalidade' in colunas_nomes:
                    print("🔄 Migrando estrutura de turmas (removendo campos financeiros)...")
                    
                    # Criar tabela temporária com dados acadêmicos
                    cursor.execute("""
                        CREATE TABLE turmas_temp (
                            id INTEGER PRIMARY KEY,
                            nome TEXT NOT NULL,
                            serie TEXT NOT NULL,
                            ano_letivo TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Copiar apenas dados acadêmicos
                    cursor.execute("""
                        INSERT INTO turmas_temp (id, nome, serie, ano_letivo, created_at)
                        SELECT id, nome, serie, ano_letivo, 
                               COALESCE(created_at, CURRENT_TIMESTAMP)
                        FROM turmas
                    """)
                    
                    # Renomear tabelas
                    cursor.execute("DROP TABLE turmas")
                    cursor.execute("ALTER TABLE turmas_temp RENAME TO turmas")
                    
                    print("✅ Estrutura de turmas migrada com sucesso!")
                else:
                    print("✅ Estrutura de turmas já está correta!")
            
        except sqlite3.Error as e:
            print(f"⚠️ Aviso na migração: {e}")
    
    def _finalizar_migracao_turmas(self, cursor):
        """Finaliza migração removendo tabela temporária se existir"""
        try:
            cursor.execute("DROP TABLE IF EXISTS turmas_new")
        except sqlite3.Error:
            pass
    
    def _adicionar_colunas_alunos(self, cursor):
        """Adiciona colunas financeiras aos alunos se não existirem"""
        try:
            # Verificar se colunas financeiras existem
            cursor.execute("PRAGMA table_info(alunos)")
            colunas = cursor.fetchall()
            colunas_nomes = [col[1] for col in colunas]
            
            colunas_financeiras = [
                ('valor_mensalidade', 'REAL NOT NULL DEFAULT 0'),
                ('desconto_fixo', 'REAL DEFAULT 0'),
                ('multa_por_dia', 'REAL DEFAULT 0'),
                ('dias_carencia_multa', 'INTEGER DEFAULT 30'),
                ('data_matricula', 'DATE DEFAULT (date("now"))')
            ]
            
            for coluna, definicao in colunas_financeiras:
                if coluna not in colunas_nomes:
                    cursor.execute(f"ALTER TABLE alunos ADD COLUMN {coluna} {definicao}")
                    print(f"✅ Coluna {coluna} adicionada à tabela alunos")
                    
        except sqlite3.Error as e:
            print(f"⚠️ Aviso ao adicionar colunas: {e}")

# Instância global do banco
db = DatabaseConnection()
