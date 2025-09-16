# -*- coding: utf-8 -*-
"""
Demonstração Completa dos Cenários Avançados de Transferência
Execute este arquivo para ver todos os 4 cenários em funcionamento
"""

from services.transferencia_avancada_service import TransferenciaAvancadaService
from services.aluno_service import AlunoService
from services.turma_service import TurmaService
from database.connection import db
from datetime import date
import time

def demonstrar_todos_cenarios():
    """Demonstra todos os cenários de transferência"""
    
    print("🎓 DEMONSTRAÇÃO COMPLETA - TRANSFERÊNCIAS AVANÇADAS")
    print("=" * 70)
    print()
    
    # Inicializar serviços
    transfer_service = TransferenciaAvancadaService()
    aluno_service = AlunoService()
    turma_service = TurmaService()
    
    try:
        # Criar dados de exemplo se não existir
        print("📊 Preparando dados de demonstração...")
        from create_sample_data import criar_dados_exemplo
        criar_dados_exemplo()
        print("✅ Dados de exemplo criados/verificados")
        print()
        
        # Listar recursos disponíveis
        turmas = transfer_service.listar_turmas_para_filtro()
        if len(turmas) < 4:
            print("⚠️ Aviso: Poucos dados de exemplo. Alguns cenários podem não funcionar.")
            print()
        
        print(f"📋 Sistema inicializado com:")
        print(f"   • {len(turmas)} turmas disponíveis")
        
        stats = transfer_service.obter_estatisticas_avancadas()
        total_alunos = sum(stats['alunos_por_status'].values())
        print(f"   • {total_alunos} alunos no sistema")
        print()
        
        # === CENÁRIO 1: TRANSFERÊNCIA NO MESMO ANO LETIVO ===
        print("🔄 CENÁRIO 1: TRANSFERÊNCIA NO MESMO ANO LETIVO")
        print("-" * 50)
        demonstrar_cenario_mesmo_ano(transfer_service, turmas)
        print()
        
        # === CENÁRIO 2: TRANSFERÊNCIA PARA NOVO ANO LETIVO ===
        print("📅 CENÁRIO 2: TRANSFERÊNCIA PARA NOVO ANO LETIVO")
        print("-" * 50)
        demonstrar_cenario_novo_ano(transfer_service, turmas)
        print()
        
        # === CENÁRIO 3: DESLIGAMENTO DA ESCOLA ===
        print("❌ CENÁRIO 3: DESLIGAMENTO DA ESCOLA")
        print("-" * 40)
        demonstrar_cenario_desligamento(transfer_service, turmas)
        print()
        
        # === CENÁRIO 4: REATIVAÇÃO DE ALUNO ===
        print("✅ CENÁRIO 4: REATIVAÇÃO DE ALUNO")
        print("-" * 35)
        demonstrar_cenario_reativacao(transfer_service, turmas)
        print()
        
        # === RELATÓRIO FINAL ===
        print("📊 RELATÓRIO FINAL DA DEMONSTRAÇÃO")
        print("=" * 40)
        gerar_relatorio_final(transfer_service)
        
        print("🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a demonstração: {e}")
        return False

