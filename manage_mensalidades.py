#!/usr/bin/env python3
"""
Ferramenta para gerenciar mensalidades
"""

from services.mensalidade_service import MensalidadeService
from services.aluno_service import AlunoService
import sys

def menu_principal():
    """Menu principal da ferramenta"""
    
    mensalidade_service = MensalidadeService()
    aluno_service = AlunoService()
    
    while True:
        print("\n" + "="*50)
        print("🎓 GERENCIADOR DE MENSALIDADES")
        print("="*50)
        print("1. 📋 Gerar mensalidades para um aluno")
        print("2. 🏫 Gerar mensalidades para todos os alunos")
        print("3. 🔄 Recalcular status das mensalidades")
        print("4. 👤 Listar mensalidades de um aluno")
        print("5. 🚪 Sair")
        print("-"*50)
        
        try:
            opcao = input("Digite sua opção: ").strip()
            
            if opcao == '1':
                gerar_mensalidades_aluno(mensalidade_service, aluno_service)
            elif opcao == '2':
                gerar_mensalidades_todos(mensalidade_service)
            elif opcao == '3':
                recalcular_status(mensalidade_service)
            elif opcao == '4':
                listar_mensalidades_aluno(mensalidade_service)
            elif opcao == '5':
                print("👋 Encerrando...")
                break
            else:
                print("❌ Opção inválida!")
                
        except KeyboardInterrupt:
            print("\n👋 Encerrando...")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

def gerar_mensalidades_aluno(mensalidade_service, aluno_service):
    """Gera mensalidades para um aluno específico"""
    try:
        # Listar alunos
        alunos = aluno_service.listar_alunos()
        
        if not alunos:
            print("❌ Nenhum aluno encontrado!")
            return
        
        print("\n📋 Alunos disponíveis:")
        for aluno in alunos[:10]:  # Mostrar apenas os primeiros 10
            print(f"  {aluno['id']:2d} - {aluno['nome']}")
        
        if len(alunos) > 10:
            print(f"  ... e mais {len(alunos) - 10} alunos")
        
        aluno_id = int(input("\nDigite o ID do aluno: "))
        
        resultado = mensalidade_service.gerar_mensalidades_aluno(aluno_id)
        
        if resultado['success']:
            print(f"\n✅ Sucesso!")
            print(f"👤 Aluno: {resultado['aluno']}")
            print(f"📅 Mensalidades criadas: {resultado['mensalidades_criadas']}")
            print(f"📅 Mês da matrícula: {resultado['mes_matricula']}")
            print(f"📅 Ano de referência: {resultado['ano_referencia']}")
        else:
            print(f"\n❌ Erro: {resultado['error']}")
            
    except ValueError:
        print("❌ ID inválido!")
    except Exception as e:
        print(f"❌ Erro: {e}")

def gerar_mensalidades_todos(mensalidade_service):
    """Gera mensalidades para todos os alunos"""
    confirm = input("⚠️ Isso irá gerar mensalidades para TODOS os alunos. Confirma? (s/n): ")
    if confirm.lower() != 's':
        print("❌ Operação cancelada.")
        return
    
    print("🔄 Gerando mensalidades para todos os alunos...")
    resultado = mensalidade_service.gerar_mensalidades_todas_turmas()
    
    print(f"\n📊 Resultado:")
    print(f"👥 Total de alunos: {resultado['total_alunos']}")
    print(f"✅ Sucessos: {resultado['total_sucesso']}")
    print(f"❌ Erros: {resultado['total_erro']}")
    
    if resultado['detalhes']:
        print(f"\n📋 Detalhes:")
        for detalhe in resultado['detalhes'][:10]:  # Mostrar apenas os primeiros 10
            print(f"  {detalhe}")
        
        if len(resultado['detalhes']) > 10:
            print(f"  ... e mais {len(resultado['detalhes']) - 10} resultados")

def recalcular_status(mensalidade_service):
    """Recalcula status das mensalidades"""
    print("🔄 Recalculando status das mensalidades...")
    resultado = mensalidade_service.recalcular_status_mensalidades()
    
    if resultado['success']:
        print(f"✅ {resultado['mensalidades_atualizadas']} mensalidades atualizadas!")
    else:
        print(f"❌ Erro: {resultado['error']}")

def listar_mensalidades_aluno(mensalidade_service):
    """Lista mensalidades de um aluno"""
    try:
        aluno_id = int(input("Digite o ID do aluno: "))
        mensalidades = mensalidade_service.listar_mensalidades_aluno(aluno_id)
        
        if not mensalidades:
            print("❌ Nenhuma mensalidade encontrada!")
            return
        
        aluno_nome = mensalidades[0]['aluno_nome']
        print(f"\n📋 Mensalidades de {aluno_nome}:")
        print("-" * 80)
        print(f"{'Mês/Ano':<10} {'Valor':<12} {'Vencimento':<12} {'Pagamento':<12} {'Status':<10}")
        print("-" * 80)
        
        for m in mensalidades:
            pagamento = m['data_pagamento'] if m['data_pagamento'] else '-'
            print(f"{m['mes_referencia']:<10} R$ {m['valor_final']:>6.2f}    {m['data_vencimento']:<12} {pagamento:<12} {m['status']:<10}")
        
    except ValueError:
        print("❌ ID inválido!")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    menu_principal()
