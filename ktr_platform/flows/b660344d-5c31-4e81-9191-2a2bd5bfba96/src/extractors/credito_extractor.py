"""
Extração de dados - credito
Gerado automaticamente do KTR: importatabelas.ktr
"""
import pandas as pd
from sqlalchemy import create_engine, text
from loguru import logger
from typing import Dict, Any, Optional
from ..utils.database_utils import DatabaseUtils
from ..utils.validation_utils import ValidationUtils

class CreditoPipelineExtractor:
    """
    Extractor para: credito
    Tipo: TableInput
    """
    
    def __init__(self, connections: Dict[str, Any]):
        self.connections = connections
        self.validator = ValidationUtils()
        
    def extract(self) -> pd.DataFrame:
        """
        Executa a extração de dados
        """
        logger.info(f"🔄 Iniciando extração: credito")
        
        try:
                         # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT cred_nu_chavecredito , cred_nu_riputilizacao , cast(rtrim(cred_in_creditoidentificado) as varchar(1)) cred_in_creditoidentificado , cred_sg_grpu , cred_sg_ufriputilizacao , cred_co_receita , cred_nu_pagamentosrf , cast(cred_da_arrecadacao as timestamp) cred_da_arrecadacao , cred_va_totalpago , cred_nu_banco , cred_nu_agencia , cred_nu_municipiopagamento , cast(rtrim(cred_in_cpfcnpjresponsavel) as varchar(1)) cred_in_cpfcnpjresponsavel , cred_nu_cpfcnpjresponsavel , cred_co_origemcredito , cast(cred_da_anomesdecendiosrf as timestamp) cred_da_anomesdecendiosrf , cred_co_unidademonetaria , cast(cred_da_inclusaocredito as timestamp) cred_da_inclusaocredito FROM credito""", connection)
            
            # Validação dos dados extraídos
            if self.validator.validate_dataframe(df):
                logger.info(f"✅ Extração concluída: {len(df)} registros")
                return df
            else:
                logger.warning("⚠️ Dados extraídos não passaram na validação")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"❌ Erro na extração credito: {e}")
            raise
    
    def get_schema(self) -> Dict[str, str]:
        """
        Retorna o schema esperado dos dados
        """
        return {
            # Definir schema baseado no tipo de extração
            "extracted_at": "datetime",
            "source": "string"
        }
