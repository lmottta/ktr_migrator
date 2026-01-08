"""
Carga de dados - o_po
Gerado automaticamente do KTR: importatabelas.ktr
"""
import pandas as pd
from sqlalchemy import create_engine, text
from loguru import logger
from typing import Dict, Any, Optional
from ..utils.database_utils import DatabaseUtils
from ..utils.validation_utils import ValidationUtils

class OPoPipelineLoader:
    """
    Loader para: o_po
    Tipo: TableOutput
    """
    
    def __init__(self, connections: Dict[str, Any]):
        self.connections = connections
        self.db_utils = DatabaseUtils()
        self.validator = ValidationUtils()
        
    def load(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Executa a carga dos dados
        """
        logger.info(f"🔄 Iniciando carga: o_po")
        
        try:
            if df.empty:
                logger.warning("⚠️ DataFrame vazio recebido para carga")
                return {"status": "warning", "records": 0}
            
            # Validação pré-carga
            if not self.validator.validate_dataframe(df):
                raise ValueError("Dados não passaram na validação pré-carga")
            
            records_count = len(df)
            
                         # Carga para PostgreSQL
            connection = self.connections["oltp"]
            
            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.proprietariooficial"))
                logger.info("🗑️ Tabela truncada: spiunet.proprietariooficial")
            
            df.to_sql(
                name="proprietariooficial",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            
            logger.info(f"✅ Carga concluída: {records_count} registros")
            
            return {
                "status": "success",
                "records": records_count,
                "target": "o_po"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na carga o_po: {e}")
            raise
    
    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara os dados para carga (formatação final)
        """
        # Adicionar timestamp de carga
        df['loaded_at'] = pd.Timestamp.now()
        
        return df
    
    def get_target_schema(self) -> Dict[str, str]:
        """
        Retorna o schema da tabela/destino de carga
        """
        return {
            # Definir schema baseado no destino
            "loaded_at": "datetime"
        }
