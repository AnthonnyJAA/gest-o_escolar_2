from database.connection import db
import sqlite3
from datetime import datetime, date, timedelta
import calendar
from utils.formatters import format_date, format_currency

class TransferenciaAvancadaService:
    def __init__(self):
        self.db = db
        self.init_advanced_tables()

    def init_advanced_tables(self):
        """Cria tabelas avançadas para transferências"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Tabela de histórico de transferências (expandida)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historico_transferencias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aluno_id INTEGER NOT NULL,
                    turma_origem_id INTEGER,
                    turma_destino_id INTEGER,
                    tipo_transferencia TEXT NOT NULL,  -- 'MESMO_ANO', 'NOVO_ANO', 'DESLIGAMENTO'
                    ano_letivo_origem TEXT,
                    ano_letivo_destino TEXT,
                    valor_mensalidade_anterior DECIMAL(10,2),
                    valor_mensalidade_novo DECIMAL(10,2),
                    alterou_mensalidade INTEGER DEFAULT 0,  -- 0=não, 1=sim
                    data_transferencia DATE NOT NULL,
                    motivo TEXT,
                    observacoes TEXT,
                    usuario_responsavel TEXT DEFAULT 'Sistema',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (aluno_id) REFERENCES alunos (id),
                    FOREIGN KEY (turma_origem_id) REFERENCES turmas (id),
                    FOREIGN KEY (turma_destino_id) REFERENCES turmas (id)
                )
            """)
            
            # Tabela de contratos financeiros (para histórico separado por ano)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contratos_financeiros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aluno_id INTEGER NOT NULL,
                    turma_id INTEGER NOT NULL,
                    ano_letivo TEXT NOT NULL,
                    valor_mensalidade DECIMAL(10,2) NOT NULL,
                    data_inicio DATE NOT NULL,
                    data_fim DATE,
                    status TEXT DEFAULT 'ATIVO',  -- 'ATIVO', 'ENCERRADO', 'SUSPENSO'
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (aluno_id) REFERENCES alunos (id),
                    FOREIGN KEY (turma_id) REFERENCES turmas (id),
                    UNIQUE(aluno_id, ano_letivo)
                )
            """)
            
            # Atualizar tabela de pagamentos com referência ao contrato
            cursor.execute("""
                ALTER TABLE pagamentos 
                ADD COLUMN contrato_financeiro_id INTEGER 
                REFERENCES contratos_financeiros(id)
            """)
            
            # Adicionar campos ao aluno se não existir
            try:
                cursor.execute("ALTER TABLE alunos ADD COLUMN data_desligamento DATE")
                cursor.execute("ALTER TABLE alunos ADD COLUMN motivo_desligamento TEXT")
            except sqlite3.OperationalError:
                pass  # Campos já existem
            
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            conn.close()
            print(f"Erro ao criar tabelas avançadas: {e}")

    def detectar_tipo_transferencia(self, turma_origem_id, turma_destino_id, tipo_operacao='TRANSFERENCIA'):
        """Detecta o tipo de transferência baseado nas turmas"""
        if tipo_operacao == 'DESLIGAMENTO':
            return 'DESLIGAMENTO'
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Buscar anos letivos das turmas
            cursor.execute("SELECT ano_letivo FROM turmas WHERE id = ?", (turma_origem_id,))
            ano_origem = cursor.fetchone()
            
            cursor.execute("SELECT ano_letivo FROM turmas WHERE id = ?", (turma_destino_id,))
            ano_destino = cursor.fetchone()
            
            conn.close()
            
            if not ano_origem or not ano_destino:
                return 'MESMO_ANO'  # Default
            
            if ano_origem[0] == ano_destino[0]:
                return 'MESMO_ANO'
            else:
                return 'NOVO_ANO'
                
        except sqlite3.Error as e:
            conn.close()
            print(f"Erro ao detectar tipo de transferência: {e}")
            return 'MESMO_ANO'

    def obter_info_transferencia(self, aluno_id, turma_origem_id, turma_destino_id):
        """Obtém informações detalhadas para a transferência"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Buscar dados do aluno
            cursor.execute("""
                SELECT a.nome, a.valor_mensalidade, a.status,
                       t_origem.nome as turma_origem, t_origem.ano_letivo as ano_origem,
                       t_destino.nome as turma_destino, t_destino.ano_letivo as ano_destino,
                       t_destino.valor_mensalidade_padrao as valor_destino
                FROM alunos a
                LEFT JOIN turmas t_origem ON a.turma_id = t_origem.id
                LEFT JOIN turmas t_destino ON t_destino.id = ?
                WHERE a.id = ? AND a.turma_id = ?
            """, (turma_destino_id, aluno_id, turma_origem_id))
            
            resultado = cursor.fetchone()
            
            if not resultado:
                conn.close()
                return None
            
            info = {
                'aluno_nome': resultado[0],
                'valor_atual': resultado[1] or 0,
                'status_aluno': resultado[2],
                'turma_origem': resultado[3],
                'ano_origem': resultado[4],
                'turma_destino': resultado[5],
                'ano_destino': resultado[6],
                'valor_destino_padrao': resultado[7] or resultado[1] or 0,
                'tipo_transferencia': self.detectar_tipo_transferencia(turma_origem_id, turma_destino_id),
                'valores_diferentes': False
            }
            
            # Verificar se os valores são diferentes
            info['valores_diferentes'] = abs(info['valor_atual'] - info['valor_destino_padrao']) > 0.01
            
            # Contar mensalidades pendentes
            cursor.execute("""
                SELECT COUNT(*) as pendentes,
                       COALESCE(SUM(valor_final), 0) as valor_pendente
                FROM pagamentos p
                WHERE p.aluno_id = ? 
                AND p.status IN ('Pendente', 'Atrasado')
            """, (aluno_id,))
            
            pendencias = cursor.fetchone()
            info['mensalidades_pendentes'] = pendencias[0] or 0
            info['valor_pendente'] = pendencias[1] or 0
            
            conn.close()
            return info
            
        except sqlite3.Error as e:
            conn.close()
            print(f"Erro ao obter info transferência: {e}")
            return None

    def transferir_aluno_mesmo_ano(self, aluno_id, turma_origem_id, turma_destino_id, 
                                   alterar_valor=False, novo_valor=None, motivo="", observacoes=""):
        """Cenário 1: Transferência dentro do mesmo ano letivo"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            conn.execute("BEGIN TRANSACTION")
            
            # Obter informações
            info = self.obter_info_transferencia(aluno_id, turma_origem_id, turma_destino_id)
            if not info:
                conn.rollback()
                conn.close()
                return {'success': False, 'error': 'Não foi possível obter informações da transferência'}
            
            valor_anterior = info['valor_atual']
            valor_novo = novo_valor if alterar_valor else valor_anterior
            
            # Atualizar turma do aluno
            cursor.execute("""
                UPDATE alunos 
                SET turma_id = ?, valor_mensalidade = ?
                WHERE id = ?
            """, (turma_destino_id, valor_novo, aluno_id))
            
            # Se alterar valor, atualizar mensalidades não pagas
            if alterar_valor and novo_valor is not None:
                cursor.execute("""
                    UPDATE pagamentos 
                    SET valor_original = ?, 
                        valor_final = ? + multa_aplicada - desconto_aplicado
                    WHERE aluno_id = ? 
                    AND status IN ('Pendente', 'Atrasado')
                """, (novo_valor, novo_valor, aluno_id))
                
                mensalidades_alteradas = cursor.rowcount
            else:
                mensalidades_alteradas = 0
            
            # Registrar no histórico
            cursor.execute("""
                INSERT INTO historico_transferencias
                (aluno_id, turma_origem_id, turma_destino_id, tipo_transferencia,
                 ano_letivo_origem, ano_letivo_destino, valor_mensalidade_anterior,
                 valor_mensalidade_novo, alterou_mensalidade, data_transferencia,
                 motivo, observacoes)
                VALUES (?, ?, ?, 'MESMO_ANO', ?, ?, ?, ?, ?, ?, ?, ?)
            """, (aluno_id, turma_origem_id, turma_destino_id, info['ano_origem'],
                  info['ano_destino'], valor_anterior, valor_novo, 
                  1 if alterar_valor else 0, date.today().strftime('%Y-%m-%d'),
                  motivo, observacoes))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'tipo': 'MESMO_ANO',
                'aluno': info['aluno_nome'],
                'turma_origem': info['turma_origem'],
                'turma_destino': info['turma_destino'],
                'valor_alterado': alterar_valor,
                'valor_anterior': valor_anterior,
                'valor_novo': valor_novo,
                'mensalidades_alteradas': mensalidades_alteradas
            }
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return {'success': False, 'error': f'Erro na transferência: {str(e)}'}

    def transferir_aluno_novo_ano(self, aluno_id, turma_origem_id, turma_destino_id, 
                                  valor_novo_contrato=None, motivo="", observacoes=""):
        """Cenário 2: Transferência para novo ano letivo"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            conn.execute("BEGIN TRANSACTION")
            
            # Obter informações
            info = self.obter_info_transferencia(aluno_id, turma_origem_id, turma_destino_id)
            if not info:
                conn.rollback()
                conn.close()
                return {'success': False, 'error': 'Não foi possível obter informações da transferência'}
            
            # Encerrar contrato atual (se existir)
            cursor.execute("""
                UPDATE contratos_financeiros 
                SET status = 'ENCERRADO', data_fim = ?
                WHERE aluno_id = ? AND ano_letivo = ? AND status = 'ATIVO'
            """, (date.today().strftime('%Y-%m-%d'), aluno_id, info['ano_origem']))
            
            # Criar novo contrato financeiro
            valor_novo_contrato = valor_novo_contrato or info['valor_destino_padrao']
            
            cursor.execute("""
                INSERT OR REPLACE INTO contratos_financeiros
                (aluno_id, turma_id, ano_letivo, valor_mensalidade, data_inicio, status)
                VALUES (?, ?, ?, ?, ?, 'ATIVO')
            """, (aluno_id, turma_destino_id, info['ano_destino'], 
                  valor_novo_contrato, date.today().strftime('%Y-%m-%d')))
            
            contrato_id = cursor.lastrowid
            
            # Atualizar dados do aluno
            cursor.execute("""
                UPDATE alunos 
                SET turma_id = ?, valor_mensalidade = ?
                WHERE id = ?
            """, (turma_destino_id, valor_novo_contrato, aluno_id))
            
            # Gerar mensalidades do novo ano letivo
            mensalidades_geradas = self.gerar_mensalidades_novo_ano(
                cursor, aluno_id, contrato_id, info['ano_destino'], valor_novo_contrato
            )
            
            # Registrar no histórico
            cursor.execute("""
                INSERT INTO historico_transferencias
                (aluno_id, turma_origem_id, turma_destino_id, tipo_transferencia,
                 ano_letivo_origem, ano_letivo_destino, valor_mensalidade_anterior,
                 valor_mensalidade_novo, alterou_mensalidade, data_transferencia,
                 motivo, observacoes)
                VALUES (?, ?, ?, 'NOVO_ANO', ?, ?, ?, ?, 1, ?, ?, ?)
            """, (aluno_id, turma_origem_id, turma_destino_id, info['ano_origem'],
                  info['ano_destino'], info['valor_atual'], valor_novo_contrato,
                  date.today().strftime('%Y-%m-%d'), motivo, observacoes))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'tipo': 'NOVO_ANO',
                'aluno': info['aluno_nome'],
                'turma_origem': info['turma_origem'],
                'turma_destino': info['turma_destino'],
                'ano_origem': info['ano_origem'],
                'ano_destino': info['ano_destino'],
                'valor_anterior': info['valor_atual'],
                'valor_novo': valor_novo_contrato,
                'mensalidades_geradas': mensalidades_geradas,
                'pendencias_preservadas': info['mensalidades_pendentes']
            }
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return {'success': False, 'error': f'Erro na transferência: {str(e)}'}

    def desligar_aluno(self, aluno_id, motivo_desligamento="", observacoes=""):
        """Cenário 3: Desligamento do aluno"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            conn.execute("BEGIN TRANSACTION")
            
            # Obter dados do aluno
            cursor.execute("""
                SELECT a.nome, a.turma_id, a.status, 
                       t.nome as turma_nome, t.ano_letivo,
                       COUNT(p.id) as mensalidades_pendentes,
                       COALESCE(SUM(p.valor_final), 0) as valor_pendente
                FROM alunos a
                LEFT JOIN turmas t ON a.turma_id = t.id
                LEFT JOIN pagamentos p ON a.id = p.aluno_id AND p.status IN ('Pendente', 'Atrasado')
                WHERE a.id = ?
                GROUP BY a.id
            """, (aluno_id,))
            
            resultado = cursor.fetchone()
            if not resultado:
                conn.rollback()
                conn.close()
                return {'success': False, 'error': 'Aluno não encontrado'}
            
            aluno_nome, turma_id, status_atual, turma_nome, ano_letivo, pendentes, valor_pendente = resultado
            
            if status_atual == 'Inativo':
                conn.rollback()
                conn.close()
                return {'success': False, 'error': 'Aluno já está inativo'}
            
            # Atualizar status do aluno
            cursor.execute("""
                UPDATE alunos 
                SET status = 'Inativo', 
                    data_desligamento = ?, 
                    motivo_desligamento = ?
                WHERE id = ?
            """, (date.today().strftime('%Y-%m-%d'), motivo_desligamento, aluno_id))
            
            # Encerrar contratos ativos
            cursor.execute("""
                UPDATE contratos_financeiros 
                SET status = 'ENCERRADO', data_fim = ?
                WHERE aluno_id = ? AND status = 'ATIVO'
            """, (date.today().strftime('%Y-%m-%d'), aluno_id))
            
            # Registrar no histórico
            cursor.execute("""
                INSERT INTO historico_transferencias
                (aluno_id, turma_origem_id, turma_destino_id, tipo_transferencia,
                 ano_letivo_origem, valor_mensalidade_anterior, data_transferencia,
                 motivo, observacoes)
                VALUES (?, ?, NULL, 'DESLIGAMENTO', ?, ?, ?, ?, ?)
            """, (aluno_id, turma_id, ano_letivo, 0, 
                  date.today().strftime('%Y-%m-%d'), motivo_desligamento, observacoes))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'tipo': 'DESLIGAMENTO',
                'aluno': aluno_nome,
                'turma_origem': turma_nome,
                'ano_letivo': ano_letivo,
                'mensalidades_pendentes': pendentes,
                'valor_pendente': valor_pendente
            }
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return {'success': False, 'error': f'Erro no desligamento: {str(e)}'}

    def reativar_aluno(self, aluno_id, turma_destino_id, valor_mensalidade, motivo="", observacoes=""):
        """Reativa aluno que estava desligado"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            conn.execute("BEGIN TRANSACTION")
            
            # Verificar se aluno está inativo
            cursor.execute("""
                SELECT nome, status, data_desligamento 
                FROM alunos WHERE id = ?
            """, (aluno_id,))
            
            resultado = cursor.fetchone()
            if not resultado:
                conn.rollback()
                conn.close()
                return {'success': False, 'error': 'Aluno não encontrado'}
            
            nome, status, data_desligamento = resultado
            
            if status != 'Inativo':
                conn.rollback()
                conn.close()
                return {'success': False, 'error': 'Aluno já está ativo'}
            
            # Obter ano letivo da turma destino
            cursor.execute("SELECT nome, ano_letivo FROM turmas WHERE id = ?", (turma_destino_id,))
            turma_info = cursor.fetchone()
            
            if not turma_info:
                conn.rollback()
                conn.close()
                return {'success': False, 'error': 'Turma de destino não encontrada'}
            
            turma_nome, ano_letivo = turma_info
            
            # Reativar aluno
            cursor.execute("""
                UPDATE alunos 
                SET status = 'Ativo', 
                    turma_id = ?, 
                    valor_mensalidade = ?,
                    data_desligamento = NULL,
                    motivo_desligamento = NULL
                WHERE id = ?
            """, (turma_destino_id, valor_mensalidade, aluno_id))
            
            # Criar novo contrato
            cursor.execute("""
                INSERT INTO contratos_financeiros
                (aluno_id, turma_id, ano_letivo, valor_mensalidade, data_inicio, status)
                VALUES (?, ?, ?, ?, ?, 'ATIVO')
            """, (aluno_id, turma_destino_id, ano_letivo, valor_mensalidade,
                  date.today().strftime('%Y-%m-%d')))
            
            # Registrar no histórico
            cursor.execute("""
                INSERT INTO historico_transferencias
                (aluno_id, turma_origem_id, turma_destino_id, tipo_transferencia,
                 ano_letivo_destino, valor_mensalidade_novo, data_transferencia,
                 motivo, observacoes)
                VALUES (?, NULL, ?, 'REATIVACAO', ?, ?, ?, ?, ?)
            """, (aluno_id, turma_destino_id, ano_letivo, valor_mensalidade,
                  date.today().strftime('%Y-%m-%d'), motivo, observacoes))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'tipo': 'REATIVACAO',
                'aluno': nome,
                'turma_destino': turma_nome,
                'data_desligamento': data_desligamento,
                'valor_mensalidade': valor_mensalidade
            }
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return {'success': False, 'error': f'Erro na reativação: {str(e)}'}

    def gerar_mensalidades_novo_ano(self, cursor, aluno_id, contrato_id, ano_letivo, valor_mensalidade):
        """Gera mensalidades para o novo ano letivo"""
        try:
            ano = int(ano_letivo)
            mensalidades_criadas = 0
            
            # Gerar mensalidades de março a dezembro (padrão escolar)
            for mes in range(3, 13):  # Março a Dezembro
                # Data de vencimento no dia 10 do mês
                try:
                    data_vencimento = date(ano, mes, 10)
                except ValueError:
                    continue  # Pular se data inválida
                
                mes_referencia = f"{ano}-{mes:02d}"
                
                # Verificar se já existe
                cursor.execute("""
                    SELECT id FROM pagamentos 
                    WHERE aluno_id = ? AND mes_referencia = ?
                """, (aluno_id, mes_referencia))
                
                if cursor.fetchone():
                    continue  # Já existe, pular
                
                # Criar mensalidade
                cursor.execute("""
                    INSERT INTO pagamentos
                    (aluno_id, contrato_financeiro_id, mes_referencia, valor_original,
                     desconto_aplicado, multa_aplicada, valor_final, data_vencimento,
                     status, pode_receber_multa)
                    VALUES (?, ?, ?, ?, 0, 0, ?, ?, 'Pendente', 1)
                """, (aluno_id, contrato_id, mes_referencia, valor_mensalidade,
                      valor_mensalidade, data_vencimento.strftime('%Y-%m-%d')))
                
                mensalidades_criadas += 1
            
            return mensalidades_criadas
            
        except Exception as e:
            print(f"Erro ao gerar mensalidades: {e}")
            return 0

    def obter_historico_avancado(self, filtros=None, limite=50):
        """Obtém histórico avançado com filtros"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            sql = """
                SELECT 
                    ht.id, ht.data_transferencia, ht.tipo_transferencia,
                    a.nome as aluno_nome,
                    t_origem.nome as turma_origem_nome, t_origem.serie as turma_origem_serie,
                    t_destino.nome as turma_destino_nome, t_destino.serie as turma_destino_serie,
                    ht.ano_letivo_origem, ht.ano_letivo_destino,
                    ht.valor_mensalidade_anterior, ht.valor_mensalidade_novo,
                    ht.alterou_mensalidade, ht.motivo, ht.observacoes,
                    ht.created_at
                FROM historico_transferencias ht
                INNER JOIN alunos a ON ht.aluno_id = a.id
                LEFT JOIN turmas t_origem ON ht.turma_origem_id = t_origem.id
                LEFT JOIN turmas t_destino ON ht.turma_destino_id = t_destino.id
                WHERE 1=1
            """
            
            params = []
            
            if filtros:
                if filtros.get('ano_letivo'):
                    sql += " AND (ht.ano_letivo_origem = ? OR ht.ano_letivo_destino = ?)"
                    params.extend([filtros['ano_letivo'], filtros['ano_letivo']])
                
                if filtros.get('tipo_transferencia'):
                    sql += " AND ht.tipo_transferencia = ?"
                    params.append(filtros['tipo_transferencia'])
                
                if filtros.get('data_inicio'):
                    sql += " AND ht.data_transferencia >= ?"
                    params.append(filtros['data_inicio'])
                
                if filtros.get('data_fim'):
                    sql += " AND ht.data_transferencia <= ?"
                    params.append(filtros['data_fim'])
            
            sql += " ORDER BY ht.created_at DESC LIMIT ?"
            params.append(limite)
            
            cursor.execute(sql, params)
            
            historico = []
            for row in cursor.fetchall():
                item = {
                    'id': row[0],
                    'data_transferencia': row[1],
                    'tipo_transferencia': row[2],
                    'aluno_nome': row[3],
                    'turma_origem': f"{row[4]} - {row[5]}" if row[4] else "N/A",
                    'turma_destino': f"{row[6]} - {row[7]}" if row[6] else "N/A",
                    'ano_origem': row[8],
                    'ano_destino': row[9],
                    'valor_anterior': row[10] or 0,
                    'valor_novo': row[11] or 0,
                    'alterou_mensalidade': row[12],
                    'motivo': row[13] or '',
                    'observacoes': row[14] or '',
                    'created_at': row[15]
                }
                historico.append(item)
            
            conn.close()
            return historico
            
        except sqlite3.Error as e:
            conn.close()
            print(f"Erro ao obter histórico avançado: {e}")
            return []

    def obter_estatisticas_avancadas(self):
        """Obtém estatísticas avançadas de transferências"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            stats = {}
            
            # Total por tipo
            cursor.execute("""
                SELECT tipo_transferencia, COUNT(*) as total
                FROM historico_transferencias
                GROUP BY tipo_transferencia
            """)
            
            stats['por_tipo'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Alunos ativos vs inativos
            cursor.execute("""
                SELECT status, COUNT(*) as total
                FROM alunos
                GROUP BY status
            """)
            
            stats['alunos_por_status'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Transferências por ano letivo
            cursor.execute("""
                SELECT ano_letivo_destino, COUNT(*) as total
                FROM historico_transferencias
                WHERE ano_letivo_destino IS NOT NULL
                GROUP BY ano_letivo_destino
                ORDER BY ano_letivo_destino DESC
            """)
            
            stats['por_ano_letivo'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Pendências financeiras de alunos inativos
            cursor.execute("""
                SELECT COUNT(DISTINCT p.aluno_id) as alunos_com_pendencia,
                       COALESCE(SUM(p.valor_final), 0) as valor_total_pendente
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                WHERE a.status = 'Inativo' 
                AND p.status IN ('Pendente', 'Atrasado')
            """)
            
            pendencias = cursor.fetchone()
            stats['pendencias_inativos'] = {
                'alunos': pendencias[0] or 0,
                'valor': pendencias[1] or 0
            }
            
            # Transferências do mês atual
            mes_atual = date.today().strftime('%Y-%m')
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM historico_transferencias
                WHERE strftime('%Y-%m', data_transferencia) = ?
            """, (mes_atual,))
            
            stats['mes_atual'] = cursor.fetchone()[0] or 0
            
            conn.close()
            return stats
            
        except sqlite3.Error as e:
            conn.close()
            print(f"Erro ao obter estatísticas avançadas: {e}")
            return {}

    def validar_transferencia_avancada(self, aluno_id, turma_destino_id, tipo_operacao='TRANSFERENCIA'):
        """Validação avançada de transferências"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            validacao = {'valido': True, 'avisos': [], 'erros': []}
            
            # Verificar aluno
            cursor.execute("""
                SELECT a.nome, a.status, a.turma_id, t_atual.nome as turma_atual
                FROM alunos a
                LEFT JOIN turmas t_atual ON a.turma_id = t_atual.id
                WHERE a.id = ?
            """, (aluno_id,))
            
            aluno_data = cursor.fetchone()
            if not aluno_data:
                validacao['valido'] = False
                validacao['erros'].append('Aluno não encontrado')
                conn.close()
                return validacao
            
            nome, status, turma_atual_id, turma_atual_nome = aluno_data
            
            # Validações por tipo de operação
            if tipo_operacao == 'TRANSFERENCIA':
                if status != 'Ativo':
                    validacao['erros'].append(f'Aluno está {status}. Apenas alunos ativos podem ser transferidos.')
                
                if turma_atual_id == turma_destino_id:
                    validacao['erros'].append('Aluno já está na turma de destino')
                
                # Verificar turma destino
                cursor.execute("SELECT nome, ano_letivo FROM turmas WHERE id = ?", (turma_destino_id,))
                turma_destino = cursor.fetchone()
                
                if not turma_destino:
                    validacao['erros'].append('Turma de destino não encontrada')
                
            elif tipo_operacao == 'DESLIGAMENTO':
                if status != 'Ativo':
                    validacao['erros'].append(f'Aluno já está {status}')
                
                # Verificar pendências
                cursor.execute("""
                    SELECT COUNT(*), COALESCE(SUM(valor_final), 0)
                    FROM pagamentos 
                    WHERE aluno_id = ? AND status IN ('Pendente', 'Atrasado')
                """, (aluno_id,))
                
                pendencias = cursor.fetchone()
                if pendencias[0] > 0:
                    validacao['avisos'].append(
                        f'Aluno possui {pendencias[0]} mensalidade(s) pendente(s) no valor de R$ {pendencias[1]:.2f}'
                    )
            
            elif tipo_operacao == 'REATIVACAO':
                if status != 'Inativo':
                    validacao['erros'].append('Apenas alunos inativos podem ser reativados')
            
            # Verificar se há erros críticos
            if validacao['erros']:
                validacao['valido'] = False
            
            conn.close()
            return validacao
            
        except sqlite3.Error as e:
            conn.close()
            return {
                'valido': False,
                'erros': [f'Erro na validação: {str(e)}'],
                'avisos': []
            }

    def listar_alunos_inativos(self):
        """Lista alunos inativos para possível reativação"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    a.id, a.nome, a.data_desligamento, a.motivo_desligamento,
                    t.nome as ultima_turma, t.serie, t.ano_letivo,
                    COUNT(p.id) as mensalidades_pendentes,
                    COALESCE(SUM(p.valor_final), 0) as valor_pendente
                FROM alunos a
                LEFT JOIN turmas t ON a.turma_id = t.id
                LEFT JOIN pagamentos p ON a.id = p.aluno_id AND p.status IN ('Pendente', 'Atrasado')
                WHERE a.status = 'Inativo'
                GROUP BY a.id
                ORDER BY a.data_desligamento DESC
            """)
            
            alunos_inativos = []
            for row in cursor.fetchall():
                aluno = {
                    'id': row[0],
                    'nome': row[1],
                    'data_desligamento': row[2],
                    'motivo_desligamento': row[3] or 'Não informado',
                    'ultima_turma': row[4],
                    'serie': row[5],
                    'ano_letivo': row[6],
                    'mensalidades_pendentes': row[7],
                    'valor_pendente': row[8]
                }
                alunos_inativos.append(aluno)
            
            conn.close()
            return alunos_inativos
            
        except sqlite3.Error as e:
            conn.close()
            print(f"Erro ao listar alunos inativos: {e}")
            return []

    def gerar_relatorio_completo(self, filtros=None):
        """Gera relatório completo com todos os dados"""
        try:
            relatorio = {
                'historico': self.obter_historico_avancado(filtros, 1000),
                'estatisticas': self.obter_estatisticas_avancadas(),
                'alunos_inativos': self.listar_alunos_inativos(),
                'data_geracao': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return relatorio
            
        except Exception as e:
            print(f"Erro ao gerar relatório completo: {e}")
            return None