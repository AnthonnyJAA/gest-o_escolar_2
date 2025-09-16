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
            try:
                cursor.execute("""
                    ALTER TABLE pagamentos 
                    ADD COLUMN contrato_financeiro_id INTEGER 
                    REFERENCES contratos_financeiros(id)
                """)
            except sqlite3.OperationalError:
                pass  # Coluna já existe
            
            # Adicionar campos ao aluno se não existir
            try:
                cursor.execute("ALTER TABLE alunos ADD COLUMN data_desligamento DATE")
            except sqlite3.OperationalError:
                pass  # Campo já existe
                
            try:
                cursor.execute("ALTER TABLE alunos ADD COLUMN motivo_desligamento TEXT")
            except sqlite3.OperationalError:
                pass  # Campo já existe
            
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            conn.close()
            print(f"Erro ao criar tabelas avançadas: {e}")

    def listar_turmas_para_filtro(self):
        """Lista turmas formatadas para filtro"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, nome, serie, ano_letivo, valor_mensalidade_padrao,
                       (SELECT COUNT(*) FROM alunos WHERE turma_id = t.id AND status = 'Ativo') as total_alunos
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
                    'valor_mensalidade_padrao': row[4] or 0,
                    'total_alunos': row[5],
                    'display': f"{row[1]} - {row[2]} ({row[3]}) - {row[5]} aluno(s)"
                }
                turmas.append(turma)
            
            conn.close()
            return turmas
            
        except sqlite3.Error as e:
            conn.close()
            print(f"Erro ao listar turmas: {e}")
            return []

    def listar_alunos_por_turma(self, turma_id):
        """Lista alunos de uma turma específica"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT a.id, a.nome, a.data_nascimento, a.valor_mensalidade, a.status,
                       r.nome as responsavel_nome,
                       strftime('%Y', 'now') - strftime('%Y', a.data_nascimento) as idade
                FROM alunos a
                LEFT JOIN responsaveis r ON a.responsavel_id = r.id
                WHERE a.turma_id = ?
                ORDER BY a.nome
            """, (turma_id,))
            
            alunos = []
            for row in cursor.fetchall():
                aluno = {
                    'id': row[0],
                    'nome': row[1],
                    'data_nascimento': row[2],
                    'valor_mensalidade': row[3] or 0,
                    'status': row[4],
                    'responsavel_nome': row[5] or 'Não informado',
                    'idade': row[6] or 0
                }
                alunos.append(aluno)
            
            conn.close()
            return alunos
            
        except sqlite3.Error as e:
            conn.close()
            print(f"Erro ao listar alunos: {e}")
            return []

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
                        valor_final = ? + multa_aplicada + outros - desconto_aplicado
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

    def obter_historico_avancado(self, filtros=None, limite=50):
        """Obtém histórico avançado com filtros"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            sql = """
                SELECT 
                    ht.id, ht.data_transferencia, ht.tipo_transferencia,
                    a.nome as aluno_nome,
                    t_origem.nome as turma_origem_nome,
                    t_destino.nome as turma_destino_nome,
                    ht.valor_mensalidade_anterior, ht.valor_mensalidade_novo,
                    ht.motivo, ht.created_at
                FROM historico_transferencias ht
                INNER JOIN alunos a ON ht.aluno_id = a.id
                LEFT JOIN turmas t_origem ON ht.turma_origem_id = t_origem.id
                LEFT JOIN turmas t_destino ON ht.turma_destino_id = t_destino.id
                WHERE 1=1
            """
            
            params = []
            
            if filtros:
                if filtros.get('tipo_transferencia'):
                    sql += " AND ht.tipo_transferencia = ?"
                    params.append(filtros['tipo_transferencia'])
            
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
                    'turma_origem': row[4] or "N/A",
                    'turma_destino': row[5] or "N/A",
                    'valor_anterior': row[6] or 0,
                    'valor_novo': row[7] or 0,
                    'motivo': row[8] or '',
                    'created_at': row[9]
                }
                historico.append(item)
            
            conn.close()
            return historico
            
        except sqlite3.Error as e:
            conn.close()
            print(f"Erro ao obter histórico avançado: {e}")
            return []

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