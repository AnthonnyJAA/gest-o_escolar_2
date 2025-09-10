from database.connection import db
import sqlite3
from datetime import datetime, date, timedelta
import calendar

class MensalidadeService:
    def __init__(self):
        self.db = db
    
    def gerar_mensalidades_aluno(self, aluno_id):
        """Gera mensalidades APENAS a partir do mês da matrícula (sem retroativas)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Buscar dados do aluno (incluindo dados financeiros)
            cursor.execute("""
                SELECT a.nome, a.valor_mensalidade, t.ano_letivo, a.data_matricula
                FROM alunos a
                INNER JOIN turmas t ON a.turma_id = t.id
                WHERE a.id = ?
            """, (aluno_id,))
            
            aluno_row = cursor.fetchone()
            if not aluno_row:
                return {'success': False, 'error': 'Aluno não encontrado'}
            
            nome_aluno, valor_mensalidade, ano_letivo, data_matricula = aluno_row
            
            # Verificar se já existem mensalidades
            cursor.execute("SELECT COUNT(*) FROM pagamentos WHERE aluno_id = ?", (aluno_id,))
            mensalidades_existentes = cursor.fetchone()[0]
            
            if mensalidades_existentes > 0:
                return {'success': True, 'message': 'Mensalidades já existem'}
            
            # Data da matrícula
            if isinstance(data_matricula, str):
                try:
                    data_mat = datetime.strptime(data_matricula, '%Y-%m-%d').date()
                except:
                    data_mat = date.today()
            else:
                data_mat = data_matricula or date.today()
            
            mes_matricula = data_mat.month
            ano_matricula = data_mat.year
            
            # Usar ano letivo da turma ou ano da matrícula
            if ano_letivo:
                try:
                    ano_referencia = int(ano_letivo)
                except:
                    ano_referencia = ano_matricula
            else:
                ano_referencia = ano_matricula
            
            # Dia de vencimento padrão (pode ser configurável)
            dia_vencimento = 10
            
            print(f"📅 Gerando mensalidades para {nome_aluno}")
            print(f"📅 Data da matrícula: {data_mat.strftime('%d/%m/%Y')}")
            print(f"📅 Ano letivo: {ano_referencia}")
            print(f"💰 Valor: R$ {valor_mensalidade:.2f}")
            
            mensalidades_criadas = 0
            
            # NOVA REGRA: Gerar mensalidades APENAS do mês da matrícula até dezembro
            # Elimina mensalidades retroativas (anteriores à matrícula)
            meses_gerar = list(range(mes_matricula, 13))  # Do mês da matrícula até dezembro
            
            print(f"📋 Mensalidades a gerar: {[self._nome_mes(m) for m in meses_gerar]}")
            print(f"🚫 Mensalidades retroativas eliminadas: {[self._nome_mes(m) for m in range(1, mes_matricula)]}")
            
            for mes in meses_gerar:
                # Calcular data de vencimento
                try:
                    data_vencimento = date(ano_referencia, mes, dia_vencimento)
                except ValueError:
                    # Se o dia não existe no mês, usar último dia do mês
                    ultimo_dia = calendar.monthrange(ano_referencia, mes)[1]
                    data_vencimento = date(ano_referencia, mes, min(dia_vencimento, ultimo_dia))
                
                # Todas as mensalidades podem receber multa (já que são do período válido)
                pode_receber_multa = 1  # True
                
                # Determinar status inicial baseado na data atual
                hoje = date.today()
                if data_vencimento < hoje:
                    status_inicial = 'Atrasado'
                    print(f"  📅 {self._nome_mes(mes)}/{ano_referencia}: Atrasado (já vencida)")
                else:
                    status_inicial = 'Pendente'
                    print(f"  📅 {self._nome_mes(mes)}/{ano_referencia}: Pendente (a vencer)")
                
                # Criar registro de pagamento
                mes_referencia = f"{ano_referencia}-{mes:02d}"
                
                try:
                    cursor.execute("""
                        INSERT INTO pagamentos 
                        (aluno_id, mes_referencia, valor_original, valor_final, data_vencimento, 
                         status, pode_receber_multa, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        aluno_id, 
                        mes_referencia, 
                        valor_mensalidade, 
                        valor_mensalidade, 
                        data_vencimento,
                        status_inicial,
                        pode_receber_multa,
                        datetime.now().isoformat()
                    ))
                except sqlite3.Error as e:
                    # Se a coluna não existir, usar versão simples
                    cursor.execute("""
                        INSERT INTO pagamentos 
                        (aluno_id, mes_referencia, valor_original, valor_final, data_vencimento, 
                         status, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        aluno_id, 
                        mes_referencia, 
                        valor_mensalidade, 
                        valor_mensalidade, 
                        data_vencimento,
                        status_inicial,
                        datetime.now().isoformat()
                    ))
                
                mensalidades_criadas += 1
            
            conn.commit()
            conn.close()
            
            print(f"✅ {mensalidades_criadas} mensalidades criadas para {nome_aluno}")
            print(f"🎯 Período: {self._nome_mes(mes_matricula)} a Dezembro/{ano_referencia}")
            
            return {
                'success': True, 
                'mensalidades_criadas': mensalidades_criadas,
                'aluno': nome_aluno,
                'data_matricula': data_mat.strftime('%d/%m/%Y'),
                'mes_inicio': self._nome_mes(mes_matricula),
                'ano_referencia': ano_referencia,
                'valor_mensalidade': valor_mensalidade,
                'meses_gerados': [self._nome_mes(m) for m in meses_gerar]
            }
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            print(f"❌ Erro SQL: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"❌ Erro geral: {e}")
            return {'success': False, 'error': str(e)}
    
    def regenerar_mensalidades_aluno(self, aluno_id):
        """Regenera mensalidades quando dados do aluno são alterados"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            print(f"🔄 Regenerando mensalidades para aluno ID: {aluno_id}")
            
            # Remover mensalidades existentes não pagas
            cursor.execute("""
                DELETE FROM pagamentos 
                WHERE aluno_id = ? AND status != 'Pago'
            """, (aluno_id,))
            
            mensalidades_removidas = cursor.rowcount
            print(f"🗑️ {mensalidades_removidas} mensalidades não pagas removidas")
            
            conn.commit()
            conn.close()
            
            # Gerar novas mensalidades
            resultado = self.gerar_mensalidades_aluno(aluno_id)
            
            if resultado['success']:
                resultado['mensalidades_removidas'] = mensalidades_removidas
                resultado['regeneracao'] = True
            
            return resultado
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            print(f"❌ Erro ao regenerar: {e}")
            return {'success': False, 'error': str(e)}
    
    def _nome_mes(self, mes):
        """Retorna nome do mês"""
        meses = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        return meses[mes] if 1 <= mes <= 12 else str(mes)
    
    def recalcular_status_mensalidades(self):
        """Recalcula status das mensalidades baseado na data atual"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            hoje = date.today()
            
            # Atualizar mensalidades vencidas para "Atrasado" (apenas as não pagas)
            cursor.execute("""
                UPDATE pagamentos 
                SET status = 'Atrasado'
                WHERE status = 'Pendente' 
                AND date(data_vencimento) < date('now')
                AND data_pagamento IS NULL
            """)
            
            mensalidades_atualizadas = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            print(f"🔄 {mensalidades_atualizadas} mensalidades atualizadas para 'Atrasado'")
            
            return {
                'success': True, 
                'mensalidades_atualizadas': mensalidades_atualizadas
            }
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return {'success': False, 'error': str(e)}
    
    def obter_resumo_mensalidades_aluno(self, aluno_id):
        """Obtém resumo das mensalidades de um aluno"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'Pago' THEN 1 END) as pagas,
                    COUNT(CASE WHEN status = 'Pendente' THEN 1 END) as pendentes,
                    COUNT(CASE WHEN status = 'Atrasado' THEN 1 END) as atrasadas,
                    SUM(valor_final) as valor_total,
                    SUM(CASE WHEN status = 'Pago' THEN valor_final ELSE 0 END) as valor_pago,
                    SUM(CASE WHEN status != 'Pago' THEN valor_final ELSE 0 END) as valor_devido,
                    MIN(mes_referencia) as primeira_mensalidade,
                    MAX(mes_referencia) as ultima_mensalidade
                FROM pagamentos 
                WHERE aluno_id = ?
            """, (aluno_id,))
            
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado and resultado[0] > 0:
                return {
                    'total': resultado[0],
                    'pagas': resultado[1] or 0,
                    'pendentes': resultado[2] or 0,
                    'atrasadas': resultado[3] or 0,
                    'valor_total': resultado[4] or 0,
                    'valor_pago': resultado[5] or 0,
                    'valor_devido': resultado[6] or 0,
                    'primeira_mensalidade': resultado[7],
                    'ultima_mensalidade': resultado[8],
                    'periodo': f"{resultado[7]} a {resultado[8]}" if resultado[7] and resultado[8] else "N/A"
                }
            else:
                return {
                    'total': 0, 'pagas': 0, 'pendentes': 0, 'atrasadas': 0,
                    'valor_total': 0, 'valor_pago': 0, 'valor_devido': 0,
                    'primeira_mensalidade': None, 'ultima_mensalidade': None,
                    'periodo': "Nenhuma mensalidade encontrada"
                }
                
        except Exception as e:
            conn.close()
            return None
