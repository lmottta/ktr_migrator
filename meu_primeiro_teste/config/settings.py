"""
Configurações do pipeline exemplo_simples
"""
import os
from decouple import config

# Configurações de banco de dados
DATABASE_CONFIGS = {
    "fonte": {
        "host": config("FONTE_HOST", default="localhost"),
        "port": config("FONTE_PORT", default=5432, cast=int),
        "database": config("FONTE_DATABASE", default="dados_fonte"),
        "username": config("FONTE_USERNAME", default="user_fonte"),
        "password": config("FONTE_PASSWORD", default=""),
        "type": "POSTGRESQL",
    },
    "destino": {
        "host": config("DESTINO_HOST", default="localhost"),
        "port": config("DESTINO_PORT", default=5432, cast=int),
        "database": config("DESTINO_DATABASE", default="dados_destino"),
        "username": config("DESTINO_USERNAME", default="user_destino"),
        "password": config("DESTINO_PASSWORD", default=""),
        "type": "POSTGRESQL",
    },
}

# Configurações de logging
LOG_LEVEL = config("LOG_LEVEL", default="INFO")
LOG_FILE = config("LOG_FILE", default="logs/exemplo_simples.log")

# Configurações do pipeline
PIPELINE_CONFIG = {
    "name": "exemplo_simples",
    "description": "Pipeline ETL simples para demonstração do KTR Migrator",
    "batch_size": config("BATCH_SIZE", default=1000, cast=int),
    "timeout": config("TIMEOUT", default=3600, cast=int),
}
