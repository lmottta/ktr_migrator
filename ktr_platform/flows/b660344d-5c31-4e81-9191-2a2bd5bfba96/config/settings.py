"""
Configurações do pipeline importatabelas
"""
import os
from decouple import config

# Configurações de banco de dados
DATABASE_CONFIGS = {
    "DAAS": {
        "host": config("DAAS_HOST", default=""),
        "port": config("DAAS_PORT", default=1521, cast=int),
        "database": config("DAAS_DATABASE", default=""),
        "username": config("DAAS_USERNAME", default="41728130115"),
        "password": config("DAAS_PASSWORD", default=""),
        "type": "GENERIC"
    },
    "oltp": {
        "host": config("OLTP_HOST", default="10.209.9.227"),
        "port": config("OLTP_PORT", default=5432, cast=int),
        "database": config("OLTP_DATABASE", default="oltp"),
        "username": config("OLTP_USERNAME", default="postgres"),
        "password": config("OLTP_PASSWORD", default=""),
        "type": "POSTGRESQL"
    }
}

# Configurações de logging
LOG_LEVEL = config("LOG_LEVEL", default="INFO")
LOG_FILE = config("LOG_FILE", default="logs/importatabelas.log")

# Configurações do pipeline
PIPELINE_CONFIG = {
    "name": "importatabelas",
    "description": "Pipeline gerado do KTR importatabelas",
    "batch_size": config("BATCH_SIZE", default=1000, cast=int),
    "timeout": config("TIMEOUT", default=3600, cast=int)
}
