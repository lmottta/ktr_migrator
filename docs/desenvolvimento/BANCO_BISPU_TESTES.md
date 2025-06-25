# 🗄️ Banco BISPU para Testes de KTR

## 📋 Visão Geral

Esta documentação descreve a implementação do banco de dados BISPU para testes de persistência dos KTRs migrados. O banco replica a estrutura do ambiente real, permitindo testes seguros e isolados.

## 🎯 Objetivos

- ✅ Replicar ambiente real BISPU para testes
- ✅ Permitir testes de persistência dos KTRs migrados
- ✅ Isolar dados de teste do ambiente de produção
- ✅ Facilitar validação e debug dos pipelines
- ✅ Fornecer dados de exemplo para desenvolvimento

## 🏗️ Arquitetura

### 📊 Banco de Dados
- **Sistema**: PostgreSQL 15
- **Nome**: `bispu`
- **Porta**: `5433` (diferente do KTR Platform)
- **Encoding**: UTF-8 com suporte a português

### 🔧 Schemas Implementados
```sql
-- Schemas principais para testes
mgc                    # Dados de documentos e localização
etl                    # Processos de ETL
tmp                    # Tabelas temporárias
relatorios            # Relatórios finais
arrecadacao_dw        # Data warehouse arrecadação
```

### 📚 Tabelas de Teste

