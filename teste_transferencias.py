# -*- coding: utf-8 -*-
"""
Demonstração do Sistema de Transferências
Executa transferências de exemplo para mostrar o funcionamento
"""

from services.transferencia_service import TransferenciaService
from services.aluno_service import AlunoService
from services.turma_service import TurmaService
from database.connection import db
from datetime import date

def demonstrar_transferencias():
    """Demonstra as funcionalidades do sistema de transferências"""
    
    print("🔄 DEMONSTRAÇÃO DO SISTEMA DE TRANSFERÊNCIAS")
    print("=" * 60)
    
    # Inicializar serviços
    transfer_service = TransferenciaService()
    aluno_service = AlunoService()
    turma_service = TurmaService()
    
    try:
        # 1. Listar turmas disponíveis
        print("\n📋 1. TURMAS DISPONÍVEIS:")
        print("-" * 30)
        turmas = transfer_service.listar_turmas_para_filtro()
        
        for i, turma in enumerate(turmas[:5]):  # Mostrar apenas 5 turmas
            print(f"{i+1}. {turma['display']}")
        
        if len(turmas) < 2:
            print("⚠️ É necessário pelo menos 2 turmas para demonstrar transferências")
            return False
        
        # 2. Selecionar turmas de origem e destino
        turma_origem = turmas[0]  # Primeira turma
        turma_destino = turmas[1] if len(turmas) > 1 else turmas[0]  # Segunda turma
        
        print(f"\n🎯 2. TURMAS SELECIONADAS:")
        print("-" * 30)
        print(f"📤 Origem:  {turma_origem['display']}")
        print(f"📥 Destino: {turma_destino['display']}")
        
        # 3. Listar alunos da turma de origem
        print(f"\n👥 3. ALUNOS DA TURMA DE ORIGEM:")
        print("-" * 30)
        alunos = transfer_service.listar_alunos_por_turma(turma_origem['id'])
        
        if not alunos:
            print("📭 Nenhum aluno encontrado na turma de origem")
            return False
        
        for i, aluno in enumerate(alunos[:3]):  # Mostrar apenas 3 alunos
            print(f"{i+1}. {aluno['nome']} - {aluno['idade']} anos - R$ {aluno['valor_mensalidade']:.2f}")
        
        # 4. Demonstrar validação
        print(f"\n🔍 4. VALIDANDO TRANSFERÊNCIA:")
        print("-" * 30)
        aluno_teste = alunos[0]  # Primeiro aluno
        
        validacao = transfer_service.validar_transferencia(
            aluno_teste['id'], 
            turma_destino['id']
        )
        
        if validacao['valido']:
            print(f"✅ Transferência válida para {aluno_teste['nome']}")
            print(f"   De: {validacao['turma_atual']}")
            print(f"   Para: {validacao['turma_destino']}")
        else:
            print(f"❌ Problema na validação: {validacao['erro']}")
            return False
        
        # 5. Executar transferência de exemplo
        print(f"\n🚀 5. EXECUTANDO TRANSFERÊNCIA DE DEMONSTRAÇÃO:")
        print("-" * 30)
        
        resultado = transfer_service.transferir_aluno(
            aluno_id=aluno_teste['id'],
            turma_origem_id=turma_origem['id'],
            turma_destino_id=turma_destino['id'],
            motivo="Demonstração do sistema",
            observacoes="Transferência automática para demonstração das funcionalidades"
        )
        
        if resultado['success']:
            print(f"✅ Sucesso! {resultado['aluno']} transferido com sucesso!")
            print(f"   De: {resultado['turma_origem']}")
            print(f"   Para: {resultado['turma_destino']}")
        else:
            print(f"❌ Erro na transferência: {resultado['error']}")
            return False
        
        # 6. Mostrar histórico
        print(f"\n📚 6. HISTÓRICO DE TRANSFERÊNCIAS:")
        print("-" * 30)
        historico = transfer_service.obter_historico_transferencias(5)
        
        for item in historico:
            print(f"📅 {item['data_transferencia']} - {item['aluno_nome']}")
            print(f"   {item['turma_origem']} → {item['turma_destino']}")
            print(f"   Motivo: {item['motivo']}")
            print()
        
        # 7. Estatísticas
        print(f"\n📊 7. ESTATÍSTICAS ATUAIS:")
        print("-" * 30)
        stats = transfer_service.obter_estatisticas_transferencias()
        
        print(f"📊 Total de transferências: {stats['total_transferencias']}")
        print(f"📅 Transferências este mês: {stats['transferencias_mes']}")
        print(f"📈 Turma que mais recebe: {stats['turma_mais_recebe']}")
        print(f"📉 Turma que mais perde: {stats['turma_mais_perde']}")
        
        # 8. Demonstrar transferência em lote (simulação)
        print(f"\n🎯 8. SIMULAÇÃO DE TRANSFERÊNCIA EM LOTE:")
        print("-" * 30)
        
        if len(alunos) >= 2:
            alunos_lote = [alunos[1]['id']]  # Segundo aluno, se existir
            
            print(f"Simulando transferência de {len(alunos_lote)} aluno(s)...")
            print("(Esta é apenas uma simulação - não será executada)")
            print(f"Aluno selecionado: {alunos[1]['nome']}")
        
        print(f"\n✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante a demonstração: {e}")
        return False