def demonstrar_cenario_mesmo_ano(transfer_service, turmas):
    """Demonstra transferência no mesmo ano letivo"""
    try:
        # Encontrar turmas do mesmo ano
        turmas_2025 = [t for t in turmas if '2025' in t['ano_letivo']]
        
        if len(turmas_2025) < 2:
            print("⚠️ Não há turmas suficientes de 2025 para demonstração")
            return
        
        turma_origem = turmas_2025[0]
        turma_destino = turmas_2025[1]
        
        print(f"📤 Origem:  {turma_origem['display']}")
        print(f"📥 Destino: {turma_destino['display']}")
        print()
        
        # Buscar um aluno na turma origem
        alunos = transfer_service.listar_alunos_por_turma(turma_origem['id'])
        alunos_ativos = [a for a in alunos if a['status'] == 'Ativo']
        
        if not alunos_ativos:
            print("⚠️ Nenhum aluno ativo encontrado na turma origem")
            return
        
        aluno = alunos_ativos[0]
        print(f"👤 Aluno selecionado: {aluno['nome']}")
        print(f"💰 Mensalidade atual: R$ {aluno['valor_mensalidade']:.2f}")
        
        # Obter informações da transferência
        info = transfer_service.obter_info_transferencia(
            aluno['id'], turma_origem['id'], turma_destino['id']
        )
        
        if info:
            print(f"🔍 Tipo detectado: {info['tipo_transferencia']}")
            print(f"💰 Valor destino: R$ {info['valor_destino_padrao']:.2f}")
            print(f"⚠️ Pendências: {info['mensalidades_pendentes']} mensalidade(s)")
            print()
            
            if info['tipo_transferencia'] == 'MESMO_ANO':
                # Executar transferência
                alterar_valor = info['valores_diferentes']
                novo_valor = info['valor_destino_padrao'] if alterar_valor else info['valor_atual']
                
                print(f"🚀 Executando transferência...")
                print(f"   {'✅' if alterar_valor else '❌'} Alterando valor da mensalidade: {alterar_valor}")
                
                resultado = transfer_service.transferir_aluno_mesmo_ano(
                    aluno['id'], turma_origem['id'], turma_destino['id'],
                    alterar_valor, novo_valor,
                    "Demonstração - Cenário 1",
                    "Transferência automática para demonstrar o cenário de mesmo ano letivo"
                )
                
                if resultado['success']:
                    print(f"✅ SUCESSO! {resultado['aluno']} transferido")
                    print(f"   De: {resultado['turma_origem']}")
                    print(f"   Para: {resultado['turma_destino']}")
                    if resultado['valor_alterado']:
                        print(f"   💰 Valor alterado: R$ {resultado['valor_anterior']:.2f} → R$ {resultado['valor_novo']:.2f}")
                        print(f"   📋 {resultado['mensalidades_alteradas']} mensalidade(s) atualizada(s)")
                else:
                    print(f"❌ Erro: {resultado['error']}")
            else:
                print("⚠️ Turmas não são do mesmo ano letivo - pulando demonstração")
        else:
            print("❌ Não foi possível obter informações da transferência")
            
    except Exception as e:
        print(f"❌ Erro no cenário 1: {e}")

def demonstrar_cenario_novo_ano(transfer_service, turmas):
    """Demonstra transferência para novo ano letivo"""
    try:
        # Criar turma de 2026 se não existir
        turmas_2025 = [t for t in turmas if '2025' in t['ano_letivo']]
        turmas_2026 = [t for t in turmas if '2026' in t['ano_letivo']]
        
        if not turmas_2025:
            print("⚠️ Nenhuma turma de 2025 encontrada")
            return
            
        if not turmas_2026:
            print("📝 Criando turma de 2026 para demonstração...")
            # Simular criação de turma 2026
            turma_origem = turmas_2025[0]
            print(f"📤 Origem: {turma_origem['display']}")
            print(f"📥 Destino: [Simulado] 6º Ano A - 6º Ano (2026)")
            print()
            
            # Buscar aluno
            alunos = transfer_service.listar_alunos_por_turma(turma_origem['id'])
            alunos_ativos = [a for a in alunos if a['status'] == 'Ativo']
            
            if alunos_ativos:
                aluno = alunos_ativos[0]
                print(f"👤 Aluno selecionado: {aluno['nome']}")
                print(f"💰 Mensalidade atual: R$ {aluno['valor_mensalidade']:.2f}")
                print()
                print("🔍 Tipo detectado: NOVO_ANO")
                print("📋 EFEITOS SIMULADOS:")
                print("   ✅ Preservaria pendências de 2025")
                print("   ✅ Criaria novo contrato para 2026")
                print("   ✅ Geraria 10 mensalidades para 2026")
                print("   ⚠️ Demonstração sem execução real (falta turma 2026)")
            else:
                print("⚠️ Nenhum aluno ativo encontrado")
            
            return
        
        # Se existir turma 2026, fazer transferência real
        turma_origem = turmas_2025[0]
        turma_destino = turmas_2026[0]
        
        print(f"📤 Origem:  {turma_origem['display']}")
        print(f"📥 Destino: {turma_destino['display']}")
        print()
        
        # Buscar um aluno na turma origem
        alunos = transfer_service.listar_alunos_por_turma(turma_origem['id'])
        alunos_ativos = [a for a in alunos if a['status'] == 'Ativo']
        
        if not alunos_ativos:
            print("⚠️ Nenhum aluno ativo encontrado na turma origem")
            return
        
        aluno = alunos_ativos[0]
        print(f"👤 Aluno selecionado: {aluno['nome']}")
        print(f"💰 Mensalidade atual: R$ {aluno['valor_mensalidade']:.2f}")
        print()
        
        # Executar transferência
        print("🚀 Executando transferência para novo ano letivo...")
        
        resultado = transfer_service.transferir_aluno_novo_ano(
            aluno['id'], turma_origem['id'], turma_destino['id'], 
            turma_destino.get('valor_mensalidade_padrao', 350.00),
            "Demonstração - Cenário 2",
            "Transferência automática para demonstrar promoção de ano letivo"
        )
        
        if resultado['success']:
            print(f"✅ SUCESSO! {resultado['aluno']} transferido")
            print(f"   De: {resultado['turma_origem']} ({resultado['ano_origem']})")
            print(f"   Para: {resultado['turma_destino']} ({resultado['ano_destino']})")
            print(f"   💰 Nova mensalidade: R$ {resultado['valor_novo']:.2f}")
            print(f"   📋 {resultado['mensalidades_geradas']} mensalidade(s) criada(s) para {resultado['ano_destino']}")
            print(f"   ⚠️ {resultado['pendencias_preservadas']} pendência(s) preservada(s) de {resultado['ano_origem']}")
        else:
            print(f"❌ Erro: {resultado['error']}")
            
    except Exception as e:
        print(f"❌ Erro no cenário 2: {e}")

