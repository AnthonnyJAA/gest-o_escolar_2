from database.connection import db
import sqlite3
from datetime import datetime, date
from utils.formatters import format_date

class DashboardService:
    def __init__(self):
        self.db = db
    
    def obter_estatisticas_gerais(self):
        """Obtém estatísticas gerais para o dashboard"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Total de alunos ativos
            cursor.execute("SELECT COUNT(*) FROM alunos WHERE status = 'Ativo'")
            total_alunos = cursor.fetchone()[0]
            
            # Total de turmas
            cursor.execute("SELECT COUNT(*) FROM turmas")
            total_turmas = cursor.fetchone()[0]
            
            # Receita do mês atual
            mes_atual = date.today().strftime('%Y-%m')
            cursor.execute("""
                SELECT COALESCE(SUM(valor_final), 0) 
                FROM pagamentos 
                WHERE status = 'Pago' 
                AND strftime('%Y-%m', data_pagamento) = ?
            """, (mes_atual,))
            receita_mes = cursor.fetchone()[0]
            
            # Mensalidades pendentes
            cursor.execute("""
                SELECT COUNT(*) 
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                WHERE p.status = 'Pendente' 
                AND a.status = 'Ativo'
            """)
            pendentes = cursor.fetchone()[0]
            
            # Mensalidades atrasadas
            cursor.execute("""
                SELECT COUNT(*) 
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                WHERE (p.status = 'Atrasado' OR (p.status = 'Pendente' AND date(p.data_vencimento) < date('now')))
                AND a.status = 'Ativo'
            """)
            atrasadas = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_alunos': total_alunos,
                'total_turmas': total_turmas,
                'receita_mes': receita_mes,
                'pendentes': pendentes,
                'atrasadas': atrasadas
            }
            
        except Exception as e:
            conn.close()
            print(f"Erro ao obter estatísticas: {e}")
            return {
                'total_alunos': 0,
                'total_turmas': 0,
                'receita_mes': 0,
                'pendentes': 0,
                'atrasadas': 0
            }
    
    def obter_resumos(self):
        """Obtém resumos adicionais"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Turma com mais alunos
            cursor.execute("""
                SELECT t.nome, t.serie, COUNT(a.id) as total_alunos
                FROM turmas t
                LEFT JOIN alunos a ON t.id = a.turma_id AND a.status = 'Ativo'
                GROUP BY t.id, t.nome, t.serie
                ORDER BY total_alunos DESC
                LIMIT 1
            """)
            turma_popular_row = cursor.fetchone()
            turma_popular = f"{turma_popular_row[0]} - {turma_popular_row[1]} ({turma_popular_row[2]} alunos)" if turma_popular_row else "N/A"
            
            # Valor total em aberto
            cursor.execute("""
                SELECT COALESCE(SUM(p.valor_final), 0)
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                WHERE p.status IN ('Pendente', 'Atrasado')
                AND a.status = 'Ativo'
            """)
            valor_aberto = cursor.fetchone()[0]
            
            # Próximo vencimento
            cursor.execute("""
                SELECT MIN(p.data_vencimento)
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                WHERE p.status = 'Pendente'
                AND date(p.data_vencimento) >= date('now')
                AND a.status = 'Ativo'
            """)
            proximo_venc_row = cursor.fetchone()
            proximo_vencimento = format_date(proximo_venc_row[0]) if proximo_venc_row[0] else "N/A"
            
            # Meta mensal (valor estimado baseado nas turmas)
            cursor.execute("""
                SELECT COALESCE(SUM(t.valor_mensalidade), 0)
                FROM turmas t
                INNER JOIN alunos a ON t.id = a.turma_id
                WHERE a.status = 'Ativo'
            """)
            meta_mensal = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'turma_popular': turma_popular,
                'valor_aberto': valor_aberto,
                'proximo_vencimento': proximo_vencimento,
                'meta_mensal': meta_mensal
            }
            
        except Exception as e:
            conn.close()
            print(f"Erro ao obter resumos: {e}")
            return {
                'turma_popular': 'N/A',
                'valor_aberto': 0,
                'proximo_vencimento': 'N/A',
                'meta_mensal': 0
            }
