from database.connection import db
import sqlite3
from datetime import datetime, date, timedelta
import calendar

class MensalidadeService:
    def __init__(self):
        self.db = db
    
    def gerar_mensalidades_aluno(self, aluno_id):
        """Gera mensalidades para um aluno específico"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Buscar dados do aluno e turma
            cursor.execute("""
                SELECT a.nome, t.valor_mensalidade, t.dia_vencimento
                FROM alunos a
                INNER JOIN turmas t ON a.turma_id = t.id
                WHERE a.id = ?
            """, (aluno_id,))
            
            aluno_row = cursor.fetchone()
            if not aluno_row:
                return {'success': False, 'error': 'Aluno não encontrado'}
            
            nome_aluno, valor_mensalidade, dia_vencimento = aluno_row
            
            # Verificar se já existem mensalidades
            cursor.execute("SELECT COUNT(*) FROM pagamentos WHERE aluno_id = ?", (aluno_id,))
            mensalidades_existentes = cursor.fetchone()[0]
            
            if mensalidades_existentes > 0:
                return {'success': True, 'message': 'Mensalidades já existem'}
            
            # Gerar mensalidades para os próximos 12 meses
            hoje = date.today()
            ano_atual = hoje.year
            mes_atual = hoje.month
            
            mensalidades_criadas = 0
            
            for i in range(12):
                # Calcular mês e ano
                mes = mes_atual + i
                ano = ano_atual
                
                if mes > 12:
                    mes = mes - 12
                    ano = ano_atual + 1
                
                # Calcular data de vencimento
                try:
                    data_vencimento = date(ano, mes, dia_vencimento)
                except ValueError:
                    # Se o dia não existe no mês (ex: 31/02), usar último dia do mês
                    ultimo_dia = calendar.monthrange(ano, mes)[1]
                    data_vencimento = date(ano, mes, min(dia_vencimento, ultimo_dia))
                
                # Criar registro de pagamento
                mes_referencia = f"{ano}-{mes:02d}"
                
                cursor.execute("""
                    INSERT INTO pagamentos 
                    (aluno_id, mes_referencia, valor_original, valor_final, data_vencimento, status)
                    VALUES (?, ?, ?, ?, ?, 'Pendente')
                """, (aluno_id, mes_referencia, valor_mensalidade, valor_mensalidade, data_vencimento))
                
                mensalidades_criadas += 1
            
            conn.commit()
            conn.close()
            
            return {
                'success': True, 
                'mensalidades_criadas': mensalidades_criadas,
                'aluno': nome_aluno
            }
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return {'success': False, 'error': str(e)}
    
    def gerar_mensalidades_todas_turmas(self):
        """Gera mensalidades para todos os alunos ativos"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM alunos WHERE status = 'Ativo'")
        alunos_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        total_sucesso = 0
        total_erro = 0
        
        for aluno_id in alunos_ids:
            resultado = self.gerar_mensalidades_aluno(aluno_id)
            if resultado['success']:
                total_sucesso += 1
            else:
                total_erro += 1
        
        return {
            'success': True,
            'total_alunos': len(alunos_ids),
            'total_sucesso': total_sucesso,
            'total_erro': total_erro
        }
