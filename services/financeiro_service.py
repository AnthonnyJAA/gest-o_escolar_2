from database.connection import db
import sqlite3
from datetime import datetime, date, timedelta
from utils.formatters import format_currency, format_date

class FinanceiroService:
    def __init__(self):
        self.db = db

    def listar_mensalidades(self, status_filtro=None, mes_filtro=None):
        """Lista mensalidades com filtros CORRIGIDO"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Query base corrigida
            sql = """
                SELECT 
                    p.id,
                    p.aluno_id,
                    a.nome as aluno_nome,
                    t.nome as turma_nome,
                    t.serie as turma_serie,
                    p.mes_referencia,
                    p.valor_original,
                    p.desconto_aplicado,
                    p.multa_aplicada,
                    p.valor_final,
                    p.data_vencimento,
                    p.data_pagamento,
                    p.status,
                    p.observacoes
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                INNER JOIN turmas t ON a.turma_id = t.id
                WHERE a.status = 'Ativo'
            """
            
            params = []
            
            # Aplicar filtros
            if status_filtro and status_filtro != "Todos":
                if status_filtro == "Atrasado":
                    sql += """ AND (p.status = 'Atrasado' OR 
                                  (p.status = 'Pendente' AND date(p.data_vencimento) < date('now')))"""
                else:
                    sql += " AND p.status = ?"
                    params.append(status_filtro)
            
            if mes_filtro and mes_filtro != "Todos":
                sql += " AND strftime('%m', p.data_vencimento) = ?"
                params.append(mes_filtro)
            
            sql += " ORDER BY p.data_vencimento DESC, a.nome"
            
            cursor.execute(sql, params)
            
            mensalidades = []
            for row in cursor.fetchall():
                # Determinar status real (considerar atrasos)
                status_real = self._determinar_status_real(row[12], row[10])
                
                mensalidade = {
                    'id': row[0],
                    'aluno_id': row[1],
                    'aluno_nome': row[2],
                    'turma_nome': f"{row[3]} - {row[4]}",
                    'mes_referencia': row[5],
                    'valor_original': row[6],
                    'desconto_aplicado': row[7] or 0,
                    'multa_aplicada': row[8] or 0,
                    'valor_final': row[9],
                    'data_vencimento': row[10],
                    'data_pagamento': row[11],
                    'status': status_real,
                    'observacoes': row[13] or ''
                }
                mensalidades.append(mensalidade)
            
            conn.close()
            print(f"✅ {len(mensalidades)} mensalidades carregadas")
            return mensalidades
            
        except sqlite3.Error as e:
            conn.close()
            print(f"❌ Erro ao listar mensalidades: {e}")
            return []

    def _determinar_status_real(self, status_bd, data_vencimento):
        """Determina o status real considerando atrasos"""
        try:
            if status_bd == 'Pago':
                return 'Pago'
            
            if data_vencimento:
                if isinstance(data_vencimento, str):
                    venc_date = datetime.strptime(data_vencimento, '%Y-%m-%d').date()
                else:
                    venc_date = data_vencimento
                
                hoje = date.today()
                
                if venc_date < hoje:
                    return 'Atrasado'
                else:
                    return 'Pendente'
            else:
                return status_bd
                
        except:
            return status_bd or 'Pendente'

    def processar_pagamento(self, pagamento_id, valor_final, desconto, multa, observacoes):
        """Processa pagamento de mensalidade CORRIGIDO"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Buscar mensalidade atual
            cursor.execute("SELECT * FROM pagamentos WHERE id = ?", (pagamento_id,))
            mensalidade = cursor.fetchone()
            
            if not mensalidade:
                return {'success': False, 'error': 'Mensalidade não encontrada'}
            
            if mensalidade[12] == 'Pago':  # status
                return {'success': False, 'error': 'Mensalidade já foi paga'}
            
            # Atualizar pagamento
            data_pagamento = date.today().strftime('%Y-%m-%d')
            
            cursor.execute("""
                UPDATE pagamentos 
                SET desconto_aplicado = ?, multa_aplicada = ?, valor_final = ?,
                    data_pagamento = ?, status = 'Pago', observacoes = ?
                WHERE id = ?
            """, (desconto, multa, valor_final, data_pagamento, observacoes, pagamento_id))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Pagamento processado: ID {pagamento_id}, Valor: R$ {valor_final:.2f}")
            return {'success': True}
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            print(f"❌ Erro ao processar pagamento: {e}")
            return {'success': False, 'error': str(e)}

    def obter_mensalidade_por_id(self, mensalidade_id):
        """Obtém mensalidade específica por ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    p.*,
                    a.nome as aluno_nome,
                    t.nome as turma_nome,
                    t.serie as turma_serie
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                INNER JOIN turmas t ON a.turma_id = t.id
                WHERE p.id = ?
            """, (mensalidade_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'aluno_id': row[1],
                    'mes_referencia': row[2],
                    'valor_original': row[3],
                    'desconto_aplicado': row[4] or 0,
                    'multa_aplicada': row[5] or 0,
                    'valor_final': row[6],
                    'data_vencimento': row[7],
                    'data_pagamento': row[8],
                    'status': row[9],
                    'observacoes': row[11] or '',
                    'aluno_nome': row[13],
                    'turma_nome': f"{row[14]} - {row[15]}"
                }
            else:
                return None
                
        except sqlite3.Error as e:
            conn.close()
            print(f"❌ Erro ao obter mensalidade: {e}")
            return None

    def obter_estatisticas_financeiras(self):
        """Obtém estatísticas financeiras"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Total de mensalidades por status
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN status = 'Pago' THEN 1 END) as pagas,
                    COUNT(CASE WHEN status = 'Pendente' THEN 1 END) as pendentes,
                    COUNT(CASE WHEN status = 'Atrasado' OR (status = 'Pendente' AND date(data_vencimento) < date('now')) THEN 1 END) as atrasadas,
                    SUM(CASE WHEN status = 'Pago' THEN valor_final ELSE 0 END) as receita_total,
                    SUM(CASE WHEN status != 'Pago' THEN valor_final ELSE 0 END) as valor_pendente
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                WHERE a.status = 'Ativo'
            """)
            
            row = cursor.fetchone()
            
            stats = {
                'pagas': row[0] or 0,
                'pendentes': row[1] or 0,
                'atrasadas': row[2] or 0,
                'receita_total': row[3] or 0,
                'valor_pendente': row[4] or 0
            }
            
            conn.close()
            return stats
            
        except sqlite3.Error as e:
            conn.close()
            print(f"❌ Erro ao obter estatísticas: {e}")
            return {
                'pagas': 0, 'pendentes': 0, 'atrasadas': 0,
                'receita_total': 0, 'valor_pendente': 0
            }

    def gerar_relatorio_financeiro(self, data_inicio=None, data_fim=None):
        """Gera relatório financeiro por período"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            sql = """
                SELECT 
                    a.nome as aluno_nome,
                    t.nome as turma_nome,
                    p.mes_referencia,
                    p.valor_original,
                    p.desconto_aplicado,
                    p.multa_aplicada,
                    p.valor_final,
                    p.data_vencimento,
                    p.data_pagamento,
                    p.status
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                INNER JOIN turmas t ON a.turma_id = t.id
                WHERE a.status = 'Ativo'
            """
            
            params = []
            
            if data_inicio:
                sql += " AND date(p.data_vencimento) >= ?"
                params.append(data_inicio)
            
            if data_fim:
                sql += " AND date(p.data_vencimento) <= ?"
                params.append(data_fim)
            
            sql += " ORDER BY p.data_vencimento DESC"
            
            cursor.execute(sql, params)
            
            relatorio = []
            for row in cursor.fetchall():
                item = {
                    'aluno_nome': row[0],
                    'turma_nome': row[1],
                    'mes_referencia': row[2],
                    'valor_original': row[3],
                    'desconto_aplicado': row[4] or 0,
                    'multa_aplicada': row[5] or 0,
                    'valor_final': row[6],
                    'data_vencimento': row[7],
                    'data_pagamento': row[8],
                    'status': row[9]
                }
                relatorio.append(item)
            
            conn.close()
            return relatorio
            
        except sqlite3.Error as e:
            conn.close()
            print(f"❌ Erro ao gerar relatório: {e}")
            return []

    def buscar_mensalidades_aluno(self, aluno_id):
        """Busca mensalidades específicas de um aluno"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    p.*,
                    a.nome as aluno_nome,
                    t.nome as turma_nome,
                    t.serie as turma_serie
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                INNER JOIN turmas t ON a.turma_id = t.id
                WHERE p.aluno_id = ?
                ORDER BY p.data_vencimento DESC
            """, (aluno_id,))
            
            mensalidades = []
            for row in cursor.fetchall():
                mensalidade = {
                    'id': row[0],
                    'aluno_id': row[1],
                    'mes_referencia': row[2],
                    'valor_original': row[3],
                    'desconto_aplicado': row[4] or 0,
                    'multa_aplicada': row[5] or 0,
                    'valor_final': row[6],
                    'data_vencimento': row[7],
                    'data_pagamento': row[8],
                    'status': row[9],
                    'observacoes': row[11] or '',
                    'aluno_nome': row[13],
                    'turma_nome': f"{row[14]} - {row[15]}"
                }
                mensalidades.append(mensalidade)
            
            conn.close()
            return mensalidades
            
        except sqlite3.Error as e:
            conn.close()
            print(f"❌ Erro ao buscar mensalidades do aluno: {e}")
            return []
