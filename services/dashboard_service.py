from database.connection import db
import sqlite3
from datetime import datetime, date, timedelta
from utils.formatters import format_date
import calendar

class DashboardService:
    def __init__(self):
        self.db = db

    def obter_estatisticas_gerais(self):
        """Obtém estatísticas gerais para o dashboard"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            # Total de alunos ativos
            cursor.execute("SELECT COUNT(*) FROM alunos WHERE status = 'Ativo'")
            total_alunos = cursor.fetchone()[0] or 0

            # Total de turmas
            cursor.execute("SELECT COUNT(*) FROM turmas")
            total_turmas = cursor.fetchone()[0] or 0

            # Receita do mês atual
            mes_atual = date.today().strftime('%Y-%m')
            cursor.execute("""
                SELECT COALESCE(SUM(valor_final), 0)
                FROM pagamentos
                WHERE status = 'Pago'
                AND strftime('%Y-%m', data_pagamento) = ?
            """, (mes_atual,))
            receita_mes = cursor.fetchone()[0] or 0

            # Mensalidades pendentes
            cursor.execute("""
                SELECT COUNT(*)
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                WHERE p.status = 'Pendente'
                AND a.status = 'Ativo'
            """)
            pendentes = cursor.fetchone()[0] or 0

            # Mensalidades atrasadas
            cursor.execute("""
                SELECT COUNT(*)
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                WHERE (p.status = 'Atrasado' OR (p.status = 'Pendente' AND date(p.data_vencimento) < date('now')))
                AND a.status = 'Ativo'
            """)
            atrasadas = cursor.fetchone()[0] or 0

            conn.close()

            return {
                'total_alunos': total_alunos,
                'total_turmas': total_turmas,
                'receita_mes': receita_mes,
                'pendentes': pendentes,
                'atrasadas': atrasadas
            }

        except Exception as e:
            conn.close()
            print(f"Erro ao obter estatísticas: {e}")
            return {
                'total_alunos': 0,
                'total_turmas': 0,
                'receita_mes': 0,
                'pendentes': 0,
                'atrasadas': 0
            }

    def obter_resumos(self):
        """Obtém resumos adicionais"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            # Turma com mais alunos
            cursor.execute("""
                SELECT t.nome, t.serie, COUNT(a.id) as total_alunos
                FROM turmas t
                LEFT JOIN alunos a ON t.id = a.turma_id AND a.status = 'Ativo'
                GROUP BY t.id, t.nome, t.serie
                ORDER BY total_alunos DESC
                LIMIT 1
            """)
            turma_popular_row = cursor.fetchone()
            turma_popular = f"{turma_popular_row[0]} - {turma_popular_row[1]} ({turma_popular_row[2]} alunos)" if turma_popular_row else "N/A"

            # Valor total em aberto
            cursor.execute("""
                SELECT COALESCE(SUM(p.valor_final), 0)
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                WHERE p.status IN ('Pendente', 'Atrasado')
                AND a.status = 'Ativo'
            """)
            valor_aberto = cursor.fetchone()[0] or 0

            # Próximo vencimento
            cursor.execute("""
                SELECT MIN(p.data_vencimento)
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                WHERE p.status = 'Pendente'
                AND date(p.data_vencimento) >= date('now')
                AND a.status = 'Ativo'
            """)
            proximo_venc_row = cursor.fetchone()
            proximo_vencimento = format_date(proximo_venc_row[0]) if proximo_venc_row and proximo_venc_row[0] else "N/A"

            # Meta mensal (valor estimado baseado nos alunos ativos)
            cursor.execute("""
                SELECT COALESCE(SUM(a.valor_mensalidade), 0)
                FROM alunos a
                WHERE a.status = 'Ativo'
            """)
            meta_mensal = cursor.fetchone()[0] or 0

            conn.close()

            return {
                'turma_popular': turma_popular,
                'valor_aberto': valor_aberto,
                'proximo_vencimento': proximo_vencimento,
                'meta_mensal': meta_mensal
            }

        except Exception as e:
            conn.close()
            print(f"Erro ao obter resumos: {e}")
            return {
                'turma_popular': 'N/A',
                'valor_aberto': 0,
                'proximo_vencimento': 'N/A',
                'meta_mensal': 0
            }

    def obter_dados_grafico_status_mensalidades(self):
        """Dados para gráfico de pizza - Status das mensalidades"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN p.status = 'Pago' THEN 'Pagas'
                        WHEN p.status = 'Atrasado' OR (p.status = 'Pendente' AND date(p.data_vencimento) < date('now')) THEN 'Atrasadas'
                        ELSE 'Pendentes'
                    END as status_categoria,
                    COUNT(*) as quantidade
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                WHERE a.status = 'Ativo'
                GROUP BY status_categoria
                ORDER BY quantidade DESC
            """)
            
            dados = cursor.fetchall()
            conn.close()

            labels = [row[0] for row in dados]
            valores = [row[1] for row in dados]
            cores = ['#28a745', '#dc3545', '#ffc107']  # Verde, Vermelho, Amarelo

            return {
                'labels': labels,
                'valores': valores,
                'cores': cores[:len(labels)]
            }

        except Exception as e:
            conn.close()
            print(f"Erro ao obter dados do gráfico de status: {e}")
            return {'labels': [], 'valores': [], 'cores': []}

    def obter_dados_grafico_receita_mensal(self):
        """Dados para gráfico de barras - Receita mensal dos últimos 6 meses"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            # Obter últimos 6 meses
            meses = []
            data_atual = date.today()
            
            for i in range(5, -1, -1):  # 6 meses para trás
                if data_atual.month - i <= 0:
                    mes = data_atual.month - i + 12
                    ano = data_atual.year - 1
                else:
                    mes = data_atual.month - i
                    ano = data_atual.year
                
                meses.append(f"{ano}-{mes:02d}")

            receitas = []
            labels = []

            for mes_ano in meses:
                cursor.execute("""
                    SELECT COALESCE(SUM(valor_final), 0)
                    FROM pagamentos
                    WHERE status = 'Pago'
                    AND strftime('%Y-%m', data_pagamento) = ?
                """, (mes_ano,))
                
                receita = cursor.fetchone()[0] or 0
                receitas.append(receita)
                
                # Converter para nome do mês
                ano, mes = mes_ano.split('-')
                nome_mes = calendar.month_name[int(mes)][:3]  # Primeiras 3 letras
                labels.append(f"{nome_mes}/{ano[2:]}")

            conn.close()

            return {
                'labels': labels,
                'valores': receitas,
                'cor': '#007bff'
            }

        except Exception as e:
            conn.close()
            print(f"Erro ao obter dados de receita mensal: {e}")
            return {'labels': [], 'valores': [], 'cor': '#007bff'}

    def obter_dados_grafico_alunos_por_turma(self):
        """Dados para gráfico de barras - Alunos por turma"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT 
                    t.nome || ' - ' || t.serie as turma_display,
                    COUNT(a.id) as total_alunos
                FROM turmas t
                LEFT JOIN alunos a ON t.id = a.turma_id AND a.status = 'Ativo'
                GROUP BY t.id, t.nome, t.serie
                HAVING total_alunos > 0  -- Apenas turmas com alunos
                ORDER BY total_alunos DESC
                LIMIT 8  -- Top 8 turmas
            """)
            
            dados = cursor.fetchall()
            conn.close()

            labels = [row[0] for row in dados]
            valores = [row[1] for row in dados]

            return {
                'labels': labels,
                'valores': valores,
                'cor': '#28a745'
            }

        except Exception as e:
            conn.close()
            print(f"Erro ao obter dados de alunos por turma: {e}")
            return {'labels': [], 'valores': [], 'cor': '#28a745'}

    def obter_dados_grafico_inadimplencia(self):
        """Dados para gráfico de linha - Evolução da inadimplência"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            # Últimos 6 meses de inadimplência
            meses = []
            data_atual = date.today()
            
            for i in range(5, -1, -1):  # 6 meses para trás
                if data_atual.month - i <= 0:
                    mes = data_atual.month - i + 12
                    ano = data_atual.year - 1
                else:
                    mes = data_atual.month - i
                    ano = data_atual.year
                
                meses.append(f"{ano}-{mes:02d}")

            inadimplencia = []
            labels = []

            for mes_ano in meses:
                # Contar mensalidades atrasadas neste mês
                cursor.execute("""
                    SELECT COUNT(DISTINCT p.aluno_id)
                    FROM pagamentos p
                    INNER JOIN alunos a ON p.aluno_id = a.id
                    WHERE (p.status = 'Atrasado' OR (p.status = 'Pendente' AND date(p.data_vencimento) < date('now')))
                    AND strftime('%Y-%m', p.data_vencimento) <= ?
                    AND a.status = 'Ativo'
                """, (mes_ano,))
                
                total_inadimplentes = cursor.fetchone()[0] or 0
                inadimplencia.append(total_inadimplentes)
                
                # Converter para nome do mês
                ano, mes = mes_ano.split('-')
                nome_mes = calendar.month_name[int(mes)][:3]
                labels.append(f"{nome_mes}/{ano[2:]}")

            conn.close()

            return {
                'labels': labels,
                'valores': inadimplencia,
                'cor': '#dc3545'
            }

        except Exception as e:
            conn.close()
            print(f"Erro ao obter dados de inadimplência: {e}")
            return {'labels': [], 'valores': [], 'cor': '#dc3545'}

    def obter_dados_grafico_top_inadimplentes(self):
        """Dados para gráfico de barras horizontais - Top 5 turmas com mais inadimplentes"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT 
                    t.nome || ' - ' || t.serie as turma_display,
                    COUNT(DISTINCT p.aluno_id) as total_inadimplentes
                FROM turmas t
                INNER JOIN alunos a ON t.id = a.turma_id AND a.status = 'Ativo'
                INNER JOIN pagamentos p ON a.id = p.aluno_id
                WHERE (p.status = 'Atrasado' OR (p.status = 'Pendente' AND date(p.data_vencimento) < date('now')))
                GROUP BY t.id, t.nome, t.serie
                HAVING total_inadimplentes > 0
                ORDER BY total_inadimplentes DESC
                LIMIT 5
            """)
            
            dados = cursor.fetchall()
            conn.close()

            labels = [row[0] for row in dados]
            valores = [row[1] for row in dados]

            return {
                'labels': labels,
                'valores': valores,
                'cor': '#fd7e14'
            }

        except Exception as e:
            conn.close()
            print(f"Erro ao obter dados de top inadimplentes: {e}")
            return {'labels': [], 'valores': [], 'cor': '#fd7e14'}

    def obter_resumo_financeiro_atual(self):
        """Resumo financeiro para exibição rápida"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            # Receita total do ano
            ano_atual = date.today().year
            cursor.execute("""
                SELECT COALESCE(SUM(valor_final), 0)
                FROM pagamentos
                WHERE status = 'Pago'
                AND strftime('%Y', data_pagamento) = ?
            """, (str(ano_atual),))
            receita_ano = cursor.fetchone()[0] or 0

            # Total de alunos inadimplentes
            cursor.execute("""
                SELECT COUNT(DISTINCT p.aluno_id)
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                WHERE (p.status = 'Atrasado' OR (p.status = 'Pendente' AND date(p.data_vencimento) < date('now')))
                AND a.status = 'Ativo'
            """)
            total_inadimplentes = cursor.fetchone()[0] or 0

            # Valor médio de mensalidade
            cursor.execute("""
                SELECT AVG(valor_mensalidade)
                FROM alunos
                WHERE status = 'Ativo'
                AND valor_mensalidade > 0
            """)
            valor_medio = cursor.fetchone()[0] or 0

            conn.close()

            return {
                'receita_ano': receita_ano,
                'total_inadimplentes': total_inadimplentes,
                'valor_medio_mensalidade': valor_medio
            }

        except Exception as e:
            conn.close()
            print(f"Erro ao obter resumo financeiro: {e}")
            return {
                'receita_ano': 0,
                'total_inadimplentes': 0,
                'valor_medio_mensalidade': 0
            }