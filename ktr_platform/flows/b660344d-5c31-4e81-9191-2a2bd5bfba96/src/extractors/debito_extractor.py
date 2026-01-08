"""
Extração de dados - debito
Gerado automaticamente do KTR: importatabelas.ktr
"""
import pandas as pd
from sqlalchemy import create_engine, text
from loguru import logger
from typing import Dict, Any, Optional
from ..utils.database_utils import DatabaseUtils
from ..utils.validation_utils import ValidationUtils

class DebitoPipelineExtractor:
    """
    Extractor para: debito
    Tipo: TableInput
    """
    
    def __init__(self, connections: Dict[str, Any]):
        self.connections = connections
        self.validator = ValidationUtils()
        
    def extract(self) -> pd.DataFrame:
        """
        Executa a extração de dados
        """
        logger.info(f"🔄 Iniciando extração: debito")
        
        try:
                         # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT deb_nu_chavedebito , deb_nu_riputilizacao , deb_sg_grpu , deb_co_receita , cast(deb_da_referenciadebito as timestamp) deb_da_referenciadebito , cast(deb_da_vencimentodebito as timestamp) deb_da_vencimentodebito , deb_va_debito , deb_co_unidademonetaria , cast(deb_da_inclusaodebito as timestamp) deb_da_inclusaodebito , cast(rtrim(deb_in_cpfcnpjresponsavel) as varchar(1)) deb_in_cpfcnpjresponsavel , deb_nu_cpfcnpjresponsavel FROM debito""", connection)
            
            # Validação dos dados extraídos
            if self.validator.validate_dataframe(df):
                logger.info(f"✅ Extração concluída: {len(df)} registros")
                return df
            else:
                logger.warning("⚠️ Dados extraídos não passaram na validação")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"❌ Erro na extração debito: {e}")
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
