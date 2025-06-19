"""
Utilities para configuração
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
from decouple import config
from loguru import logger

class ConfigUtils:
    """Utilidades para gerenciamento de configuração"""
    
    @staticmethod
    def load_database_config(connection_name: str) -> Dict[str, Any]:
        """Carrega configuração de banco de dados"""
        try:
            db_config = {
                "host": config(f"{connection_name.upper()}_HOST"),
                "port": config(f"{connection_name.upper()}_PORT", cast=int),
                "database": config(f"{connection_name.upper()}_DATABASE"),
                "username": config(f"{connection_name.upper()}_USERNAME"),
                "password": config(f"{connection_name.upper()}_PASSWORD"),
            }
            
            logger.info(f"✅ Configuração carregada para: {connection_name}")
            return db_config
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar config de {connection_name}: {e}")
            raise
    
    @staticmethod
    def get_pipeline_config() -> Dict[str, Any]:
        """Carrega configuração geral do pipeline"""
        return {
            "log_level": config("LOG_LEVEL", default="INFO"),
            "environment": config("ENVIRONMENT", default="development"),
            "batch_size": config("BATCH_SIZE", default=1000, cast=int),
            "max_retries": config("MAX_RETRIES", default=3, cast=int),
            "timeout": config("TIMEOUT", default=300, cast=int),
        }
    
    @staticmethod
    def validate_required_env_vars(required_vars: list) -> bool:
        """Valida se todas as variáveis obrigatórias estão definidas"""
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Variáveis de ambiente obrigatórias não definidas: {missing_vars}")
            return False
        
        logger.info("✅ Todas as variáveis obrigatórias estão definidas")
        return True
    
    @staticmethod
    def create_sqlalchemy_url(db_config: Dict[str, Any], db_type: str = "postgresql") -> str:
        """Cria URL do SQLAlchemy"""
        if db_type == "postgresql":
            driver = "psycopg2"
        elif db_type == "mysql":
            driver = "pymysql"
        else:
            driver = ""
        
        driver_suffix = f"+{driver}" if driver else ""
        
        url = f"{db_type}{driver_suffix}://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        
        return url
