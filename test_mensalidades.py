#!/usr/bin/env python3
"""
Teste das regras de geração de mensalidades
"""

from services.mensalidade_service import MensalidadeService
from datetime import date
import sys

def testar_regras_mensalidades():
    """Testa as regras de geração de mensalidades"""
    
    print("🎓 TESTE DAS REGRAS DE MENSALIDADES")
    print("=" * 50)
    
    # Simular diferentes cenários
    cenarios = [
        {"mes": 1, "descricao": "Matrícula em Janeiro"},
        {"mes": 3, "descricao": "Matrícula em Março"}, 
        {"mes": 6, "descricao": "Matrícula em Junho"},
        {"mes": 9, "descricao": "Matrícula em Setembro"},
        {"mes": 11, "descricao": "Matrícula em Novembro"},
    ]
    
    for cenario in cenarios:
        mes = cenario["mes"]
        desc = cenario["descricao"]
        
        print(f"\n📅 {desc} (Mês {mes})")
        print("-" * 30)
        
        if mes == 1:
            print("✅ Regra: Criar 12 mensalidades (Janeiro a Dezembro)")
            meses = list(range(1, 13))
        else:
            print(f"✅ Regra: Criar mensalidades do mês {mes} até Dezembro")
            print(f"✅ Regra: Criar mensalidades dos meses 1 a {mes-1} como 'Pendente'")
            meses_passados = list(range(1, mes))
            meses_futuros = list(range(mes, 13))
            meses = meses_passados + meses_futuros
        
        print(f"📋 Meses a gerar: {meses}")
        
        # Mostrar status que seria aplicado
        hoje = date.today()
        for m in meses:
            if m < mes:
                status = "Pendente (mês passado)"
            else:
                status = "Pendente (atual/futuro)"
            print(f"  - Mês {m:2d}: {status}")

def main():
    print("Executando teste de regras...")
    testar_regras_mensalidades()
    
    resposta = input("\n❓ Deseja testar geração real de mensalidades para um aluno? (s/n): ")
    if resposta.lower() == 's':
        try:
            aluno_id = input("Digite o ID do aluno: ")
            mensalidade_service = MensalidadeService()
            resultado = mensalidade_service.gerar_mensalidades_aluno(int(aluno_id))
            
            print(f"\n📋 Resultado: {resultado}")
            
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
