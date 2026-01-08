"""
Extração de dados - Benfeitoria
Gerado automaticamente do KTR: importatabelas.ktr
"""
import pandas as pd
from sqlalchemy import create_engine, text
from loguru import logger
from typing import Dict, Any, Optional
from ..utils.database_utils import DatabaseUtils
from ..utils.validation_utils import ValidationUtils

class BenfeitoriaPipelineExtractor:
    """
    Extractor para: Benfeitoria
    Tipo: TableInput
    """
    
    def __init__(self, connections: Dict[str, Any]):
        self.connections = connections
        self.validator = ValidationUtils()
        
    def extract(self) -> pd.DataFrame:
        """
        Executa a extração de dados
        """
        logger.info(f"🔄 Iniciando extração: Benfeitoria")
        
        try:
                         # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT cast(bnf_nu_benfeitoria as bigint) bnf_nu_benfeitoria , cast(bnf_nu_rip_imovel as bigint) bnf_nu_rip_imovel , cast(bnf_nu_rip_utilizacao as bigint) bnf_nu_rip_utilizacao , bnf_mq_areaconstruida , bnf_op_cub , cast(bnf_co_estadoconservacao as bigint) bnf_co_estadoconservacao , cast(bnf_co_tipoestrutura as bigint) bnf_co_tipoestrutura , cast(bnf_co_idadeaparente as bigint) bnf_co_idadeaparente , bnf_op_fatorkp , bnf_va_benfeitoria , cast(bnf_co_uso as bigint) bnf_co_uso , cast(bnf_co_padraoacabamento as bigint) bnf_co_padraoacabamento , bnf_qt_pavimento , bnf_no_denominacaopredio , bnf_mq_areautil , bnf_mq_areaindividualprivativaescritorio , bnf_mq_areacoletivaprivativaescritorio , bnf_mq_areacoletivacomumescritorio , bnf_mq_areaprivativaapoio , bnf_mq_areacomumapoio , bnf_mq_areaestacionamento , bnf_qt_vagascomunsestacionamento , bnf_qt_vagasprivativasestacionamento , bnf_mq_areaoutros , bnf_mq_areaespecifica FROM benfeitoria""", connection)
            
            # Validação dos dados extraídos
            if self.validator.validate_dataframe(df):
                logger.info(f"✅ Extração concluída: {len(df)} registros")
                return df
            else:
                logger.warning("⚠️ Dados extraídos não passaram na validação")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"❌ Erro na extração Benfeitoria: {e}")
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
