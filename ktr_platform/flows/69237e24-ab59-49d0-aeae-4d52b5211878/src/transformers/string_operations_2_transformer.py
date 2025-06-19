"""
Transformação de dados - String operations 2
Gerado automaticamente do KTR: localizacao_imovel.ktr
"""
import pandas as pd
import numpy as np
from loguru import logger
from typing import Dict, Any, Optional, List
from ..utils.validation_utils import ValidationUtils

class Stringoperations2PipelineTransformer:
    """
    Transformer para: String operations 2
    Tipo: StringOperations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.validator = ValidationUtils()
        
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executa as transformações nos dados
        """
        logger.info(f"🔄 Iniciando transformação: String operations 2")
        
        try:
            if df.empty:
                logger.warning("⚠️ DataFrame vazio recebido para transformação")
                return df
            
            original_count = len(df)
            
            df['fonte'] = df['fonte'].str.strip()
            df['Nivel de Precisao - Por extenso'] = df['Nivel de Precisao - Por extenso'].str.strip()
            
            # Adicionar metadata de transformação
            df['transformed_at'] = pd.Timestamp.now()
            df['transformation_applied'] = 'String operations 2'
            
            final_count = len(df)
            logger.info(f"✅ Transformação concluída: {original_count} → {final_count} registros")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Erro na transformação String operations 2: {e}")
            raise
    
    def validate_input(self, df: pd.DataFrame) -> bool:
        """
        Valida se os dados de entrada estão corretos
        """
        return self.validator.validate_dataframe(df)
    
    def get_required_columns(self) -> List[str]:
        """
        Retorna as colunas obrigatórias para esta transformação
        """
        return []  # Definir baseado no tipo de transformação
