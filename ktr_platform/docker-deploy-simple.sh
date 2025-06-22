#!/bin/bash

# =============================================================================
# KTR PLATFORM - SCRIPT DE DEPLOY SIMPLIFICADO
# =============================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Funções auxiliares
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] ✅${NC} $1"
}

info() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] ℹ️${NC}  $1"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ❌${NC} $1" >&2
}

# Banner
echo "🚀 KTR PLATFORM - Deploy Simplificado"
echo "======================================"

# Verificar se está no diretório correto
if [ ! -f docker-compose.yml ]; then
    error "Execute este script no diretório ktr_platform!"
    exit 1
fi

# 1. Preparar requirements no contexto
info "Preparando dependências..."
if [ ! -f ../requirements_platform.txt ]; then
    error "Arquivo requirements_platform.txt não encontrado no diretório raiz!"
    exit 1
fi
log "requirements_platform.txt encontrado no diretório raiz"

# 2. Verificar arquivo .env
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        log "Arquivo .env criado a partir do exemplo"
    else
        error "Arquivo .env.example não encontrado!"
        exit 1
    fi
fi

# 3. Limpar ambiente anterior
info "Limpando ambiente anterior..."
docker-compose down --remove-orphans || true
docker system prune -f || true

# 4. Build das imagens
info "Construindo imagens..."
docker-compose build --no-cache ktr-platform

if [ $? -ne 0 ]; then
    error "Falha no build da imagem!"
    exit 1
fi

log "Build concluído com sucesso"

# 5. Iniciar apenas os serviços essenciais
info "Iniciando serviços essenciais..."
docker-compose up -d postgres-db redis-cache

# Aguardar banco de dados
info "Aguardando banco de dados..."
sleep 10

# 6. Iniciar aplicação principal
info "Iniciando aplicação principal..."
docker-compose up -d ktr-platform

# 7. Verificar status
info "Verificando status dos containers..."
docker-compose ps

# 8. Mostrar logs iniciais
info "Logs da aplicação:"
docker-compose logs --tail=20 ktr-platform

echo
log "Deploy simplificado concluído!"
echo "Acesse: http://localhost:8501"
echo
echo "Comandos úteis:"
echo "  docker-compose logs -f ktr-platform  # Ver logs em tempo real"
echo "  docker-compose down                  # Parar containers"
echo "  docker-compose ps                    # Status dos containers" 