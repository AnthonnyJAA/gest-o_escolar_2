# -*- coding: utf-8 -*-
"""
Sistema de Gestão Escolar v2.0
Sistema completo para gerenciamento escolar com gráficos interativos
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

def verificar_dependencias():
    """Verifica se as dependências necessárias estão instaladas"""
    try:
        import matplotlib
        import numpy
        print("✅ Matplotlib e NumPy encontrados")
        return True
    except ImportError as e:
        erro_msg = """
❌ Dependências não encontradas!

Para usar os gráficos interativos, instale as dependências:

pip install matplotlib numpy

Ou execute:
pip install -r requirements.txt

Erro específico: """ + str(e)
        
        print(erro_msg)
        messagebox.showerror("Dependências Faltando", erro_msg)
        return False

def criar_dados_exemplo_se_necessario():
    """Cria dados de exemplo para demonstrar os gráficos"""
    try:
        from create_sample_data import criar_dados_exemplo
        criar_dados_exemplo()
    except Exception as e:
        print(f"⚠️ Aviso: Não foi possível criar dados de exemplo: {e}")

def main():
    """Função principal"""
    try:
        print("🎓 Sistema de Gestão Escolar v2.0 - Com Gráficos Interativos")
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

        # Verificar dependências dos gráficos
        if not verificar_dependencias():
            resposta = messagebox.askyesno(
                "Continuar sem gráficos?", 
                "Deseja continuar sem os gráficos interativos?\n\n"
                "O sistema funcionará normalmente, mas o dashboard será simplificado."
            )
            if not resposta:
                return 1

        print("🚀 Carregando interface...")

        # Importar e iniciar sistema
        from interface.main_window import SistemaGestaoEscolar

        print("✅ Sistema carregado!")

        # Criar dados de exemplo se necessário (para demonstração dos gráficos)
        criar_dados_exemplo_se_necessario()

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
            os.system("title Sistema de Gestão Escolar v2.0 - Gráficos Interativos")
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