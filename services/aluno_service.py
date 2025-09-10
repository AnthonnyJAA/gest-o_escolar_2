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
        """Salva aluno e responsáveis - SEM EMAIL"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            if 'id' in aluno_data:
                # Atualizar aluno existente (SEM EMAIL)
                cursor.execute("""
                    UPDATE alunos 
                    SET nome = ?, data_nascimento = ?, cpf = ?, sexo = ?, endereco = ?, 
                        telefone = ?, nacionalidade = ?, turma_id = ?, status = ?
                    WHERE id = ?
                """, (
                    aluno_data['nome'],
                    aluno_data['data_nascimento'],
                    aluno_data.get('cpf'),
                    aluno_data.get('sexo'),
                    aluno_data.get('endereco'),
                    aluno_data.get('telefone'),
                    aluno_data.get('nacionalidade'),
                    aluno_data['turma_id'],
                    aluno_data['status'],
                    aluno_data['id']
                ))
                aluno_id = aluno_data['id']
                
                # Remover responsáveis antigos
                cursor.execute("DELETE FROM responsaveis_financeiros WHERE aluno_id = ?", (aluno_id,))
            else:
                # Criar novo aluno (SEM EMAIL)
                cursor.execute("""
                    INSERT INTO alunos (nome, data_nascimento, cpf, sexo, endereco, telefone, 
                                       nacionalidade, turma_id, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    aluno_data['nome'],
                    aluno_data['data_nascimento'],
                    aluno_data.get('cpf'),
                    aluno_data.get('sexo'),
                    aluno_data.get('endereco'),
                    aluno_data.get('telefone'),
                    aluno_data.get('nacionalidade'),
                    aluno_data['turma_id'],
                    aluno_data['status']
                ))
                aluno_id = cursor.lastrowid
            
            # Salvar responsáveis (SEM EMAIL)
            for i, resp in enumerate(responsaveis_data):
                cursor.execute("""
                    INSERT INTO responsaveis_financeiros (aluno_id, nome, telefone, parentesco, principal)
                    VALUES (?, ?, ?, ?, ?)
                """, (aluno_id, resp['nome'], resp['telefone'], resp['parentesco'], 1 if i == 0 else 0))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'id': aluno_id}
            
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return {'success': False, 'error': str(e)}
    
    def listar_alunos(self, turma_id=None):
        """Lista alunos com informações básicas"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        sql = """
            SELECT 
                a.id,
                a.nome,
                a.data_nascimento,
                a.cpf,
                a.telefone,
                a.status,
                t.nome as turma_nome,
                t.serie as turma_serie,
                rf.nome as responsavel_principal,
                rf.telefone as telefone_responsavel
            FROM alunos a
            INNER JOIN turmas t ON a.turma_id = t.id
            LEFT JOIN responsaveis_financeiros rf ON a.id = rf.aluno_id AND rf.principal = 1
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
                'turma_nome': row[6],
                'turma_serie': row[7],
                'responsavel_principal': row[8] or 'N/I',
                'telefone_responsavel': row[9]
            }
            alunos.append(aluno)
        
        conn.close()
        return alunos
    
    def buscar_aluno_por_id(self, aluno_id):
        """Busca aluno completo por ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Dados do aluno (SEM EMAIL)
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
            FROM responsaveis_financeiros
            WHERE aluno_id = ?
            ORDER BY principal DESC
        """, (aluno_id,))
        
        responsaveis = []
        for resp_row in cursor.fetchall():
            responsaveis.append({
                'nome': resp_row[0],
                'telefone': resp_row[1],
                'parentesco': resp_row[2],
                'principal': resp_row[3]
            })
        
        conn.close()
        
        # Montar dados do aluno (SEM EMAIL)
        aluno = {
            'id': aluno_row[0],
            'nome': aluno_row[1],
            'data_nascimento': aluno_row[2],
            'cpf': aluno_row[3],
            'sexo': aluno_row[4],
            'endereco': aluno_row[5],
            'telefone': aluno_row[6],
            'nacionalidade': aluno_row[7],
            'turma_id': aluno_row[8],
            'status': aluno_row[9],
            'turma_nome': aluno_row[11],
            'turma_serie': aluno_row[12],
            'responsaveis': responsaveis
        }
        
        return aluno
    
    def excluir_aluno(self, aluno_id):
        """Exclui aluno e dados relacionados"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Excluir responsáveis (cascade)
            cursor.execute("DELETE FROM responsaveis_financeiros WHERE aluno_id = ?", (aluno_id,))
            
            # Excluir pagamentos
            cursor.execute("DELETE FROM pagamentos WHERE aluno_id = ?", (aluno_id,))
            
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
    
    def gerar_mensalidades_aluno(self, aluno_id):
        """Gera mensalidades automáticas para novo aluno - SEM IMPORTAÇÃO CIRCULAR"""
        try:
            print(f"🔄 Iniciando geração de mensalidades para aluno ID: {aluno_id}")
            
            # Importar apenas quando necessário para evitar ciclo
            from services.mensalidade_service import MensalidadeService
            
            mensalidade_service = MensalidadeService()
            resultado = mensalidade_service.gerar_mensalidades_aluno(aluno_id)
            
            if resultado['success']:
                print(f"✅ Mensalidades geradas: {resultado.get('mensalidades_criadas', 0)} parcelas")
            else:
                print(f"❌ Erro ao gerar mensalidades: {resultado.get('error', 'Erro desconhecido')}")
                
            return resultado
        except Exception as e:
            erro_msg = f"Erro inesperado ao gerar mensalidades: {str(e)}"
            print(f"❌ {erro_msg}")
            return {'success': False, 'error': erro_msg}
