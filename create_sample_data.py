# -*- coding: utf-8 -*-
"""
📊 Script para Criação de Dados de Exemplo
Sistema de Gestão Escolar v2.1

Este script cria dados de exemplo para testar o sistema:
- Turmas
- Alunos com responsáveis
- Mensalidades automáticas
"""

import sys
import os
from pathlib import Path

# Adicionar diretório atual ao path para importações
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from database.connection import db
    from services.aluno_service import AlunoService
    from services.mensalidade_service import MensalidadeService
    import sqlite3
    from datetime import datetime, date
    import random
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Certifique-se de estar executando na pasta raiz do projeto")
    sys.exit(1)

def criar_turmas_exemplo():
    """Cria turmas de exemplo se não existirem"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Verificar se já existem turmas
        cursor.execute("SELECT COUNT(*) FROM turmas")
        total_turmas = cursor.fetchone()[0]
        
        if total_turmas > 0:
            print(f"ℹ️ Já existem {total_turmas} turmas no sistema")
            conn.close()
            return
        
        print("🏫 Criando turmas de exemplo...")
        
        turmas_exemplo = [
            ("1º Ano A", "1º Ano", "2025"),
            ("1º Ano B", "1º Ano", "2025"),
            ("2º Ano A", "2º Ano", "2025"),
            ("2º Ano B", "2º Ano", "2025"),
            ("3º Ano A", "3º Ano", "2025"),
            ("3º Ano B", "3º Ano", "2025"),
            ("Pré-escola - Infantil", "Infantil", "2025"),
            ("Maternal I", "Infantil", "2025"),
            ("Maternal II", "Infantil", "2025"),
            ("Jardim I", "Infantil", "2025")
        ]
        
        cursor.executemany("""
            INSERT INTO turmas (nome, serie, ano_letivo) 
            VALUES (?, ?, ?)
        """, turmas_exemplo)
        
        conn.commit()
        conn.close()
        
        print(f"✅ {len(turmas_exemplo)} turmas criadas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar turmas: {e}")

def criar_alunos_exemplo():
    """Cria alunos de exemplo com responsáveis"""
    try:
        print("👥 Criando alunos de exemplo...")
        
        aluno_service = AlunoService()
        
        # Buscar turmas disponíveis
        turmas = aluno_service.listar_turmas()
        
        if not turmas:
            print("❌ Nenhuma turma encontrada. Execute criar_turmas_exemplo() primeiro")
            return
        
        # Verificar se já existem alunos
        alunos_existentes = aluno_service.listar_alunos()
        if len(alunos_existentes) >= 10:
            print(f"ℹ️ Já existem {len(alunos_existentes)} alunos no sistema")
            return
        
        # Dados de alunos de exemplo
        alunos_exemplo = [
            {
                'nome': 'Ana Clara Silva Santos',
                'data_nascimento': '2015-03-15',
                'cpf': '123.456.789-01',
                'sexo': 'Feminino',
                'nacionalidade': 'Brasileira',
                'telefone': '(11) 99999-0001',
                'endereco': 'Rua das Flores, 123 - Centro',
                'valor_mensalidade': 850.00,
                'responsaveis': [
                    {'nome': 'Maria Silva Santos', 'telefone': '(11) 98888-0001', 'parentesco': 'Mãe', 'principal': True},
                    {'nome': 'João Silva Santos', 'telefone': '(11) 97777-0001', 'parentesco': 'Pai', 'principal': False}
                ]
            },
            {
                'nome': 'Pedro Henrique Costa',
                'data_nascimento': '2014-07-22',
                'cpf': '234.567.890-12',
                'sexo': 'Masculino',
                'nacionalidade': 'Brasileira',
                'telefone': '(11) 99999-0002',
                'endereco': 'Avenida Principal, 456 - Jardins',
                'valor_mensalidade': 920.00,
                'responsaveis': [
                    {'nome': 'Laura Costa', 'telefone': '(11) 98888-0002', 'parentesco': 'Mãe', 'principal': True}
                ]
            },
            {
                'nome': 'Sofia Rodrigues Lima',
                'data_nascimento': '2013-11-08',
                'cpf': '345.678.901-23',
                'sexo': 'Feminino',
                'nacionalidade': 'Brasileira',
                'telefone': '(11) 99999-0003',
                'endereco': 'Praça da Liberdade, 789 - Vila Nova',
                'valor_mensalidade': 780.50,
                'responsaveis': [
                    {'nome': 'Roberto Oliveira Lima', 'telefone': '(11) 98888-0003', 'parentesco': 'Pai', 'principal': True},
                    {'nome': 'Fernanda Rodrigues', 'telefone': '(11) 97777-0003', 'parentesco': 'Mãe', 'principal': False}
                ]
            },
            {
                'nome': 'Lucas Gabriel Ferreira',
                'data_nascimento': '2014-05-30',
                'cpf': '456.789.012-34',
                'sexo': 'Masculino',
                'nacionalidade': 'Brasileira',
                'telefone': '(11) 99999-0004',
                'endereco': 'Rua do Comércio, 321 - São João',
                'valor_mensalidade': 990.00,
                'responsaveis': [
                    {'nome': 'Carlos Ferreira', 'telefone': '(11) 98888-0004', 'parentesco': 'Pai', 'principal': True}
                ]
            },
            {
                'nome': 'Valentina Santos Pereira',
                'data_nascimento': '2015-09-12',
                'cpf': '567.890.123-45',
                'sexo': 'Feminino',
                'nacionalidade': 'Brasileira',
                'telefone': '(11) 99999-0005',
                'endereco': 'Alameda dos Anjos, 654 - Alto da Serra',
                'valor_mensalidade': 825.75,
                'responsaveis': [
                    {'nome': 'Patrícia Santos', 'telefone': '(11) 98888-0005', 'parentesco': 'Mãe', 'principal': True},
                    {'nome': 'Anderson Pereira', 'telefone': '(11) 97777-0005', 'parentesco': 'Pai', 'principal': False}
                ]
            },
            {
                'nome': 'Arthur Souza Almeida',
                'data_nascimento': '2013-12-25',
                'cpf': '678.901.234-56',
                'sexo': 'Masculino',
                'nacionalidade': 'Brasileira',
                'telefone': '(11) 99999-0006',
                'endereco': 'Travessa da Paz, 987 - Bela Vista',
                'valor_mensalidade': 750.00,
                'responsaveis': [
                    {'nome': 'Cristina Almeida', 'telefone': '(11) 98888-0006', 'parentesco': 'Mãe', 'principal': True}
                ]
            },
            {
                'nome': 'Isabella Ferreira Costa',
                'data_nascimento': '2014-02-14',
                'cpf': '789.012.345-67',
                'sexo': 'Feminino',
                'nacionalidade': 'Brasileira',
                'telefone': '(11) 99999-0007',
                'endereco': 'Rua das Palmeiras, 147 - Parque das Árvores',
                'valor_mensalidade': 880.25,
                'responsaveis': [
                    {'nome': 'Ricardo Costa', 'telefone': '(11) 98888-0007', 'parentesco': 'Pai', 'principal': True},
                    {'nome': 'Juliana Ferreira', 'telefone': '(11) 97777-0007', 'parentesco': 'Mãe', 'principal': False}
                ]
            },
            {
                'nome': 'Miguel Santos Oliveira',
                'data_nascimento': '2015-06-18',
                'cpf': '890.123.456-78',
                'sexo': 'Masculino',
                'nacionalidade': 'Brasileira',
                'telefone': '(11) 99999-0008',
                'endereco': 'Estrada do Sol, 258 - Campo Verde',
                'valor_mensalidade': 795.50,
                'responsaveis': [
                    {'nome': 'Beatriz Oliveira', 'telefone': '(11) 98888-0008', 'parentesco': 'Mãe', 'principal': True}
                ]
            },
            {
                'nome': 'Alice Pereira Rocha',
                'data_nascimento': '2013-10-03',
                'cpf': '901.234.567-89',
                'sexo': 'Feminino',
                'nacionalidade': 'Brasileira',
                'telefone': '(11) 99999-0009',
                'endereco': 'Avenida das Américas, 369 - Novo Mundo',
                'valor_mensalidade': 865.00,
                'responsaveis': [
                    {'nome': 'Marcelo Rocha', 'telefone': '(11) 98888-0009', 'parentesco': 'Pai', 'principal': True},
                    {'nome': 'Carla Pereira', 'telefone': '(11) 97777-0009', 'parentesco': 'Mãe', 'principal': False}
                ]
            },
            {
                'nome': 'Benjamín Silva Martins',
                'data_nascimento': '2014-04-27',
                'cpf': '012.345.678-90',
                'sexo': 'Masculino',
                'nacionalidade': 'Brasileira',
                'telefone': '(11) 99999-0010',
                'endereco': 'Vila Esperança, 741 - Distrito Industrial',
                'valor_mensalidade': 720.00,
                'responsaveis': [
                    {'nome': 'Sandra Martins', 'telefone': '(11) 98888-0010', 'parentesco': 'Mãe', 'principal': True}
                ]
            }
        ]
        
        alunos_criados = 0
        
        for i, aluno_data in enumerate(alunos_exemplo):
            try:
                # Selecionar turma aleatória
                turma_escolhida = random.choice(turmas)
                
                # Preparar dados do aluno
                aluno_dados = {
                    'nome': aluno_data['nome'],
                    'data_nascimento': aluno_data['data_nascimento'],
                    'cpf': aluno_data['cpf'],
                    'sexo': aluno_data['sexo'],
                    'nacionalidade': aluno_data['nacionalidade'],
                    'telefone': aluno_data['telefone'],
                    'endereco': aluno_data['endereco'],
                    'turma_id': turma_escolhida['id'],
                    'status': 'Ativo',
                    'valor_mensalidade': aluno_data['valor_mensalidade']
                }
                
                # Salvar aluno (isso vai gerar mensalidades automaticamente)
                resultado = aluno_service.salvar_aluno(aluno_dados, aluno_data['responsaveis'])
                
                if resultado['success']:
                    alunos_criados += 1
                    print(f"✅ Aluno {i+1}/10 criado: {aluno_data['nome']}")
                else:
                    print(f"❌ Erro ao criar aluno {aluno_data['nome']}: {resultado['error']}")
                
            except Exception as e:
                print(f"❌ Erro ao processar aluno {aluno_data['nome']}: {e}")
        
        print(f"🎉 {alunos_criados} alunos criados com sucesso!")
        print("💰 Mensalidades foram geradas automaticamente para cada aluno!")
        
    except Exception as e:
        print(f"❌ Erro ao criar alunos de exemplo: {e}")

def gerar_mensalidades_para_todos_alunos():
    """Gera mensalidades para todos os alunos ativos que não têm mensalidades"""
    try:
        from services.mensalidade_service import MensalidadeService
        
        print("💰 Verificando e gerando mensalidades para todos os alunos...")
        
        aluno_service = AlunoService()
        mensalidade_service = MensalidadeService()
        
        # Listar todos os alunos ativos
        alunos = aluno_service.listar_alunos()
        alunos_ativos = [a for a in alunos if a['status'] == 'Ativo']
        
        if not alunos_ativos:
            print("ℹ️ Nenhum aluno ativo encontrado")
            return
        
        total_geradas = 0
        alunos_processados = 0
        
        for aluno in alunos_ativos:
            try:
                # Verificar se já tem mensalidades
                stats = mensalidade_service.verificar_mensalidades_aluno(aluno['id'])
                
                if stats['total'] == 0:
                    print(f"📋 Gerando mensalidades para {aluno['nome']}...")
                    
                    resultado = mensalidade_service.gerar_mensalidades_aluno(aluno['id'])
                    
                    if resultado['success']:
                        mensalidades_criadas = resultado.get('mensalidades_criadas', 0)
                        total_geradas += mensalidades_criadas
                        print(f"✅ {mensalidades_criadas} mensalidades criadas")
                    else:
                        print(f"❌ Erro: {resultado.get('error', 'Desconhecido')}")
                else:
                    print(f"ℹ️ {aluno['nome']} já possui {stats['total']} mensalidades")
                
                alunos_processados += 1
                
            except Exception as e:
                print(f"❌ Erro ao processar {aluno['nome']}: {e}")
        
        print(f"🎉 Processamento concluído:")
        print(f"   📊 {alunos_processados} alunos processados")
        print(f"   💰 {total_geradas} mensalidades geradas no total")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar mensalidades em lote: {e}")
        return False

def criar_dados_exemplo():
    """Função principal para criar todos os dados de exemplo"""
    try:
        print("🚀 CRIANDO DADOS DE EXEMPLO PARA O SISTEMA")
        print("=" * 60)
        
        # 1. Verificar se o banco está funcionando
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            total_tabelas = cursor.fetchone()[0]
            conn.close()
            
            if total_tabelas < 5:
                print("⚠️ Banco parece não estar inicializado. Execute o main.py primeiro.")
                return False
            
        except Exception as e:
            print(f"❌ Erro ao verificar banco: {e}")
            return False
        
        # 2. Criar turmas
        criar_turmas_exemplo()
        
        # 3. Criar alunos (mensalidades são geradas automaticamente)
        criar_alunos_exemplo()
        
        # 4. Verificar se há alunos sem mensalidades e gerar
        gerar_mensalidades_para_todos_alunos()
        
        print("=" * 60)
        print("🎉 DADOS DE EXEMPLO CRIADOS COM SUCESSO!")
        print("")
        print("📋 O que foi criado:")
        print("   🏫 10 turmas de diferentes séries")
        print("   👥 10 alunos com responsáveis")
        print("   💰 Mensalidades automáticas (março-dezembro)")
        print("")
        print("🚀 Agora você pode executar o sistema e testar todas as funcionalidades!")
        print("   Execute: python main.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro geral na criação de dados: {e}")
        return False

def obter_estatisticas_sistema():
    """Mostra estatísticas do sistema"""
    try:
        print("📊 ESTATÍSTICAS DO SISTEMA")
        print("=" * 40)
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Total de turmas
        cursor.execute("SELECT COUNT(*) FROM turmas")
        total_turmas = cursor.fetchone()[0]
        print(f"🏫 Turmas: {total_turmas}")
        
        # Total de alunos por status
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM alunos 
            GROUP BY status
        """)
        alunos_por_status = cursor.fetchall()
        
        total_alunos = 0
        for status, count in alunos_por_status:
            print(f"👥 Alunos {status}: {count}")
            total_alunos += count
        
        print(f"👥 Total de Alunos: {total_alunos}")
        
        # Total de responsáveis
        cursor.execute("SELECT COUNT(*) FROM responsaveis")
        total_responsaveis = cursor.fetchone()[0]
        print(f"👨‍👩‍👧‍👦 Responsáveis: {total_responsaveis}")
        
        # Total de mensalidades
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM pagamentos 
            GROUP BY status
        """)
        mensalidades_por_status = cursor.fetchall()
        
        total_mensalidades = 0
        for status, count in mensalidades_por_status:
            print(f"💰 Mensalidades {status}: {count}")
            total_mensalidades += count
        
        print(f"💰 Total de Mensalidades: {total_mensalidades}")
        
        # Total de transferências
        cursor.execute("SELECT COUNT(*) FROM historico_transferencias")
        total_transferencias = cursor.fetchone()[0]
        print(f"🔄 Transferências: {total_transferencias}")
        
        conn.close()
        print("=" * 40)
        
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")

def limpar_dados():
    """Limpa todos os dados do sistema (USE COM CUIDADO!)"""
    try:
        resposta = input("⚠️ ATENÇÃO: Isso vai APAGAR TODOS OS DADOS! Digite 'CONFIRMAR' para continuar: ")
        
        if resposta != "CONFIRMAR":
            print("❌ Operação cancelada")
            return False
        
        print("🗑️ Limpando todos os dados...")
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Ordem importante devido às chaves estrangeiras
        tabelas = [
            'historico_transferencias',
            'pagamentos', 
            'responsaveis',
            'alunos',
            'turmas',
            'configuracoes'
        ]
        
        for tabela in tabelas:
            cursor.execute(f"DELETE FROM {tabela}")
            print(f"✅ Tabela {tabela} limpa")
        
        # Reset dos auto-increment
        cursor.execute("DELETE FROM sqlite_sequence")
        
        conn.commit()
        conn.close()
        
        print("🧹 Todos os dados foram removidos!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao limpar dados: {e}")
        return False

# === EXECUÇÃO PRINCIPAL ===
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerenciar dados de exemplo do Sistema de Gestão Escolar')
    parser.add_argument('--stats', action='store_true', help='Mostrar estatísticas do sistema')
    parser.add_argument('--clean', action='store_true', help='Limpar todos os dados (CUIDADO!)')
    parser.add_argument('--mensalidades', action='store_true', help='Gerar mensalidades para alunos existentes')
    
    args = parser.parse_args()
    
    if args.stats:
        obter_estatisticas_sistema()
    elif args.clean:
        limpar_dados()
    elif args.mensalidades:
        gerar_mensalidades_para_todos_alunos()
    else:
        # Execução padrão - criar dados de exemplo
        criar_dados_exemplo()
