#!/bin/bash

# Entrypoint script para KTR Platform
# Desenvolvido por: Engenheiro de Dados Senior
# Data: 2025-06-19

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] KTR-PLATFORM:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

# Banner de inicialização
cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                     KTR PLATFORM v1.0                      ║
║              Sistema de Migração de Pipelines ETL           ║
║                                                              ║
║              🚀 Iniciando Container Docker...                ║
╚══════════════════════════════════════════════════════════════╝
EOF

# Verificar se está rodando como usuário correto
if [ "$(id -u)" = "0" ]; then
    warning "Rodando como root - isso pode ser um risco de segurança"
fi

# Função para verificar saúde da aplicação
health_check() {
    log "🔍 Verificando dependências..."
    
    # Verificar Python
    if ! command -v python &> /dev/null; then
        error "Python não encontrado"
        exit 1
    fi
    
    # Verificar Streamlit
    if ! python -c "import streamlit" &> /dev/null; then
        error "Streamlit não instalado"
        exit 1
    fi
    
    # Verificar estrutura de diretórios
    for dir in data logs flows config; do
        if [ ! -d "/app/$dir" ]; then
            warning "Criando diretório ausente: $dir"
            mkdir -p "/app/$dir"
        fi
    done
    
    log "✅ Verificações de saúde concluídas"
}

# Função para inicializar dados
initialize_data() {
    log "📊 Inicializando estrutura de dados..."
    
    # Criar arquivos de dados básicos se não existirem
    if [ ! -f "/app/data/flows.json" ]; then
        echo '[]' > /app/data/flows.json
        info "Arquivo flows.json criado"
    fi
    
    if [ ! -f "/app/data/schedules.json" ]; then
        echo '[]' > /app/data/schedules.json
        info "Arquivo schedules.json criado"
    fi
    
    # Verificar permissões
    if [ ! -w "/app/data" ]; then
        warning "Sem permissão de escrita em /app/data"
    fi
    
    log "✅ Inicialização de dados concluída"
}

# Função para configurar logging
setup_logging() {
    log "📝 Configurando sistema de logs..."
    
    # Criar diretório de logs com rotação
    mkdir -p /app/logs/platform /app/logs/flows /app/logs/executor
    
    # Configurar nível de log baseado na variável de ambiente
    export LOG_LEVEL="${LOG_LEVEL:-INFO}"
    
    log "✅ Sistema de logs configurado (Nível: $LOG_LEVEL)"
}

# Função para aguardar dependências
wait_for_dependencies() {
    # Se houver variáveis de ambiente para serviços externos, aguardar
    if [ -n "$DATABASE_HOST" ]; then
        log "⏳ Aguardando banco de dados ($DATABASE_HOST)..."
        
        # Usar Python para verificar conectividade (sempre disponível na imagem)
        python -c "
        
import socket
import time
import sys

def check_connection(host, port, timeout=3):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

host = '$DATABASE_HOST'
port = ${DATABASE_PORT:-5432}
max_attempts = 60
attempt = 0

while attempt < max_attempts:
    if check_connection(host, port):
        print(f'✅ Conectado com sucesso ao banco {host}:{port}')
        sys.exit(0)
    time.sleep(2)
    attempt += 1

print(f'❌ Timeout após {max_attempts * 2} segundos aguardando {host}:{port}')
sys.exit(1)
"
        
        if [ $? -ne 0 ]; then
            error "Falha ao conectar com o banco de dados"
            exit 1
        fi
        
        log "✅ Banco de dados disponível"
    fi
}

# Função de limpeza para shutdown graceful
cleanup() {
    log "🛑 Recebido sinal de parada - realizando shutdown graceful..."
    
    # Salvar estado atual se necessário
    if [ -f "/app/.pid" ]; then
        PID=$(cat /app/.pid)
        if kill -0 "$PID" 2>/dev/null; then
            log "Parando processo principal (PID: $PID)..."
            kill -TERM "$PID"
            
            # Aguardar até 30 segundos para shutdown graceful
            for i in {1..30}; do
                if ! kill -0 "$PID" 2>/dev/null; then
                    break
                fi
                sleep 1
            done
            
            # Forçar parada se necessário
            if kill -0 "$PID" 2>/dev/null; then
                warning "Forçando parada do processo..."
                kill -KILL "$PID"
            fi
        fi
        rm -f /app/.pid
    fi
    
    log "✅ Shutdown graceful concluído"
    exit 0
}

# Configurar handlers de sinal
trap cleanup SIGTERM SIGINT SIGQUIT

# Executar verificações e inicializações
health_check
initialize_data
setup_logging
wait_for_dependencies

# Variáveis de ambiente específicas para produção
export STREAMLIT_SERVER_PORT=${STREAMLIT_SERVER_PORT:-8501}
export STREAMLIT_SERVER_ADDRESS=${STREAMLIT_SERVER_ADDRESS:-0.0.0.0}
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_HEADLESS=true

# Mostrar configuração
info "Configuração da aplicação:"
info "  - Porta: $STREAMLIT_SERVER_PORT"
info "  - Endereço: $STREAMLIT_SERVER_ADDRESS"
info "  - Diretório de trabalho: $(pwd)"
info "  - Usuário: $(whoami)"
info "  - Python: $(python --version)"

# Executar comando principal
log "🚀 Iniciando KTR Platform..."

if [ "$#" -eq 0 ] || [ "$1" = "streamlit" ]; then
    # Modo padrão - executar Streamlit
    log "Modo: Aplicação Streamlit"
    exec streamlit run app.py \
        --server.port="$STREAMLIT_SERVER_PORT" \
        --server.address="$STREAMLIT_SERVER_ADDRESS" \
        --server.headless=true \
        --browser.gatherUsageStats=false &
    
    # Salvar PID para shutdown graceful
    echo $! > /app/.pid
    
    # Aguardar processo principal
    wait $!
    
else
    # Modo customizado - executar comando fornecido
    log "Modo: Comando customizado ($*)"
    exec "$@"
fi 