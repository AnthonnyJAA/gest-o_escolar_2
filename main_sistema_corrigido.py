# -*- coding: utf-8 -*-
"""
Sistema de Gestão Escolar v2.1 - TOTALMENTE CORRIGIDO
Problemas resolvidos: Financeiro + Transferências
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

def verificar_estrutura_projeto():
    """Verifica se a estrutura do projeto está correta"""
    estrutura_necessaria = [
        'services',
        'interface', 
        'database',
        'utils'
    ]
    
    for pasta in estrutura_necessaria:
        if not os.path.exists(pasta):
            return False, f"Pasta '{pasta}' não encontrada"
    
    return True, "Estrutura OK"

def main():
    """Função principal"""
    try:
        print("🎓 SISTEMA DE GESTÃO ESCOLAR v2.1 - TOTALMENTE CORRIGIDO")
        print("=" * 60)
        print("🔧 Problemas RESOLVIDOS:")
        print("   ✅ Financeiro: Campos habilitados e funcionando")
        print("   ✅ Transferências: Carregamento de dados corrigido")
        print("   ✅ Nova lógica: Original - Desconto + Multa + Outros")
        print("=" * 60)
        
        # Verificar estrutura do projeto
        estrutura_ok, msg = verificar_estrutura_projeto()
        if not estrutura_ok:
            messagebox.showerror("Erro de Estrutura", 
                f"Estrutura do projeto incorreta:\n{msg}\n\n"
                f"Certifique-se de executar na pasta raiz com as pastas:\n"
                f"• services/\n• interface/\n• database/\n• utils/")
            return 1
        
        print("✅ Estrutura do projeto verificada")
        
        # Verificar arquivos corrigidos
        arquivos_corrigidos = [
            'interface/financeiro_corrigido.py',
            'interface/transferencia_corrigida.py', 
            'interface/main_window_corrigido.py'
        ]
        
        arquivos_faltando = []
        for arquivo in arquivos_corrigidos:
            if not os.path.exists(arquivo):
                arquivos_faltando.append(arquivo)
        
        if arquivos_faltando:
            messagebox.showerror("Arquivos Corrigidos Não Encontrados",
                f"Os seguintes arquivos corrigidos não foram encontrados:\n\n" +
                "\n".join(f"• {arq}" for arq in arquivos_faltando) +
                "\n\nBaixe os arquivos corrigidos e coloque nas pastas corretas.")
            return 1
        
        print("✅ Arquivos corrigidos encontrados")
        
        # Mostrar informações de correção
        info_msg = """
🎉 SISTEMA TOTALMENTE CORRIGIDO!

🔧 O QUE FOI CORRIGIDO:

💰 MÓDULO FINANCEIRO:
✅ Campos de entrada HABILITADOS
✅ Seleção de mensalidade FUNCIONANDO
✅ Botão "Dar Baixa" ATIVO
✅ Nova lógica implementada:
   Total = Original - Desconto + Multa + Outros

🔄 MÓDULO TRANSFERÊNCIAS:
✅ Carregamento de turmas FUNCIONANDO
✅ Lista de alunos FUNCIONANDO  
✅ Seleção múltipla com checkboxes
✅ Validações completas

🎯 COMO TESTAR:
1. Clique em "💰 Financeiro"
2. Selecione uma mensalidade na lista
3. Os campos devem habilitar automaticamente
4. Teste a nova lógica de pagamentos

5. Clique em "🔄 Transferências"
6. Selecione uma turma de origem
7. Os alunos devem carregar automaticamente
8. Teste a transferência

Deseja executar o sistema corrigido?
        """
        
        if not messagebox.askyesno("Sistema Corrigido", info_msg.strip()):
            return 0
        
        # Importar e executar sistema corrigido
        print("🚀 Carregando sistema corrigido...")
        
        from interface.main_window_corrigido import SistemaGestaoEscolarCorrigido
        
        print("✅ Módulos carregados com sucesso!")
        
        # Criar e executar aplicação
        app = SistemaGestaoEscolarCorrigido()
        app.run()
        
        print("👋 Sistema encerrado com sucesso")
        return 0
        
    except ImportError as e:
        error_msg = f"""
❌ ERRO DE IMPORTAÇÃO

Problema: {str(e)}

🔧 SOLUÇÕES POSSÍVEIS:

1. VERIFIQUE OS ARQUIVOS:
   • financeiro_corrigido.py → interface/
   • transferencia_corrigida.py → interface/  
   • main_window_corrigido.py → interface/

2. EXECUTE NA PASTA RAIZ:
   Certifique-se de estar na pasta que contém:
   • services/
   • interface/
   • database/ 
   • utils/

3. ESTRUTURA ESPERADA:
   SEU-PROJETO/
   ├── services/
   ├── interface/
   │   ├── financeiro_corrigido.py
   │   ├── transferencia_corrigida.py
   │   └── main_window_corrigido.py
   ├── database/
   ├── utils/
   └── main.py

4. SE PERSISTIR:
   Execute o sistema original: python main_original.py
        """
        
        print(error_msg)
        messagebox.showerror("Erro de Importação", error_msg.strip())
        return 1
        
    except Exception as e:
        error_msg = f"Erro inesperado: {str(e)}"
        print(f"💥 {error_msg}")
        messagebox.showerror("Erro", error_msg)
        return 1

if __name__ == "__main__":
    # Configurar console Windows
    if sys.platform == "win32":
        try:
            os.system("title Sistema de Gestão Escolar v2.1 - CORRIGIDO")
        except:
            pass
    
    # Executar
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Sistema interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Erro crítico: {e}")
        sys.exit(1)