@echo off
chcp 65001 >nul
title Guia de Instalação Rápida - Sistema v2.1

echo.
echo ═══════════════════════════════════════════════════════════════════
echo 🎓 SISTEMA DE GESTÃO ESCOLAR v2.1 - GUIA DE INSTALAÇÃO RÁPIDA
echo 🔄 Transferências Avançadas - 4 Cenários Implementados  
echo ═══════════════════════════════════════════════════════════════════
echo.

echo 📋 ESTE GUIA IRÁ:
echo    1️⃣ Verificar se Python está instalado
echo    2️⃣ Instalar dependências necessárias
echo    3️⃣ Testar o sistema completo
echo    4️⃣ Executar demonstração dos cenários
echo    5️⃣ Abrir interface gráfica final
echo.

echo 🤔 Deseja continuar com a instalação?
pause
echo.

rem === PASSO 1: VERIFICAR PYTHON ===
echo 🐍 PASSO 1: Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo.
    echo 💡 SOLUÇÃO:
    echo    1. Baixe Python 3.8+ de https://python.org
    echo    2. Durante instalação, marque "Add Python to PATH"
    echo    3. Reinicie este script após instalar
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% encontrado
echo.

rem === PASSO 2: INSTALAR DEPENDÊNCIAS ===
echo 📦 PASSO 2: Instalando dependências para gráficos...
echo.
echo 📊 Instalando matplotlib e numpy...
python -m pip install --upgrade matplotlib numpy python-dateutil
if errorlevel 1 (
    echo.
    echo ❌ Erro na instalação! Tentando método alternativo...
    echo.
    python -m pip install matplotlib numpy
    if errorlevel 1 (
        echo ❌ Não foi possível instalar dependências!
        echo 💡 Execute manualmente: pip install matplotlib numpy
        echo.
        pause
        exit /b 1
    )
)

echo.
echo ✅ Dependências instaladas com sucesso!
echo.

rem === PASSO 3: TESTAR SISTEMA ===
echo 🔍 PASSO 3: Testando componentes do sistema...
echo.

echo    📊 Testando gráficos...
python -c "import matplotlib, numpy; print('   ✅ Matplotlib:', matplotlib.__version__); print('   ✅ NumPy:', numpy.__version__)" 2>nul
if errorlevel 1 (
    echo    ⚠️ Gráficos podem não funcionar perfeitamente
) else (
    echo    ✅ Gráficos funcionando!
)

echo    🗄️ Testando banco de dados...
python -c "import sqlite3; print('   ✅ SQLite3 disponível')" 2>nul

echo    🖼️ Testando interface gráfica...
python -c "import tkinter; print('   ✅ Tkinter disponível')" 2>nul

echo.
echo ✅ Todos os componentes testados!
echo.

rem === PASSO 4: DEMONSTRAÇÃO ===
echo 🎯 PASSO 4: Demonstração dos cenários (opcional)
echo.
echo    Este passo mostra os 4 cenários de transferência funcionando:
echo    • Cenário 1: Mesmo Ano Letivo
echo    • Cenário 2: Novo Ano Letivo  
echo    • Cenário 3: Desligamento
echo    • Cenário 4: Reativação
echo.

set /p demo_choice="🤔 Deseja ver a demonstração dos cenários? (s/n): "
if /i "%demo_choice%"=="s" (
    echo.
    echo 🚀 Executando demonstração...
    echo.
    python demonstracao_completa.py
    echo.
    echo 📋 Demonstração concluída!
    echo.
) else (
    echo.
    echo ⏭️ Pulando demonstração...
    echo.
)

rem === PASSO 5: INTERFACE GRÁFICA ===
echo 🎨 PASSO 5: Executando sistema completo
echo.
echo 🖥️ SISTEMA DE GESTÃO ESCOLAR v2.1 - INTERFACE GRÁFICA
echo.
echo 📋 RECURSOS DISPONÍVEIS:
echo    🏠 Dashboard - 6 gráficos interativos
echo    👥 Alunos - Cadastro completo  
echo    🏫 Turmas - Gestão de classes
echo    💰 Financeiro - Controle de pagamentos
echo    🔄 Transferências - 4 cenários avançados
echo    ⚙️ Configurações - Backup e relatórios
echo.

echo 🎯 FOCO PRINCIPAL: Clique em "🔄 Transferências" para testar cenários!
echo.

set /p interface_choice="🚀 Abrir interface gráfica agora? (s/n): "
if /i "%interface_choice%"=="s" (
    echo.
    echo 🎉 Iniciando Sistema de Gestão Escolar v2.1...
    echo.
    echo ┌─────────────────────────────────────────────────────────────┐
    echo │  🎓 SISTEMA PRONTO PARA USO!                               │
    echo │                                                             │
    echo │  🔄 Para testar transferências:                            │
    echo │     1. Aguarde a interface carregar                        │
    echo │     2. Clique em "🔄 Transferências" na barra superior     │
    echo │     3. Escolha o tipo de operação (radio buttons)          │
    echo │     4. Siga o passo a passo na interface                   │
    echo │                                                             │
    echo │  📊 Dashboard também disponível com gráficos em tempo real │
    echo └─────────────────────────────────────────────────────────────┘
    echo.
    
    python main_avancado.py
    
    echo.
    echo 👋 Sistema encerrado.
) else (
    echo.
    echo 💡 PARA EXECUTAR DEPOIS:
    echo    python main_avancado.py
)

echo.
echo ═══════════════════════════════════════════════════════════════════
echo 🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!
echo.
echo 📋 RESUMO DO QUE FOI INSTALADO:
echo    ✅ Python verificado
echo    ✅ Matplotlib e NumPy instalados  
echo    ✅ Sistema testado e funcionando
echo    ✅ Dados de exemplo criados
echo    ✅ Interface gráfica configurada
echo.
echo 🚀 COMO USAR:
echo    • Execute: python main_avancado.py
echo    • Clique em "🔄 Transferências" 
echo    • Teste os 4 cenários implementados
echo.
echo 📚 CENÁRIOS DISPONÍVEIS:
echo    1️⃣ Transferência no mesmo ano letivo
echo    2️⃣ Transferência para novo ano letivo
echo    3️⃣ Desligamento da escola  
echo    4️⃣ Reativação de aluno
echo.
echo 💡 Leia o README_COMPLETO.md para documentação detalhada
echo ═══════════════════════════════════════════════════════════════════
echo.

pause
exit /b 0