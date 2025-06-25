@echo off
title KTR Migrator - Execucao Rapida
color 0B
chcp 65001 >nul

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                    🚀 KTR Migrator Platform Pro                       ║
echo ║                       Execução Rápida - Windows                       ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.

:: Verificar se ambiente virtual existe
if not exist "venv" (
    echo ⚠️  Ambiente virtual não encontrado!
    echo 🔧 Execute primeiro: SETUP_WINDOWS.bat
    echo.
    pause
    exit /b 1
)

:: Ativar ambiente virtual
echo 🔄 Ativando ambiente virtual...
call venv\Scripts\activate.bat

:: Verificar se Streamlit está instalado
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Streamlit não encontrado!
    echo 🔧 Execute primeiro: SETUP_WINDOWS.bat
    echo.
    pause
    exit /b 1
)

:: Criar logs se não existir
if not exist "ktr_platform\logs" mkdir ktr_platform\logs

echo.
echo ✅ Ambiente configurado!
echo 🎯 Iniciando KTR Platform...
echo.
echo 📍 URL de acesso: http://localhost:8501
echo 🛑 Para parar: Pressione Ctrl+C no terminal
echo.

:: Aguardar 2 segundos e abrir navegador
timeout /t 2 /nobreak >nul
start http://localhost:8501

:: Iniciar aplicação
cd ktr_platform
streamlit run app.py --server.port=8501 --server.address=localhost --browser.gatherUsageStats=false --server.headless=true

:: Mensagem de finalização
echo.
echo 👋 KTR Platform finalizada
pause 