# 🐳 Implementação Docker do KTR Platform

## 📋 Visão Geral

Documentação técnica completa da implementação Docker do KTR Platform, incluindo decisões arquiteturais, considerações de segurança e diretrizes operacionais.

## 🏗️ Arquitetura da Solução

### Multi-stage Build Strategy

A implementação utiliza uma estratégia de **multi-stage build** para otimizar o tamanho da imagem final:

```dockerfile
# Stage 1: Builder (inclui ferramentas de compilação)
FROM python:3.11-slim as builder
RUN apt-get update && apt-get install -y build-essential...

# Stage 2: Production (apenas runtime)
FROM python:3.11-slim
COPY --from=builder /usr/local/lib/python3.11/site-packages...
```

**Benefícios:**
- Redução de 40-50% no tamanho da imagem final
- Exclusão de ferramentas de desenvolvimento da produção
- Melhor performance em pulls/pushes

### Container Security

#### Usuário Não-Root
```dockerfile
RUN groupadd -r ktruser && useradd -r -g ktruser ktruser
USER ktruser
```

#### Configurações de Segurança
- **Princípio do menor privilégio**: Containers executam com usuários dedicados
- **Read-only filesystems**: Volumes específicos para dados mutáveis
- **Health checks**: Monitoramento automático de saúde dos containers
- **Resource limits**: Limitação de CPU e memória via Docker Compose

### Rede e Isolamento

```yaml
networks:
  ktr-network:
    driver: bridge
    name: ktr-platform-network
```

**Características:**
- Rede isolada para todos os serviços
- Comunicação inter-container via DNS interno
- Exposição seletiva de portas para o host
- Configuração de firewall via Docker

## 📊 Serviços e Componentes

### 1. KTR Platform App
- **Imagem**: Custom build (ktr-platform:latest)
- **Recursos**: 1GB RAM, 1 CPU core
- **Volumes**: data, logs, flows
- **Health Check**: HTTP endpoint `/_stcore/health`

### 2. PostgreSQL Database
- **Imagem**: postgres:15-alpine
- **Volumes**: postgres_data (persistente)
- **Inicialização**: Script SQL automático
- **Backup**: Automated via cron jobs

### 3. Redis Cache
- **Imagem**: redis:7-alpine
- **Configuração**: AOF persistence habilitado
- **Autenticação**: Password-based
- **Uso**: Cache de sessões e dados temporários

### 4. Nginx Proxy (Produção)
- **Imagem**: nginx:alpine
- **Configuração**: Proxy reverso + SSL/TLS
- **Balanceamento**: Ready para múltiplas instâncias
- **Compressão**: Gzip habilitado

### 5. Prometheus + Grafana (Monitoramento)
- **Prometheus**: Coleta de métricas
- **Grafana**: Dashboards e alertas
- **Retenção**: 15 dias de métricas
- **Alertas**: Configuráveis via webhook

## 🔐 Segurança e Compliance

### Secrets Management

#### Geração de Senhas
```bash
# Senhas criptograficamente seguras
openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
```

#### Armazenamento Seguro
- Senhas armazenadas em variáveis de ambiente
- Arquivo `.env` excluído do build via `.dockerignore`
- Rotação periódica recomendada

### Configurações de Segurança

#### Container Security
```yaml
security_opt:
  - no-new-privileges:true
cap_drop:
  - ALL
cap_add:
  - CHOWN
  - SETGID
  - SETUID
```

#### Network Security
- Comunicação TLS entre serviços
- Isolamento de rede por ambiente
- Rate limiting via Nginx
- CORS configurado adequadamente

### Compliance

#### LGPD/GDPR
- Logs com retenção limitada (30 dias)
- Pseudonimização de dados sensíveis
- Direito ao esquecimento via scripts automatizados
- Auditoria completa de acessos

#### SOX/ISO 27001
- Segregação de ambientes (dev/staging/prod)
- Controle de versão de configurações
- Backup e recuperação testados
- Documentação de mudanças

## 🚀 Deployment Strategies

### Ambiente de Desenvolvimento
```bash
# Deploy simples
docker-compose up -d

# Com rebuild
docker-compose up -d --build
```

### Ambiente de Staging
```bash
# Deploy com monitoramento
docker-compose --profile monitoring up -d

# Testes automatizados
docker-compose exec ktr-platform python -m pytest
```

### Ambiente de Produção
```bash
# Deploy completo com proxy
docker-compose --profile production --profile monitoring up -d

# Zero-downtime deployment
docker-compose pull
docker-compose up -d --no-deps --force-recreate ktr-platform
```

### Blue-Green Deployment
```bash
# Terminal 1: Ambiente Blue (atual)
docker-compose -f docker-compose.blue.yml up -d

# Terminal 2: Ambiente Green (nova versão)
docker-compose -f docker-compose.green.yml up -d

# Switch no load balancer
# Rollback se necessário
```

## 📈 Monitoramento e Observabilidade

### Métricas Coletadas

#### Aplicação
- Tempo de resposta de endpoints
- Número de pipelines executados
- Taxa de erro por pipeline
- Uso de memória e CPU

#### Infraestrutura
- Status dos containers
- Uso de recursos do sistema
- Métricas de rede
- Espaço em disco

### Alertas Configurados

#### Críticos
- Container down
- Alto uso de CPU (>80%)
- Erro em pipeline crítico
- Falha de backup

