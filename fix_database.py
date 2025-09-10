#!/usr/bin/env python3
"""
Script para corrigir estrutura do banco de dados
Remove campos financeiros das turmas e migra dados
"""

import sqlite3
from pathlib import Path
from datetime import datetime

def migrar_banco():
    """Migra banco removendo campos financeiros das turmas"""
    
    db_path = Path("database/escola.db")
    
    if not db_path.exists():
        print("❌ Banco de dados não encontrado!")
        return
    
    print("🔄 Iniciando migração do banco de dados...")
    
    # Backup do banco
    backup_path = Path(f"database/escola_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup criado: {backup_path}")
    except Exception as e:
        print(f"⚠️ Erro ao criar backup: {e}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar estrutura atual da tabela turmas
        cursor.execute("PRAGMA table_info(turmas)")
        colunas = cursor.fetchall()
        colunas_nomes = [col[1] for col in colunas]
        
        print(f"📋 Colunas atuais na tabela turmas: {colunas_nomes}")
        
        # Se tem campos financeiros, migrar
        if 'valor_mensalidade' in colunas_nomes:
            print("🔄 Removendo campos financeiros da tabela turmas...")
            
            # 1. Criar nova tabela sem campos financeiros
            cursor.execute("""
                CREATE TABLE turmas_nova (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    serie TEXT NOT NULL,
                    ano_letivo TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 2. Copiar dados acadêmicos
            cursor.execute("""
                INSERT INTO turmas_nova (id, nome, serie, ano_letivo, created_at)
                SELECT id, nome, serie, ano_letivo, 
                       COALESCE(created_at, CURRENT_TIMESTAMP)
                FROM turmas
            """)
            
            # 3. Verificar se há alunos para atualizar com dados financeiros das turmas
            cursor.execute("""
                SELECT a.id, a.valor_mensalidade, t.valor_mensalidade as turma_mensalidade
                FROM alunos a
                INNER JOIN turmas t ON a.turma_id = t.id
                WHERE a.valor_mensalidade = 0 OR a.valor_mensalidade IS NULL
            """)
            
            alunos_atualizar = cursor.fetchall()
            
            if alunos_atualizar:
                print(f"🔄 Atualizando {len(alunos_atualizar)} alunos com dados financeiros das turmas...")
                
                for aluno_id, aluno_mens, turma_mens in alunos_atualizar:
                    if turma_mens and turma_mens > 0:
                        cursor.execute("""
                            UPDATE alunos 
                            SET valor_mensalidade = ?
                            WHERE id = ? AND (valor_mensalidade = 0 OR valor_mensalidade IS NULL)
                        """, (turma_mens, aluno_id))
            
            # 4. Remover tabela antiga e renomear nova
            cursor.execute("DROP TABLE turmas")
            cursor.execute("ALTER TABLE turmas_nova RENAME TO turmas")
            
            print("✅ Migração da tabela turmas concluída!")
        
        else:
            print("✅ Tabela turmas já está na estrutura correta!")
        
        # Verificar se tabela alunos tem campos financeiros
        cursor.execute("PRAGMA table_info(alunos)")
        colunas_alunos = cursor.fetchall()
        colunas_alunos_nomes = [col[1] for col in colunas_alunos]
        
        # Adicionar campos financeiros aos alunos se não existirem
        colunas_adicionar = [
            ('valor_mensalidade', 'REAL NOT NULL DEFAULT 0'),
            ('desconto_fixo', 'REAL DEFAULT 0'),
            ('multa_por_dia', 'REAL DEFAULT 0'),
            ('dias_carencia_multa', 'INTEGER DEFAULT 30'),
            ('data_matricula', 'DATE DEFAULT (date("now"))')
        ]
        
        for coluna, definicao in colunas_adicionar:
            if coluna not in colunas_alunos_nomes:
                cursor.execute(f"ALTER TABLE alunos ADD COLUMN {coluna} {definicao}")
                print(f"✅ Coluna {coluna} adicionada à tabela alunos")
        
        # Verificar tabela responsáveis (renomear se necessário)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='responsaveis_financeiros'")
        if cursor.fetchone():
            try:
                cursor.execute("ALTER TABLE responsaveis_financeiros RENAME TO responsaveis")
                print("✅ Tabela responsaveis_financeiros renomeada para responsaveis")
            except sqlite3.Error:
                print("✅ Tabela responsaveis já existe")
        
        conn.commit()
        print("🎉 Migração concluída com sucesso!")
        
        # Estatísticas finais
        cursor.execute("SELECT COUNT(*) FROM turmas")
        total_turmas = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM alunos")
        total_alunos = cursor.fetchone()[0]
        
        print(f"📊 Estatísticas finais:")
        print(f"   📚 Turmas: {total_turmas}")
        print(f"   👥 Alunos: {total_alunos}")
        
    except Exception as e:
        print(f"❌ Erro durante migração: {e}")
        conn.rollback()
    
    finally:
        conn.close()

def verificar_estrutura():
    """Verifica estrutura atual do banco"""
    db_path = Path("database/escola.db")
    
    if not db_path.exists():
        print("❌ Banco de dados não encontrado!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔍 Estrutura atual do banco:")
    print("=" * 50)
    
    # Tabelas existentes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tabelas = cursor.fetchall()
    
    for tabela in tabelas:
        nome_tabela = tabela[0]
        print(f"\n📋 Tabela: {nome_tabela}")
        
        cursor.execute(f"PRAGMA table_info({nome_tabela})")
        colunas = cursor.fetchall()
        
        for coluna in colunas:
            print(f"   • {coluna[1]} ({coluna[2]}) {'NOT NULL' if coluna[3] else 'NULL'}")
    
    conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--verificar':
        verificar_estrutura()
    else:
        migrar_banco()
