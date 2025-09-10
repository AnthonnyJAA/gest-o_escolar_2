#!/usr/bin/env python3
"""
Teste do sistema de pagamento
"""

def test_interface_pagamento():
    """Testa interface de pagamento"""
    import tkinter as tk
    from interface.pagamento_dialog import PagamentoDialog
    
    # Dados de teste
    mensalidade_teste = {
        'id': 1,
        'aluno_nome': 'João Silva',
        'mes_referencia': '2025-09',
        'valor_original': 350.00,
        'data_vencimento': '2025-09-10'
    }
    
    def callback_teste(dados):
        print("✅ Pagamento processado:")
        for key, value in dados.items():
            print(f"   {key}: {value}")
    
    # Criar janela de teste
    root = tk.Tk()
    root.title("Teste - Pagamento")
    root.geometry("400x300")
    
    def abrir_dialog():
        PagamentoDialog(root, mensalidade_teste, callback_teste)
    
    tk.Button(
        root, 
        text="🧪 Testar Dialog de Pagamento",
        command=abrir_dialog,
        font=('Arial', 12, 'bold'),
        bg='#007bff',
        fg='white',
        padx=20,
        pady=10
    ).pack(expand=True)
    
    print("🧪 Teste de pagamento iniciado")
    print("📋 Clique no botão para abrir o dialog")
    print("💡 Teste os atalhos: Enter, F12, Escape")
    
    root.mainloop()

if __name__ == "__main__":
    test_interface_pagamento()