#### Informativos
- Deploy realizado
- Limpeza de logs
- Atualização de dependências
- Renovação de certificados

### Dashboards Grafana

#### Dashboard Operacional
- Status geral dos serviços
- Throughput de pipelines
- Tempo médio de execução
- Taxa de sucesso/falha

#### Dashboard Técnico
- Métricas de containers
- Logs agregados
- Performance de queries
- Análise de tendências

## 💾 Backup e Disaster Recovery

### Estratégia de Backup

#### Dados da Aplicação
```bash
# Backup automático diário (2h da manhã)
0 2 * * * /app/scripts/backup-data.sh

# Componentes incluídos:
- Configurações de flows
- Logs de execução
- Metadados de pipelines
- Configurações do sistema
```

#### Banco de Dados
```bash
# Backup PostgreSQL
docker-compose exec postgres-db pg_dump -U ktr_user -Fc ktr_platform > backup.sql

# Backup incremental
pg_basebackup -D /backup/base -Ft -z -P -U ktr_user
```

#### Volumes Docker
```bash
# Backup de volumes
docker run --rm -v ktr-platform-data:/source -v /backup:/dest alpine \
  tar czf /dest/data-backup-$(date +%Y%m%d).tar.gz -C /source .
```

### Disaster Recovery

#### RTO/RPO Targets
- **RTO (Recovery Time Objective)**: < 30 minutos
- **RPO (Recovery Point Objective)**: < 4 horas
- **Disponibilidade**: 99.5% (4h downtime/mês)

#### Procedimentos de Recuperação

##### Perda Total do Ambiente
```bash
# 1. Restaurar infraestrutura
docker-compose down
docker system prune -f

# 2. Restaurar dados
./scripts/restore-from-backup.sh /backup/latest

# 3. Validar integridade
./scripts/validate-restore.sh

# 4. Reiniciar serviços
docker-compose up -d
```

##### Corrupção de Dados
```bash
# 1. Identificar escopo da corrupção
./scripts/data-integrity-check.sh

# 2. Restaurar apenas dados afetados
./scripts/selective-restore.sh --table flows --date 2025-06-19

# 3. Validar consistência
./scripts/validate-data-consistency.sh
```

## 🔄 CI/CD Integration

### Pipeline de Build

```yaml
# .github/workflows/docker-build.yml
name: Docker Build and Push
on:
  push:
    branches: [main, develop]
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and test
        run: |
          docker-compose -f docker-compose.test.yml build
          docker-compose -f docker-compose.test.yml run --rm tests
      
      - name: Build production image
        run: |
          docker build -t ktr-platform:${{ github.sha }} .
          docker tag ktr-platform:${{ github.sha }} ktr-platform:latest
      
      - name: Push to registry
        run: |
          docker push ktr-platform:${{ github.sha }}
          docker push ktr-platform:latest
```

### Deployment Automation

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production
on:
  workflow_run:
    workflows: ["Docker Build and Push"]
    types: [completed]
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: |
          ssh staging-server 'cd /app && docker-compose pull && docker-compose up -d'
      
      - name: Run smoke tests
        run: |
          curl -f http://staging.ktr-platform.com/health
      
      - name: Deploy to production
        if: success()
        run: |
          ssh prod-server 'cd /app && ./scripts/zero-downtime-deploy.sh'
```

## 🛠️ Troubleshooting

### Problemas Comuns

#### Container não inicia
```bash
# Diagnóstico
docker-compose logs ktr-platform
docker-compose config
docker inspect ktr-platform-app

# Soluções comuns
- Verificar variáveis de ambiente
- Validar permissões de volumes
- Confirmar dependências de rede
```

#### Performance baixa
```bash
# Análise de recursos
docker stats
docker-compose top

# Otimizações
- Aumentar limits de CPU/memoria
- Otimizar queries de banco
- Configurar cache Redis
```

#### Problemas de conectividade
```bash
# Teste de rede
docker-compose exec ktr-platform ping postgres-db
docker-compose exec ktr-platform telnet redis-cache 6379

# Verificar DNS interno
docker-compose exec ktr-platform nslookup postgres-db
```

### Ferramentas de Debug

#### Logs Estruturados
```bash
# Logs da aplicação
docker-compose logs -f --tail=100 ktr-platform

# Logs do sistema
docker-compose exec ktr-platform tail -f /var/log/app/*.log

# Logs agregados
docker-compose logs | grep ERROR
```

#### Monitoring em Tempo Real
```bash
# Recursos em tempo real
watch docker stats

# Processos nos containers
docker-compose exec ktr-platform htop

# Conexões de rede
docker-compose exec ktr-platform netstat -tulpn
```

## 📚 Referências e Recursos

### Documentação Oficial
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Compose Production](https://docs.docker.com/compose/production/)
- [Container Security](https://docs.docker.com/engine/security/)

### Ferramentas Recomendadas
- **Portainer**: Interface web para Docker
- **Watchtower**: Auto-update de containers
- **Traefik**: Load balancer moderno
- **Loki**: Agregação de logs

### Comunidade e Suporte
- [KTR Platform GitHub](https://github.com/organization/ktr-platform)
- [Docker Community Forum](https://forums.docker.com/)
- [Stack Overflow - Docker](https://stackoverflow.com/questions/tagged/docker)

---

**Implementado em**: 2025-06-19  
**Versão Docker**: 1.0  
**Responsável Técnico**: Engenheiro de Dados Senior  
**Próxima Revisão**: 2025-07-19 