def demonstrar_cenario_desligamento(transfer_service, turmas):
    """Demonstra desligamento de aluno"""
    try:
        if not turmas:
            print("⚠️ Nenhuma turma disponível")
            return
        
        turma_origem = turmas[0]
        print(f"📤 Turma: {turma_origem['display']}")
        print()
        
        # Buscar um aluno ativo
        alunos = transfer_service.listar_alunos_por_turma(turma_origem['id'])
        alunos_ativos = [a for a in alunos if a['status'] == 'Ativo']
        
        if not alunos_ativos:
            print("⚠️ Nenhum aluno ativo encontrado para desligamento")
            return
        
        aluno = alunos_ativos[0]
        print(f"👤 Aluno selecionado: {aluno['nome']}")
        print(f"💰 Mensalidade: R$ {aluno['valor_mensalidade']:.2f}")
        print()
        
        print("🚀 Executando desligamento...")
        
        resultado = transfer_service.desligar_aluno(
            aluno['id'],
            "Demonstração - Cenário 3",
            "Desligamento automático para demonstrar preservação de dados"
        )
        
        if resultado['success']:
            print(f"✅ SUCESSO! {resultado['aluno']} desligado")
            print(f"   📤 Última turma: {resultado['turma_origem']}")
            print(f"   📅 Ano letivo: {resultado['ano_letivo']}")
            print(f"   📊 Status: INATIVO")
            if resultado['mensalidades_pendentes'] > 0:
                print(f"   ⚠️ {resultado['mensalidades_pendentes']} pendência(s) preservada(s): R$ {resultado['valor_pendente']:.2f}")
            else:
                print("   ✅ Sem pendências financeiras")
        else:
            print(f"❌ Erro: {resultado['error']}")
            
    except Exception as e:
        print(f"❌ Erro no cenário 3: {e}")

def demonstrar_cenario_reativacao(transfer_service, turmas):
    """Demonstra reativação de aluno"""
    try:
        # Listar alunos inativos
        alunos_inativos = transfer_service.listar_alunos_inativos()
        
        if not alunos_inativos:
            print("⚠️ Nenhum aluno inativo encontrado para reativação")
            print("   (Execute primeiro o Cenário 3 para criar um aluno inativo)")
            return
        
        if not turmas:
            print("⚠️ Nenhuma turma disponível para reativação")
            return
        
        aluno_inativo = alunos_inativos[0]
        turma_destino = turmas[0]
        
        print(f"👤 Aluno selecionado: {aluno_inativo['nome']}")
        print(f"📅 Desligado em: {aluno_inativo['data_desligamento']}")
        print(f"💼 Última turma: {aluno_inativo['ultima_turma']}")
        if aluno_inativo['mensalidades_pendentes'] > 0:
            print(f"⚠️ Pendências: {aluno_inativo['mensalidades_pendentes']} mensalidade(s) - R$ {aluno_inativo['valor_pendente']:.2f}")
        print()
        
        print(f"📥 Nova turma: {turma_destino['display']}")
        valor_mensalidade = turma_destino.get('valor_mensalidade_padrao', 300.00)
        print(f"💰 Nova mensalidade: R$ {valor_mensalidade:.2f}")
        print()
        
        print("🚀 Executando reativação...")
        
        resultado = transfer_service.reativar_aluno(
            aluno_inativo['id'], turma_destino['id'], valor_mensalidade,
            "Demonstração - Cenário 4",
            "Reativação automática para demonstrar restauração de aluno"
        )
        
        if resultado['success']:
            print(f"✅ SUCESSO! {resultado['aluno']} reativado")
            print(f"   📥 Nova turma: {resultado['turma_destino']}")
            print(f"   💰 Mensalidade: R$ {resultado['valor_mensalidade']:.2f}")
            print(f"   📊 Status: ATIVO")
            print(f"   📅 Estava inativo desde: {resultado['data_desligamento']}")
        else:
            print(f"❌ Erro: {resultado['error']}")
            
    except Exception as e:
        print(f"❌ Erro no cenário 4: {e}")

