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
        """Cria as tabelas se não existirem - SEM EMAIL"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela TURMAS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS turmas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                serie TEXT NOT NULL,
                ano_letivo TEXT NOT NULL,
                valor_mensalidade REAL NOT NULL,
                dia_vencimento INTEGER DEFAULT 10,
                dia_limite_desconto INTEGER DEFAULT 5,
                percentual_desconto REAL DEFAULT 0,
                percentual_multa REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela ALUNOS (SEM EMAIL)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alunos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                data_nascimento DATE NOT NULL,
                cpf TEXT,
                sexo TEXT,
                endereco TEXT,
                telefone TEXT,
                nacionalidade TEXT DEFAULT 'Brasileira',
                turma_id INTEGER NOT NULL,
                status TEXT DEFAULT 'Ativo',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (turma_id) REFERENCES turmas (id)
            )
        """)
        
        # Tabela RESPONSÁVEIS FINANCEIROS (SEM EMAIL)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS responsaveis_financeiros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                telefone TEXT NOT NULL,
                parentesco TEXT DEFAULT 'Responsável',
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
        
        conn.commit()
        conn.close()
        print("✅ Banco de dados inicializado SEM EMAIL!")

# Instância global do banco
db = DatabaseConnection()
