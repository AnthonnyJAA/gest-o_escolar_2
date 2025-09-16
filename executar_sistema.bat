@echo off
chcp 65001 >nul
title Sistema de Gestão Escolar v2.0 - Inicialização

echo.
echo ═══════════════════════════════════════════════════════════
echo 🎓 SISTEMA DE GESTÃO ESCOLAR v2.0 - COM TRANSFERÊNCIAS
echo ═══════════════════════════════════════════════════════════
echo.

rem Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado! 
    echo 💡 Instale Python 3.6+ de https://python.org
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

rem Verificar se pip está disponível
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip não encontrado!
    echo 💡 Reinstale Python com pip incluído
    echo.
    pause
    exit /b 1
)

echo ✅ pip disponível
echo.

rem Instalar dependências
echo 📦 Instalando dependências necessárias...
echo.
python -m pip install matplotlib numpy
if errorlevel 1 (
    echo.
    echo ❌ Erro ao instalar dependências!
    echo 💡 Tente executar manualmente: pip install matplotlib numpy
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Dependências instaladas com sucesso!
echo.

rem Executar sistema
echo 🚀 Iniciando Sistema de Gestão Escolar...
echo.
echo ┌─────────────────────────────────────────────────────────┐
echo │ 📊 Dashboard Interativo com Gráficos em Tempo Real     │
echo │ 🔄 Sistema Completo de Transferência de Alunos         │
echo │ 📈 Relatórios Detalhados e Estatísticas Avançadas     │
echo │ 👥 Gestão de Alunos, Turmas e Financeiro              │
echo └─────────────────────────────────────────────────────────┘
echo.

rem Tentar executar o inicializador primeiro
if exist "iniciar_sistema.py" (
    echo 🔧 Executando configuração automática...
    python iniciar_sistema.py
    if errorlevel 1 (
        echo.
        echo ⚠️ Configuração automática falhou, tentando execução direta...
        goto execucao_direta
    )
) else (
    echo ⚠️ iniciar_sistema.py não encontrado, executando diretamente...
    goto execucao_direta
)

goto fim

:execucao_direta
echo.
echo 🎯 Executando sistema principal...
python main_sistema_corrigido.py
if errorlevel 1 (
    echo.
    echo ❌ Erro ao executar o sistema principal!
    echo 💡 Verifique se todos os arquivos estão presentes
    echo.
    pause
    exit /b 1
)

:fim
echo.
echo 👋 Sistema encerrado
echo 💡 Execute este arquivo novamente para reiniciar
echo.
pause