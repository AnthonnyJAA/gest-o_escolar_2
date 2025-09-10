from database.connection import db
import sqlite3
from datetime import datetime, date, timedelta
import calendar

class MensalidadeService:
    def __init__(self):
        self.db = db
    
    def gerar_mensalidades_aluno(self, aluno_id):
        """Gera mensalidades para um aluno seguindo as regras básicas"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Buscar dados do aluno e turma
            cursor.execute("""
                SELECT a.nome, t.valor_mensalidade, t.dia_vencimento, t.ano_letivo
                FROM alunos a
                INNER JOIN turmas t ON a.turma_id = t.id
                WHERE a.id = ?
            """, (aluno_id,))
            
            aluno_row = cursor.fetchone()
            if not aluno_row:
                return {'success': False, 'error': 'Aluno não encontrado'}
            
            nome_aluno, valor_mensalidade, dia_vencimento, ano_letivo = aluno_row
            
            # Verificar se já existem mensalidades
            cursor.execute("SELECT COUNT(*) FROM pagamentos WHERE aluno_id = ?", (aluno_id,))
            mensalidades_existentes = cursor.fetchone()[0]
            
            if mensalidades_existentes > 0:
                return {'success': True, 'message': 'Mensalidades já existem'}
            
            # Data atual (data da matrícula)
            hoje = date.today()
            mes_matricula = hoje.month
            ano_matricula = hoje.year
            
            # Usar ano letivo da turma ou ano atual se não especificado
            if ano_letivo:
                try:
                    ano_referencia = int(ano_letivo)
                except:
                    ano_referencia = ano_matricula
            else:
                ano_referencia = ano_matricula
            
            print(f"📅 Gerando mensalidades para {nome_aluno}")
            print(f"📅 Mês da matrícula: {mes_matricula}/{ano_matricula}")
            print(f"📅 Ano letivo: {ano_referencia}")
            
            mensalidades_criadas = 0
            
            # REGRA 1: Se matriculado em janeiro, criar 12 parcelas
            if mes_matricula == 1:
                print("📋 Matrícula em Janeiro - Criando 12 mensalidades")
                meses_gerar = list(range(1, 13))  # Janeiro a Dezembro
                
            else:
                # REGRA 2: Se matriculado em outro mês, criar do mês atual até dezembro
                print(f"📋 Matrícula em {self._nome_mes(mes_matricula)} - Criando mensalidades do mês {mes_matricula} até 12")
                meses_gerar = list(range(mes_matricula, 13))  # Do mês atual até dezembro
                
                # REGRA 3: Criar também as mensalidades dos meses já passados como "Pendente"
                if mes_matricula > 1:
                    print(f"📋 Adicionando mensalidades em atraso (Janeiro a {self._nome_mes(mes_matricula-1)})")
                    meses_passados = list(range(1, mes_matricula))
                    meses_gerar = meses_passados + meses_gerar
            
            print(f"📋 Meses a gerar: {meses_gerar}")
            
            for mes in meses_gerar:
                # Calcular data de vencimento
                try:
                    data_vencimento = date(ano_referencia, mes, dia_vencimento)
                except ValueError:
                    # Se o dia não existe no mês (ex: 31/02), usar último dia do mês
                    ultimo_dia = calendar.monthrange(ano_referencia, mes)[1]
                    data_vencimento = date(ano_referencia, mes, min(dia_vencimento, ultimo_dia))
                
                # Determinar se pode receber multa baseado na regra
                if mes < mes_matricula:
                    # Mensalidade de mês anterior à matrícula - NÃO pode receber multa
                    pode_receber_multa = 0  # False
                    print(f"  📅 {self._nome_mes(mes)}/{ano_referencia}: Pendente (sem multa)")
                else:
                    # Mensalidade do mês da matrícula em diante - PODE receber multa  
                    pode_receber_multa = 1  # True
                    print(f"  📅 {self._nome_mes(mes)}/{ano_referencia}: Pendente (pode ter multa)")
                
                # Criar registro de pagamento com campo pode_receber_multa
                mes_referencia = f"{ano_referencia}-{mes:02d}"
                
                try:
                    cursor.execute("""
                        INSERT INTO pagamentos 
                        (aluno_id, mes_referencia, valor_original, valor_final, data_vencimento, 
                         status, pode_receber_multa, created_at)
                        VALUES (?, ?, ?, ?, ?, 'Pendente', ?, ?)
                    """, (
                        aluno_id, 
                        mes_referencia, 
                        valor_mensalidade, 
                        valor_mensalidade, 
                        data_vencimento,
                        pode_receber_multa,
                        datetime.now().isoformat()
                    ))
                except sqlite3.Error as e:
                    # Se a coluna não existir, usar versão simples
                    cursor.execute("""
                        INSERT INTO pagamentos 
                        (aluno_id, mes_referencia, valor_original, valor_final, data_vencimento, 
                         status, created_at)
                        VALUES (?, ?, ?, ?, ?, 'Pendente', ?)
                    """, (
                        aluno_id, 
                        mes_referencia, 
                        valor_mensalidade, 
                        valor_mensalidade, 
                        data_vencimento,
                        datetime.now().isoformat()
                    ))
                
                mensalidades_criadas += 1
            
            conn.commit()
            conn.close()
            
            print(f"✅ {mensalidades_criadas} mensalidades criadas para {nome_aluno}")
            
            return {
                'success': True, 
                'mensalidades_criadas': mensalidades_criadas,
                'aluno': nome_aluno,
                'mes_matricula': mes_matricula,
                'ano_referencia': ano_referencia,
                'meses_gerados': meses_gerar
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
