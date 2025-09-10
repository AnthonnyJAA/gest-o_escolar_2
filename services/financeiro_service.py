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
            LEFT JOIN responsaveis rf ON a.id = rf.aluno_id AND rf.principal = 1
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
    
    def buscar_mensalidade_por_id(self, mensalidade_id):
        """Busca mensalidade completa por ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.*, a.nome as aluno_nome 
            FROM pagamentos p
            INNER JOIN alunos a ON p.aluno_id = a.id
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
                'observacoes': row[11] if len(row) > 11 else '',
                'aluno_nome': row[-1]
            }
        return None
    
    def processar_pagamento(self, dados_pagamento):
        """Processa pagamento com desconto e multa aplicados na hora"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Converter data de pagamento
            data_pagamento_str = dados_pagamento['data_pagamento']
            try:
                data_pagamento = datetime.strptime(data_pagamento_str, '%d/%m/%Y').strftime('%Y-%m-%d')
            except:
                data_pagamento = date.today().strftime('%Y-%m-%d')
            
            # Atualizar pagamento
            cursor.execute("""
                UPDATE pagamentos 
                SET desconto_aplicado = ?, multa_aplicada = ?, valor_final = ?,
                    data_pagamento = ?, status = 'Pago', observacoes = ?
                WHERE id = ?
            """, (
                dados_pagamento['desconto_aplicado'],
                dados_pagamento['multa_aplicada'],
                dados_pagamento['valor_final'],
                data_pagamento,
                dados_pagamento.get('observacoes', ''),
                dados_pagamento['mensalidade_id']
            ))
            
            conn.commit()
            conn.close()
            
            return {'success': True}
            
        except Exception as e:
            conn.rollback()
            conn.close()
            return {'success': False, 'error': str(e)}
    
    def registrar_pagamento(self, pagamento_id, data_pagamento, valor_pago=None, desconto=0, multa=0, observacoes=""):
        """Registra pagamento simples (método legacy)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Buscar dados do pagamento
            cursor.execute("SELECT valor_original FROM pagamentos WHERE id = ?", (pagamento_id,))
            row = cursor.fetchone()
            if not row:
                return {'success': False, 'error': 'Mensalidade não encontrada'}
            
            valor_original = row[0]
            valor_final = valor_pago if valor_pago is not None else valor_original
            
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
            """, (data_pagamento, valor_final, desconto, multa, observacoes, pagamento_id))
            
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
        
        try:
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
            
            conn.close()
            
            return {
                'receita_periodo': receita_periodo or 0,
                'receita_mes': receita_periodo or 0,
                'total_pagos': contadores[0] or 0,
                'total_pendentes': contadores[1] or 0, 
                'total_atrasados': contadores[2] or 0,
                'total_inadimplentes': contadores[2] or 0,
                'total_mensalidades': contadores[3] or 0,
                'valor_pendente': valores[0] or 0,
                'valor_atraso': valores[1] or 0,
                'valor_em_atraso': valores[1] or 0,
                'receitas_diarias': []
            }
            
        except Exception as e:
            conn.close()
            print(f"Erro ao obter estatísticas financeiras: {e}")
            return {
                'receita_periodo': 0, 'receita_mes': 0, 'total_pagos': 0,
                'total_pendentes': 0, 'total_atrasados': 0, 'total_inadimplentes': 0,
                'total_mensalidades': 0, 'valor_pendente': 0, 'valor_atraso': 0,
                'valor_em_atraso': 0, 'receitas_diarias': []
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
            LEFT JOIN responsaveis rf ON a.id = rf.aluno_id AND rf.principal = 1
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
    
    def obter_resumo_financeiro_periodo(self, data_inicio=None, data_fim=None):
        """Obtém resumo financeiro de um período específico"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            where_clause = "WHERE 1=1"
            params = []
            
            if data_inicio and data_fim:
                where_clause += " AND p.data_vencimento BETWEEN ? AND ?"
                params.extend([data_inicio, data_fim])
            
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_mensalidades,
                    COUNT(CASE WHEN p.status = 'Pago' THEN 1 END) as pagas,
                    COUNT(CASE WHEN p.status = 'Pendente' THEN 1 END) as pendentes,
                    COUNT(CASE WHEN p.status = 'Atrasado' THEN 1 END) as atrasadas,
                    SUM(p.valor_original) as valor_total_original,
                    SUM(CASE WHEN p.status = 'Pago' THEN p.valor_final ELSE 0 END) as valor_recebido,
                    SUM(CASE WHEN p.status != 'Pago' THEN p.valor_final ELSE 0 END) as valor_pendente,
                    SUM(p.desconto_aplicado) as total_descontos,
                    SUM(p.multa_aplicada) as total_multas
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                {where_clause}
                AND a.status = 'Ativo'
            """, params)
            
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado:
                return {
                    'total_mensalidades': resultado[0] or 0,
                    'pagas': resultado[1] or 0,
                    'pendentes': resultado[2] or 0,
                    'atrasadas': resultado[3] or 0,
                    'valor_total_original': resultado[4] or 0,
                    'valor_recebido': resultado[5] or 0,
                    'valor_pendente': resultado[6] or 0,
                    'total_descontos': resultado[7] or 0,
                    'total_multas': resultado[8] or 0
                }
            
            return {
                'total_mensalidades': 0, 'pagas': 0, 'pendentes': 0, 'atrasadas': 0,
                'valor_total_original': 0, 'valor_recebido': 0, 'valor_pendente': 0,
                'total_descontos': 0, 'total_multas': 0
            }
            
        except Exception as e:
            conn.close()
            print(f"Erro ao obter resumo financeiro: {e}")
            return None
    
    def gerar_relatorio_mensal(self, mes, ano):
        """Gera relatório financeiro mensal detalhado"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            mes_referencia = f"{ano}-{mes:02d}"
            
            cursor.execute("""
                SELECT 
                    a.nome as aluno_nome,
                    t.nome as turma_nome,
                    p.valor_original,
                    p.desconto_aplicado,
                    p.multa_aplicada,
                    p.valor_final,
                    p.data_vencimento,
                    p.data_pagamento,
                    p.status,
                    rf.nome as responsavel_nome
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                INNER JOIN turmas t ON a.turma_id = t.id
                LEFT JOIN responsaveis rf ON a.id = rf.aluno_id AND rf.principal = 1
                WHERE p.mes_referencia = ?
                AND a.status = 'Ativo'
                ORDER BY t.nome, a.nome
            """, (mes_referencia,))
            
            mensalidades = []
            for row in cursor.fetchall():
                mensalidades.append({
                    'aluno_nome': row[0],
                    'turma_nome': row[1],
                    'valor_original': row[2],
                    'desconto_aplicado': row[3] or 0,
                    'multa_aplicada': row[4] or 0,
                    'valor_final': row[5],
                    'data_vencimento': row[6],
                    'data_pagamento': row[7],
                    'status': row[8],
                    'responsavel_nome': row[9] or 'N/I'
                })
            
            conn.close()
            return mensalidades
            
        except Exception as e:
            conn.close()
            print(f"Erro ao gerar relatório mensal: {e}")
            return []
