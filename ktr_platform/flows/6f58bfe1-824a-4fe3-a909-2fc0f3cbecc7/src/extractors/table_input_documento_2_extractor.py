"""
Extração de dados - Table input documento 2
Gerado automaticamente do KTR: documento_mgc.ktr
"""
import pandas as pd
from sqlalchemy import create_engine, text
from loguru import logger
from typing import Dict, Any, Optional
from ..utils.database_utils import DatabaseUtils
from ..utils.validation_utils import ValidationUtils

class Tableinputdocumento2PipelineExtractor:
    """
    Extractor para: Table input documento 2
    Tipo: TableInput
    """
    
    def __init__(self, connections: Dict[str, Any]):
        self.connections = connections
        self.validator = ValidationUtils()
        
    def extract(self) -> pd.DataFrame:
        """
        Executa a extração de dados
        """
        logger.info(f"🔄 Iniciando extração: Table input documento 2")
        
        try:
                         # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT documento , d.data_versionamento as data_alteracao , d.responsavel_alteracao as responsavel_alteracao --, m.situacao as situacao_minuta --, m.id as id_minuta FROM dbpro_12350_spunet_gcc_VBL.documento d --LEFT JOIN dbpro_12350_spunet_gcc_VBL.minuta_contrato m ON SUBSTRING(documento,55,36) = m.id WHERE d.is_versao_atual = TRUE;""", connection)
            
            # Validação dos dados extraídos
            if self.validator.validate_dataframe(df):
                logger.info(f"✅ Extração concluída: {len(df)} registros")
                return df
            else:
                logger.warning("⚠️ Dados extraídos não passaram na validação")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"❌ Erro na extração Table input documento 2: {e}")
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