def criar_transferencias_exemplo():
    """Cria algumas transferências de exemplo para demonstrar o histórico"""
    
    print("\n🎲 Criando transferências de exemplo...")
    
    transfer_service = TransferenciaService()
    
    try:
        turmas = transfer_service.listar_turmas_para_filtro()
        
        if len(turmas) < 2:
            print("⚠️ Necessário pelo menos 2 turmas")
            return
        
        # Pegar alguns alunos aleatoriamente
        from random import choice, sample
        
        for i in range(3):  # Criar 3 transferências de exemplo
            turma_origem = choice(turmas)
            turma_destino = choice([t for t in turmas if t['id'] != turma_origem['id']])
            
            alunos = transfer_service.listar_alunos_por_turma(turma_origem['id'])
            
            if alunos:
                aluno = choice(alunos)
                
                motivos = [
                    "Promoção para próxima série",
                    "Mudança de turno",
                    "Remanejamento de turma", 
                    "Solicitação dos pais",
                    "Adequação pedagógica"
                ]
                
                resultado = transfer_service.transferir_aluno(
                    aluno_id=aluno['id'],
                    turma_origem_id=turma_origem['id'],
                    turma_destino_id=turma_destino['id'],
                    motivo=choice(motivos),
                    observacoes=f"Transferência de exemplo #{i+1} para demonstração"
                )
                
                if resultado['success']:
                    print(f"✅ Exemplo {i+1}: {aluno['nome']} transferido")
                else:
                    print(f"❌ Exemplo {i+1} falhou: {resultado['error']}")
    
    except Exception as e:
        print(f"❌ Erro ao criar exemplos: {e}")

if __name__ == "__main__":
    print("🎓 SISTEMA DE GESTÃO ESCOLAR v2.0")
    print("🔄 Teste do Sistema de Transferências")
    print("=" * 60)
    
    # Inicializar banco de dados
    try:
        db.init_database()
        print("✅ Banco de dados inicializado")
    except Exception as e:
        print(f"❌ Erro no banco de dados: {e}")
        exit(1)
    
    # Verificar se existem dados de exemplo
    try:
        from create_sample_data import criar_dados_exemplo
        criar_dados_exemplo()
        print("✅ Dados de exemplo verificados")
    except Exception as e:
        print(f"⚠️ Aviso: {e}")
    
    # Executar demonstração
    sucesso = demonstrar_transferencias()
    
    if sucesso:
        # Criar alguns exemplos adicionais
        resposta = input("\n🎲 Deseja criar transferências de exemplo adicionais? (s/n): ")
        if resposta.lower() in ['s', 'sim', 'y', 'yes']:
            criar_transferencias_exemplo()
        
        print("\n🎉 Teste concluído! Execute 'python main.py' para ver o sistema completo.")
    else:
        print("\n❌ Teste não pôde ser concluído. Verifique se há dados suficientes no banco.")
    
    print("\n👋 Pressione Enter para sair...")
    input()