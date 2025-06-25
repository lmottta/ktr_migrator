#!/bin/bash

# ================================================================================
# SCRIPT DE DEPLOY - AMBIENTE BISPU PARA TESTES KTR
# ================================================================================
# Desenvolvido por: Engenheiro de Dados Senior
# Data: 2025-01-23
# Propósito: Deploy do banco BISPU para testes de persistência dos KTRs

set -e  # Para execução no primeiro erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

# Banner
echo "
╔════════════════════════════════════════════════════════════════════════════════╗
║                        KTR PLATFORM - DEPLOY BISPU                            ║
║                        Banco de Testes para KTRs                              ║
║                     Desenvolvido por: Engenheiro de Dados                     ║
╚════════════════════════════════════════════════════════════════════════════════╝
"

# Verificar se Docker está rodando
log "Verificando Docker..."
if ! docker info >/dev/null 2>&1; then
    log_error "Docker não está rodando. Inicie o Docker Desktop primeiro."
    exit 1
fi
log_success "Docker está rodando"

# Verificar se arquivo .env.bispu existe
if [ ! -f ".env.bispu" ]; then
    log_warning "Arquivo .env.bispu não encontrado. Criando a partir do exemplo..."
    if [ -f ".env.bispu.example" ]; then
        cp .env.bispu.example .env.bispu
        log_success "Arquivo .env.bispu criado. Configure as variáveis conforme necessário."
    else
        log_error "Arquivo .env.bispu.example não encontrado!"
        exit 1
    fi
fi

