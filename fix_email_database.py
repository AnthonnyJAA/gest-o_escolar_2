#!/usr/bin/env python3
"""
Script para remover campo email do banco de dados
"""

import sqlite3
import os
from pathlib import Path

def fix_email_database():
    """Remove campo email da tabela alunos"""
    
    db_path = Path("database/escola.db")
    
    if not db_path.exists():
        print("❌ Banco de dados não encontrado!")
        return False
    
    print("🔧 Removendo campo email do banco de dados...")
    
    # Fazer backup primeiro
    backup_path = Path("database/escola_backup.db")
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup criado: {backup_path}")
    except:
        print("⚠️ Não foi possível criar backup")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar estrutura atual da tabela alunos
        cursor.execute("PRAGMA table_info(alunos)")
        columns_info = cursor.fetchall()
        
        print("📋 Estrutura atual da tabela alunos:")
        for col in columns_info:
            print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
        
        # Criar nova tabela sem campo email
        print("🔄 Criando nova estrutura SEM email...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alunos_new (
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
        
        # Copiar dados da tabela antiga (sem email)
        print("📋 Copiando dados existentes...")
        cursor.execute("""
            INSERT INTO alunos_new (id, nome, data_nascimento, cpf, sexo, endereco, telefone, nacionalidade, turma_id, status, created_at)
            SELECT id, nome, data_nascimento, cpf, sexo, endereco, telefone, nacionalidade, turma_id, status, created_at
            FROM alunos
        """)
        
        # Remover tabela antiga e renomear nova
        cursor.execute("DROP TABLE alunos")
        cursor.execute("ALTER TABLE alunos_new RENAME TO alunos")
        
        print("✅ Campo email removido com sucesso!")
        
        # Verificar nova estrutura
        cursor.execute("PRAGMA table_info(alunos)")
        new_columns = cursor.fetchall()
        
        print("📋 Nova estrutura da tabela alunos (SEM EMAIL):")
        for col in new_columns:
            print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
        
        conn.commit()
        print("💾 Alterações salvas!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante correção: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🎓 Script de Correção - Remover Email")
    print("=" * 50)
    
    if fix_email_database():
        print("\n✅ Correção concluída com sucesso!")
        print("🚀 Agora você pode executar o sistema normalmente.")
    else:
        print("\n❌ Erro na correção!")
        print("💡 Tente deletar o arquivo database/escola.db e executar o sistema novamente.")
    
    input("\nPressione Enter para sair...")
