from database.connection import db
import sqlite3
from datetime import datetime

class TurmaService:
    def __init__(self):
        self.db = db
    
    def listar_turmas(self):
        """Retorna todas as turmas com quantidade de alunos"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                t.id, t.nome, t.serie, t.ano_letivo, 
                t.valor_mensalidade, t.dia_vencimento, t.dia_limite_desconto,
                t.percentual_desconto, t.percentual_multa,
                COUNT(a.id) as total_alunos
            FROM turmas t
            LEFT JOIN alunos a ON t.id = a.turma_id AND a.status = 'Ativo'
            GROUP BY t.id
            ORDER BY t.nome
        """)
        
        turmas = []
        for row in cursor.fetchall():
            turma = {
                'id': row[0],
                'nome': row[1], 
                'serie': row[2],
                'ano_letivo': row[3],
                'valor_mensalidade': row[4],
                'dia_vencimento': row[5],
                'dia_limite_desconto': row[6],
                'percentual_desconto': row[7],
                'percentual_multa': row[8],
                'total_alunos': row[9]
            }
            turmas.append(turma)
        
        conn.close()
        return turmas
    
    def salvar_turma(self, turma_data):
        """Salva uma nova turma ou atualiza existente"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            if turma_data.get('id'):
                # Atualizar turma existente
                cursor.execute("""
                    UPDATE turmas SET
                        nome = ?, serie = ?, ano_letivo = ?, valor_mensalidade = ?,
                        dia_vencimento = ?, dia_limite_desconto = ?,
                        percentual_desconto = ?, percentual_multa = ?
                    WHERE id = ?
                """, (
                    turma_data['nome'],
                    turma_data['serie'], 
                    turma_data['ano_letivo'],
                    turma_data['valor_mensalidade'],
                    turma_data['dia_vencimento'],
                    turma_data['dia_limite_desconto'],
                    turma_data['percentual_desconto'],
                    turma_data['percentual_multa'],
                    turma_data['id']
                ))
                turma_id = turma_data['id']
            else:
                # Inserir nova turma
                cursor.execute("""
                    INSERT INTO turmas (nome, serie, ano_letivo, valor_mensalidade,
                                      dia_vencimento, dia_limite_desconto,
                                      percentual_desconto, percentual_multa)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    turma_data['nome'],
                    turma_data['serie'],
                    turma_data['ano_letivo'], 
                    turma_data['valor_mensalidade'],
                    turma_data['dia_vencimento'],
                    turma_data['dia_limite_desconto'],
                    turma_data['percentual_desconto'],
                    turma_data['percentual_multa']
                ))
                turma_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            return {'success': True, 'id': turma_id}
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return {'success': False, 'error': str(e)}
    
    def excluir_turma(self, turma_id):
        """Exclui uma turma se não houver alunos vinculados"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar se há alunos vinculados
            cursor.execute("SELECT COUNT(*) FROM alunos WHERE turma_id = ? AND status = 'Ativo'", (turma_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                conn.close()
                return {'success': False, 'error': f'Não é possível excluir. Há {count} alunos vinculados a esta turma.'}
            
            # Excluir turma
            cursor.execute("DELETE FROM turmas WHERE id = ?", (turma_id,))
            conn.commit()
            conn.close()
            return {'success': True}
            
        except sqlite3.Error as e:
            conn.rollback() 
            conn.close()
            return {'success': False, 'error': str(e)}
    
    def buscar_turma_por_id(self, turma_id):
        """Busca uma turma específica por ID"""
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
                'ano_letivo': row[3],
                'valor_mensalidade': row[4],
                'dia_vencimento': row[5],
                'dia_limite_desconto': row[6],
                'percentual_desconto': row[7],
                'percentual_multa': row[8]
            }
        return None
