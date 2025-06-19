"""
Utilities para configuração de logging
"""
import sys
from pathlib import Path
from loguru import logger
from typing import Optional

class LoggingUtils:
    """Utilidades para configuração de logging"""
    
    @staticmethod
    def setup_pipeline_logging(
        pipeline_name: str,
        log_level: str = "INFO",
        log_dir: str = "logs",
        console_output: bool = True
    ) -> None:
        """Configura logging para pipeline"""
        
        # Remover handlers existentes
        logger.remove()
        
        # Console output
        if console_output:
            logger.add(
                sys.stdout,
                level=log_level,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
            )
        
        # File output
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        log_filename = f"{pipeline_name}_" + "{time:YYYY-MM-DD}.log"
        logger.add(
            log_path / log_filename,
            rotation="1 day",
            retention="30 days",
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
        )
        
        logger.info(f"🚀 Logging configurado para pipeline: {pipeline_name}")
    
    @staticmethod
    def log_pipeline_metrics(metrics: dict) -> None:
        """Log das métricas do pipeline"""
        logger.info("📊 Métricas do Pipeline:")
        for key, value in metrics.items():
            logger.info(f"   {key}: {value}")
    
    @staticmethod
    def log_dataframe_info(df, name: str = "DataFrame") -> None:
        """Log das informações do DataFrame"""
        logger.info(f"📊 {name} - Shape: {df.shape}")
        logger.info(f"📊 {name} - Colunas: {list(df.columns)}")
        logger.info(f"📊 {name} - Tipos: {df.dtypes.to_dict()}")
