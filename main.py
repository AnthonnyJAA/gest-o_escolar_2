# -*- coding: utf-8 -*-
"""
Sistema de Gestão Escolar v2.0
Sistema completo para gerenciamento escolar
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

def main():
    """Função principal"""
    try:
        print("🎓 Sistema de Gestão Escolar v2.0")
        print("📚 Inicializando sistema...")
        
        # Verificar versão do Python
        if sys.version_info < (3, 6):
            messagebox.showerror("Erro", "Python 3.6+ é necessário!")
            return 1
        
        # Verificar tkinter
        try:
            import tkinter
            import tkinter.ttk
        except ImportError as e:
            messagebox.showerror("Erro", f"Tkinter não encontrado: {e}")
            return 1
        
        print("🚀 Carregando interface...")
        
        # Importar e iniciar sistema
        from interface.main_window import SistemaGestaoEscolar
        
        print("✅ Sistema carregado!")
        
        # Criar e executar aplicação
        app = SistemaGestaoEscolar()
        app.run()
        
        print("👋 Sistema encerrado.")
        return 0
        
    except ImportError as e:
        error_msg = f"Erro ao importar módulos: {str(e)}"
        print(f"❌ {error_msg}")
        messagebox.showerror("Erro de Importação", error_msg)
        return 1
        
    except Exception as e:
        error_msg = f"Erro inesperado: {str(e)}"
        print(f"💥 {error_msg}")
        messagebox.showerror("Erro", error_msg)
        return 1

if __name__ == "__main__":
    # Configurar título do console no Windows
    if sys.platform == "win32":
        try:
            os.system("title Sistema de Gestão Escolar v2.0")
        except:
            pass
    
    # Executar sistema
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Sistema interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"💥 Erro crítico: {e}")
        sys.exit(1)
