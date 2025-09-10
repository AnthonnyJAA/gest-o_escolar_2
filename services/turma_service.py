from database.connection import db
import sqlite3

class TurmaService:
    def __init__(self):
        self.db = db
    
    def salvar_turma(self, turma_data):
        """Salva turma (apenas dados acadêmicos)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            if 'id' in turma_data:
                # Atualizar turma existente
                cursor.execute("""
                    UPDATE turmas 
                    SET nome = ?, serie = ?, ano_letivo = ?
                    WHERE id = ?
                """, (
                    turma_data['nome'],
                    turma_data['serie'],
                    turma_data['ano_letivo'],
                    turma_data['id']
                ))
                turma_id = turma_data['id']
            else:
                # Criar nova turma
                cursor.execute("""
                    INSERT INTO turmas (nome, serie, ano_letivo)
                    VALUES (?, ?, ?)
                """, (
                    turma_data['nome'],
                    turma_data['serie'],
                    turma_data['ano_letivo']
                ))
                turma_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'id': turma_id}
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return {'success': False, 'error': f'Erro ao salvar turma: {str(e)}'}
    
    def listar_turmas(self):
        """Lista turmas com contagem de alunos"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                t.id,
                t.nome,
                t.serie,
                t.ano_letivo,
                COUNT(a.id) as total_alunos
            FROM turmas t
            LEFT JOIN alunos a ON t.id = a.turma_id AND a.status = 'Ativo'
            GROUP BY t.id, t.nome, t.serie, t.ano_letivo
            ORDER BY t.nome
        """)
        
        turmas = []
        for row in cursor.fetchall():
            turma = {
                'id': row[0],
                'nome': row[1],
                'serie': row[2],
                'ano_letivo': row[3],
                'total_alunos': row[4],
                'display': f"{row[1]} - {row[2]} ({row[3]})"
            }
            turmas.append(turma)
        
        conn.close()
        return turmas
    
    def buscar_turma_por_id(self, turma_id):
        """Busca turma por ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM turmas WHERE id = ?", (turma_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'nome': row[1],
                'serie': row[2],
                'ano_letivo': row[3]
            }
        return None
    
    def excluir_turma(self, turma_id):
        """Exclui turma (apenas se não tiver alunos)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar se há alunos na turma
            cursor.execute("SELECT COUNT(*) FROM alunos WHERE turma_id = ?", (turma_id,))
            total_alunos = cursor.fetchone()[0]
            
            if total_alunos > 0:
                conn.close()
                return {'success': False, 'error': f'Não é possível excluir. Turma possui {total_alunos} aluno(s).'}
            
            # Excluir turma
            cursor.execute("DELETE FROM turmas WHERE id = ?", (turma_id,))
            
            conn.commit()
            conn.close()
            
            return {'success': True}
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return {'success': False, 'error': f'Erro ao excluir turma: {str(e)}'}
    
    def obter_estatisticas_turma(self, turma_id):
        """Obtém estatísticas de uma turma específica"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Dados básicos da turma
            cursor.execute("SELECT nome, serie, ano_letivo FROM turmas WHERE id = ?", (turma_id,))
            turma_info = cursor.fetchone()
            
            if not turma_info:
                return None
            
            # Estatísticas dos alunos
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_alunos,
                    SUM(CASE WHEN status = 'Ativo' THEN 1 ELSE 0 END) as alunos_ativos,
                    AVG(valor_mensalidade) as media_mensalidade,
                    MIN(valor_mensalidade) as min_mensalidade,
                    MAX(valor_mensalidade) as max_mensalidade
                FROM alunos 
                WHERE turma_id = ?
            """, (turma_id,))
            
            stats = cursor.fetchone()
            
            conn.close()
            
            return {
                'nome': turma_info[0],
                'serie': turma_info[1],
                'ano_letivo': turma_info[2],
                'total_alunos': stats[0] or 0,
                'alunos_ativos': stats[1] or 0,
                'media_mensalidade': stats[2] or 0,
                'min_mensalidade': stats[3] or 0,
                'max_mensalidade': stats[4] or 0
            }
            
        except sqlite3.Error as e:
            conn.close()
            return None
