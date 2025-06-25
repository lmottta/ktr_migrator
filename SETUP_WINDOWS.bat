@echo off
title KTR Migrator - Setup e Execucao Windows
color 0A
chcp 65001 >nul

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    🚀 KTR Migrator Platform Pro                             ║
echo ║              Configuração e Execução Automática - Windows                   ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

:: Verificar se Python está instalado
echo 🔍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado!
    echo.
    echo 📥 Baixe Python em: https://www.python.org/downloads/
    echo 💡 Durante instalação, marque "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% encontrado

:: Verificar se pip está disponível
echo 🔍 Verificando pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip não encontrado!
    echo 📥 Instalando pip...
    python -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo ❌ Falha ao instalar pip
        pause
        exit /b 1
    )
)
echo ✅ pip disponível

:: Criar ambiente virtual se não existir
echo.
echo 🔧 Configurando ambiente virtual...
if not exist "venv" (
    echo 📦 Criando ambiente virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Falha ao criar ambiente virtual
        pause
        exit /b 1
    )
    echo ✅ Ambiente virtual criado
) else (
    echo ✅ Ambiente virtual já existe
)

:: Ativar ambiente virtual
echo 🔄 Ativando ambiente virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Falha ao ativar ambiente virtual
    pause
    exit /b 1
)
echo ✅ Ambiente virtual ativo

:: Atualizar pip
echo 📦 Atualizando pip...
python -m pip install --upgrade pip --quiet
echo ✅ pip atualizado

:: Instalar dependências principais
echo.
echo 📚 Instalando dependências principais...
echo    - pandas, sqlalchemy, psycopg2-binary...
pip install pandas>=2.0.0 sqlalchemy>=2.0.0 psycopg2-binary>=2.9.0 openpyxl>=3.1.0 --quiet
if %errorlevel% neq 0 (
    echo ❌ Falha ao instalar dependências principais
    pause
    exit /b 1
)

echo    - lxml, jinja2, click...  
pip install lxml>=4.9.0 xmltodict>=0.13.0 jinja2>=3.1.0 click>=8.1.0 --quiet
if %errorlevel% neq 0 (
    echo ❌ Falha ao instalar dependências de parsing
    pause
    exit /b 1
)

echo    - loguru, pydantic, networkx...
pip install python-decouple>=3.8 pyyaml>=6.0 loguru>=0.7.0 pydantic>=2.0.0 networkx>=3.1 --quiet
if %errorlevel% neq 0 (
    echo ❌ Falha ao instalar dependências de configuração
    pause
    exit /b 1
)

:: Instalar dependências da plataforma
echo.
echo 🎯 Instalando dependências da plataforma...
echo    - streamlit, plotly, schedule...
pip install streamlit>=1.28.0 plotly>=5.17.0 streamlit-autorefresh>=0.1.0 schedule>=1.2.0 --quiet
if %errorlevel% neq 0 (
    echo ❌ Falha ao instalar dependências da plataforma
    pause
    exit /b 1
)

echo    - psutil, conectores de banco...
pip install psutil>=5.9.0 pymysql>=1.0.0 pyodbc>=4.0.0 --quiet
if %errorlevel% neq 0 (
    echo ❌ Falha ao instalar conectores de banco
    pause
    exit /b 1
)

:: Verificar estrutura do projeto
echo.
echo 🔍 Verificando estrutura do projeto...
if not exist "ktr_platform" (
    echo ❌ Diretório ktr_platform não encontrado!
    echo 💡 Certifique-se de estar no diretório correto do projeto
    pause
    exit /b 1
)

if not exist "ktr_platform\app.py" (
    echo ❌ Arquivo app.py não encontrado!
    echo 💡 Estrutura do projeto incompleta
    pause
    exit /b 1
)

:: Criar diretórios necessários
echo 📁 Criando diretórios necessários...
if not exist "ktr_platform\data" mkdir ktr_platform\data
if not exist "ktr_platform\flows" mkdir ktr_platform\flows
if not exist "ktr_platform\logs" mkdir ktr_platform\logs
echo ✅ Diretórios criados

:: Verificar/criar arquivos de configuração
echo.
echo ⚙️  Verificando configurações...
if not exist "ktr_platform\.env" (
    if exist "ktr_platform\.env.example" (
        echo 📝 Copiando configurações exemplo...
        copy "ktr_platform\.env.example" "ktr_platform\.env" >nul
        echo ✅ Arquivo .env criado a partir do exemplo
    ) else (
        echo 🔧 Criando configuração básica...
        call :create_basic_env
        echo ✅ Configuração básica criada
    )
) else (
    echo ✅ Configuração já existe
)

:: Verificar se arquivos de dados existem
if not exist "ktr_platform\data\flows.json" (
    echo 📄 Criando arquivo de flows...
    echo [] > "ktr_platform\data\flows.json"
)

if not exist "ktr_platform\data\schedules.json" (
    echo 📄 Criando arquivo de agendamentos...
    echo [] > "ktr_platform\data\schedules.json"
)

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                            ✅ SETUP CONCLUÍDO!                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 🎯 Iniciando KTR Platform...
echo 📍 URL de acesso: http://localhost:8501
echo 🛑 Para parar: Pressione Ctrl+C
echo.

:: Iniciar a aplicação
cd ktr_platform
streamlit run app.py --server.port=8501 --server.address=localhost --browser.gatherUsageStats=false

:: Se chegou aqui, houve algum problema
echo.
echo ⚠️  A aplicação foi finalizada
pause
goto :eof

:: Função para criar .env básico
:create_basic_env
(
echo # Configurações básicas da KTR Platform
echo.
echo # Configuração da aplicação
echo APP_NAME=KTR Platform Pro
echo APP_VERSION=1.0.0
echo DEBUG=false
echo.
echo # Configuração do servidor
echo HOST=localhost
echo PORT=8501
echo.
echo # Configurações de banco - PostgreSQL local
echo DATABASE_TYPE=postgresql
echo DATABASE_HOST=localhost
echo DATABASE_PORT=5432
echo DATABASE_NAME=ktr_platform
echo DATABASE_USER=postgres
echo DATABASE_PASSWORD=postgres
echo.
echo # Configurações de logging
echo LOG_LEVEL=INFO
echo LOG_FILE=logs/platform.log
echo.
echo # Configurações de execução
echo MAX_CONCURRENT_JOBS=3
echo JOB_TIMEOUT=3600
echo.
echo # Configurações de interface
echo THEME=light
echo LANGUAGE=pt_BR
) > "ktr_platform\.env"
goto :eof 