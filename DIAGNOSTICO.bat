@echo off
title KTR Migrator - Diagnostico do Sistema
color 0E
chcp 65001 >nul

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                    🔍 KTR Migrator - Diagnóstico                      ║
echo ║                    Verificação do Ambiente Windows                    ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.

:: Verificar Python
echo 🐍 PYTHON:
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo    ✅ Python %%i instalado
    python -c "import sys; print('    📍 Localização:', sys.executable)"
) else (
    echo    ❌ Python não encontrado
    echo    💡 Baixe em: https://www.python.org/downloads/
)

echo.

:: Verificar pip
echo 📦 PIP:
pip --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('pip --version 2^>^&1') do echo    ✅ pip %%i disponível
) else (
    echo    ❌ pip não encontrado
)

echo.

:: Verificar ambiente virtual
echo 🏠 AMBIENTE VIRTUAL:
if exist "venv" (
    echo    ✅ Ambiente virtual existe
    if exist "venv\Scripts\activate.bat" (
        echo    ✅ Script de ativação OK
    ) else (
        echo    ❌ Script de ativação não encontrado
    )
) else (
    echo    ❌ Ambiente virtual não existe
    echo    💡 Execute: SETUP_WINDOWS.bat
)

echo.

:: Verificar estrutura do projeto
echo 📁 ESTRUTURA DO PROJETO:
if exist "ktr_platform" (
    echo    ✅ Diretório ktr_platform existe
) else (
    echo    ❌ Diretório ktr_platform não encontrado
)

if exist "ktr_platform\app.py" (
    echo    ✅ Arquivo app.py existe
) else (
    echo    ❌ Arquivo app.py não encontrado
)

if exist "ktr_platform\data" (
    echo    ✅ Diretório data existe
) else (
    echo    ⚠️  Diretório data não existe
)

if exist "ktr_platform\flows" (
    echo    ✅ Diretório flows existe
) else (
    echo    ⚠️  Diretório flows não existe
)

echo.

:: Verificar configurações
echo ⚙️  CONFIGURAÇÕES:
if exist "ktr_platform\.env" (
    echo    ✅ Arquivo .env existe
) else (
    echo    ⚠️  Arquivo .env não existe
    if exist "ktr_platform\.env.example" (
        echo    💡 Arquivo .env.example disponível
    )
)

echo.

:: Verificar dependências se ambiente virtual existir
if exist "venv" (
    echo 📚 DEPENDÊNCIAS:
    call venv\Scripts\activate.bat
    
    python -c "import streamlit" >nul 2>&1
    if %errorlevel% equ 0 (
        echo    ✅ Streamlit instalado
    ) else (
        echo    ❌ Streamlit não instalado
    )
    
    python -c "import pandas" >nul 2>&1
    if %errorlevel% equ 0 (
        echo    ✅ Pandas instalado
    ) else (
        echo    ❌ Pandas não instalado
    )
    
    python -c "import sqlalchemy" >nul 2>&1
    if %errorlevel% equ 0 (
        echo    ✅ SQLAlchemy instalado
    ) else (
        echo    ❌ SQLAlchemy não instalado
    )
    
    python -c "import psycopg2" >nul 2>&1
    if %errorlevel% equ 0 (
        echo    ✅ PostgreSQL driver instalado
    ) else (
        echo    ❌ PostgreSQL driver não instalado
    )
)

echo.

:: Verificar portas
echo 🌐 REDE:
netstat -an | find "8501" >nul 2>&1
if %errorlevel% equ 0 (
    echo    ⚠️  Porta 8501 já está em uso
    echo    💡 Pare outros processos ou mude a porta
) else (
    echo    ✅ Porta 8501 disponível
)

echo.

:: Verificar espaço em disco
echo 💾 SISTEMA:
for /f "tokens=3" %%i in ('dir /-c ^| find "bytes free"') do (
    set FREE_SPACE=%%i
)
echo    📊 Espaço livre: %FREE_SPACE% bytes

:: Verificar memória RAM
for /f "skip=1" %%i in ('wmic computersystem get TotalPhysicalMemory /value') do (
    if "%%i" neq "" (
        set TOTAL_RAM=%%i
        goto :ram_done
    )
)
:ram_done
echo    🧠 RAM total: %TOTAL_RAM:~20% bytes

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                           📋 DIAGNÓSTICO COMPLETO                     ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.

:: Sugestões baseadas no diagnóstico
echo 💡 SUGESTÕES:
if not exist "venv" (
    echo    🔧 Execute: SETUP_WINDOWS.bat para configurar o ambiente
)
if not exist "ktr_platform\.env" (
    echo    ⚙️  Configure o arquivo .env na pasta ktr_platform
)

echo.
pause 