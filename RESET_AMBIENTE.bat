@echo off
title KTR Migrator - Reset do Ambiente
color 0C
chcp 65001 >nul

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                    🔄 KTR Migrator - Reset Ambiente                   ║
echo ║                     Limpeza e Recriação - Windows                     ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.

echo ⚠️  ATENÇÃO: Este script irá REMOVER o ambiente virtual atual
echo 📄 Configurações e dados dos projetos serão PRESERVADOS
echo.

set /p CONFIRM="Deseja continuar? (S/N): "
if /i "%CONFIRM%" neq "S" (
    echo ❌ Operação cancelada
    pause
    exit /b 0
)

echo.
echo 🧹 Iniciando limpeza do ambiente...

:: Remover ambiente virtual
if exist "venv" (
    echo 🗑️  Removendo ambiente virtual...
    rmdir /s /q "venv" 2>nul
    if exist "venv" (
        echo ⚠️  Algumas pastas podem estar em uso
        echo 💡 Feche todos os processos Python e tente novamente
        timeout /t 3 /nobreak >nul
        rmdir /s /q "venv" 2>nul
    )
    
    if not exist "venv" (
        echo ✅ Ambiente virtual removido
    ) else (
        echo ❌ Falha ao remover ambiente virtual
        echo 💡 Remova manualmente a pasta "venv"
        pause
        exit /b 1
    )
) else (
    echo ✅ Nenhum ambiente virtual encontrado
)

:: Limpar cache Python
echo 🧽 Limpando cache Python...
for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        rmdir /s /q "%%d" 2>nul
    )
)

:: Limpar arquivos temporários
echo 🧽 Limpando arquivos temporários...
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul
del /s /q .coverage 2>nul

:: Limpar logs antigos (opcional)
echo 🧽 Limpando logs antigos...
if exist "ktr_platform\logs" (
    set /p CLEAN_LOGS="Limpar logs também? (S/N): "
    if /i "!CLEAN_LOGS!" equ "S" (
        del /q "ktr_platform\logs\*.log" 2>nul
        echo ✅ Logs limpos
    )
)

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                            ✅ LIMPEZA CONCLUÍDA                       ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.

echo 🎯 Próximos passos:
echo    1. Execute: SETUP_WINDOWS.bat
echo    2. Ou execute: START_KTR.bat (irá fazer setup automático)
echo.

set /p RUN_SETUP="Executar SETUP_WINDOWS.bat agora? (S/N): "
if /i "%RUN_SETUP%" equ "S" (
    echo.
    echo 🚀 Iniciando setup...
    call SETUP_WINDOWS.bat
) else (
    echo.
    echo 👋 Reset concluído! Execute SETUP_WINDOWS.bat quando estiver pronto.
    pause
)

goto :eof 