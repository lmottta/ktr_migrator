# ��� KTR Platform Pro - Central de Jobs e Automação

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29%2B-red.svg)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

Sistema completo para **migração**, **execução** e **agendamento** de pipelines Pentaho KTR para Python, com interface web moderna, sistema de agendamentos avançado e **deployment Docker otimizado**.

## ��� **Características Principais**

### ��� **Migração Automatizada**
- ✅ **Parser KTR** - Análise completa de arquivos Pentaho
- ✅ **Geração de Código Python** - Templates otimizados e testados
- ✅ **Estrutura de Projeto** - Organização profissional com testes
- ✅ **Validação Inteligente** - Análise de compatibilidade avançada

### ⚡ **Execução e Monitoramento**
- ✅ **Executor Assíncrono** - Execução não-bloqueante multi-thread
- ✅ **Logs em Tempo Real** - Monitoramento detalhado com streaming
- ✅ **Status Tracking** - Acompanhamento completo de execuções
- ✅ **Métricas de Performance** - Analytics detalhadas de pipelines

### ⏰ **Sistema de Agendamentos Avançado**
- ✅ **7 Tipos de Agendamento** - Máxima flexibilidade de configuração
- ✅ **Cron Expressions** - Suporte completo a sintaxe cron
- ✅ **Scheduler Robusto** - Execução automática confiável 24/7
- ✅ **Interface Intuitiva** - Gerenciamento visual completo

### ��� **Interface Web Moderna**
- ✅ **Dashboard Interativo** - Visão geral em tempo real
- ✅ **Design Responsivo** - Funciona perfeitamente em qualquer dispositivo
- ✅ **UX Profissional** - Experiência do usuário excepcional
- ✅ **Analytics Avançado** - Métricas e insights de performance

### ��� **Deployment Docker (Novo!)**
- ✅ **Containerização Completa** - App + PostgreSQL + Redis + Nginx
- ✅ **Multi-Stage Build** - Imagens otimizadas para produção
- ✅ **Health Checks** - Monitoramento automático de saúde
- ✅ **Volumes Persistentes** - Dados seguros e backups automáticos
- ✅ **Scaling Ready** - Pronto para escalonamento horizontal

---

## ��� **Métodos de Instalação**

Escolha o método de instalação que melhor se adequa ao seu ambiente:

### ��� **Comparação dos Métodos**

| Característica | ��� Docker | ��� Local |
|----------------|-----------|----------|
| **Facilidade** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Isolamento** | ✅ Completo | ❌ Depende do Sistema |
| **Dependências** | ✅ Gerenciadas | ⚠️ Manual |
| **Produção** | ✅ Recomendado | ⚠️ Configuração Extra |
| **Desenvolvimento** | ✅ Excelente | ✅ Flexível |
| **Backup/Restore** | ✅ Automático | ❌ Manual |

---

## ��� **Instalação com Docker (Recomendado)**

### **✅ Vantagens do Docker**
- ��� **Isolamento Total** - Ambiente consistente
- ��� **Deploy em 1 Comando** - Configuração automatizada
- ��� **Monitoramento Integrado** - Prometheus + Grafana
- ��� **Backup Automático** - Volumes persistentes
- ��� **Proxy Reverso** - Nginx configurado

### **��� Pré-requisitos Docker**
- Docker Desktop 4.0+ ou Docker Engine 20.0+
- Docker Compose 2.0+
- 4GB RAM mínimo (8GB recomendado)
- 10GB espaço em disco

### **⚡ Quick Start Docker**

