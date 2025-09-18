from database.connection import db
import sqlite3
from datetime import datetime, date, timedelta
from calendar import monthrange

class MensalidadeService:
    def __init__(self):
        self.db = db

    def gerar_mensalidades_aluno(self, aluno_id):
        """Gera mensalidades automáticas para um aluno recém-cadastrado"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            print(f"💰 Gerando mensalidades para aluno ID: {aluno_id}")
            
            # Buscar dados do aluno
            cursor.execute("""
                SELECT a.nome, a.valor_mensalidade, a.data_matricula, 
                       t.ano_letivo, t.nome as turma_nome
                FROM alunos a
                INNER JOIN turmas t ON a.turma_id = t.id
                WHERE a.id = ?
            """, (aluno_id,))
            
            aluno_data = cursor.fetchone()
            if not aluno_data:
                return {'success': False, 'error': 'Aluno não encontrado'}
            
            nome_aluno, valor_mensalidade, data_matricula, ano_letivo, turma_nome = aluno_data
            
            if not valor_mensalidade or valor_mensalidade <= 0:
                return {'success': False, 'error': 'Valor da mensalidade deve ser maior que zero'}
            
            # Determinar ano letivo
            ano_referencia = int(ano_letivo) if ano_letivo else date.today().year
            
            # Determinar mês de início (março se não especificado)
            if data_matricula:
                try:
                    if isinstance(data_matricula, str):
                        data_mat = datetime.strptime(data_matricula, '%Y-%m-%d').date()
                    else:
                        data_mat = data_matricula
                    
                    # Se a matrícula foi no ano letivo atual, começar do mês da matrícula
                    if data_mat.year == ano_referencia:
                        mes_inicio = max(data_mat.month, 3)  # Não antes de março
                    else:
                        mes_inicio = 3  # Março (início do ano letivo)
                except:
                    mes_inicio = 3
            else:
                mes_inicio = 3
            
            # Gerar mensalidades de março a dezembro (10 meses)
            mensalidades_geradas = 0
            mes_atual = date.today().month
            ano_atual = date.today().year
            
            print(f"📅 Gerando mensalidades de {mes_inicio:02d}/{ano_referencia} a 12/{ano_referencia}")
            
            for mes in range(mes_inicio, 13):  # De março (3) até dezembro (12)
                # Verificar se já existe mensalidade para este mês
                cursor.execute("""
                    SELECT id FROM pagamentos 
                    WHERE aluno_id = ? AND mes_referencia = ?
                """, (aluno_id, f"{ano_referencia}-{mes:02d}"))
                
                if cursor.fetchone():
                    print(f"⚠️ Mensalidade {mes:02d}/{ano_referencia} já existe - pulando")
                    continue
                
                # Calcular data de vencimento (dia 10 do mês)
                try:
                    data_vencimento = date(ano_referencia, mes, 10)
                except ValueError:
                    # Se o dia 10 não existir no mês (improvável), usar último dia do mês
                    ultimo_dia = monthrange(ano_referencia, mes)[1]
                    data_vencimento = date(ano_referencia, mes, ultimo_dia)
                
                # Determinar status baseado na data atual
                if ano_atual > ano_referencia or (ano_atual == ano_referencia and mes_atual > mes):
                    # Mês já passou
                    if data_vencimento < date.today():
                        status = 'Atrasado'
                    else:
                        status = 'Pendente'
                elif ano_atual == ano_referencia and mes_atual == mes:
                    # Mês atual
                    status = 'Pendente'
                else:
                    # Mês futuro
                    status = 'Pendente'
                
                # Inserir mensalidade
                cursor.execute("""
                    INSERT INTO pagamentos 
                    (aluno_id, mes_referencia, valor_original, desconto_aplicado, 
                     multa_aplicada, valor_final, data_vencimento, status, pode_receber_multa)
                    VALUES (?, ?, ?, 0, 0, ?, ?, ?, 1)
                """, (
                    aluno_id,
                    f"{ano_referencia}-{mes:02d}",
                    valor_mensalidade,
                    valor_mensalidade,
                    data_vencimento.strftime('%Y-%m-%d'),
                    status
                ))
                
                mensalidades_geradas += 1
                print(f"✅ Mensalidade {mes:02d}/{ano_referencia}: R$ {valor_mensalidade:.2f} - {status}")
            
            conn.commit()
            conn.close()
            
            if mensalidades_geradas > 0:
                print(f"🎉 {mensalidades_geradas} mensalidades geradas para {nome_aluno}")
                return {
                    'success': True,
                    'mensalidades_criadas': mensalidades_geradas,
                    'aluno_nome': nome_aluno,
                    'valor_mensalidade': valor_mensalidade,
                    'ano_referencia': ano_referencia,
                    'mes_inicio': mes_inicio
                }
            else:
                return {
                    'success': True,
                    'mensalidades_criadas': 0,
                    'message': 'Todas as mensalidades já existiam'
                }
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            print(f"❌ Erro ao gerar mensalidades: {e}")
            return {'success': False, 'error': f'Erro no banco de dados: {str(e)}'}
        
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"❌ Erro inesperado ao gerar mensalidades: {e}")
            return {'success': False, 'error': f'Erro inesperado: {str(e)}'}

    def regenerar_mensalidades_aluno(self, aluno_id):
        """Regenera mensalidades quando valor é alterado"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            print(f"🔄 Regenerando mensalidades para aluno ID: {aluno_id}")
            
            # Buscar mensalidades não pagas
            cursor.execute("""
                SELECT id, mes_referencia, valor_original
                FROM pagamentos
                WHERE aluno_id = ? AND status != 'Pago'
                ORDER BY mes_referencia
            """, (aluno_id,))
            
            mensalidades_pendentes = cursor.fetchall()
            
            if not mensalidades_pendentes:
                print("ℹ️ Nenhuma mensalidade pendente para regenerar")
                return {'success': True, 'mensalidades_removidas': 0, 'mensalidades_criadas': 0}
            
            # Buscar novo valor da mensalidade
            cursor.execute("""
                SELECT valor_mensalidade, nome
                FROM alunos
                WHERE id = ?
            """, (aluno_id,))
            
            aluno_info = cursor.fetchone()
            if not aluno_info:
                return {'success': False, 'error': 'Aluno não encontrado'}
            
            novo_valor, nome_aluno = aluno_info
            
            # Remover mensalidades pendentes antigas
            cursor.execute("""
                DELETE FROM pagamentos
                WHERE aluno_id = ? AND status != 'Pago'
            """, (aluno_id,))
            
            mensalidades_removidas = cursor.rowcount
            
            conn.commit()
            
            # Gerar novas mensalidades
            resultado_geracao = self.gerar_mensalidades_aluno(aluno_id)
            
            if resultado_geracao['success']:
                print(f"✅ Mensalidades regeneradas: {mensalidades_removidas} removidas, {resultado_geracao['mensalidades_criadas']} criadas")
                return {
                    'success': True,
                    'mensalidades_removidas': mensalidades_removidas,
                    'mensalidades_criadas': resultado_geracao['mensalidades_criadas'],
                    'aluno_nome': nome_aluno
                }
            else:
                return resultado_geracao
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            print(f"❌ Erro ao regenerar mensalidades: {e}")
            return {'success': False, 'error': f'Erro no banco de dados: {str(e)}'}
        
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"❌ Erro inesperado ao regenerar mensalidades: {e}")
            return {'success': False, 'error': f'Erro inesperado: {str(e)}'}

    def atualizar_valores_mensalidades_pendentes(self, aluno_id, novo_valor):
        """Atualiza valor das mensalidades pendentes quando aluno é editado"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Atualizar mensalidades pendentes
            cursor.execute("""
                UPDATE pagamentos 
                SET valor_original = ?, valor_final = ?
                WHERE aluno_id = ? AND status != 'Pago'
            """, (novo_valor, novo_valor, aluno_id))
            
            mensalidades_atualizadas = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            print(f"✅ {mensalidades_atualizadas} mensalidades pendentes atualizadas para R$ {novo_valor:.2f}")
            
            return {
                'success': True,
                'mensalidades_atualizadas': mensalidades_atualizadas
            }
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return {'success': False, 'error': str(e)}

    def verificar_mensalidades_aluno(self, aluno_id):
        """Verifica quantas mensalidades o aluno tem"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN status = 'Pago' THEN 1 END) as pagas,
                       COUNT(CASE WHEN status != 'Pago' THEN 1 END) as pendentes
                FROM pagamentos
                WHERE aluno_id = ?
            """, (aluno_id,))
            
            resultado = cursor.fetchone()
            conn.close()
            
            return {
                'total': resultado[0] or 0,
                'pagas': resultado[1] or 0,
                'pendentes': resultado[2] or 0
            }
            
        except sqlite3.Error as e:
            conn.close()
            return {'total': 0, 'pagas': 0, 'pendentes': 0}
