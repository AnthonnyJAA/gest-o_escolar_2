# -*- coding: utf-8 -*-
"""
🚀 INICIALIZAÇÃO RÁPIDA DO SISTEMA DE TRANSFERÊNCIAS
Execute este arquivo para configurar e testar rapidamente o sistema
"""

import os
import sys
import subprocess
from pathlib import Path

def verificar_python():
    """Verifica versão do Python"""
    print("🐍 Verificando Python...")
    
    if sys.version_info < (3, 6):
        print("❌ Python 3.6+ é necessário!")
        print(f"   Versão atual: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} detectado")
    return True

def instalar_dependencias():
    """Instala dependências automaticamente"""
    print("\n📦 Verificando dependências...")
    
    dependencias = ['matplotlib', 'numpy']
    faltando = []
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"✅ {dep} já instalado")
        except ImportError:
            faltando.append(dep)
            print(f"❌ {dep} não encontrado")
    
    if faltando:
        print(f"\n📥 Instalando dependências: {', '.join(faltando)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--upgrade"
            ] + faltando)
            print("✅ Dependências instaladas com sucesso!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar dependências: {e}")
            print("\n💡 Tente instalar manualmente:")
            print(f"   pip install {' '.join(faltando)}")
            return False
    
    return True

def verificar_arquivos():
    """Verifica se os arquivos necessários existem"""
    print("\n📁 Verificando arquivos do sistema...")
    
    arquivos_necessarios = [
        'main.py',
        'services/transferencia_service.py',
        'interface/transferencia.py', 
        'interface/main_window.py',
        'create_sample_data.py'
    ]
    
    faltando = []
    for arquivo in arquivos_necessarios:
        if not Path(arquivo).exists():
            faltando.append(arquivo)
            print(f"❌ {arquivo} não encontrado")
        else:
            print(f"✅ {arquivo}")
    
    if faltando:
        print(f"\n❌ Arquivos faltando: {faltando}")
        return False
    
    return True

def inicializar_banco():
    """Inicializa banco de dados"""
    print("\n🗄️ Inicializando banco de dados...")
    
    try:
        from database.connection import db
        db.init_database()
        print("✅ Banco de dados inicializado")
        return True
    except Exception as e:
        print(f"❌ Erro no banco: {e}")
        return False

def criar_dados_exemplo():
    """Cria dados de exemplo"""
    print("\n📊 Criando dados de exemplo...")
    
    try:
        from create_sample_data import criar_dados_exemplo
        criar_dados_exemplo()
        print("✅ Dados de exemplo criados")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar dados: {e}")
        return False

def testar_transferencias():
    """Testa sistema de transferências"""
    print("\n🔄 Testando sistema de transferências...")
    
    try:
        from services.transferencia_service import TransferenciaService
        
        service = TransferenciaService()
        turmas = service.listar_turmas_para_filtro()
        
        if len(turmas) >= 2:
            alunos = service.listar_alunos_por_turma(turmas[0]['id'])
            if alunos:
                print(f"✅ Sistema funcionando! {len(turmas)} turmas, {len(alunos)} alunos na primeira turma")
                return True
        
        print("⚠️ Sistema funcional, mas poucos dados de teste")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def executar_sistema():
    """Executa o sistema principal"""
    print("\n🚀 Iniciando Sistema de Gestão Escolar...")
    print("=" * 60)
    
    try:
        # Importar e executar
        from interface.main_window import SistemaGestaoEscolar
        
        print("✅ Carregando interface...")
        app = SistemaGestaoEscolar()
        
        print("🎉 Sistema iniciado com sucesso!")
        print("👆 Use a barra de navegação para acessar 'Transferências'")
        print("-" * 60)
        
        app.run()
        
    except Exception as e:
        print(f"❌ Erro ao executar sistema: {e}")
        return False
    
    return True

def main():
    """Função principal de inicialização"""
    print("🎓 SISTEMA DE GESTÃO ESCOLAR v2.0")
    print("🔄 CONFIGURAÇÃO AUTOMÁTICA COM TRANSFERÊNCIAS")
    print("=" * 60)
    
    # Lista de verificações
    verificacoes = [
        ("Python", verificar_python),
        ("Dependências", instalar_dependencias), 
        ("Arquivos", verificar_arquivos),
        ("Banco de Dados", inicializar_banco),
        ("Dados de Exemplo", criar_dados_exemplo),
        ("Sistema de Transferências", testar_transferencias)
    ]
    
    # Executar verificações
    for nome, funcao in verificacoes:
        if not funcao():
            print(f"\n💥 Falha na verificação: {nome}")
            print("❌ Não é possível continuar")
            input("Pressione Enter para sair...")
            return False
    
    # Tudo OK - perguntar se quer executar
    print("\n" + "=" * 60)
    print("🎉 SISTEMA PRONTO PARA USO!")
    print("✅ Todas as verificações passaram")
    print("📋 Recursos disponíveis:")
    print("   • Dashboard interativo com gráficos")
    print("   • Sistema completo de transferências")
    print("   • Histórico e relatórios detalhados")
    print("   • Validações automáticas")
    print("   • Transferências individuais e em lote")
    
    resposta = input("\n🚀 Executar o sistema agora? (s/n): ")
    
    if resposta.lower() in ['s', 'sim', 'y', 'yes', '']:
        return executar_sistema()
    else:
        print("\n💡 Para executar manualmente, use:")
        print("   python main.py")
        print("\n👋 Configuração concluída!")
        return True

if __name__ == "__main__":
    try:
        sucesso = main()
        if not sucesso:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")
        sys.exit(1)
    
    input("\nPressione Enter para sair...")
    sys.exit(0)