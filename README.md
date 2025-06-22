# KTR Platform Pro - Central de Jobs e Automação

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29%2B-red.svg)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

---

**KTR Platform Pro** é um sistema completo para **migração, execução e agendamento** de pipelines de dados, modernizando fluxos criados em Pentaho (KTR) para código Python executável, modular e performático.

A plataforma oferece uma interface web para gerenciar todo o ciclo de vida dos fluxos, desde a importação e geração de código até a execução e o monitoramento contínuo.

## Principais Funcionalidades

- **Migração Automatizada**: Converte arquivos `.ktr` do Pentaho em uma estrutura de projeto Python robusta, com código organizado em extratores, transformadores e carregadores.
- **Execução e Monitoramento**: Permite a execução de pipelines de forma assíncrona, com logs em tempo real e tracking de status para cada etapa do processo.
- **Sistema de Agendamentos**: Oferece múltiplos tipos de agendamento, incluindo suporte a expressões cron, para automatizar a execução dos fluxos.
- **Interface Web Intuitiva**: Um dashboard centralizado construído com Streamlit para gerenciar fluxos, agendamentos e visualizar o histórico de execuções.
- **Deployment com Docker**: Ambiente de produção e desenvolvimento containerizado com Docker Compose, incluindo banco de dados, cache e proxy reverso.

---

## Como Começar

Você pode executar o projeto utilizando Docker (recomendado para maior simplicidade e consistência) ou em seu ambiente local.

### Pré-requisitos

- **Docker**: Docker Desktop 4.0+ ou Docker Engine 20.0+ e Docker Compose 2.0+.
- **Local**: Python 3.8 ou superior e `pip`.

### 1. Instalação com Docker (Recomendado)

O método com Docker provisiona todo o ambiente necessário, incluindo banco de dados e outros serviços.

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/ktr-platform-pro.git
cd ktr-platform-pro/ktr_platform

# 2. Execute o script de deploy simplificado
# Este comando irá construir as imagens e iniciar os contêineres.
./docker-deploy-simple.sh

# 3. Acesse a aplicação
# A interface estará disponível em http://localhost:8501
```

Para mais detalhes sobre a configuração avançada com Docker, incluindo perfis de monitoramento e produção, consulte a documentação em `docs/desenvolvimento/DOCKER_IMPLEMENTATION.md`.

### 2. Instalação em Ambiente Local

Recomendado para desenvolvimento e testes diretos.

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/ktr-platform-pro.git
cd ktr-platform-pro

# 2. Crie e ative um ambiente virtual
python -m venv venv
# No Windows: venv\Scripts\activate
# No Linux/macOS: source venv/bin/activate

# 3. Instale as dependências
pip install --upgrade pip
pip install -r requirements_platform.txt

# 4. Execute a aplicação
cd ktr_platform
streamlit run app.py
```

---

## Guia de Uso

1.  **Importar Fluxo**: Na interface web, utilize a opção "➕ Importar Fluxo" para fazer o upload de um arquivo `.ktr`.
2.  **Análise e Geração**: A plataforma analisará o arquivo, exibirá os componentes detectados e permitirá que você gere o código Python correspondente.
3.  **Execução**: Após a geração, o novo fluxo aparecerá no dashboard, de onde poderá ser executado manualmente.
4.  **Agendamento**: Crie agendamentos para executar os fluxos automaticamente em intervalos definidos.
5.  **Monitoramento**: Acompanhe o status e os logs de cada execução na seção de "Histórico".

## Estrutura do Projeto Gerado

Ao migrar um KTR, a plataforma cria a seguinte estrutura de diretórios dentro de `ktr_platform/flows/`:

```
[flow-id]/
├── src/
│   ├── extractors/     # Módulos de extração de dados
│   ├── transformers/   # Módulos de transformação
│   ├── loaders/        # Módulos de carregamento
│   ├── pipelines/      # Orquestração do pipeline principal
│   └── utils/          # Utilitários e helpers
├── tests/              # Testes para o pipeline
├── config/             # Arquivos de configuração
├── requirements.txt    # Dependências Python do fluxo
└── README.md           # Documentação específica do fluxo
```

---

## Licença

Este projeto está licenciado sob a Licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
