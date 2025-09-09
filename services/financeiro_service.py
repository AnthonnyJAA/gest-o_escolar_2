from database.connection import db
import sqlite3
from datetime import datetime, date, timedelta
import calendar

class FinanceiroService:
    def __init__(self):
        self.db = db
    
    def listar_mensalidades(self, filtros=None):
        """Lista mensalidades com filtros opcionais"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        sql = """
            SELECT 
                p.id, p.aluno_id, a.nome as aluno_nome, t.nome as turma_nome, t.serie,
                p.mes_referencia, p.valor_original, p.desconto_aplicado, p.multa_aplicada,
                p.valor_final, p.data_vencimento, p.data_pagamento, p.status, p.observacoes,
                t.id as turma_id, rf.nome as responsavel_nome, rf.telefone as responsavel_telefone,
                CASE 
                    WHEN p.status = 'Pago' THEN p.valor_final
                    ELSE 0 
                END as valor_recebido
            FROM pagamentos p
            INNER JOIN alunos a ON p.aluno_id = a.id
            INNER JOIN turmas t ON a.turma_id = t.id
            LEFT JOIN responsaveis_financeiros rf ON a.id = rf.aluno_id AND rf.principal = 1
            WHERE 1=1
        """
        
        params = []
        
        # Aplicar filtros
        if filtros:
            if filtros.get('status') and filtros['status'] != 'Todos':
                sql += " AND p.status = ?"
                params.append(filtros['status'])
            
            if filtros.get('turma_id') and filtros['turma_id'] != 'Todas':
                sql += " AND t.id = ?"
                params.append(filtros['turma_id'])
            
            if filtros.get('mes_ano'):
                sql += " AND p.mes_referencia = ?"
                params.append(filtros['mes_ano'])
            
            if filtros.get('data_inicio') and filtros.get('data_fim'):
                sql += " AND p.data_vencimento BETWEEN ? AND ?"
                params.extend([filtros['data_inicio'], filtros['data_fim']])
        
        sql += " ORDER BY p.data_vencimento DESC, a.nome"
        
        cursor.execute(sql, params)
        
        mensalidades = []
        for row in cursor.fetchall():
            # Calcular status automático baseado na data
            status_calculado = self._calcular_status_automatico(row[10], row[11])  # data_venc, data_pag
            
            mensalidade = {
                'id': row[0],
                'aluno_id': row[1],
                'aluno_nome': row[2],
                'turma_nome': row[3],
                'turma_serie': row[4],
                'mes_referencia': row[5],
                'valor_original': row[6],
                'desconto_aplicado': row[7],
                'multa_aplicada': row[8],
                'valor_final': row[9],
                'data_vencimento': row[10],
                'data_pagamento': row[11],
                'status': row[12],
                'status_calculado': status_calculado,
                'observacoes': row[13] or '',
                'turma_id': row[14],
                'responsavel_nome': row[15] or 'N/I',
                'responsavel_telefone': row[16] or 'N/I',
                'valor_recebido': row[17]
            }
            mensalidades.append(mensalidade)
        
        conn.close()
        return mensalidades
    
    def _calcular_status_automatico(self, data_vencimento, data_pagamento):
        """Calcula status baseado nas datas"""
        if data_pagamento:
            return 'Pago'
        
        if not data_vencimento:
            return 'Pendente'
        
        try:
            vencimento = datetime.strptime(data_vencimento, '%Y-%m-%d').date()
            hoje = date.today()
            
            if vencimento < hoje:
                return 'Atrasado'
            else:
                return 'Pendente'
        except:
            return 'Pendente'
    
    def registrar_pagamento(self, pagamento_id, data_pagamento, valor_pago, desconto=0, multa=0, observacoes=""):
        """Registra pagamento manualmente"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Calcular valor final
            cursor.execute("SELECT valor_original FROM pagamentos WHERE id = ?", (pagamento_id,))
            row = cursor.fetchone()
            if not row:
                return {'success': False, 'error': 'Mensalidade não encontrada'}
            
            valor_original = row[0]
            valor_final = valor_original - desconto + multa
            
            if valor_pago is None:
                valor_pago = valor_final
            
            # Atualizar pagamento
            cursor.execute("""
                UPDATE pagamentos SET
                    data_pagamento = ?,
                    valor_final = ?,
                    desconto_aplicado = ?,
                    multa_aplicada = ?,
                    status = 'Pago',
                    observacoes = ?
                WHERE id = ?
            """, (data_pagamento, valor_pago, desconto, multa, observacoes, pagamento_id))
            
            conn.commit()
            conn.close()
            return {'success': True}
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return {'success': False, 'error': str(e)}
    
    def cancelar_pagamento(self, pagamento_id):
        """Cancela um pagamento"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE pagamentos SET
                    data_pagamento = NULL,
                    desconto_aplicado = 0,
                    multa_aplicada = 0,
                    status = 'Pendente',
                    observacoes = ''
                WHERE id = ?
            """, (pagamento_id,))
            
            # Recalcular valor final baseado no valor original
            cursor.execute("""
                UPDATE pagamentos SET
                    valor_final = valor_original
                WHERE id = ?
            """, (pagamento_id,))
            
            conn.commit()
            conn.close()
            return {'success': True}
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return {'success': False, 'error': str(e)}
    
    def obter_estatisticas_financeiras(self, periodo=None):
        """Obtém estatísticas financeiras por período"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Base das queries
        base_where = "WHERE p.status = 'Pago'"
        params = []
        
        if periodo:
            if periodo['tipo'] == 'dia':
                base_where += " AND date(p.data_pagamento) = ?"
                params.append(periodo['data'])
            elif periodo['tipo'] == 'mes':
                base_where += " AND strftime('%Y-%m', p.data_pagamento) = ?"
                params.append(periodo['mes_ano'])
            elif periodo['tipo'] == 'ano':
                base_where += " AND strftime('%Y', p.data_pagamento) = ?"
                params.append(str(periodo['ano']))
        
        # Receita do período (corrigir para receita do mês atual se não especificado)
        if not periodo:
            mes_atual = date.today().strftime('%Y-%m')
            base_where += " AND strftime('%Y-%m', p.data_pagamento) = ?"
            params.append(mes_atual)
        
        cursor.execute(f"""
            SELECT COALESCE(SUM(p.valor_final), 0) as receita
            FROM pagamentos p {base_where}
        """, params)
        receita_periodo = cursor.fetchone()[0]
        
        # Contadores por status
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN status = 'Pago' THEN 1 ELSE 0 END) as pagos,
                SUM(CASE WHEN status = 'Pendente' THEN 1 ELSE 0 END) as pendentes,
                SUM(CASE WHEN status = 'Atrasado' OR (status = 'Pendente' AND date(data_vencimento) < date('now')) THEN 1 ELSE 0 END) as atrasados,
                COUNT(*) as total
            FROM pagamentos p
            INNER JOIN alunos a ON p.aluno_id = a.id
            WHERE a.status = 'Ativo'
        """)
        contadores = cursor.fetchone()
        
        # Valores pendentes e em atraso
        cursor.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN p.status = 'Pendente' THEN p.valor_final ELSE 0 END), 0) as valor_pendente,
                COALESCE(SUM(CASE WHEN p.status = 'Atrasado' OR (p.status = 'Pendente' AND date(p.data_vencimento) < date('now')) THEN p.valor_final ELSE 0 END), 0) as valor_atraso
            FROM pagamentos p
            INNER JOIN alunos a ON p.aluno_id = a.id
            WHERE a.status = 'Ativo'
        """)
        valores = cursor.fetchone()
        
        # Receita por dia dos últimos 30 dias (para gráfico)
        cursor.execute("""
            SELECT 
                date(p.data_pagamento) as data,
                SUM(p.valor_final) as valor
            FROM pagamentos p
            WHERE p.status = 'Pago' 
            AND date(p.data_pagamento) >= date('now', '-30 days')
            GROUP BY date(p.data_pagamento)
            ORDER BY data
        """)
        receitas_diarias = cursor.fetchall()
        
        conn.close()
        
        return {
            'receita_periodo': receita_periodo or 0,
            'receita_mes': receita_periodo or 0,  # Adicionar para compatibilidade
            'total_pagos': contadores[0] or 0,
            'total_pendentes': contadores[1] or 0, 
            'total_atrasados': contadores[2] or 0,
            'total_inadimplentes': contadores[2] or 0,  # Alias para dashboard
            'total_mensalidades': contadores[3] or 0,
            'valor_pendente': valores[0] or 0,
            'valor_atraso': valores[1] or 0,
            'valor_em_atraso': valores[1] or 0,  # Alias para dashboard
            'receitas_diarias': [{'data': r[0], 'valor': r[1]} for r in receitas_diarias]
        }
    
    def listar_turmas(self):
        """Lista turmas para filtros"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, nome, serie FROM turmas ORDER BY nome")
        turmas = []
        for row in cursor.fetchall():
            turmas.append({
                'id': row[0],
                'nome': row[1],
                'serie': row[2],
                'display': f"{row[1]} - {row[2]}"
            })
        
        conn.close()
        return turmas
    
    def buscar_inadimplentes(self):
        """Busca alunos com mensalidades em atraso"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                a.id, a.nome as aluno_nome, t.nome as turma_nome,
                COUNT(p.id) as mensalidades_atrasadas,
                SUM(p.valor_final) as valor_total_devido,
                MIN(p.data_vencimento) as primeira_pendencia,
                rf.nome as responsavel_nome, rf.telefone as responsavel_telefone
            FROM alunos a
            INNER JOIN turmas t ON a.turma_id = t.id
            INNER JOIN pagamentos p ON a.id = p.aluno_id
            LEFT JOIN responsaveis_financeiros rf ON a.id = rf.aluno_id AND rf.principal = 1
            WHERE (p.status = 'Atrasado' OR (p.status = 'Pendente' AND date(p.data_vencimento) < date('now')))
            AND a.status = 'Ativo'
            GROUP BY a.id, a.nome, t.nome, rf.nome, rf.telefone
            ORDER BY primeira_pendencia ASC, valor_total_devido DESC
        """)
        
        inadimplentes = []
        for row in cursor.fetchall():
            inadimplente = {
                'aluno_id': row[0],
                'aluno_nome': row[1],
                'turma_nome': row[2],
                'mensalidades_atrasadas': row[3],
                'valor_total_devido': row[4],
                'primeira_pendencia': row[5],
                'responsavel_nome': row[6] or 'N/I',
                'responsavel_telefone': row[7] or 'N/I'
            }
            inadimplentes.append(inadimplente)
        
        conn.close()
        return inadimplentes
    
    def atualizar_status_automatico(self):
        """Atualiza status das mensalidades baseado na data atual"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Atualizar mensalidades vencidas para "Atrasado"
            cursor.execute("""
                UPDATE pagamentos 
                SET status = 'Atrasado'
                WHERE status = 'Pendente' 
                AND date(data_vencimento) < date('now')
            """)
            
            conn.commit()
            conn.close()
            return {'success': True}
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return {'success': False, 'error': str(e)}
    
    def obter_fluxo_caixa_mensal(self, ano=None):
        """Obtém fluxo de caixa mensal"""
        if not ano:
            ano = date.today().year
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                strftime('%m', p.data_pagamento) as mes,
                SUM(p.valor_final) as receita
            FROM pagamentos p
            WHERE p.status = 'Pago' 
            AND strftime('%Y', p.data_pagamento) = ?
            GROUP BY strftime('%m', p.data_pagamento)
            ORDER BY mes
        """, (str(ano),))
        
        fluxo = {}
        for row in cursor.fetchall():
            mes_num = int(row[0])
            fluxo[mes_num] = row[1]
        
        # Preencher meses sem dados com 0
        meses_nome = ['', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                      'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        resultado = []
        for i in range(1, 13):
            resultado.append({
                'mes': i,
                'mes_nome': meses_nome[i],
                'receita': fluxo.get(i, 0)
            })
        
        conn.close()
        return resultado
    
    def gerar_mensalidades_aluno(self, aluno_id):
        """Gera mensalidades para um aluno"""
        try:
            from services.mensalidade_service import MensalidadeService
            mensalidade_service = MensalidadeService()
            return mensalidade_service.gerar_mensalidades_aluno(aluno_id)
        except Exception as e:
            return {'success': False, 'error': str(e)}
