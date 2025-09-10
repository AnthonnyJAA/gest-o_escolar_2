#!/usr/bin/env python3
"""
Teste da funcionalidade de responsáveis
"""

def test_responsavel_modal():
    """Teste simples da janela de responsável"""
    import tkinter as tk
    from interface.alunos import AlunosInterface
    
    # Criar janela de teste
    root = tk.Tk()
    root.title("Teste - Responsáveis")
    root.geometry("800x600")
    
    # Container
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    try:
        # Criar interface de alunos
        alunos_interface = AlunosInterface(main_frame)
        
        # Botão para testar modal
        tk.Button(
            root, text="🧪 Testar Modal Responsável",
            command=alunos_interface.adicionar_responsavel,
            font=('Arial', 12, 'bold'), bg='#007bff', fg='white',
            padx=20, pady=10
        ).pack(pady=20)
        
        print("✅ Interface de teste criada!")
        print("🔍 Clique no botão para testar o modal de responsável")
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        root.destroy()

if __name__ == "__main__":
    test_responsavel_modal()
