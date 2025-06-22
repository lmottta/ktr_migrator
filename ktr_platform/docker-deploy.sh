#!/bin/bash

# =============================================================================
# KTR PLATFORM - SCRIPT DE DEPLOY AUTOMATIZADO
# =============================================================================
# Script para automatizar o deployment do KTR Platform com Docker
# Data: 2025-06-19
# Desenvolvido por: Engenheiro de Dados Senior

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner de boas-vindas
cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                          🚀 KTR PLATFORM v1.0                              ║
║                     Sistema de Migração de Pipelines ETL                    ║
║                                                                              ║
║                        🐳 Deploy Automatizado com Docker                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF

# Funções auxiliares
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] ✅${NC} $1"
}

info() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] ℹ️${NC}  $1"
}

warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] ⚠️${NC}  $1"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ❌${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] 🎉${NC} $1"
}

# Verificar dependências
check_dependencies() {
    info "Verificando dependências..."
    
    # Docker
    if ! command -v docker &> /dev/null; then
        error "Docker não encontrado. Por favor, instale Docker Desktop."
        error "Download: https://www.docker.com/products/docker-desktop"
        exit 1
    fi
    log "Docker encontrado: $(docker --version | cut -d' ' -f3)"
    
    # Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose não encontrado."
        exit 1
    fi
    log "Docker Compose encontrado: $(docker-compose --version | cut -d' ' -f3)"
    
    # Verificar se Docker está rodando
    if ! docker info &> /dev/null; then
        error "Docker não está rodando. Por favor, inicie o Docker Desktop."
        exit 1
    fi
    log "Docker está rodando"
}

# Função para preparar o ambiente de build
prepare_build_environment() {
    info "Preparando ambiente de build..."
    if [ ! -f "requirements_platform.txt" ]; then
        if [ -f "../requirements_platform.txt" ]; then
            info "Copiando 'requirements_platform.txt' do diretório raiz para o contexto do build."
            cp ../requirements_platform.txt .
            # Garante que o arquivo seja removido ao final da execução do script
            trap "info 'Limpando arquivo temporário...' && rm -f requirements_platform.txt" EXIT
        else
            error "'requirements_platform.txt' não encontrado no diretório raiz."
            exit 1
        fi
    fi
    log "Ambiente de build preparado."
}

# Gerar senhas seguras
generate_secure_passwords() {
    info "Gerando senhas seguras..."
    
    # Função para gerar senha aleatória
    generate_password() {
        if command -v openssl &> /dev/null; then
            openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
        else
            # Fallback para sistemas sem openssl
            date +%s | sha256sum | base64 | head -c 25
        fi
    }
    
    DB_PASSWORD=$(generate_password)
    REDIS_PASSWORD=$(generate_password)
    GRAFANA_PASSWORD=$(generate_password)
    SECRET_KEY=$(generate_password)
    JWT_SECRET=$(generate_password)
    
    log "Senhas geradas com sucesso"
}

# Configurar arquivo .env
setup_environment() {
    info "Configurando arquivo de ambiente..."
    
    if [ ! -f .env.example ]; then
        error "Arquivo .env.example não encontrado!"
        exit 1
    fi
    
    # Fazer backup do .env existente
    if [ -f .env ]; then
        warning "Arquivo .env existente encontrado. Criando backup..."
        cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    fi
    
    # Copiar template
    cp .env.example .env
    
    # Perguntar configurações ao usuário
    echo
    echo -e "${PURPLE}📝 Configuração do Ambiente${NC}"
    echo "=================================="
    
    # Porta da aplicação
    read -p "🌐 Porta da aplicação (padrão: 8501): " user_port
    KTR_PORT=${user_port:-8501}
    
    # Ambiente
    echo
    echo "🏗️  Selecione o ambiente:"
    echo "1) Development (padrão)"
    echo "2) Staging"
    echo "3) Production"
    read -p "Escolha (1-3): " env_choice
    
    case $env_choice in
        2) ENV="staging" ;;
        3) ENV="production" ;;
        *) ENV="development" ;;
    esac
    
    # Nível de log
    echo
    echo "📋 Selecione o nível de log:"
    echo "1) INFO (padrão)"
    echo "2) DEBUG"
    echo "3) WARNING"
    echo "4) ERROR"
    read -p "Escolha (1-4): " log_choice
    
    case $log_choice in
        2) LOG_LEVEL="DEBUG" ;;
        3) LOG_LEVEL="WARNING" ;;
        4) LOG_LEVEL="ERROR" ;;
        *) LOG_LEVEL="INFO" ;;
    esac
    
    # Atualizar arquivo .env
    sed -i.bak \
        -e "s/KTR_PORT=8501/KTR_PORT=$KTR_PORT/" \
        -e "s/ENV=development/ENV=$ENV/" \
        -e "s/LOG_LEVEL=INFO/LOG_LEVEL=$LOG_LEVEL/" \
        -e "s/DB_PASSWORD=ktr_secure_pass_2025/DB_PASSWORD=$DB_PASSWORD/" \
        -e "s/REDIS_PASSWORD=redis_secure_pass_2025/REDIS_PASSWORD=$REDIS_PASSWORD/" \
        -e "s/GRAFANA_PASSWORD=admin_secure_2025/GRAFANA_PASSWORD=$GRAFANA_PASSWORD/" \
        -e "s/SECRET_KEY=your_secret_key_here_change_in_production/SECRET_KEY=$SECRET_KEY/" \
        -e "s/JWT_SECRET=your_jwt_secret_here_change_in_production/JWT_SECRET=$JWT_SECRET/" \
        .env
    
    # Remover arquivo backup temporário
    rm -f .env.bak
    
    log "Arquivo .env configurado"
}

