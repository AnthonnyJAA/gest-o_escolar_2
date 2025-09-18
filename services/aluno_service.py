from database.connection import db
import sqlite3
from datetime import datetime, date
from utils.formatters import format_date, calculate_age

class AlunoService:
    def __init__(self):
        self.db = db
    
    def listar_turmas(self):
        """Lista todas as turmas para dropdown"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, nome, serie, ano_letivo 
            FROM turmas 
            ORDER BY nome
        """)
        
        turmas = []
        for row in cursor.fetchall():
            turma = {
                'id': row[0],
                'nome': row[1],
                'serie': row[2],
                'ano_letivo': row[3],
                'display': f"{row[1]} - {row[2]} ({row[3]})"
            }
            turmas.append(turma)
        
        conn.close()
        return turmas
    
    def salvar_aluno(self, aluno_data, responsaveis_data):
        """Salva aluno e GERA MENSALIDADES AUTOMATICAMENTE"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            is_edicao = 'id' in aluno_data
            
            if is_edicao:
                # === EDIÇÃO DE ALUNO EXISTENTE ===
                print(f"✏️ Editando aluno ID: {aluno_data['id']}")
                
                # Buscar valor antigo para comparação
                cursor.execute("SELECT valor_mensalidade FROM alunos WHERE id = ?", (aluno_data['id'],))
                valor_antigo_row = cursor.fetchone()
                valor_antigo = valor_antigo_row[0] if valor_antigo_row else 0
                
                # Atualizar aluno existente
                cursor.execute("""
                    UPDATE alunos 
                    SET nome = ?, data_nascimento = ?, cpf = ?, sexo = ?, nacionalidade = ?, 
                        telefone = ?, endereco = ?, turma_id = ?, status = ?, valor_mensalidade = ?
                    WHERE id = ?
                """, (
                    aluno_data['nome'],
                    aluno_data['data_nascimento'],
                    aluno_data.get('cpf'),
                    aluno_data.get('sexo'),
                    aluno_data.get('nacionalidade'),
                    aluno_data.get('telefone'),
                    aluno_data.get('endereco'),
                    aluno_data['turma_id'],
                    aluno_data['status'],
                    aluno_data['valor_mensalidade'],
                    aluno_data['id']
                ))
                aluno_id = aluno_data['id']
                
                # Remover responsáveis antigos
                cursor.execute("DELETE FROM responsaveis WHERE aluno_id = ?", (aluno_id,))
                
                # Se valor mudou, atualizar mensalidades pendentes
                if abs(float(valor_antigo) - float(aluno_data['valor_mensalidade'])) > 0.01:
                    print(f"💰 Valor mudou: R$ {valor_antigo:.2f} → R$ {aluno_data['valor_mensalidade']:.2f}")
                    conn.commit()  # Commit das alterações do aluno primeiro
                    
                    # Atualizar mensalidades pendentes
                    from services.mensalidade_service import MensalidadeService
                    mensalidade_service = MensalidadeService()
                    
                    resultado_atualizacao = mensalidade_service.atualizar_valores_mensalidades_pendentes(
                        aluno_id, aluno_data['valor_mensalidade']
                    )
                    
                    if resultado_atualizacao['success']:
                        print(f"✅ {resultado_atualizacao['mensalidades_atualizadas']} mensalidades atualizadas")
                    else:
                        print(f"⚠️ Erro ao atualizar mensalidades: {resultado_atualizacao['error']}")
                
            else:
                # === CRIAÇÃO DE NOVO ALUNO ===
                print(f"👤 Criando novo aluno: {aluno_data['nome']}")
                
                # Criar novo aluno
                cursor.execute("""
                    INSERT INTO alunos (nome, data_nascimento, cpf, sexo, nacionalidade, telefone, 
                                       endereco, turma_id, status, valor_mensalidade, data_matricula)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, date('now'))
                """, (
                    aluno_data['nome'],
                    aluno_data['data_nascimento'],
                    aluno_data.get('cpf'),
                    aluno_data.get('sexo'),
                    aluno_data.get('nacionalidade'),
                    aluno_data.get('telefone'),
                    aluno_data.get('endereco'),
                    aluno_data['turma_id'],
                    aluno_data['status'],
                    aluno_data['valor_mensalidade']
                ))
                aluno_id = cursor.lastrowid
                
                print(f"✅ Aluno criado com ID: {aluno_id}")
            
            # Salvar responsáveis
            for i, resp in enumerate(responsaveis_data):
                cursor.execute("""
                    INSERT INTO responsaveis (aluno_id, nome, telefone, parentesco, principal)
                    VALUES (?, ?, ?, ?, ?)
                """, (aluno_id, resp['nome'], resp['telefone'], resp['parentesco'], 
                     1 if resp.get('principal', False) else 0))
            
            conn.commit()
            conn.close()
            
            # === GERAR MENSALIDADES PARA NOVO ALUNO ===
            if not is_edicao and aluno_data.get('status', '').lower() == 'ativo':
                print(f"💰 Gerando mensalidades para novo aluno...")
                
                try:
                    from services.mensalidade_service import MensalidadeService
                    mensalidade_service = MensalidadeService()
                    
                    resultado_mensalidades = mensalidade_service.gerar_mensalidades_aluno(aluno_id)
                    
                    if resultado_mensalidades['success']:
                        mensalidades_criadas = resultado_mensalidades.get('mensalidades_criadas', 0)
                        print(f"🎉 {mensalidades_criadas} mensalidades criadas automaticamente!")
                    else:
                        print(f"⚠️ Erro ao gerar mensalidades: {resultado_mensalidades.get('error', 'Erro desconhecido')}")
                        
                except ImportError:
                    print("⚠️ Serviço de mensalidades não disponível")
                except Exception as e:
                    print(f"⚠️ Erro ao gerar mensalidades: {e}")
            
            acao = "atualizado" if is_edicao else "cadastrado"
            print(f"✅ Aluno {acao} com sucesso: {aluno_data['nome']}")
            
            return {'success': True, 'id': aluno_id}
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            print(f"❌ Erro SQL ao salvar aluno: {e}")
            return {'success': False, 'error': str(e)}
        
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"❌ Erro geral ao salvar aluno: {e}")
            return {'success': False, 'error': str(e)}
    
    def listar_alunos(self, turma_id=None):
        """Lista alunos simplificado"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        sql = """
            SELECT 
                a.id, a.nome, a.data_nascimento, a.cpf, a.telefone, a.status,
                a.valor_mensalidade,
                t.nome as turma_nome, t.serie as turma_serie,
                r.nome as responsavel_principal, r.telefone as telefone_responsavel
            FROM alunos a
            INNER JOIN turmas t ON a.turma_id = t.id
            LEFT JOIN responsaveis r ON a.id = r.aluno_id AND r.principal = 1
        """
        
        params = []
        if turma_id:
            sql += " WHERE a.turma_id = ?"
            params.append(turma_id)
        
        sql += " ORDER BY a.nome"
        
        cursor.execute(sql, params)
        
        alunos = []
        for row in cursor.fetchall():
            idade = calculate_age(row[2]) if row[2] else 0
            
            aluno = {
                'id': row[0],
                'nome': row[1],
                'data_nascimento': row[2],
                'cpf': row[3],
                'idade': idade,
                'telefone': row[4],
                'status': row[5],
                'valor_mensalidade': row[6],
                'turma_nome': row[7],
                'turma_serie': row[8],
                'responsavel_principal': row[9] or 'N/I',
                'telefone_responsavel': row[10]
            }
            alunos.append(aluno)
        
        conn.close()
        return alunos
    
    def buscar_aluno_por_id(self, aluno_id):
        """Busca aluno completo com responsáveis"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Dados do aluno
        cursor.execute("""
            SELECT a.*, t.nome as turma_nome, t.serie as turma_serie
            FROM alunos a
            INNER JOIN turmas t ON a.turma_id = t.id
            WHERE a.id = ?
        """, (aluno_id,))
        
        aluno_row = cursor.fetchone()
        if not aluno_row:
            conn.close()
            return None
        
        # Responsáveis
        cursor.execute("""
            SELECT nome, telefone, parentesco, principal
            FROM responsaveis
            WHERE aluno_id = ?
            ORDER BY principal DESC, nome
        """, (aluno_id,))
        
        responsaveis = []
        for resp_row in cursor.fetchall():
            responsaveis.append({
                'nome': resp_row[0],
                'telefone': resp_row[1],
                'parentesco': resp_row[2],
                'principal': bool(resp_row[3])
            })
        
        conn.close()
        
        # Montar dados do aluno
        aluno = {
            'id': aluno_row[0],
            'nome': aluno_row[1],
            'data_nascimento': aluno_row[2],
            'cpf': aluno_row[3],
            'sexo': aluno_row[4],
            'nacionalidade': aluno_row[5],
            'telefone': aluno_row[6],
            'endereco': aluno_row[7],
            'turma_id': aluno_row[8],
            'status': aluno_row[9],
            'valor_mensalidade': aluno_row[10] if len(aluno_row) > 10 else 0,
            'turma_nome': aluno_row[-2],
            'turma_serie': aluno_row[-1],
            'responsaveis': responsaveis
        }
        
        return aluno
    
    def excluir_aluno(self, aluno_id):
        """Exclui aluno e dados relacionados"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Excluir responsáveis (cascade)
            cursor.execute("DELETE FROM responsaveis WHERE aluno_id = ?", (aluno_id,))
            
            # Excluir pagamentos
            cursor.execute("DELETE FROM pagamentos WHERE aluno_id = ?", (aluno_id,))
            
            # Excluir histórico de transferências
            cursor.execute("DELETE FROM historico_transferencias WHERE aluno_id = ?", (aluno_id,))
            
            # Excluir aluno
            cursor.execute("DELETE FROM alunos WHERE id = ?", (aluno_id,))
            
            conn.commit()
            conn.close()
            
            return {'success': True}
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return {'success': False, 'error': str(e)}
    
    def buscar_historico_financeiro(self, aluno_id):
        """Busca histórico financeiro do aluno"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT mes_referencia, valor_original, desconto_aplicado, multa_aplicada,
                   valor_final, data_vencimento, data_pagamento, status
            FROM pagamentos
            WHERE aluno_id = ?
            ORDER BY data_vencimento DESC
        """, (aluno_id,))
        
        historico = []
        for row in cursor.fetchall():
            registro = {
                'mes_referencia': row[0],
                'valor_original': row[1],
                'desconto_aplicado': row[2],
                'multa_aplicada': row[3],
                'valor_final': row[4],
                'data_vencimento': row[5],
                'data_pagamento': row[6],
                'status': row[7]
            }
            historico.append(registro)
        
        conn.close()
        return historico
    
    def buscar_alunos_por_turma(self, turma_id):
        """Busca todos os alunos de uma turma específica"""
        return self.listar_alunos(turma_id)
    
    def atualizar_status_aluno(self, aluno_id, novo_status):
        """Atualiza apenas o status do aluno"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE alunos 
                SET status = ?
                WHERE id = ?
            """, (novo_status, aluno_id))
            
            conn.commit()
            conn.close()
            
            return {'success': True}
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return {'success': False, 'error': str(e)}
    
    def obter_estatisticas_gerais(self):
        """Obtém estatísticas gerais dos alunos"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Total de alunos por status
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'Ativo' THEN 1 END) as ativos,
                    COUNT(CASE WHEN status = 'Inativo' THEN 1 END) as inativos
                FROM alunos
            """)
            
            stats_status = cursor.fetchone()
            
            # Alunos por turma
            cursor.execute("""
                SELECT t.nome, t.serie, COUNT(a.id) as total_alunos
                FROM turmas t
                LEFT JOIN alunos a ON t.id = a.turma_id AND a.status = 'Ativo'
                GROUP BY t.id, t.nome, t.serie
                ORDER BY t.nome
            """)
            
            alunos_por_turma = []
            for row in cursor.fetchall():
                alunos_por_turma.append({
                    'turma_nome': row[0],
                    'serie': row[1],
                    'total_alunos': row[2]
                })
            
            # Média de idade
            cursor.execute("""
                SELECT AVG(CAST((julianday('now') - julianday(data_nascimento)) / 365 AS INTEGER)) as media_idade
                FROM alunos 
                WHERE status = 'Ativo' AND data_nascimento IS NOT NULL
            """)
            
            media_idade = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'total_alunos': stats_status[0] or 0,
                'alunos_ativos': stats_status[1] or 0,
                'alunos_inativos': stats_status[2] or 0,
                'media_idade': round(media_idade, 1),
                'alunos_por_turma': alunos_por_turma
            }
            
        except Exception as e:
            conn.close()
            print(f"Erro ao obter estatísticas gerais: {e}")
            return {
                'total_alunos': 0, 'alunos_ativos': 0, 'alunos_inativos': 0,
                'media_idade': 0, 'alunos_por_turma': []
            }
    
    def verificar_mensalidades_aluno(self, aluno_id):
        """Verifica se aluno tem mensalidades geradas"""
        try:
            from services.mensalidade_service import MensalidadeService
            mensalidade_service = MensalidadeService()
            return mensalidade_service.verificar_mensalidades_aluno(aluno_id)
        except:
            return {'total': 0, 'pagas': 0, 'pendentes': 0}