def gerar_relatorio_final(transfer_service):
    """Gera relatório final da demonstração"""
    try:
        # Obter estatísticas atualizadas
        stats = transfer_service.obter_estatisticas_avancadas()
        historico = transfer_service.obter_historico_avancado(limite=10)
        alunos_inativos = transfer_service.listar_alunos_inativos()
        
        print("📊 ESTATÍSTICAS FINAIS:")
        print(f"   👥 Alunos ativos: {stats['alunos_por_status'].get('Ativo', 0)}")
        print(f"   ❌ Alunos inativos: {stats['alunos_por_status'].get('Inativo', 0)}")
        print()
        
        print("🔄 TRANSFERÊNCIAS POR TIPO:")
        for tipo, qtd in stats['por_tipo'].items():
            tipo_nome = {
                'MESMO_ANO': 'Mesmo Ano Letivo',
                'NOVO_ANO': 'Novo Ano Letivo',
                'DESLIGAMENTO': 'Desligamentos',
                'REATIVACAO': 'Reativações'
            }.get(tipo, tipo)
            print(f"   • {tipo_nome}: {qtd}")
        print()
        
        print("📚 ÚLTIMAS TRANSFERÊNCIAS:")
        for i, item in enumerate(historico[:5], 1):
            print(f"   {i}. {item['data_transferencia']} - {item['aluno_nome']}")
            print(f"      {item['tipo_transferencia']}: {item['motivo']}")
        
        if alunos_inativos:
            print()
            print(f"⚠️ ALUNOS INATIVOS: {len(alunos_inativos)}")
            total_pendente = sum(a['valor_pendente'] for a in alunos_inativos)
            if total_pendente > 0:
                print(f"   💰 Total de pendências: R$ {total_pendente:.2f}")
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")

def main():
    """Função principal"""
    print("🎓 SISTEMA DE GESTÃO ESCOLAR v2.1")
    print("🔄 Demonstração Completa de Transferências Avançadas")
    print("=" * 70)
    print()
    
    # Inicializar banco de dados
    try:
        db.init_database()
        print("✅ Banco de dados inicializado")
    except Exception as e:
        print(f"❌ Erro no banco de dados: {e}")
        return 1
    
    # Confirmar demonstração
    resposta = input("🤔 Deseja executar a demonstração completa? (s/n): ")
    if resposta.lower() not in ['s', 'sim', 'y', 'yes']:
        print("👋 Demonstração cancelada pelo usuário")
        return 0
    
    print()
    print("⏳ Iniciando demonstração em 3 segundos...")
    time.sleep(3)
    print()
    
    # Executar demonstração
    sucesso = demonstrar_todos_cenarios()
    
    if sucesso:
        print()
        print("🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print()
        print("💡 PRÓXIMOS PASSOS:")
        print("   1. Execute 'python main_avancado.py' para usar o sistema completo")
        print("   2. Acesse 'Transferências' na barra de navegação")
        print("   3. Teste os 4 cenários implementados na interface gráfica")
        print("   4. Veja os relatórios e estatísticas avançadas")
        print()
        print("📚 Todos os dados e transferências foram preservados no banco!")
    else:
        print("❌ Demonstração não pôde ser concluída completamente")
        print("💡 Execute 'python main_avancado.py' para usar a interface gráfica")
    
    print()
    print("👋 Pressione Enter para sair...")
    input()
    return 0 if sucesso else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Demonstração interrompida pelo usuário")
        exit(0)
    except Exception as e:
        print(f"\n💥 Erro crítico: {e}")
        exit(1)