from database.connection import db
import sqlite3
from datetime import datetime, date

class TransferenciaService:
    def __init__(self):
        self.db = db
        # Verificar e corrigir estrutura da tabela
        self._verificar_estrutura_historico()

    def _verificar_estrutura_historico(self):
        """Verifica e corrige estrutura da tabela de histórico"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Verificar se tabela existe
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='historico_transferencias'
            """)
            
            if not cursor.fetchone():
                # Criar tabela se não existir
                cursor.execute("""
                    CREATE TABLE historico_transferencias (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        aluno_id INTEGER NOT NULL,
                        turma_origem_id INTEGER,
                        turma_destino_id INTEGER,
                        motivo TEXT NOT NULL,
                        observacoes TEXT,
                        data_transferencia TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        tipo_transferencia TEXT DEFAULT 'TRANSFERENCIA',
                        FOREIGN KEY (aluno_id) REFERENCES alunos (id),
                        FOREIGN KEY (turma_origem_id) REFERENCES turmas (id),
                        FOREIGN KEY (turma_destino_id) REFERENCES turmas (id)
                    )
                """)
                print("✅ Tabela historico_transferencias criada")
            else:
                # Verificar se coluna tipo_transferencia existe
                cursor.execute("PRAGMA table_info(historico_transferencias)")
                colunas = [col[1] for col in cursor.fetchall()]
                
                if 'tipo_transferencia' not in colunas:
                    cursor.execute("""
                        ALTER TABLE historico_transferencias 
                        ADD COLUMN tipo_transferencia TEXT DEFAULT 'TRANSFERENCIA'
                    """)
                    print("✅ Coluna tipo_transferencia adicionada")
            
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            print(f"❌ Erro ao verificar estrutura: {e}")

    def listar_turmas_para_filtro(self):
        """Lista turmas para filtros"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, nome, serie, ano_letivo
                FROM turmas
                ORDER BY ano_letivo DESC, serie, nome
            """)
            
            turmas = []
            for row in cursor.fetchall():
                turma = {
                    'id': row[0],
                    'nome': row[1],
                    'serie': row[2],
                    'ano_letivo': row[3],
                    'display': f"{row[1]} - {row[2]} ({row[3]})"
                }
                turmas.append(turma)
            
            conn.close()
            return turmas
            
        except sqlite3.Error as e:
            conn.close()
            print(f"❌ Erro ao listar turmas: {e}")
            return []

    def listar_alunos_por_turma(self, turma_id):
        """Lista alunos de uma turma específica"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    a.id,
                    a.nome,
                    a.data_nascimento,
                    a.status,
                    a.valor_mensalidade,
                    t.nome as turma_nome,
                    t.serie as turma_serie,
                    (julianday('now') - julianday(a.data_nascimento)) / 365 as idade
                FROM alunos a
                INNER JOIN turmas t ON a.turma_id = t.id
                WHERE a.turma_id = ? AND a.status = 'Ativo'
                ORDER BY a.nome
            """, (turma_id,))
            
            alunos = []
            for row in cursor.fetchall():
                aluno = {
                    'id': row[0],
                    'nome': row[1],
                    'data_nascimento': row[2],
                    'status': row[3],
                    'valor_mensalidade': row[4] or 0,
                    'turma_nome': row[5],
                    'turma_serie': row[6],
                    'idade': int(row[7]) if row[7] else 0
                }
                alunos.append(aluno)
            
            conn.close()
            return alunos
            
        except sqlite3.Error as e:
            conn.close()
            print(f"❌ Erro ao listar alunos da turma: {e}")
            return []

    def transferir_aluno(self, aluno_id, turma_origem_id, turma_destino_id, motivo, observacoes):
        """Transfere aluno entre turmas - VERSÃO CORRIGIDA"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar se aluno existe e está ativo
            cursor.execute("""
                SELECT nome, status, turma_id 
                FROM alunos 
                WHERE id = ?
            """, (aluno_id,))
            
            aluno_data = cursor.fetchone()
            if not aluno_data:
                return {'success': False, 'error': 'Aluno não encontrado'}
            
            if aluno_data[1].lower() != 'ativo':
                return {'success': False, 'error': f'Aluno {aluno_data[0]} não está ativo'}
            
            if aluno_data[2] != turma_origem_id:
                return {'success': False, 'error': f'Aluno não pertence à turma de origem especificada'}
            
            # Verificar se turma de destino existe
            cursor.execute("SELECT nome, serie FROM turmas WHERE id = ?", (turma_destino_id,))
            turma_destino = cursor.fetchone()
            if not turma_destino:
                return {'success': False, 'error': 'Turma de destino não encontrada'}
            
            # Verificar se não é a mesma turma
            if turma_origem_id == turma_destino_id:
                return {'success': False, 'error': 'Turma de origem deve ser diferente da turma de destino'}
            
            # Executar transferência
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
            
            # Obter nomes das turmas para retorno
            cursor.execute("""
                SELECT t1.nome as origem, t2.nome as destino
                FROM turmas t1, turmas t2
                WHERE t1.id = ? AND t2.id = ?
            """, (turma_origem_id, turma_destino_id))
            
            turmas_info = cursor.fetchone()
            conn.close()
            
            return {
                'success': True,
                'aluno_nome': aluno_data[0],
                'turma_origem': turmas_info[0] if turmas_info else 'N/A',
                'turma_destino': turmas_info[1] if turmas_info else 'N/A'
            }
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return {'success': False, 'error': f'Erro no banco de dados: {str(e)}'}

    def obter_historico_transferencias(self, limite=10):
        """Obtém histórico de transferências"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    h.data_transferencia,
                    a.nome as aluno_nome,
                    t1.nome as turma_origem,
                    t2.nome as turma_destino,
                    h.motivo,
                    h.observacoes
                FROM historico_transferencias h
                INNER JOIN alunos a ON h.aluno_id = a.id
                LEFT JOIN turmas t1 ON h.turma_origem_id = t1.id
                LEFT JOIN turmas t2 ON h.turma_destino_id = t2.id
                ORDER BY h.data_transferencia DESC
                LIMIT ?
            """, (limite,))
            
            historico = []
            for row in cursor.fetchall():
                item = {
                    'data_transferencia': row[0],
                    'aluno_nome': row[1],
                    'turma_origem': row[2] or 'N/A',
                    'turma_destino': row[3] or 'N/A',
                    'motivo': row[4],
                    'observacoes': row[5] or ''
                }
                historico.append(item)
            
            conn.close()
            return historico
            
        except sqlite3.Error as e:
            conn.close()
            print(f"❌ Erro ao obter histórico: {e}")
            return []

    def obter_estatisticas_transferencias(self):
        """Obtém estatísticas de transferências"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Total de transferências
            cursor.execute("SELECT COUNT(*) FROM historico_transferencias")
            total = cursor.fetchone()[0] or 0
            
            # Transferências este mês
            cursor.execute("""
                SELECT COUNT(*) FROM historico_transferencias
                WHERE strftime('%Y-%m', data_transferencia) = strftime('%Y-%m', 'now')
            """)
            este_mes = cursor.fetchone()[0] or 0
            
            # Turma que mais recebe alunos
            cursor.execute("""
                SELECT t.nome, COUNT(*) as total
                FROM historico_transferencias h
                INNER JOIN turmas t ON h.turma_destino_id = t.id
                GROUP BY t.id, t.nome
                ORDER BY total DESC
                LIMIT 1
            """)
            turma_mais_recebe = cursor.fetchone()
            
            conn.close()
            
            return {
                'total_transferencias': total,
                'transferencias_mes': este_mes,
                'turma_mais_recebe': f"{turma_mais_recebe[0]} ({turma_mais_recebe[1]})" if turma_mais_recebe else "N/A"
            }
            
        except sqlite3.Error as e:
            conn.close()
            print(f"❌ Erro ao obter estatísticas: {e}")
            return {
                'total_transferencias': 0,
                'transferencias_mes': 0,
                'turma_mais_recebe': 'N/A'
            }

    def validar_transferencia(self, aluno_id, turma_origem_id, turma_destino_id):
        """Valida se transferência é possível"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            problemas = []
            
            # Verificar aluno
            cursor.execute("SELECT nome, status FROM alunos WHERE id = ?", (aluno_id,))
            aluno = cursor.fetchone()
            
            if not aluno:
                problemas.append("Aluno não encontrado")
            elif aluno[1].lower() != 'ativo':
                problemas.append(f"Aluno {aluno[0]} não está ativo")
            
            # Verificar turmas
            if turma_origem_id == turma_destino_id:
                problemas.append("Turma de origem deve ser diferente da destino")
            
            cursor.execute("SELECT COUNT(*) FROM turmas WHERE id = ?", (turma_destino_id,))
            if cursor.fetchone()[0] == 0:
                problemas.append("Turma de destino não encontrada")
            
            conn.close()
            
            return {
                'success': len(problemas) == 0,
                'problemas': problemas
            }
            
        except sqlite3.Error as e:
            conn.close()
            return {
                'success': False,
                'problemas': [f'Erro no banco: {str(e)}']
            }
