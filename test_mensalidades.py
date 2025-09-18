# test_mensalidades.py - Teste das mensalidades

from services.aluno_service import AlunoService
from services.mensalidade_service import MensalidadeService

print("🧪 Testando geração de mensalidades...")

aluno_service = AlunoService()
mensalidade_service = MensalidadeService()

# Listar alunos
alunos = aluno_service.listar_alunos()
print(f"📊 Total de alunos: {len(alunos)}")

if alunos:
    aluno_teste = alunos[0]
    print(f"🧪 Testando com aluno: {aluno_teste['nome']} (ID: {aluno_teste['id']})")
    
    # Verificar mensalidades existentes
    stats = mensalidade_service.verificar_mensalidades_aluno(aluno_teste['id'])
    print(f"📋 Mensalidades existentes: {stats['total']}")
    
    if stats['total'] == 0:
        # Gerar mensalidades
        resultado = mensalidade_service.gerar_mensalidades_aluno(aluno_teste['id'])
        
        if resultado['success']:
            print(f"✅ {resultado['mensalidades_criadas']} mensalidades geradas!")
        else:
            print(f"❌ Erro: {resultado['error']}")
    else:
        print("ℹ️ Aluno já possui mensalidades")

print("🏁 Teste concluído!")
