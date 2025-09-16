from database.connection import db
import sqlite3
from datetime import datetime, date, timedelta
import calendar

class FinanceiroService:
    def __init__(self):
        self.db = db
        self.init_enhanced_payment_tables()

    def init_enhanced_payment_tables(self):
        """Inicializa tabelas com novos campos de pagamento"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Adicionar novos campos à tabela de pagamentos
            new_columns = [
                ("multa_aplicada", "DECIMAL(10,2) DEFAULT 0"),
                ("outros", "DECIMAL(10,2) DEFAULT 0"),
                ("observacoes_pagamento", "TEXT"),
                ("detalhes_outros", "TEXT")
            ]
            
            for column_name, column_def in new_columns:
                try:
                    cursor.execute(f"ALTER TABLE pagamentos ADD COLUMN {column_name} {column_def}")
                    print(f"✅ Campo {column_name} adicionado")
                except sqlite3.OperationalError:
                    # Campo já existe
                    pass
            
            # Criar trigger para atualizar valor_final automaticamente
            cursor.execute("""
                DROP TRIGGER IF EXISTS update_valor_final
            """)
            
            cursor.execute("""
                CREATE TRIGGER update_valor_final
                AFTER UPDATE OF valor_original, desconto_aplicado, multa_aplicada, outros
                ON pagamentos
                FOR EACH ROW
                BEGIN
                    UPDATE pagamentos 
                    SET valor_final = NEW.valor_original - NEW.desconto_aplicado + NEW.multa_aplicada + NEW.outros
                    WHERE id = NEW.id;
                END
            """)
            
            conn.commit()
            conn.close()
            print("✅ Tabelas de pagamento atualizadas com nova lógica")
            
        except sqlite3.Error as e:
            conn.close()
            print(f"❌ Erro ao atualizar tabelas: {e}")

    def obter_pagamentos_aluno(self, aluno_id):
        """Obtém todos os pagamentos de um aluno com detalhamento"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT p.id, p.mes_referencia, p.valor_original, p.desconto_aplicado,
                       p.multa_aplicada, p.outros, p.valor_final, p.data_vencimento,
                       p.data_pagamento, p.status, p.observacoes_pagamento, p.detalhes_outros,
                       a.nome as aluno_nome, t.nome as turma_nome
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                INNER JOIN turmas t ON a.turma_id = t.id
                WHERE p.aluno_id = ?
                ORDER BY p.data_vencimento DESC
            """, (aluno_id,))
            
            pagamentos = []
            for row in cursor.fetchall():
                pagamento = {
                    'id': row[0],
                    'mes_referencia': row[1],
                    'valor_original': float(row[2]) if row[2] else 0.0,
                    'desconto_aplicado': float(row[3]) if row[3] else 0.0,
                    'multa_aplicada': float(row[4]) if row[4] else 0.0,
                    'outros': float(row[5]) if row[5] else 0.0,
                    'valor_final': float(row[6]) if row[6] else 0.0,
                    'data_vencimento': row[7],
                    'data_pagamento': row[8],
                    'status': row[9],
                    'observacoes_pagamento': row[10],
                    'detalhes_outros': row[11],
                    'aluno_nome': row[12],
                    'turma_nome': row[13]
                }
                pagamentos.append(pagamento)
            
            conn.close()
            return pagamentos
            
        except sqlite3.Error as e:
            conn.close()
            print(f"❌ Erro ao obter pagamentos: {e}")
            return []

    def calcular_valor_final(self, valor_original, desconto=0, multa=0, outros=0):
        """Calcula o valor final baseado na nova lógica"""
        valor_final = valor_original - desconto + multa + outros
        return max(0, valor_final)  # Não permite valores negativos

    def processar_pagamento_avancado(self, pagamento_id, valor_original, desconto=0, 
                                   multa=0, outros=0, observacoes="", detalhes_outros=""):
        """Processa pagamento com a nova lógica avançada"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            conn.execute("BEGIN TRANSACTION")
            
            # Calcular valor final
            valor_final = self.calcular_valor_final(valor_original, desconto, multa, outros)
            
            # Atualizar pagamento
            cursor.execute("""
                UPDATE pagamentos 
                SET valor_original = ?,
                    desconto_aplicado = ?,
                    multa_aplicada = ?,
                    outros = ?,
                    valor_final = ?,
                    observacoes_pagamento = ?,
                    detalhes_outros = ?,
                    data_pagamento = ?,
                    status = 'Pago'
                WHERE id = ?
            """, (valor_original, desconto, multa, outros, valor_final, 
                  observacoes, detalhes_outros, datetime.now().strftime('%Y-%m-%d'), pagamento_id))
            
            if cursor.rowcount == 0:
                conn.rollback()
                conn.close()
                return {'success': False, 'error': 'Pagamento não encontrado'}
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'valor_original': valor_original,
                'desconto': desconto,
                'multa': multa,
                'outros': outros,
                'valor_final': valor_final
            }
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return {'success': False, 'error': f'Erro ao processar pagamento: {str(e)}'}

    def obter_detalhes_pagamento(self, pagamento_id):
        """Obtém detalhes completos de um pagamento"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT p.id, p.mes_referencia, p.valor_original, p.desconto_aplicado,
                       p.multa_aplicada, p.outros, p.valor_final, p.data_vencimento,
                       p.data_pagamento, p.status, p.observacoes_pagamento, p.detalhes_outros,
                       a.nome as aluno_nome, a.id as aluno_id,
                       t.nome as turma_nome, t.serie
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                INNER JOIN turmas t ON a.turma_id = t.id
                WHERE p.id = ?
            """, (pagamento_id,))
            
            row = cursor.fetchone()
            if not row:
                conn.close()
                return None
            
            pagamento = {
                'id': row[0],
                'mes_referencia': row[1],
                'valor_original': float(row[2]) if row[2] else 0.0,
                'desconto_aplicado': float(row[3]) if row[3] else 0.0,
                'multa_aplicada': float(row[4]) if row[4] else 0.0,
                'outros': float(row[5]) if row[5] else 0.0,
                'valor_final': float(row[6]) if row[6] else 0.0,
                'data_vencimento': row[7],
                'data_pagamento': row[8],
                'status': row[9],
                'observacoes_pagamento': row[10] or '',
                'detalhes_outros': row[11] or '',
                'aluno_nome': row[12],
                'aluno_id': row[13],
                'turma_nome': row[14],
                'serie': row[15]
            }
            
            conn.close()
            return pagamento
            
        except sqlite3.Error as e:
            conn.close()
            print(f"❌ Erro ao obter detalhes do pagamento: {e}")
            return None

    def obter_pagamentos_pendentes(self):
        """Obtém lista de pagamentos pendentes com nova estrutura"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT p.id, a.nome as aluno_nome, t.nome as turma_nome, t.serie,
                       p.mes_referencia, p.valor_original, p.desconto_aplicado,
                       p.multa_aplicada, p.outros, p.valor_final, p.data_vencimento,
                       p.status,
                       CASE 
                           WHEN p.data_vencimento < date('now') THEN 'Atrasado'
                           ELSE p.status
                       END as status_atual
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                INNER JOIN turmas t ON a.turma_id = t.id
                WHERE p.status IN ('Pendente', 'Atrasado')
                ORDER BY p.data_vencimento ASC
            """)
            
            pagamentos = []
            for row in cursor.fetchall():
                pagamento = {
                    'id': row[0],
                    'aluno_nome': row[1],
                    'turma_nome': row[2],
                    'serie': row[3],
                    'mes_referencia': row[4],
                    'valor_original': float(row[5]) if row[5] else 0.0,
                    'desconto_aplicado': float(row[6]) if row[6] else 0.0,
                    'multa_aplicada': float(row[7]) if row[7] else 0.0,
                    'outros': float(row[8]) if row[8] else 0.0,
                    'valor_final': float(row[9]) if row[9] else 0.0,
                    'data_vencimento': row[10],
                    'status': row[11],
                    'status_atual': row[12]
                }
                pagamentos.append(pagamento)
            
            conn.close()
            return pagamentos
            
        except sqlite3.Error as e:
            conn.close()
            print(f"❌ Erro ao obter pagamentos pendentes: {e}")
            return []

    def obter_relatorio_financeiro_detalhado(self, filtros=None):
        """Gera relatório financeiro com nova estrutura de campos"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            sql = """
                SELECT 
                    a.nome as aluno_nome,
                    t.nome as turma_nome, 
                    t.serie,
                    p.mes_referencia,
                    p.valor_original,
                    p.desconto_aplicado,
                    p.multa_aplicada,
                    p.outros,
                    p.valor_final,
                    p.data_vencimento,
                    p.data_pagamento,
                    p.status,
                    p.observacoes_pagamento,
                    p.detalhes_outros,
                    CASE 
                        WHEN p.data_vencimento < date('now') AND p.status = 'Pendente' THEN 'Atrasado'
                        ELSE p.status
                    END as status_atual
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                INNER JOIN turmas t ON a.turma_id = t.id
                WHERE 1=1
            """
            
            params = []
            
            if filtros:
                if filtros.get('turma_id'):
                    sql += " AND t.id = ?"
                    params.append(filtros['turma_id'])
                
                if filtros.get('status'):
                    sql += " AND p.status = ?"
                    params.append(filtros['status'])
                    
                if filtros.get('mes_referencia'):
                    sql += " AND p.mes_referencia = ?"
                    params.append(filtros['mes_referencia'])
            
            sql += " ORDER BY p.data_vencimento DESC"
            
            cursor.execute(sql, params)
            
            relatorio = []
            for row in cursor.fetchall():
                item = {
                    'aluno_nome': row[0],
                    'turma_nome': row[1],
                    'serie': row[2],
                    'mes_referencia': row[3],
                    'valor_original': float(row[4]) if row[4] else 0.0,
                    'desconto_aplicado': float(row[5]) if row[5] else 0.0,
                    'multa_aplicada': float(row[6]) if row[6] else 0.0,
                    'outros': float(row[7]) if row[7] else 0.0,
                    'valor_final': float(row[8]) if row[8] else 0.0,
                    'data_vencimento': row[9],
                    'data_pagamento': row[10],
                    'status': row[11],
                    'observacoes_pagamento': row[12] or '',
                    'detalhes_outros': row[13] or '',
                    'status_atual': row[14]
                }
                relatorio.append(item)
            
            conn.close()
            return relatorio
            
        except sqlite3.Error as e:
            conn.close()
            print(f"❌ Erro ao gerar relatório: {e}")
            return []

    def obter_estatisticas_avancadas(self):
        """Obtém estatísticas financeiras detalhadas"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            stats = {}
            
            # Total de valores
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_pagamentos,
                    SUM(valor_original) as total_valor_original,
                    SUM(desconto_aplicado) as total_descontos,
                    SUM(multa_aplicada) as total_multas,
                    SUM(outros) as total_outros,
                    SUM(valor_final) as total_valor_final
                FROM pagamentos
                WHERE status = 'Pago'
            """)
            
            row = cursor.fetchone()
            if row:
                stats['pagamentos_realizados'] = {
                    'quantidade': row[0] or 0,
                    'valor_original': float(row[1]) if row[1] else 0.0,
                    'total_descontos': float(row[2]) if row[2] else 0.0,
                    'total_multas': float(row[3]) if row[3] else 0.0,
                    'total_outros': float(row[4]) if row[4] else 0.0,
                    'valor_final': float(row[5]) if row[5] else 0.0
                }
            
            # Pendentes
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_pendentes,
                    SUM(valor_final) as total_pendente
                FROM pagamentos
                WHERE status IN ('Pendente', 'Atrasado')
            """)
            
            row = cursor.fetchone()
            if row:
                stats['pagamentos_pendentes'] = {
                    'quantidade': row[0] or 0,
                    'valor_total': float(row[1]) if row[1] else 0.0
                }
            
            # Estatísticas por componente
            cursor.execute("""
                SELECT 
                    AVG(multa_aplicada) as multa_media,
                    MAX(multa_aplicada) as multa_maxima,
                    AVG(outros) as outros_medio,
                    MAX(outros) as outros_maximo,
                    AVG(desconto_aplicado) as desconto_medio
                FROM pagamentos
                WHERE status = 'Pago'
                AND (multa_aplicada > 0 OR outros > 0 OR desconto_aplicado > 0)
            """)
            
            row = cursor.fetchone()
            if row:
                stats['componentes'] = {
                    'multa_media': float(row[0]) if row[0] else 0.0,
                    'multa_maxima': float(row[1]) if row[1] else 0.0,
                    'outros_medio': float(row[2]) if row[2] else 0.0,
                    'outros_maximo': float(row[3]) if row[3] else 0.0,
                    'desconto_medio': float(row[4]) if row[4] else 0.0
                }
            
            conn.close()
            return stats
            
        except sqlite3.Error as e:
            conn.close()
            print(f"❌ Erro ao obter estatísticas: {e}")
            return {}

    def listar_turmas(self):
        """Lista turmas para filtros"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, nome, serie, ano_letivo,
                       (SELECT COUNT(*) FROM alunos WHERE turma_id = t.id) as total_alunos
                FROM turmas t
                ORDER BY ano_letivo, serie, nome
            """)
            
            turmas = []
            for row in cursor.fetchall():
                turma = {
                    'id': row[0],
                    'nome': row[1],
                    'serie': row[2],
                    'ano_letivo': row[3],
                    'total_alunos': row[4],
                    'display': f"{row[1]} - {row[2]} ({row[3]}) - {row[4]} aluno(s)"
                }
                turmas.append(turma)
            
            conn.close()
            return turmas
            
        except sqlite3.Error as e:
            conn.close()
            print(f"❌ Erro ao listar turmas: {e}")
            return []