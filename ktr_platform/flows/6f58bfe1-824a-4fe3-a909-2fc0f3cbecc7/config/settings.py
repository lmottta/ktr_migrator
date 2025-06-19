"""
Configurações do pipeline documento_mgc
"""
import os
from decouple import config

# Configurações de banco de dados
DATABASE_CONFIGS = {
    "DAAS": {
        "host": config("DAAS_HOST", default=""),
        "port": config("DAAS_PORT", default=1521, cast=int),
        "database": config("DAAS_DATABASE", default=""),
        "username": config("DAAS_USERNAME", default="72361417120"),
        "password": config("DAAS_PASSWORD", default=""),
        "type": "GENERIC"
    },
    "local": {
        "host": config("LOCAL_HOST", default="localhost"),
        "port": config("LOCAL_PORT", default=5432, cast=int),
        "database": config("LOCAL_DATABASE", default="servicosonline"),
        "username": config("LOCAL_USERNAME", default="postgres"),
        "password": config("LOCAL_PASSWORD", default=""),
        "type": "POSTGRESQL"
    },
    "PRODUCAO": {
        "host": config("PRODUCAO_HOST", default="10.209.9.227"),
        "port": config("PRODUCAO_PORT", default=5432, cast=int),
        "database": config("PRODUCAO_DATABASE", default="servicosonline"),
        "username": config("PRODUCAO_USERNAME", default="postgres"),
        "password": config("PRODUCAO_PASSWORD", default=""),
        "type": "POSTGRESQL"
    }
}

# Configurações de logging
LOG_LEVEL = config("LOG_LEVEL", default="INFO")
LOG_FILE = config("LOG_FILE", default="logs/documento_mgc.log")

# Configurações do pipeline
PIPELINE_CONFIG = {
    "name": "documento_mgc",
    "description": "Pipeline gerado do KTR documento_mgc",
    "batch_size": config("BATCH_SIZE", default=1000, cast=int),
    "timeout": config("TIMEOUT", default=3600, cast=int)
}