#### `mgc.documento`
```sql
CREATE TABLE mgc.documento (
    id SERIAL PRIMARY KEY,
    numero_documento VARCHAR(50) NOT NULL,
    tipo_documento VARCHAR(20),
    data_documento DATE,
    cpf_cnpj VARCHAR(18),
    nome_pessoa VARCHAR(255),
    valor DECIMAL(15,2),
    status VARCHAR(20) DEFAULT 'ATIVO',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `mgc.documento_processado`
```sql
CREATE TABLE mgc.documento_processado (
    id SERIAL PRIMARY KEY,
    documento_origem_id INTEGER,
    numero_documento VARCHAR(50),
    tipo_documento VARCHAR(20),
    data_documento DATE,
    cpf_cnpj_formatado VARCHAR(18),
    nome_pessoa_upper VARCHAR(255),
    valor_formatado DECIMAL(15,2),
    ambiente VARCHAR(20) DEFAULT 'LOCAL',
    processado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `mgc.localizacao_imovel`
```sql
CREATE TABLE mgc.localizacao_imovel (
    id SERIAL PRIMARY KEY,
    codigo_imovel VARCHAR(20) NOT NULL,
    endereco VARCHAR(500),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    uf VARCHAR(2),
    cep VARCHAR(9),
    coordenadas_lat DECIMAL(10,8),
    coordenadas_lng DECIMAL(11,8),
    area_total DECIMAL(12,2),
    status VARCHAR(20) DEFAULT 'ATIVO',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🚀 Deploy e Configuração

### 1. Configuração Inicial
```bash
# Navegar para o diretório da plataforma
cd ktr_platform

# Copiar arquivo de configuração
cp .env.bispu.example .env.bispu

# Editar configurações conforme necessário
nano .env.bispu
```

### 2. Deploy do Banco BISPU
```bash
# Deploy completo
./docker-deploy-bispu.sh

# Deploy com limpeza de dados
./docker-deploy-bispu.sh --clean
```

### 3. Verificação da Instalação
```bash
# Verificar se container está rodando
docker ps | grep bispu

# Acessar banco via psql
docker-compose exec bispu-db psql -U bispu_user -d bispu

# Verificar schemas criados
docker-compose exec bispu-db psql -U bispu_user -d bispu \
  -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast');"
```

## 🔗 Conexão e Acesso

### Informações de Conexão
```bash
Host: localhost
Porta: 5433
Banco: bispu
Usuário: bispu_user
Senha: bispu_secure_pass
```

### String de Conexão
```
postgresql://bispu_user:bispu_secure_pass@localhost:5433/bispu
```

### Acesso via DBeaver/PgAdmin
1. Criar nova conexão PostgreSQL
2. Usar as informações acima
3. Testar conexão
4. Explorar schemas: `mgc`, `etl`, `tmp`, `relatorios`

## 📊 Dados de Exemplo

### Documentos (mgc.documento)
```sql
-- 3 registros de exemplo inseridos automaticamente
SELECT * FROM mgc.documento;
```

### Localização Imóveis (mgc.localizacao_imovel)
```sql
-- 2 registros de exemplo inseridos automaticamente
SELECT * FROM mgc.localizacao_imovel;
```

## 🧪 Testes dos KTRs

### KTR: documento_mgc_pipeline
- **Origem**: `mgc.documento`
- **Destino**: `mgc.documento_processado`
- **Transformações**: Formatação de CPF/CNPJ, nome em maiúsculo

### KTR: localizacao_imovel_pipeline
- **Origem**: `mgc.localizacao_imovel`
- **Destino**: tabela a ser definida pelo KTR
- **Transformações**: Concatenação de endereço, formatação de coordenadas

## 🔧 Comandos Úteis

### Gerenciamento de Container
```bash
# Iniciar banco BISPU
docker-compose --profile bispu up -d bispu-db

# Parar banco BISPU
docker-compose --profile bispu down

# Ver logs do banco
docker-compose logs -f bispu-db

# Reiniciar banco
docker-compose restart bispu-db
```

### Backup e Restore
```bash
# Fazer backup
docker-compose exec bispu-db pg_dump -U bispu_user bispu > backup_bispu.sql

# Restaurar backup
docker-compose exec -T bispu-db psql -U bispu_user bispu < backup_bispu.sql

# Backup de schema específico
docker-compose exec bispu-db pg_dump -U bispu_user -n mgc bispu > backup_mgc.sql
```

### Monitoramento
```bash
# Verificar espaço usado
docker-compose exec bispu-db psql -U bispu_user -d bispu \
  -c "SELECT pg_size_pretty(pg_database_size('bispu'));"

# Verificar conexões ativas
docker-compose exec bispu-db psql -U bispu_user -d bispu \
  -c "SELECT * FROM pg_stat_activity WHERE datname = 'bispu';"

# Verificar performance de queries
docker-compose exec bispu-db psql -U bispu_user -d bispu \
  -c "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Porta já em uso
```bash
# Verificar processos usando porta 5433
netstat -tulpn | grep 5433

# Alterar porta no .env.bispu
BISPU_DB_PORT=5434
```

#### 2. Falha na conexão
```bash
# Verificar se container está rodando
docker ps | grep bispu

# Verificar logs para erros
docker-compose logs bispu-db

# Recriar container
docker-compose --profile bispu down
docker volume rm ktr-platform-bispu
./docker-deploy-bispu.sh
```

#### 3. Schemas não criados
```bash
# Verificar se script de inicialização existe
ls -la docker/init-bispu-db.sql

# Recriar banco com limpeza
./docker-deploy-bispu.sh --clean
```

### Logs e Debug
```bash
# Ver logs detalhados
docker-compose logs -f --tail=100 bispu-db

# Acessar container para debug
docker-compose exec bispu-db bash

# Verificar arquivos de log do PostgreSQL
docker-compose exec bispu-db ls -la /var/lib/postgresql/data/log/
```

## 📈 Performance e Otimização

### Configurações Aplicadas
```sql
-- Configurações otimizadas para testes
work_mem = 64MB
maintenance_work_mem = 256MB
effective_cache_size = 1GB
random_page_cost = 1.1
```

### Monitoramento de Performance
```sql
-- Consultas mais lentas
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 10;

-- Tamanho das tabelas
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables 
WHERE schemaname IN ('mgc', 'etl', 'tmp');
```

## 🔐 Segurança

### Controle de Acesso
- Usuário `bispu_user` com permissões limitadas
- Acesso apenas aos schemas necessários
- Porta diferente do banco principal (5433)

### Backup e Segurança
- Dados de teste, não contém informações sensíveis
- Backup automático opcional via cron
- Logs com retenção configurável

## 📝 Integração com KTR Platform

### Configuração na Aplicação
```python
# Adicionar em settings.py
BISPU_DATABASE = {
    'host': 'localhost',
    'port': 5433,
    'database': 'bispu',
    'user': 'bispu_user',
    'password': 'bispu_secure_pass',
    'schema': 'mgc'
}
```

### Testes Automatizados
- Validação de conexão ao iniciar aplicação
- Testes de persistência dos KTRs
- Verificação de integridade dos dados

---

## 📞 Suporte

Para questões técnicas ou problemas:
1. Verificar logs: `docker-compose logs bispu-db`
2. Consultar esta documentação
3. Contatar equipe de dados
4. Abrir issue no repositório

**Última atualização**: 2025-01-23  
**Versão**: 1.0  
**Desenvolvido por**: Engenheiro de Dados Senior 