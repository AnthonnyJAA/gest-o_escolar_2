from database.connection import db
import sqlite3
import pandas as pd
from datetime import datetime
import os
from utils.formatters import format_currency, format_date

# Tentar importar reportlab para PDFs
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Aviso: ReportLab não está disponível. Para gerar PDFs, instale com: pip install reportlab")

class ExportacaoService:
    def __init__(self):
        self.db = db
        # Criar pasta de exportações
        os.makedirs("exportacoes", exist_ok=True)
    
    def exportar_turmas_excel(self, arquivo=None):
        """Exporta dados das turmas para Excel"""
        try:
            if not arquivo:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                arquivo = os.path.join("exportacoes", f"turmas_{timestamp}.xlsx")
            
            # Buscar dados das turmas
            conn = self.db.get_connection()
            query = """
                SELECT 
                    t.id as ID,
                    t.nome as "Nome da Turma",
                    t.serie as "Série",
                    t.ano_letivo as "Ano Letivo",
                    t.valor_mensalidade as "Valor Mensalidade",
                    t.dia_vencimento as "Dia Vencimento",
                    t.dia_limite_desconto as "Dia Limite Desconto",
                    t.percentual_desconto as "% Desconto",
                    t.percentual_multa as "% Multa",
                    COUNT(a.id) as "Total Alunos",
                    t.created_at as "Data Criação"
                FROM turmas t
                LEFT JOIN alunos a ON t.id = a.turma_id AND a.status = 'Ativo'
                GROUP BY t.id
                ORDER BY t.nome
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            # Formatar dados
            if not df.empty:
                df['Valor Mensalidade'] = df['Valor Mensalidade'].apply(
                    lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                )
                df['Data Criação'] = pd.to_datetime(df['Data Criação']).dt.strftime('%d/%m/%Y %H:%M')
            
            # Exportar para Excel
            with pd.ExcelWriter(arquivo, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Turmas', index=False)
                
                # Ajustar larguras das colunas
                worksheet = writer.sheets['Turmas']
                for idx, col in enumerate(df.columns):
                    max_length = max(len(str(col)), df[col].astype(str).str.len().max() if not df.empty else 10)
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
            
            return {'success': True, 'arquivo': arquivo, 'registros': len(df)}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def exportar_alunos_excel(self, arquivo=None):
        """Exporta dados dos alunos para Excel"""
        try:
            if not arquivo:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                arquivo = os.path.join("exportacoes", f"alunos_{timestamp}.xlsx")
            
            conn = self.db.get_connection()
            
            # Query principal dos alunos
            query_alunos = """
                SELECT 
                    a.id as ID,
                    a.nome as "Nome do Aluno",
                    a.data_nascimento as "Data Nascimento",
                    CAST((julianday('now') - julianday(a.data_nascimento)) / 365.25 AS INTEGER) as Idade,
                    a.sexo as Sexo,
                    a.endereco as "Endereço", 
                    a.telefone as Telefone,
                    a.nacionalidade as Nacionalidade,
                    a.possui_alergia as "Possui Alergia",
                    a.detalhes_alergia as "Detalhes Alergia",
                    t.nome as Turma,
                    t.serie as "Série",
                    a.status as Status,
                    a.created_at as "Data Cadastro"
                FROM alunos a
                INNER JOIN turmas t ON a.turma_id = t.id
                ORDER BY a.nome
            """
            
            df_alunos = pd.read_sql_query(query_alunos, conn)
            
            # Query dos responsáveis
            query_responsaveis = """
                SELECT 
                    a.nome as "Nome do Aluno",
                    rf.nome as "Nome Responsável",
                    rf.telefone as "Telefone Responsável",
                    rf.parentesco as Parentesco,
                    CASE WHEN rf.principal = 1 THEN 'Sim' ELSE 'Não' END as Principal
                FROM alunos a
                INNER JOIN responsaveis_financeiros rf ON a.id = rf.aluno_id
                ORDER BY a.nome, rf.principal DESC
            """
            
            df_responsaveis = pd.read_sql_query(query_responsaveis, conn)
            conn.close()
            
            # Formatar dados dos alunos
            if not df_alunos.empty:
                df_alunos['Data Nascimento'] = pd.to_datetime(df_alunos['Data Nascimento']).dt.strftime('%d/%m/%Y')
                df_alunos['Data Cadastro'] = pd.to_datetime(df_alunos['Data Cadastro']).dt.strftime('%d/%m/%Y %H:%M')
            
            # Exportar para Excel com múltiplas abas
            with pd.ExcelWriter(arquivo, engine='openpyxl') as writer:
                df_alunos.to_excel(writer, sheet_name='Alunos', index=False)
                df_responsaveis.to_excel(writer, sheet_name='Responsáveis', index=False)
                
                # Ajustar larguras
                for sheet_name, df in [('Alunos', df_alunos), ('Responsáveis', df_responsaveis)]:
                    if not df.empty:
                        worksheet = writer.sheets[sheet_name]
                        for idx, col in enumerate(df.columns):
                            max_length = max(len(str(col)), df[col].astype(str).str.len().max())
                            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
            
            return {'success': True, 'arquivo': arquivo, 'registros': len(df_alunos)}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def exportar_financeiro_excel(self, arquivo=None, filtros=None):
        """Exporta dados financeiros para Excel"""
        try:
            if not arquivo:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                arquivo = os.path.join("exportacoes", f"financeiro_{timestamp}.xlsx")
            
            conn = self.db.get_connection()
            
            # Query base
            sql = """
                SELECT 
                    p.id as ID,
                    a.nome as Aluno,
                    t.nome as Turma,
                    t.serie as "Série",
                    p.mes_referencia as "Mês/Ano",
                    p.valor_original as "Valor Original",
                    p.desconto_aplicado as Desconto,
                    p.multa_aplicada as Multa,
                    p.valor_final as "Valor Final",
                    p.data_vencimento as Vencimento,
                    p.data_pagamento as Pagamento,
                    p.status as Status,
                    p.observacoes as "Observações"
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                INNER JOIN turmas t ON a.turma_id = t.id
                WHERE 1=1
            """
            
            params = []
            
            # Aplicar filtros se fornecidos
            if filtros:
                if filtros.get('status') and filtros['status'] != 'Todos':
                    sql += " AND p.status = ?"
                    params.append(filtros['status'])
                
                if filtros.get('turma_id') and filtros['turma_id'] != 'Todas':
                    sql += " AND t.id = ?"
                    params.append(filtros['turma_id'])
                
                if filtros.get('mes_ano'):
                    sql += " AND p.mes_referencia = ?"
                    params.append(filtros['mes_ano'])
            
            sql += " ORDER BY p.data_vencimento DESC, a.nome"
            
            df_pagamentos = pd.read_sql_query(sql, conn, params=params)
            
            # Query de resumo
            resumo_sql = """
                SELECT 
                    COUNT(*) as "Total Mensalidades",
                    SUM(CASE WHEN status = 'Pago' THEN 1 ELSE 0 END) as "Pagas",
                    SUM(CASE WHEN status = 'Pendente' THEN 1 ELSE 0 END) as "Pendentes", 
                    SUM(CASE WHEN status = 'Atrasado' THEN 1 ELSE 0 END) as "Atrasadas",
                    SUM(CASE WHEN status = 'Pago' THEN valor_final ELSE 0 END) as "Total Recebido",
                    SUM(CASE WHEN status != 'Pago' THEN valor_final ELSE 0 END) as "Total Pendente"
                FROM pagamentos p
                INNER JOIN alunos a ON p.aluno_id = a.id
                INNER JOIN turmas t ON a.turma_id = t.id
                WHERE 1=1
            """
            
            if filtros:
                if filtros.get('status') and filtros['status'] != 'Todos':
                    resumo_sql += " AND p.status = ?"
                if filtros.get('turma_id') and filtros['turma_id'] != 'Todas':
                    resumo_sql += " AND t.id = ?"
                if filtros.get('mes_ano'):
                    resumo_sql += " AND p.mes_referencia = ?"
            
            df_resumo = pd.read_sql_query(resumo_sql, conn, params=params)
            conn.close()
            
            # Formatar dados
            if not df_pagamentos.empty:
                for col in ['Valor Original', 'Desconto', 'Multa', 'Valor Final']:
                    df_pagamentos[col] = df_pagamentos[col].apply(
                        lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                    )
                
                df_pagamentos['Vencimento'] = pd.to_datetime(df_pagamentos['Vencimento']).dt.strftime('%d/%m/%Y')
                df_pagamentos['Pagamento'] = pd.to_datetime(df_pagamentos['Pagamento'], errors='coerce').dt.strftime('%d/%m/%Y')
                df_pagamentos['Pagamento'] = df_pagamentos['Pagamento'].fillna('-')
            
            if not df_resumo.empty:
                for col in ['Total Recebido', 'Total Pendente']:
                    df_resumo[col] = df_resumo[col].apply(
                        lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                    )
            
            # Exportar para Excel
            with pd.ExcelWriter(arquivo, engine='openpyxl') as writer:
                df_pagamentos.to_excel(writer, sheet_name='Mensalidades', index=False)
                df_resumo.to_excel(writer, sheet_name='Resumo', index=False)
                
                # Ajustar larguras
                for sheet_name, df in [('Mensalidades', df_pagamentos), ('Resumo', df_resumo)]:
                    if not df.empty:
                        worksheet = writer.sheets[sheet_name]
                        for idx, col in enumerate(df.columns):
                            max_length = max(len(str(col)), df[col].astype(str).str.len().max())
                            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
            
            return {'success': True, 'arquivo': arquivo, 'registros': len(df_pagamentos)}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def gerar_relatorio_inadimplencia_pdf(self, arquivo=None):
        """Gera relatório de inadimplência em PDF"""
        if not REPORTLAB_AVAILABLE:
            return {'success': False, 'error': 'ReportLab não está disponível. Instale com: pip install reportlab'}
        
        try:
            if not arquivo:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                arquivo = os.path.join("exportacoes", f"relatorio_inadimplencia_{timestamp}.pdf")
            
            # Buscar dados de inadimplentes
            conn = self.db.get_connection()
            query = """
                SELECT 
                    a.nome as aluno_nome, 
                    t.nome as turma_nome,
                    t.serie,
                    COUNT(p.id) as mensalidades_atrasadas,
                    SUM(p.valor_final) as valor_total_devido,
                    MIN(p.data_vencimento) as primeira_pendencia,
                    rf.nome as responsavel_nome, 
                    rf.telefone as responsavel_telefone
                FROM alunos a
                INNER JOIN turmas t ON a.turma_id = t.id
                INNER JOIN pagamentos p ON a.id = p.aluno_id
                LEFT JOIN responsaveis_financeiros rf ON a.id = rf.aluno_id AND rf.principal = 1
                WHERE p.status IN ('Atrasado', 'Pendente') 
                AND p.data_vencimento < date('now')
                GROUP BY a.id, a.nome, t.nome, t.serie, rf.nome, rf.telefone
                ORDER BY primeira_pendencia ASC, valor_total_devido DESC
            """
            
            cursor = conn.cursor()
            cursor.execute(query)
            inadimplentes = cursor.fetchall()
            conn.close()
            
            # Criar PDF
            doc = SimpleDocTemplate(arquivo, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # Centralizado
            )
            
            story.append(Paragraph("📋 RELATÓRIO DE INADIMPLÊNCIA", title_style))
            story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            if not inadimplentes:
                story.append(Paragraph("✅ Não há alunos inadimplentes no momento!", styles['Normal']))
            else:
                # Resumo
                total_inadimplentes = len(inadimplentes)
                valor_total = sum(row[4] for row in inadimplentes)
                
                resumo_text = f"""
                <b>RESUMO GERAL:</b><br/>
                • Total de alunos inadimplentes: {total_inadimplentes}<br/>
                • Valor total em atraso: {format_currency(valor_total)}<br/>
                • Data do relatório: {datetime.now().strftime('%d/%m/%Y')}
                """
                
                story.append(Paragraph(resumo_text, styles['Normal']))
                story.append(Spacer(1, 20))
                
                # Tabela de inadimplentes
                data = [['Aluno', 'Turma', 'Mens.\nAtrasadas', 'Valor\nDevido', 'Primeira\nPendência', 'Responsável', 'Telefone']]
                
                for row in inadimplentes:
                    data.append([
                        row[0][:20] + "..." if len(row[0]) > 20 else row[0],  # aluno_nome
                        f"{row[1]}\n{row[2]}",  # turma_nome - serie
                        str(row[3]),  # mensalidades_atrasadas
                        format_currency(row[4]),  # valor_total_devido
                        format_date(row[5]),  # primeira_pendencia
                        row[6][:15] + "..." if row[6] and len(row[6]) > 15 else (row[6] or "N/I"),  # responsavel_nome
                        row[7] or "N/I"  # responsavel_telefone
                    ])
                
                # Criar tabela
                table = Table(data, colWidths=[2*inch, 1.5*inch, 0.8*inch, 1*inch, 1*inch, 1.2*inch, 1*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                ]))
                
                story.append(table)
                
                # Rodapé
                story.append(Spacer(1, 30))
                story.append(Paragraph(
                    f"<i>Relatório gerado automaticamente pelo Sistema de Gestão Escolar em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</i>", 
                    styles['Italic']
                ))
            
            # Gerar PDF
            doc.build(story)
            
            return {'success': True, 'arquivo': arquivo, 'inadimplentes': len(inadimplentes) if inadimplentes else 0}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def gerar_relatorio_turmas_pdf(self, arquivo=None):
        """Gera relatório de turmas em PDF"""
        if not REPORTLAB_AVAILABLE:
            return {'success': False, 'error': 'ReportLab não está disponível. Instale com: pip install reportlab'}
        
        try:
            if not arquivo:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                arquivo = os.path.join("exportacoes", f"relatorio_turmas_{timestamp}.pdf")
            
            # Buscar dados das turmas
            conn = self.db.get_connection()
            query = """
                SELECT 
                    t.nome, t.serie, t.ano_letivo, t.valor_mensalidade,
                    t.dia_vencimento, t.percentual_desconto, t.percentual_multa,
                    COUNT(a.id) as total_alunos
                FROM turmas t
                LEFT JOIN alunos a ON t.id = a.turma_id AND a.status = 'Ativo'
                GROUP BY t.id
                ORDER BY t.nome
            """
            
            cursor = conn.cursor()
            cursor.execute(query)
            turmas = cursor.fetchall()
            conn.close()
            
            # Criar PDF
            doc = SimpleDocTemplate(arquivo, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1
            )
            
            story.append(Paragraph("🏫 RELATÓRIO DE TURMAS", title_style))
            story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            if not turmas:
                story.append(Paragraph("Nenhuma turma cadastrada.", styles['Normal']))
            else:
                # Resumo
                total_turmas = len(turmas)
                total_alunos = sum(row[7] for row in turmas)
                receita_potencial = sum(row[3] * row[7] for row in turmas)
                
                resumo_text = f"""
                <b>RESUMO GERAL:</b><br/>
                • Total de turmas: {total_turmas}<br/>
                • Total de alunos: {total_alunos}<br/>
                • Receita potencial mensal: {format_currency(receita_potencial)}
                """
                
                story.append(Paragraph(resumo_text, styles['Normal']))
                story.append(Spacer(1, 20))
                
                # Tabela de turmas
                data = [['Turma', 'Série', 'Ano', 'Mensalidade', 'Venc.', '% Desc.', '% Multa', 'Alunos']]
                
                for row in turmas:
                    data.append([
                        row[0],  # nome
                        row[1],  # serie
                        row[2],  # ano_letivo
                        format_currency(row[3]),  # valor_mensalidade
                        f"Dia {row[4]}",  # dia_vencimento
                        f"{row[5]}%",  # percentual_desconto
                        f"{row[6]}%",  # percentual_multa
                        str(row[7])  # total_alunos
                    ])
                
                table = Table(data, colWidths=[1.8*inch, 1*inch, 0.8*inch, 1.2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
                story.append(Spacer(1, 30))
                story.append(Paragraph(
                    f"<i>Relatório gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</i>", 
                    styles['Italic']
                ))
            
            doc.build(story)
            
            return {'success': True, 'arquivo': arquivo, 'turmas': len(turmas)}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def exportar_backup_dados_excel(self, arquivo=None):
        """Exporta backup completo dos dados em Excel"""
        try:
            if not arquivo:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                arquivo = os.path.join("exportacoes", f"backup_completo_{timestamp}.xlsx")
            
            conn = self.db.get_connection()
            
            # Queries para todas as tabelas
            queries = {
                'Turmas': "SELECT * FROM turmas ORDER BY nome",
                'Alunos': "SELECT * FROM alunos ORDER BY nome", 
                'Responsaveis': "SELECT * FROM responsaveis_financeiros ORDER BY aluno_id, principal DESC",
                'Pagamentos': "SELECT * FROM pagamentos ORDER BY data_vencimento DESC",
                'Configuracoes': "SELECT * FROM configuracoes ORDER BY chave"
            }
            
            # Exportar todas as tabelas
            with pd.ExcelWriter(arquivo, engine='openpyxl') as writer:
                total_registros = 0
                
                for sheet_name, query in queries.items():
                    df = pd.read_sql_query(query, conn)
                    
                    if not df.empty:
                        # Formatar datas
                        for col in df.columns:
                            if 'data' in col.lower() or 'created_at' in col.lower() or 'updated_at' in col.lower():
                                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d/%m/%Y %H:%M')
                        
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        total_registros += len(df)
                        
                        # Ajustar larguras
                        worksheet = writer.sheets[sheet_name]
                        for idx, col in enumerate(df.columns):
                            max_length = max(len(str(col)), df[col].astype(str).str.len().max())
                            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
            
            conn.close()
            
            return {'success': True, 'arquivo': arquivo, 'registros': total_registros}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