\`\`\`bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/ktr-platform-pro.git
cd ktr-platform-pro/ktr_platform

# 2. Deploy automatizado (RECOMENDADO)
./docker-deploy-simple.sh

# OU deploy manual
docker-compose up -d
\`\`\`

### **��� Acesso à Aplicação Docker**
\`\`\`bash
��� Aplicação Principal: http://localhost:8501
���️ PostgreSQL:         localhost:5432
��� Redis:              localhost:6379
��� Prometheus:         http://localhost:9090  (com --profile monitoring)
��� Grafana:            http://localhost:3000  (com --profile monitoring)
\`\`\`

### **��� Configuração Docker Avançada**

#### **Perfis de Deployment**
\`\`\`bash
# Desenvolvimento (App + DB + Cache)
docker-compose up -d

# Produção (+ Nginx Proxy)
docker-compose --profile production up -d

# Monitoramento (+ Prometheus + Grafana)
docker-compose --profile monitoring up -d

# Completo (Todos os serviços)
docker-compose --profile production --profile monitoring up -d
\`\`\`

#### **Comandos Úteis Docker**
\`\`\`bash
# Status dos containers
docker-compose ps

# Logs em tempo real
docker-compose logs -f ktr-platform

# Restart da aplicação
docker-compose restart ktr-platform

# Backup completo
docker-compose exec postgres-db pg_dump -U ktr_user ktr_platform > backup.sql

# Limpeza completa
docker-compose down --volumes
\`\`\`

---

## ��� **Instalação Local (Desenvolvimento)**

### **��� Pré-requisitos Locais**
- Python 3.8+ (Python 3.11 recomendado)
- pip 21.0+
- Git (opcional)
- PostgreSQL 13+ (opcional - para persistência)

### **��� Instalação Local**

\`\`\`bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/ktr-platform-pro.git
cd ktr-platform-pro

# 2. Crie um ambiente virtual (RECOMENDADO)
python -m venv venv

# Ative o ambiente virtual
# Windows:
venv\\Scripts\\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instale as dependências
pip install --upgrade pip
pip install -r requirements_platform.txt

# 4. Execute a aplicação
cd ktr_platform
streamlit run app.py
\`\`\`

### **��� Acesso à Aplicação Local**
\`\`\`bash
��� Interface Web: http://localhost:8501
��� Dashboard:     http://localhost:8501
\`\`\`

### **⚙️ Configuração Local Avançada**

#### **Banco de Dados PostgreSQL (Opcional)**
\`\`\`bash
# Instalar PostgreSQL
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# Windows: Download do site oficial
# Mac: brew install postgresql

# Criar banco de dados
sudo -u postgres createdb ktr_platform
sudo -u postgres createuser ktr_user
\`\`\`

#### **Configuração de Ambiente**
\`\`\`bash
# Criar arquivo .env (na pasta ktr_platform)
cp .env.example .env

# Editar configurações
nano .env
\`\`\`

#### **Scripts de Inicialização**
\`\`\`bash
# Windows
run_platform.bat

# Linux/Mac
chmod +x run_platform.py
python run_platform.py
\`\`\`

---

## ��� **Guia de Uso Completo**

### **��� Migração de KTR para Python**

#### **1. Upload e Análise**
\`\`\`bash
1. Acesse "➕ Importar Fluxo"
2. Faça upload do arquivo .ktr
3. Aguarde análise automática
4. Revise componentes detectados
\`\`\`

#### **2. Configuração e Geração**
\`\`\`bash
1. Customize configurações do pipeline
2. Selecione conectores de banco
3. Configure validações de dados
4. Clique "Gerar Pipeline Python"
\`\`\`

#### **3. Estrutura Gerada**
\`\`\`
flows/
└── [flow-id]/
    ├── src/
    │   ├── extractors/     # Extratores de dados
    │   ├── transformers/   # Transformações
    │   ├── loaders/        # Carregadores
    │   ├── pipelines/      # Pipeline principal
    │   └── utils/          # Utilitários
    ├── tests/              # Testes unitários
    ├── config/             # Configurações
    ├── requirements.txt    # Dependências
    └── README.md          # Documentação
\`\`\`

### **⚡ Execução e Monitoramento**

#### **1. Dashboard Principal**
- ��� **Visão Geral**: Métricas em tempo real
- ��� **Status dos Fluxos**: Monitoramento de execuções
- ��� **Analytics**: Performance e estatísticas
- ⏰ **Próximas Execuções**: Agenda de jobs

#### **2. Execução Manual**
\`\`\`bash
1. Selecione fluxo no dashboard
2. Clique "▶️ Executar"
3. Monitore logs em tempo real
4. Analise métricas de performance
\`\`\`

#### **3. Monitoramento Avançado**
- ��� **Logs Streaming**: Logs em tempo real
- ��� **Métricas**: CPU, Memória, Duração
- ��� **Debugging**: Stack traces detalhados
- ��� **Histórico**: Execuções anteriores

### **⏰ Sistema de Agendamentos**

#### **Tipos de Agendamento Disponíveis**

1. **��� Diário**
   \`\`\`python
   # Executa todos os dias no mesmo horário
   Exemplo: Todo dia às 14:30
   \`\`\`

2. **�� Semanal**
   \`\`\`python
   # Dias específicos da semana
   Exemplo: Segunda, Quarta e Sexta às 09:00
   \`\`\`

3. **���️ Datas Específicas**
   \`\`\`python
   # Datas escolhidas manualmente
   Exemplo: 15/01, 15/02, 15/03 às 10:00
   \`\`\`

4. **⚙️ Personalizado**
   \`\`\`python
   # Usando expressões cron
   Exemplo: 0 */4 * * * (a cada 4 horas)
   \`\`\`

5. **��� Múltiplos Horários**
   \`\`\`python
   # Vários horários por dia
   Exemplo: 08:00, 12:00, 18:00
   \`\`\`

6. **��� Horários por Dia**
   \`\`\`python
   # Configuração individual por dia da semana
   Exemplo: Seg(09:00), Ter(10:00), Qua(11:00)
   \`\`\`

7. **⏱️ Por Intervalo**
   \`\`\`python
   # Execução a cada X minutos
   Exemplo: A cada 30 minutos
   \`\`\`

#### **Configuração de Agendamentos**
\`\`\`bash
1. Acesse "⏰ Agendamentos"
2. Clique "➕ Novo Agendamento"
3. Selecione o fluxo
4. Escolha tipo de agendamento
5. Configure horários/periodicidade
6. Ative o agendamento
\`\`\`

---

## ���️ **Arquitetura do Sistema**

### **��� Componentes Principais**

#### **Parser Engine**
\`\`\`python
src/parser/ktr_parser.py      # Parser principal de KTR
src/models/ktr_models.py      # Modelos de dados
src/analyzer/pipeline_analyzer.py  # Análise de pipelines
\`\`\`

#### **Code Generator**
\`\`\`python
src/generator/code_generator.py    # Gerador de código Python
src/templates/                     # Templates Jinja2
\`\`\`

#### **Platform Core**
\`\`\`python
ktr_platform/flow_manager.py      # Gerenciamento de fluxos
ktr_platform/executor.py          # Executor assíncrono
ktr_platform/scheduler.py         # Sistema de agendamentos
ktr_platform/app.py               # Interface Streamlit
\`\`\`

### **��� Estrutura de Diretórios**
\`\`\`
ktr_migrator/
├── �� ktr_platform/              # Plataforma principal
│   ├── app.py                    # Interface Streamlit
│   ├── flow_manager.py           # Gerenciamento de fluxos
│   ├── executor.py               # Executor de fluxos
│   ├── scheduler.py              # Sistema de agendamentos
│   ├── ��� docker/                # Configurações Docker
│   │   ├── Dockerfile            # Imagem da aplicação
│   │   ├── docker-compose.yml    # Orquestração
│   │   ├── entrypoint.sh         # Script de inicialização
│   │   ├── nginx.conf            # Configuração Nginx
│   │   └── prometheus.yml        # Configuração Prometheus
│   ├── ��� data/                  # Dados persistentes
│   │   ├── flows.json            # Metadados dos fluxos
│   │   └── schedules.json        # Agendamentos
│   └── ��� flows/                 # Fluxos migrados
├── ��� src/                       # Código fonte da migração
│   ├── parser/                   # Parser KTR
│   ├── generator/                # Gerador de código
│   ├── analyzer/                 # Analisador de pipelines
│   ├── models/                   # Modelos de dados
│   └── templates/                # Templates de código
├── ��� examples/                  # Exemplos e demos
├── ��� tests/                     # Testes automatizados
├── ��� docs/                      # Documentação
│   └── desenvolvimento/          # Docs técnicas
└── ��� requirements*.txt          # Dependências
\`\`\`

---

## ��� **Configuração Avançada**

### **��� Variáveis de Ambiente**

#### **Aplicação**
\`\`\`env
# Configurações principais
KTR_PORT=8501                    # Porta da aplicação
LOG_LEVEL=INFO                   # Nível de log
ENV=development                  # Ambiente (dev/staging/prod)

# Streamlit
STREAMLIT_THEME_PRIMARY_COLOR=#FF6B6B
STREAMLIT_MAX_UPLOAD_SIZE=200
\`\`\`

#### **Banco de Dados**
\`\`\`env
# PostgreSQL
DATABASE_HOST=postgres-db
DATABASE_PORT=5432
DATABASE_NAME=ktr_platform
DATABASE_USER=ktr_user
DATABASE_PASSWORD=sua_senha_aqui
\`\`\`

#### **Cache e Sessões**
\`\`\`env
# Redis
REDIS_HOST=redis-cache
REDIS_PORT=6379
REDIS_PASSWORD=sua_senha_redis
REDIS_DB=0
\`\`\`

#### **Segurança**
\`\`\`env
# Chaves de segurança
SECRET_KEY=sua_chave_secreta_aqui
JWT_SECRET=sua_chave_jwt_aqui
JWT_EXPIRATION_HOURS=24
\`\`\`

### **��� Segurança e Produção**

#### **Configurações de Produção**
\`\`\`bash
# Usar senhas seguras
openssl rand -base64 32  # Gerar senha PostgreSQL
openssl rand -base64 32  # Gerar senha Redis
openssl rand -base64 64  # Gerar chave JWT

# SSL/TLS (para produção)
# Configurar certificados válidos no Nginx
\`\`\`

#### **Backup e Recuperação**
\`\`\`bash
# Backup automático (Docker)
docker-compose exec postgres-db pg_dump -U ktr_user ktr_platform > backup.sql

# Backup de volumes
docker run --rm -v ktr-platform-data:/data -v $(pwd):/backup alpine \\
  tar czf /backup/backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .

# Restauração
docker-compose exec -T postgres-db psql -U ktr_user ktr_platform < backup.sql
\`\`\`

---

## ��� **Desenvolvimento e Testes**

### **��� Ambiente de Desenvolvimento**
\`\`\`bash
# Setup desenvolvimento
git clone https://github.com/seu-usuario/ktr-platform-pro.git
cd ktr-platform-pro
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\\Scripts\\activate     # Windows
pip install -r requirements_platform.txt

# Executar testes
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html

# Executar aplicação em modo debug
cd ktr_platform
streamlit run app.py --server.runOnSave=true
\`\`\`

### **��� Testes Automatizados**
\`\`\`bash
# Executar todos os testes
pytest

# Testes com cobertura
pytest --cov=src --cov=ktr_platform

# Testes específicos
pytest tests/test_ktr_parser.py -v
pytest tests/test_code_generator.py -v
\`\`\`

### **��� Performance e Monitoramento**
\`\`\`bash
# Métricas de performance (Docker)
docker stats ktr-platform-app

# Logs detalhados
docker-compose logs -f --tail=100 ktr-platform

# Health checks
curl -f http://localhost:8501/_stcore/health
\`\`\`

---

## ��� **Troubleshooting**

### **❓ Problemas Comuns**

#### **Docker**
\`\`\`bash
# Container não inicia
docker-compose logs ktr-platform

# Erro de dependências
docker-compose build --no-cache ktr-platform

# Erro de permissões
docker-compose down --volumes
docker-compose up -d
\`\`\`

#### **Local**
\`\`\`bash
# Erro de módulos
pip install -r requirements_platform.txt --force-reinstall

# Erro de porta
lsof -ti:8501  # Linux/Mac
netstat -ano | findstr :8501  # Windows

# Cache do Streamlit
streamlit cache clear
\`\`\`

### **��� Logs e Debugging**
\`\`\`bash
# Logs da aplicação
tail -f ktr_platform/logs/*.log

# Debug modo desenvolvimento
export STREAMLIT_DEBUG=true
streamlit run app.py

# Profiling de performance
pip install streamlit-profiler
\`\`\`

---

## ��� **Documentação Adicional**

- ��� **[Guia de Migração KTR](docs/desenvolvimento/GUIA_MIGRACAO.md)**
- ��� **[Docker Deployment](ktr_platform/README_DOCKER.md)**
- ⏰ **[Sistema de Agendamentos](HORARIOS_CUSTOMIZADOS.md)**
- ��� **[API Reference](docs/desenvolvimento/API_REFERENCE.md)**
- ��� **[Guia de Testes](docs/desenvolvimento/GUIA_TESTES.md)**

---

## ��� **Contribuição**

1. Fork o projeto
2. Crie uma branch para sua feature (\`git checkout -b feature/nova-feature\`)
3. Commit suas mudanças (\`git commit -am 'Adiciona nova feature'\`)
4. Push para a branch (\`git push origin feature/nova-feature\`)
5. Abra um Pull Request

---

## ��� **Licença**

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## ��� **Roadmap**

- [ ] **Integração com Apache Airflow**
- [ ] **Suporte a Kubernetes**
- [ ] **API REST completa**
- [ ] **Integração com CI/CD**
- [ ] **Suporte a Spark/PySpark**
- [ ] **Machine Learning Pipelines**
- [ ] **Conectores adicionais** (Snowflake, BigQuery, etc.)

---

## ��� **Suporte**

- ��� **Email**: suporte@ktr-platform.com
- ��� **Discord**: [KTR Platform Community](https://discord.gg/ktr-platform)
- ��� **Issues**: [GitHub Issues](https://github.com/seu-usuario/ktr-platform-pro/issues)
- ��� **Documentação**: [Wiki Completa](https://github.com/seu-usuario/ktr-platform-pro/wiki)

---

<div align="center">

**��� Desenvolvido com ❤️ para a comunidade de Engenharia de Dados**

[![Stars](https://img.shields.io/github/stars/seu-usuario/ktr-platform-pro?style=social)](https://github.com/seu-usuario/ktr-platform-pro)
[![Forks](https://img.shields.io/github/forks/seu-usuario/ktr-platform-pro?style=social)](https://github.com/seu-usuario/ktr-platform-pro)
[![Issues](https://img.shields.io/github/issues/seu-usuario/ktr-platform-pro)](https://github.com/seu-usuario/ktr-platform-pro/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/seu-usuario/ktr-platform-pro)](https://github.com/seu-usuario/ktr-platform-pro/pulls)

</div>
