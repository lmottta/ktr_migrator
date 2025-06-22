# Multi-stage build para otimizar o tamanho da imagem
FROM python:3.11-slim as builder

# Metadados da imagem
LABEL maintainer="Leonardo A. Mota"
LABEL description="KTR Platform - Sistema de Migração e Execução de Pipelines ETL"
LABEL version="1.0"

# Variáveis de build
ARG DEBIAN_FRONTEND=noninteractive
ARG PYTHONUNBUFFERED=1
ARG PYTHONDONTWRITEBYTECODE=1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Configurar Python para containers
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Criar usuário não-root para segurança
RUN groupadd -r ktruser && useradd -r -g ktruser ktruser

# Criar diretórios de trabalho
WORKDIR /app

# Copiar requirements primeiro para cache otimizado
COPY requirements_platform.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_platform.txt

# Stage final
FROM python:3.11-slim

# Variáveis de ambiente para produção
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_HEADLESS=true

# Criar usuário não-root
RUN groupadd -r ktruser && useradd -r -g ktruser ktruser

# Instalar apenas dependências mínimas de runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Criar estrutura de diretórios
WORKDIR /app
RUN mkdir -p /app/data /app/logs /app/flows /app/config && \
    chown -R ktruser:ktruser /app

# Copiar dependências do stage builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código da aplicação ktr_platform
COPY ktr_platform/ .

# Copiar módulos src do diretório raiz  
COPY src/ /app/src

# Criar configuração do Streamlit
RUN mkdir -p /app/.streamlit
COPY ktr_platform/docker/streamlit_config.toml /app/.streamlit/config.toml

# Configurar permissões
RUN chown -R ktruser:ktruser /app && \
    chmod +x /app/docker/entrypoint.sh

# Expor porta
EXPOSE 8501

# Health check - mais flexível e com maior tempo de inicialização
HEALTHCHECK --interval=30s --timeout=15s --start-period=60s --retries=5 \
    CMD curl -f http://localhost:8501/_stcore/health || curl -f http://localhost:8501/healthz || exit 1

# Mudar para usuário não-root
USER ktruser

# Volumes para persistência
VOLUME ["/app/data", "/app/logs", "/app/flows"]

# Comando de entrada
ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["streamlit", "run", "app.py"] 