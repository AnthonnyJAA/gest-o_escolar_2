from database.connection import db
import sqlite3
from datetime import datetime, date

class TransferenciaService:
    def __init__(self):
        self.db = db
        self.init_transferencia_table()

    def init_transferencia_table(self):
        """Cria tabela de histórico de transferências se não existir"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historico_transferencias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aluno_id INTEGER NOT NULL,
                    turma_origem_id INTEGER NOT NULL,
                    turma_destino_id INTEGER NOT NULL,
                    data_transferencia DATE NOT NULL,
                    motivo TEXT,
                    observacoes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (aluno_id) REFERENCES alunos (id),
                    FOREIGN KEY (turma_origem_id) REFERENCES turmas (id),
                    FOREIGN KEY (turma_destino_id) REFERENCES turmas (id)
                )
            """)
            
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            conn.close()
            print(f"Erro ao criar tabela de transferências: {e}")

    def listar_turmas_para_filtro(self):
        """Lista todas as turmas para filtro"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT t.id, t.nome, t.serie, t.ano_letivo,
                       COUNT(a.id) as total_alunos
                FROM turmas t
                LEFT JOIN alunos a ON t.id = a.turma_id AND a.status = 'Ativo'
                GROUP BY t.id, t.nome, t.serie, t.ano_letivo
                ORDER BY t.ano_letivo DESC, t.serie, t.nome
            """)
            
            turmas = []
            for row in cursor.fetchall():
                turma = {
                    'id': row[0],
                    'nome': row[1],
                    'serie': row[2],
                    'ano_letivo': row[3],
                    'total_alunos': row[4],
                    'display': f"{row[1]} - {row[2]} ({row[3]}) - {row[4]} alunos"
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
                SELECT 
                    a.id, a.nome, a.data_nascimento, a.valor_mensalidade,
                    a.data_matricula, a.status,
                    t.nome as turma_nome, t.serie, t.ano_letivo,
                    r.nome as responsavel_nome, r.telefone as responsavel_telefone
                FROM alunos a
                INNER JOIN turmas t ON a.turma_id = t.id
                LEFT JOIN responsaveis r ON a.id = r.aluno_id AND r.principal = 1
                WHERE a.turma_id = ? AND a.status = 'Ativo'
                ORDER BY a.nome
            """, (turma_id,))
            
            alunos = []
            for row in cursor.fetchall():
                # Calcular idade
                idade = 0
                if row[2]:  # data_nascimento
                    try:
                        if isinstance(row[2], str):
                            nasc = datetime.strptime(row[2], '%Y-%m-%d').date()
                        else:
                            nasc = row[2]
                        hoje = date.today()
                        idade = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
                    except:
                        idade = 0
                
                aluno = {
                    'id': row[0],
                    'nome': row[1],
                    'data_nascimento': row[2],
                    'idade': idade,
                    'valor_mensalidade': row[3] or 0,
                    'data_matricula': row[4],
                    'status': row[5],
                    'turma_nome': row[6],
                    'turma_serie': row[7],
                    'turma_ano': row[8],
                    'responsavel_nome': row[9] or 'N/I',
                    'responsavel_telefone': row[10] or 'N/I'
                }
                alunos.append(aluno)
            
            conn.close()
            return alunos
            
        except sqlite3.Error as e:
            conn.close()
            print(f"Erro ao listar alunos da turma: {e}")
            return []

    def transferir_aluno(self, aluno_id, turma_origem_id, turma_destino_id, motivo="", observacoes=""):
        """Transfere um aluno para nova turma"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Validações
            if turma_origem_id == turma_destino_id:
                return {'success': False, 'error': 'Turma de origem e destino não podem ser iguais!'}
            
            # Verificar se o aluno existe e está na turma de origem
            cursor.execute("""
                SELECT a.nome, t_origem.nome as turma_origem, t_destino.nome as turma_destino
                FROM alunos a
                INNER JOIN turmas t_origem ON a.turma_id = t_origem.id
                INNER JOIN turmas t_destino ON t_destino.id = ?
                WHERE a.id = ? AND a.turma_id = ? AND a.status = 'Ativo'
            """, (turma_destino_id, aluno_id, turma_origem_id))
            
            resultado = cursor.fetchone()
            if not resultado:
                return {'success': False, 'error': 'Aluno não encontrado ou não está na turma de origem!'}
            
            nome_aluno, turma_origem_nome, turma_destino_nome = resultado
            
            # Registrar transferência no histórico
            cursor.execute("""
                INSERT INTO historico_transferencias 
                (aluno_id, turma_origem_id, turma_destino_id, data_transferencia, motivo, observacoes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (aluno_id, turma_origem_id, turma_destino_id, date.today().strftime('%Y-%m-%d'), motivo, observacoes))
            
            # Atualizar turma do aluno
            cursor.execute("""
                UPDATE alunos 
                SET turma_id = ?
                WHERE id = ?
            """, (turma_destino_id, aluno_id))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'aluno': nome_aluno,
                'turma_origem': turma_origem_nome,
                'turma_destino': turma_destino_nome
            }
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return {'success': False, 'error': f'Erro na transferência: {str(e)}'}

    def transferir_alunos_lote(self, alunos_ids, turma_origem_id, turma_destino_id, motivo="", observacoes=""):
        """Transfere múltiplos alunos em lote"""
        if not alunos_ids:
            return {'success': False, 'error': 'Nenhum aluno selecionado!'}
        
        transferencias_sucesso = []
        transferencias_erro = []
        
        for aluno_id in alunos_ids:
            resultado = self.transferir_aluno(aluno_id, turma_origem_id, turma_destino_id, motivo, observacoes)
            
            if resultado['success']:
                transferencias_sucesso.append(resultado['aluno'])
            else:
                transferencias_erro.append(f"Aluno ID {aluno_id}: {resultado['error']}")
        
        return {
            'success': len(transferencias_sucesso) > 0,
            'transferencias_sucesso': transferencias_sucesso,
            'transferencias_erro': transferencias_erro,
            'total_sucesso': len(transferencias_sucesso),
            'total_erro': len(transferencias_erro)
        }

    def obter_historico_transferencias(self, limite=50):
        """Obtém histórico de transferências"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    ht.id, ht.data_transferencia, ht.motivo, ht.observacoes,
                    a.nome as aluno_nome,
                    t_origem.nome as turma_origem_nome, t_origem.serie as turma_origem_serie,
                    t_destino.nome as turma_destino_nome, t_destino.serie as turma_destino_serie,
                    ht.created_at
                FROM historico_transferencias ht
                INNER JOIN alunos a ON ht.aluno_id = a.id
                INNER JOIN turmas t_origem ON ht.turma_origem_id = t_origem.id
                INNER JOIN turmas t_destino ON ht.turma_destino_id = t_destino.id
                ORDER BY ht.created_at DESC
                LIMIT ?
            """, (limite,))
            
            historico = []
            for row in cursor.fetchall():
                item = {
                    'id': row[0],
                    'data_transferencia': row[1],
                    'motivo': row[2] or '',
                    'observacoes': row[3] or '',
                    'aluno_nome': row[4],
                    'turma_origem': f"{row[5]} - {row[6]}",
                    'turma_destino': f"{row[7]} - {row[8]}",
                    'created_at': row[9]
                }
                historico.append(item)
            
            conn.close()
            return historico
            
        except sqlite3.Error as e:
            conn.close()
            print(f"Erro ao obter histórico: {e}")
            return []

    def obter_estatisticas_transferencias(self):
        """Obtém estatísticas de transferências"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Total de transferências
            cursor.execute("SELECT COUNT(*) FROM historico_transferencias")
            total_transferencias = cursor.fetchone()[0] or 0
            
            # Transferências do mês atual
            mes_atual = date.today().strftime('%Y-%m')
            cursor.execute("""
                SELECT COUNT(*) 
                FROM historico_transferencias 
                WHERE strftime('%Y-%m', data_transferencia) = ?
            """, (mes_atual,))
            transferencias_mes = cursor.fetchone()[0] or 0
            
            # Transferências do ano atual
            ano_atual = date.today().year
            cursor.execute("""
                SELECT COUNT(*) 
                FROM historico_transferencias 
                WHERE strftime('%Y', data_transferencia) = ?
            """, (str(ano_atual),))
            transferencias_ano = cursor.fetchone()[0] or 0
            
            # Turma que mais recebe alunos
            cursor.execute("""
                SELECT t.nome, t.serie, COUNT(*) as total
                FROM historico_transferencias ht
                INNER JOIN turmas t ON ht.turma_destino_id = t.id
                GROUP BY t.id, t.nome, t.serie
                ORDER BY total DESC
                LIMIT 1
            """)
            turma_mais_recebe = cursor.fetchone()
            turma_mais_recebe_str = f"{turma_mais_recebe[0]} - {turma_mais_recebe[1]} ({turma_mais_recebe[2]} transferências)" if turma_mais_recebe else "N/A"
            
            # Turma que mais perde alunos
            cursor.execute("""
                SELECT t.nome, t.serie, COUNT(*) as total
                FROM historico_transferencias ht
                INNER JOIN turmas t ON ht.turma_origem_id = t.id
                GROUP BY t.id, t.nome, t.serie
                ORDER BY total DESC
                LIMIT 1
            """)
            turma_mais_perde = cursor.fetchone()
            turma_mais_perde_str = f"{turma_mais_perde[0]} - {turma_mais_perde[1]} ({turma_mais_perde[2]} transferências)" if turma_mais_perde else "N/A"
            
            conn.close()
            
            return {
                'total_transferencias': total_transferencias,
                'transferencias_mes': transferencias_mes,
                'transferencias_ano': transferencias_ano,
                'turma_mais_recebe': turma_mais_recebe_str,
                'turma_mais_perde': turma_mais_perde_str
            }
            
        except sqlite3.Error as e:
            conn.close()
            print(f"Erro ao obter estatísticas: {e}")
            return {
                'total_transferencias': 0,
                'transferencias_mes': 0,
                'transferencias_ano': 0,
                'turma_mais_recebe': 'N/A',
                'turma_mais_perde': 'N/A'
            }

    def buscar_aluno_por_id(self, aluno_id):
        """Busca dados de um aluno específico"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT a.id, a.nome, a.status, t.nome as turma_nome, t.serie, t.id as turma_id
                FROM alunos a
                INNER JOIN turmas t ON a.turma_id = t.id
                WHERE a.id = ?
            """, (aluno_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'nome': row[1],
                    'status': row[2],
                    'turma_nome': row[3],
                    'turma_serie': row[4],
                    'turma_id': row[5]
                }
            return None
            
        except sqlite3.Error as e:
            conn.close()
            print(f"Erro ao buscar aluno: {e}")
            return None

    def obter_historico_aluno(self, aluno_id):
        """Obtém histórico de transferências de um aluno específico"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    ht.data_transferencia, ht.motivo, ht.observacoes,
                    t_origem.nome as turma_origem_nome, t_origem.serie as turma_origem_serie,
                    t_destino.nome as turma_destino_nome, t_destino.serie as turma_destino_serie
                FROM historico_transferencias ht
                INNER JOIN turmas t_origem ON ht.turma_origem_id = t_origem.id
                INNER JOIN turmas t_destino ON ht.turma_destino_id = t_destino.id
                WHERE ht.aluno_id = ?
                ORDER BY ht.data_transferencia DESC
            """, (aluno_id,))
            
            historico = []
            for row in cursor.fetchall():
                item = {
                    'data_transferencia': row[0],
                    'motivo': row[1] or 'Não informado',
                    'observacoes': row[2] or '',
                    'turma_origem': f"{row[3]} - {row[4]}",
                    'turma_destino': f"{row[5]} - {row[6]}"
                }
                historico.append(item)
            
            conn.close()
            return historico
            
        except sqlite3.Error as e:
            conn.close()
            print(f"Erro ao obter histórico do aluno: {e}")
            return []

    def validar_transferencia(self, aluno_id, turma_destino_id):
        """Valida se uma transferência é possível"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar se aluno existe e está ativo
            cursor.execute("""
                SELECT a.turma_id, a.status, t.nome as turma_atual
                FROM alunos a
                INNER JOIN turmas t ON a.turma_id = t.id
                WHERE a.id = ?
            """, (aluno_id,))
            
            aluno_data = cursor.fetchone()
            if not aluno_data:
                return {'valido': False, 'erro': 'Aluno não encontrado'}
            
            turma_atual_id, status, turma_atual_nome = aluno_data
            
            if status != 'Ativo':
                return {'valido': False, 'erro': f'Aluno não está ativo (Status: {status})'}
            
            if turma_atual_id == turma_destino_id:
                return {'valido': False, 'erro': f'Aluno já está na turma {turma_atual_nome}'}
            
            # Verificar se turma de destino existe
            cursor.execute("SELECT nome FROM turmas WHERE id = ?", (turma_destino_id,))
            turma_destino = cursor.fetchone()
            if not turma_destino:
                return {'valido': False, 'erro': 'Turma de destino não encontrada'}
            
            conn.close()
            return {
                'valido': True,
                'turma_atual': turma_atual_nome,
                'turma_destino': turma_destino[0]
            }
            
        except sqlite3.Error as e:
            conn.close()
            return {'valido': False, 'erro': f'Erro na validação: {str(e)}'}

    def gerar_relatorio_transferencias(self, data_inicio=None, data_fim=None):
        """Gera relatório de transferências por período"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            sql = """
                SELECT 
                    ht.data_transferencia,
                    a.nome as aluno_nome,
                    t_origem.nome as turma_origem_nome, t_origem.serie as turma_origem_serie,
                    t_destino.nome as turma_destino_nome, t_destino.serie as turma_destino_serie,
                    ht.motivo, ht.observacoes
                FROM historico_transferencias ht
                INNER JOIN alunos a ON ht.aluno_id = a.id
                INNER JOIN turmas t_origem ON ht.turma_origem_id = t_origem.id
                INNER JOIN turmas t_destino ON ht.turma_destino_id = t_destino.id
            """
            
            params = []
            
            if data_inicio and data_fim:
                sql += " WHERE ht.data_transferencia BETWEEN ? AND ?"
                params.extend([data_inicio, data_fim])
            elif data_inicio:
                sql += " WHERE ht.data_transferencia >= ?"
                params.append(data_inicio)
            elif data_fim:
                sql += " WHERE ht.data_transferencia <= ?"
                params.append(data_fim)
            
            sql += " ORDER BY ht.data_transferencia DESC"
            
            cursor.execute(sql, params)
            
            relatorio = []
            for row in cursor.fetchall():
                item = {
                    'data_transferencia': row[0],
                    'aluno_nome': row[1],
                    'turma_origem': f"{row[2]} - {row[3]}",
                    'turma_destino': f"{row[4]} - {row[5]}",
                    'motivo': row[6] or 'Não informado',
                    'observacoes': row[7] or ''
                }
                relatorio.append(item)
            
            conn.close()
            return relatorio
            
        except sqlite3.Error as e:
            conn.close()
            print(f"Erro ao gerar relatório: {e}")
            return []