# Selecionar perfil de deployment
select_deployment_profile() {
    echo
    echo -e "${PURPLE}🚀 Perfil de Deployment${NC}"
    echo "=================================="
    echo "1) 🔧 Development    - App + Database + Cache"
    echo "2) 🏭 Production     - Development + Proxy + SSL"
    echo "3) 📊 Monitoring     - Development + Prometheus + Grafana"
    echo "4) 🌟 Complete       - Todos os serviços"
    echo
    read -p "Escolha o perfil (1-4): " profile_choice
    
    case $profile_choice in
        2)
            DEPLOY_PROFILE="--profile production"
            PROFILE_NAME="Production"
            ;;
        3)
            DEPLOY_PROFILE="--profile monitoring"
            PROFILE_NAME="Monitoring"
            ;;
        4)
            DEPLOY_PROFILE="--profile production --profile monitoring"
            PROFILE_NAME="Complete"
            ;;
        *)
            DEPLOY_PROFILE=""
            PROFILE_NAME="Development"
            ;;
    esac
    
    info "Perfil selecionado: $PROFILE_NAME"
}

# Build das imagens
build_images() {
    info "Construindo imagens Docker..."
    
    # Limpar build cache se necessário
    if [ "$ENV" = "production" ]; then
        info "Ambiente de produção detectado. Fazendo build limpo..."
        docker-compose build --no-cache
    else
        docker-compose build
    fi
    
    log "Imagens construídas com sucesso"
}

# Deploy dos containers
deploy_containers() {
    info "Iniciando containers..."
    
    # Parar containers existentes se houver
    if docker-compose ps | grep -q "Up"; then
        warning "Containers em execução detectados. Parando..."
        docker-compose down
    fi
    
    # Iniciar containers
    if [ -n "$DEPLOY_PROFILE" ]; then
        docker-compose $DEPLOY_PROFILE up -d
    else
        docker-compose up -d
    fi
    
    log "Containers iniciados"
}

# Verificar saúde dos containers
check_health() {
    info "Verificando saúde dos containers..."
    
    # Aguardar containers ficarem saudáveis
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose ps | grep -q "unhealthy"; then
            warning "Aguardando containers ficarem saudáveis... ($((attempt + 1))/$max_attempts)"
            sleep 10
            ((attempt++))
        else
            break
        fi
    done
    
    if [ $attempt -eq $max_attempts ]; then
        error "Alguns containers não ficaram saudáveis. Verificando logs..."
        docker-compose logs --tail=20
        exit 1
    fi
    
    log "Todos os containers estão saudáveis"
}

# Mostrar informações de acesso
show_access_info() {
    echo
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    🎉 DEPLOY CONCLUÍDO!                      ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    echo -e "${GREEN}🌐 URLs de Acesso:${NC}"
    echo "   • Aplicação Principal: http://localhost:$KTR_PORT"
    echo "   • PostgreSQL:          localhost:5432"
    echo "   • Redis:               localhost:6379"
    
    if [[ "$DEPLOY_PROFILE" == *"monitoring"* ]]; then
        echo "   • Prometheus:          http://localhost:9090"
        echo "   • Grafana:             http://localhost:3000"
    fi
    
    if [[ "$DEPLOY_PROFILE" == *"production"* ]]; then
        echo "   • Nginx Proxy:         http://localhost"
    fi
    
    echo
    echo -e "${GREEN}🔐 Credenciais:${NC}"
    echo "   • Database User:       ktr_user"
    echo "   • Database Password:   $DB_PASSWORD"
    echo "   • Redis Password:      $REDIS_PASSWORD"
    
    if [[ "$DEPLOY_PROFILE" == *"monitoring"* ]]; then
        echo "   • Grafana User:        admin"
        echo "   • Grafana Password:    $GRAFANA_PASSWORD"
    fi
    
    echo
    echo -e "${GREEN}📋 Comandos Úteis:${NC}"
    echo "   • Ver logs:            docker-compose logs -f"
    echo "   • Parar containers:    docker-compose down"
    echo "   • Reiniciar:           docker-compose restart"
    echo "   • Status:              docker-compose ps"
    
    echo
    echo -e "${GREEN}📚 Documentação:${NC}"
    echo "   • Docker Guide:        README_DOCKER.md"
    echo "   • Sistema de Erros:    docs/desenvolvimento/SISTEMA_CAPTURA_ERROS_TEMPO_REAL.md"
    
    echo
}

# Função principal
main() {
    # Verificar se está no diretório correto
    if [ ! -f docker-compose.yml ]; then
        error "Este script deve ser executado no diretório ktr_platform!"
        exit 1
    fi
    
    echo -e "${BLUE}Iniciando deploy automatizado do KTR Platform...${NC}"
    echo
    
    # Executar passos
    check_dependencies
    generate_secure_passwords
    setup_environment
    prepare_build_environment
    select_deployment_profile
    build_images
    deploy_containers
    check_health
    show_access_info
    
    success "Deploy concluído com sucesso! 🚀"
}

# Verificar argumentos
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Uso: $0 [opções]"
    echo
    echo "Script de deploy automatizado para KTR Platform"
    echo
    echo "Opções:"
    echo "  -h, --help     Mostrar esta mensagem"
    echo "  --no-build     Pular build das imagens"
    echo "  --force        Forçar recreação de containers"
    echo
    exit 0
fi

# Executar deploy
main "$@" 