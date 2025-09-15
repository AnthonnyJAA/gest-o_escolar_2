from database.connection import db
import sqlite3
from datetime import datetime, date, timedelta
import random

def criar_dados_exemplo():
    """Cria dados de exemplo para demonstrar os gráficos"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        print("📊 Gerando dados de exemplo para os gráficos...")
        
        # Verificar se já existem dados
        cursor.execute("SELECT COUNT(*) FROM alunos")
        total_alunos = cursor.fetchone()[0]
        
        if total_alunos > 5:  # Já tem dados suficientes
            print("✅ Dados já existem - pulando geração")
            conn.close()
            return
        
        # Criar turmas de exemplo
        turmas_exemplo = [
            ("1º Ano A", "1º Ano", "2025"),
            ("1º Ano B", "1º Ano", "2025"), 
            ("2º Ano A", "2º Ano", "2025"),
            ("3º Ano A", "3º Ano", "2025"),
            ("Pré-escola", "Infantil", "2025")
        ]
        
        turma_ids = []
        for nome, serie, ano in turmas_exemplo:
            cursor.execute("""
                INSERT OR IGNORE INTO turmas (nome, serie, ano_letivo)
                VALUES (?, ?, ?)
            """, (nome, serie, ano))
            
            cursor.execute("SELECT id FROM turmas WHERE nome = ?", (nome,))
            turma_id = cursor.fetchone()
            if turma_id:
                turma_ids.append(turma_id[0])
        
        # Criar alunos de exemplo
        nomes_exemplo = [
            "Ana Silva Santos", "João Pedro Oliveira", "Maria Eduarda Costa", 
            "Lucas Gabriel Lima", "Sophia Rodrigues", "Miguel Santos Silva",
            "Isabella Ferreira", "Arthur Souza Lima", "Helena Costa Rocha",
            "Bernardo Alves", "Laura Pereira Santos", "Davi Martins Costa",
            "Manuela Lima Souza", "Pedro Henrique Silva", "Giovanna Oliveira",
            "Gabriel Santos Costa", "Valentina Rocha Lima", "Rafael Silva Santos",
            "Alice Pereira Costa", "Enzo Gabriel Oliveira", "Julia Santos Lima",
            "Lorenzo Costa Silva", "Lara Oliveira Santos", "Nicolas Lima Costa"
        ]
        
        aluno_ids = []
        for i, nome in enumerate(nomes_exemplo[:20]):  # 20 alunos
            # Data de nascimento aleatória
            ano_nasc = random.randint(2010, 2018)
            mes_nasc = random.randint(1, 12)
            dia_nasc = random.randint(1, 28)
            data_nasc = date(ano_nasc, mes_nasc, dia_nasc)
            
            # Turma aleatória
            turma_id = random.choice(turma_ids)
            
            # Valor de mensalidade variado
            valor_mensalidade = random.uniform(150.0, 400.0)
            
            # Data de matrícula
            data_matricula = date(2025, random.randint(1, 8), random.randint(1, 28))
            
            cursor.execute("""
                INSERT OR IGNORE INTO alunos 
                (nome, data_nascimento, turma_id, valor_mensalidade, 
                 data_matricula, status, sexo, nacionalidade)
                VALUES (?, ?, ?, ?, ?, 'Ativo', ?, 'Brasileira')
            """, (nome, data_nasc, turma_id, valor_mensalidade, data_matricula,
                  'Masculino' if i % 2 == 0 else 'Feminino'))
            
            cursor.execute("SELECT id FROM alunos WHERE nome = ?", (nome,))
            aluno_result = cursor.fetchone()
            if aluno_result:
                aluno_ids.append(aluno_result[0])
        
        # Criar responsáveis de exemplo
        responsaveis_exemplo = [
            ("Carlos Silva Santos", "(11) 99999-1001", "Pai"),
            ("Marina Silva Santos", "(11) 99999-1002", "Mãe"),
            ("Roberto Oliveira", "(11) 99999-2001", "Pai"),
            ("Patricia Oliveira", "(11) 99999-2002", "Mãe"),
            ("José Costa", "(11) 99999-3001", "Pai"),
            ("Fernanda Costa", "(11) 99999-3002", "Mãe")
        ]
        
        for i, aluno_id in enumerate(aluno_ids[:15]):  # 15 alunos com responsáveis
            resp_index = (i * 2) % len(responsaveis_exemplo)
            nome_resp, telefone, parentesco = responsaveis_exemplo[resp_index]
            
            cursor.execute("""
                INSERT OR IGNORE INTO responsaveis
                (aluno_id, nome, telefone, parentesco, principal)
                VALUES (?, ?, ?, ?, 1)
            """, (aluno_id, nome_resp, telefone, parentesco))
        
        # Gerar mensalidades realistas
        hoje = date.today()
        
        for aluno_id in aluno_ids:
            # Buscar dados do aluno
            cursor.execute("""
                SELECT valor_mensalidade, data_matricula 
                FROM alunos WHERE id = ?
            """, (aluno_id,))
            
            aluno_data = cursor.fetchone()
            if not aluno_data:
                continue
                
            valor_mensalidade, data_matricula_str = aluno_data
            
            # Converter data de matrícula
            if isinstance(data_matricula_str, str):
                data_matricula = datetime.strptime(data_matricula_str, '%Y-%m-%d').date()
            else:
                data_matricula = data_matricula_str
            
            # Gerar mensalidades dos últimos 6 meses até dezembro
            mes_inicio = max(1, data_matricula.month)
            ano = data_matricula.year
            
            for mes in range(mes_inicio, 13):  # até dezembro
                # Data de vencimento (dia 10 do mês)
                try:
                    data_vencimento = date(ano, mes, 10)
                except:
                    continue
                
                # Status baseado na data
                if data_vencimento < hoje:
                    # Mensalidade já vencida - 70% chance de estar paga
                    if random.random() < 0.7:
                        status = 'Pago'
                        # Data de pagamento aleatória após vencimento
                        dias_atraso = random.randint(0, 15)
                        data_pagamento = data_vencimento + timedelta(days=dias_atraso)
                        
                        # Calcular valor com possível desconto ou multa
                        if dias_atraso == 0:
                            # Pagou no prazo - possível desconto
                            desconto = random.choice([0, 10, 15]) if random.random() < 0.3 else 0
                            multa = 0
                        elif dias_atraso <= 5:
                            # Pequeno atraso - sem multa ainda
                            desconto = 0
                            multa = 0
                        else:
                            # Atraso com multa
                            desconto = 0
                            multa = dias_atraso * 2.0  # R$ 2 por dia
                        
                        valor_final = valor_mensalidade - desconto + multa
                    else:
                        status = 'Atrasado'
                        data_pagamento = None
                        desconto = 0
                        multa = 0
                        valor_final = valor_mensalidade
                else:
                    # Mensalidade futura
                    status = 'Pendente'
                    data_pagamento = None
                    desconto = 0
                    multa = 0
                    valor_final = valor_mensalidade
                
                mes_referencia = f"{ano}-{mes:02d}"
                
                cursor.execute("""
                    INSERT OR IGNORE INTO pagamentos
                    (aluno_id, mes_referencia, valor_original, desconto_aplicado,
                     multa_aplicada, valor_final, data_vencimento, data_pagamento,
                     status, pode_receber_multa)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (aluno_id, mes_referencia, valor_mensalidade, desconto or 0,
                      multa or 0, valor_final, data_vencimento, data_pagamento, status))
        
        conn.commit()
        conn.close()
        
        print("✅ Dados de exemplo criados com sucesso!")
        print(f"📊 Criados: {len(turma_ids)} turmas, {len(aluno_ids)} alunos")
        print("🎯 Dados prontos para os gráficos do dashboard!")
        
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"❌ Erro ao criar dados de exemplo: {e}")

if __name__ == "__main__":
    criar_dados_exemplo()