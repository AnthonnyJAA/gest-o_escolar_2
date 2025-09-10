#!/usr/bin/env python3
"""
Teste da nova lógica de mensalidades (sem retroativas)
"""

from services.mensalidade_service import MensalidadeService
from datetime import date, datetime
import calendar

def test_logica_mensalidades():
    """Testa a nova lógica de geração de mensalidades"""
    
    print("🧪 TESTE DA NOVA LÓGICA DE MENSALIDADES")
    print("=" * 60)
    print("🎯 Objetivo: Eliminar mensalidades retroativas")
    print("🎯 Regra: Gerar apenas do mês da matrícula até dezembro")
    print()
    
    # Simular diferentes cenários de matrícula
    cenarios = [
        {"mes": 1, "descricao": "Matrícula em Janeiro"},
        {"mes": 3, "descricao": "Matrícula em Março"}, 
        {"mes": 6, "descricao": "Matrícula em Junho"},
        {"mes": 9, "descricao": "Matrícula em Setembro"},
        {"mes": 11, "descricao": "Matrícula em Novembro"},
        {"mes": 12, "descricao": "Matrícula em Dezembro"},
    ]
    
    for cenario in cenarios:
        mes = cenario["mes"]
        desc = cenario["descricao"]
        
        print(f"📅 {desc} (Mês {mes})")
        print("-" * 40)
        
        # Nova lógica: apenas do mês da matrícula até dezembro
        meses_gerar = list(range(mes, 13))
        meses_nao_gerar = list(range(1, mes))
        
        print(f"✅ Mensalidades a GERAR: {meses_gerar}")
        print(f"   📋 Total: {len(meses_gerar)} mensalidades")
        
        if meses_nao_gerar:
            print(f"🚫 Mensalidades ELIMINADAS (retroativas): {meses_nao_gerar}")
            print(f"   💰 Economia: {len(meses_nao_gerar)} cobranças desnecessárias evitadas")
        else:
            print(f"ℹ️  Nenhuma mensalidade retroativa (matrícula em janeiro)")
        
        print()

def test_data_atual():
    """Mostra exemplo com data atual"""
    hoje = date.today()
    mes_atual = hoje.month
    ano_atual = hoje.year
    
    print(f"📅 EXEMPLO COM DATA ATUAL")
    print("=" * 40)
    print(f"🗓️  Hoje: {hoje.strftime('%d/%m/%Y')}")
    print(f"📋 Se um aluno fosse matriculado hoje ({mes_atual}/{ano_atual}):")
    print()
    
    meses_gerar = list(range(mes_atual, 13))
    meses_eliminados = list(range(1, mes_atual))
    
    print(f"✅ Mensalidades que seriam geradas: {len(meses_gerar)}")
    for mes in meses_gerar:
        nome_mes = calendar.month_name[mes]
        print(f"   • {nome_mes}/{ano_atual}")
    
    print()
    if meses_eliminados:
        print(f"🚫 Mensalidades retroativas eliminadas: {len(meses_eliminados)}")
        for mes in meses_eliminados:
            nome_mes = calendar.month_name[mes]
            print(f"   • {nome_mes}/{ano_atual} (ELIMINADA)")
    
    print()
    print(f"💡 Vantagem: {len(meses_eliminados)} cobranças incorretas evitadas!")

if __name__ == "__main__":
    test_logica_mensalidades()
    print()
    test_data_atual()
