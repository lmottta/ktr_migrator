"""
Utilities para validação de dados
"""
import pandas as pd
import numpy as np
from loguru import logger
from typing import Dict, Any, List, Optional

class ValidationUtils:
    """Utilidades para validação de dados"""
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> bool:
        """Validação básica de DataFrame"""
        if df is None:
            logger.error("❌ DataFrame é None")
            return False
        
        if df.empty:
            logger.warning("⚠️ DataFrame está vazio")
            return True  # Vazio é válido em alguns casos
        
        logger.info(f"✅ DataFrame válido: {len(df)} registros, {len(df.columns)} colunas")
        return True
    
    @staticmethod
    def check_required_columns(df: pd.DataFrame, required_cols: List[str]) -> bool:
        """Verifica se as colunas obrigatórias estão presentes"""
        missing_cols = set(required_cols) - set(df.columns)
        
        if missing_cols:
            logger.error(f"❌ Colunas obrigatórias ausentes: {missing_cols}")
            return False
        
        logger.info("✅ Todas as colunas obrigatórias estão presentes")
        return True
    
    @staticmethod
    def check_data_types(df: pd.DataFrame, expected_types: Dict[str, str]) -> bool:
        """Verifica tipos de dados das colunas"""
        errors = []
        
        for col, expected_type in expected_types.items():
            if col not in df.columns:
                continue
                
            actual_type = str(df[col].dtype)
            if expected_type not in actual_type:
                errors.append(f"{col}: esperado {expected_type}, encontrado {actual_type}")
        
        if errors:
            logger.error(f"❌ Tipos incorretos: {errors}")
            return False
        
        logger.info("✅ Tipos de dados corretos")
        return True
    
    @staticmethod
    def check_null_values(df: pd.DataFrame, null_threshold: float = 0.1) -> Dict[str, Any]:
        """Verifica valores nulos"""
        null_info = {}
        
        for col in df.columns:
            null_count = df[col].isnull().sum()
            null_percentage = null_count / len(df)
            
            null_info[col] = {
                "null_count": null_count,
                "null_percentage": null_percentage,
                "exceeds_threshold": null_percentage > null_threshold
            }
        
        return null_info
