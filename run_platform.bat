@echo off
title KTR Migrator - Execucao Simples
color 0C
chcp 65001 >nul

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                    🚀 KTR Migrator Platform Pro                       ║
echo ║                      Execução Simples - Windows                       ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.

:: Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado!
    echo 💡 Execute: SETUP_WINDOWS.bat primeiro
    pause
    exit /b 1
)

echo 🔧 Verificando dependências...
pip install -r ktr_platform/requirements_platform.txt --quiet
if %errorlevel% neq 0 (
    echo ⚠️  Alguns pacotes podem ter falhado
    echo 💡 Para setup completo, execute: SETUP_WINDOWS.bat
)

:: Criar diretórios se necessário
if not exist "ktr_platform\data" mkdir ktr_platform\data
if not exist "ktr_platform\logs" mkdir ktr_platform\logs

echo.
echo ✅ Dependências verificadas
echo 🎯 Iniciando KTR Platform...
echo 📍 URL: http://localhost:8501
echo 🛑 Para parar: Ctrl+C
echo.

:: Aguardar e abrir navegador      
timeout /t 2 /nobreak >nul
start http://localhost:8501

:: Iniciar aplicação
streamlit run ktr_platform/app.py --server.port=8501 --server.address=localhost --browser.gatherUsageStats=false

echo.
echo 👋 Aplicação finalizada
pause 