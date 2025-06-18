"""
Configurações do pipeline localizacao_imovel
"""
import os
from decouple import config

# Configurações de banco de dados
DATABASE_CONFIGS = {
    "local": {
        "host": config("LOCAL_HOST", default="localhost"),
        "port": config("LOCAL_PORT", default=5432, cast=int),
        "database": config("LOCAL_DATABASE", default="bispu"),
        "username": config("LOCAL_USERNAME", default="postgres"),
        "password": config("LOCAL_PASSWORD", default=""),
        "type": "POSTGRESQL"
    },
    "PRODUCAO": {
        "host": config("PRODUCAO_HOST", default="10.209.9.227"),
        "port": config("PRODUCAO_PORT", default=5432, cast=int),
        "database": config("PRODUCAO_DATABASE", default="bispu"),
        "username": config("PRODUCAO_USERNAME", default="postgres"),
        "password": config("PRODUCAO_PASSWORD", default=""),
        "type": "POSTGRESQL"
    }
}

# Configurações de logging
LOG_LEVEL = config("LOG_LEVEL", default="INFO")
LOG_FILE = config("LOG_FILE", default="logs/localizacao_imovel.log")

# Configurações do pipeline
PIPELINE_CONFIG = {
    "name": "localizacao_imovel",
    "description": "Pipeline gerado do KTR localizacao_imovel",
    "batch_size": config("BATCH_SIZE", default=1000, cast=int),
    "timeout": config("TIMEOUT", default=3600, cast=int)
}