# Carregar variáveis de ambiente
if [ -f ".env.bispu" ]; then
    log "Carregando configurações do .env.bispu..."
    set -a
    # Filtrar linhas de comentário e vazias antes de carregar
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Ignorar linhas de comentário e vazias
        if [[ ! "$line" =~ ^[[:space:]]*# ]] && [[ -n "$line" ]] && [[ "$line" =~ ^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*= ]]; then
            export "$line"
        fi
    done < .env.bispu
    set +a
    log_success "Configurações carregadas"
fi

# Verificar se o script de inicialização existe
if [ ! -f "docker/init-bispu-db.sql" ]; then
    log_error "Script de inicialização docker/init-bispu-db.sql não encontrado!"
    exit 1
fi

# Função para limpar containers antigos
cleanup_containers() {
    log "Verificando containers existentes..."
    
    if docker ps -a --format 'table {{.Names}}' | grep -q "ktr-platform-bispu-db"; then
        log_warning "Container BISPU existente encontrado. Removendo..."
        docker-compose --profile bispu down bispu-db
        docker container rm -f ktr-platform-bispu-db 2>/dev/null || true
        log_success "Container antigo removido"
    fi
}

# Função para limpar volumes (opcional)
cleanup_volumes() {
    read -p "Deseja limpar os dados existentes do BISPU? (y/N): " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_warning "Removendo volume de dados BISPU..."
        docker volume rm ktr-platform-bispu 2>/dev/null || true
        log_success "Volume removido"
    fi
}

# Função para build e deploy
deploy_bispu() {
    log "Iniciando deploy do banco BISPU..."
    
    # Subir apenas o serviço BISPU
    log "Subindo banco BISPU..."
    docker-compose --profile bispu up -d bispu-db
    
    # Aguardar o banco ficar ready
    log "Aguardando banco BISPU ficar disponível..."
    local retries=30
    local count=0
    
    while [ $count -lt $retries ]; do
        if docker-compose exec -T bispu-db pg_isready -U ${BISPU_DB_USER:-bispu_user} -d ${BISPU_DB_NAME:-bispu} >/dev/null 2>&1; then
            log_success "Banco BISPU está disponível!"
            break
        fi
        
        count=$((count + 1))
        log "Tentativa $count/$retries - Aguardando..."
        sleep 2
    done
    
    if [ $count -eq $retries ]; then
        log_error "Timeout - Banco BISPU não ficou disponível"
        exit 1
    fi
}

# Função para verificar a instalação
verify_installation() {
    log "Verificando instalação..."
    
    # Verificar se o container está rodando
    if ! docker ps --format 'table {{.Names}}' | grep -q "ktr-platform-bispu-db"; then
        log_error "Container BISPU não está rodando"
        return 1
    fi
    
    # Verificar conexão com banco
    if ! docker-compose exec -T bispu-db psql -U ${BISPU_DB_USER:-bispu_user} -d ${BISPU_DB_NAME:-bispu} -c "SELECT version();" >/dev/null 2>&1; then
        log_error "Não foi possível conectar ao banco BISPU"
        return 1
    fi
    
    # Verificar schemas
    local schema_count=$(docker-compose exec -T bispu-db psql -U ${BISPU_DB_USER:-bispu_user} -d ${BISPU_DB_NAME:-bispu} -t -c "SELECT count(*) FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast');" | tr -d ' ')
    
    if [ "$schema_count" -ge "5" ]; then
        log_success "Schemas BISPU criados: $schema_count schemas"
    else
        log_warning "Poucos schemas encontrados: $schema_count"
    fi
    
    # Verificar tabelas de teste
    local table_count=$(docker-compose exec -T bispu-db psql -U ${BISPU_DB_USER:-bispu_user} -d ${BISPU_DB_NAME:-bispu} -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'mgc';" | tr -d ' ')
    
    if [ "$table_count" -ge "2" ]; then
        log_success "Tabelas de teste criadas no schema MGC: $table_count tabelas"
    else
        log_warning "Poucas tabelas de teste encontradas: $table_count"
    fi
    
    # Verificar dados de exemplo
    local data_count=$(docker-compose exec -T bispu-db psql -U ${BISPU_DB_USER:-bispu_user} -d ${BISPU_DB_NAME:-bispu} -t -c "SELECT count(*) FROM mgc.documento;" | tr -d ' ')
    
    if [ "$data_count" -gt "0" ]; then
        log_success "Dados de exemplo inseridos: $data_count registros em mgc.documento"
    else
        log_warning "Nenhum dado de exemplo encontrado"
    fi
}

# Função para mostrar informações de conexão
show_connection_info() {
    log_success "
╔════════════════════════════════════════════════════════════════════════════════╗
║                            BANCO BISPU DISPONÍVEL                             ║
╠════════════════════════════════════════════════════════════════════════════════╣
║ 📊 Host: localhost                                                            ║
║ 🔌 Porta: ${BISPU_DB_PORT:-5433}                                                      ║
║ 🗄️  Banco: ${BISPU_DB_NAME:-bispu}                                                    ║
║ 👤 Usuário: ${BISPU_DB_USER:-bispu_user}                                              ║
║ 🔑 Senha: ${BISPU_DB_PASSWORD:-bispu_secure_pass}                                     ║
╠════════════════════════════════════════════════════════════════════════════════╣
║ 📋 Schemas principais: mgc, etl, tmp, relatorios                              ║
║ 🧪 Tabelas de teste: mgc.documento, mgc.localizacao_imovel                    ║
║ 📈 Dados de exemplo: Sim                                                      ║
╠════════════════════════════════════════════════════════════════════════════════╣
║ 🔗 String de conexão:                                                         ║
║ postgresql://${BISPU_DB_USER:-bispu_user}:${BISPU_DB_PASSWORD:-bispu_secure_pass}@localhost:${BISPU_DB_PORT:-5433}/${BISPU_DB_NAME:-bispu} ║
╚════════════════════════════════════════════════════════════════════════════════╝
"
}

# Função para listar comandos úteis
show_useful_commands() {
    echo "
╔════════════════════════════════════════════════════════════════════════════════╗
║                              COMANDOS ÚTEIS                                   ║
╠════════════════════════════════════════════════════════════════════════════════╣
║ # Acessar banco via psql:                                                     ║
║ docker-compose exec bispu-db psql -U ${BISPU_DB_USER:-bispu_user} -d ${BISPU_DB_NAME:-bispu}              ║
║                                                                                ║
║ # Ver logs do banco:                                                           ║
║ docker-compose logs -f bispu-db                                               ║
║                                                                                ║
║ # Parar o banco BISPU:                                                         ║
║ docker-compose --profile bispu down                                           ║
║                                                                                ║
║ # Backup do banco:                                                             ║
║ docker-compose exec bispu-db pg_dump -U ${BISPU_DB_USER:-bispu_user} ${BISPU_DB_NAME:-bispu} > backup.sql  ║
║                                                                                ║
║ # Verificar schemas:                                                           ║
║ docker-compose exec bispu-db psql -U ${BISPU_DB_USER:-bispu_user} -d ${BISPU_DB_NAME:-bispu} \\            ║
║   -c \"SELECT * FROM information_schema.schemata;\"                             ║
╚════════════════════════════════════════════════════════════════════════════════╝
"
}

# ================================================================================
# EXECUÇÃO PRINCIPAL
# ================================================================================

# Menu de opções
if [ "$1" = "--clean" ]; then
    cleanup_volumes
fi

# Executar steps
cleanup_containers
deploy_bispu
verify_installation
show_connection_info
show_useful_commands

log_success "✅ Deploy do banco BISPU concluído com sucesso!"
log "🚀 O banco está pronto para testes dos KTRs migrados"

# Verificar se deve subir a aplicação principal também
read -p "Deseja subir a aplicação KTR Platform também? (y/N): " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "Subindo aplicação KTR Platform..."
    docker-compose up -d ktr-platform
    log_success "Aplicação KTR Platform iniciada!"
    echo "🌐 Acesse: http://localhost:8501"
fi 