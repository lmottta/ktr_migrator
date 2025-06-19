"""
Utilities para manipulação de banco de dados
"""
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from loguru import logger
from typing import Dict, Any, List, Optional

class DatabaseUtils:
    """Utilidades para operações de banco de dados"""
    
    @staticmethod
    def test_connection(connection_string: str) -> bool:
        """Testa conexão com banco de dados"""
        try:
            engine = create_engine(connection_string)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✅ Conexão testada com sucesso")
            return True
        except Exception as e:
            logger.error(f"❌ Falha na conexão: {e}")
            return False
    
    @staticmethod
    def get_table_info(engine, table_name: str, schema: str = None) -> Dict[str, Any]:
        """Obtém informações da tabela"""
        try:
            inspector = inspect(engine)
            full_table = f"{schema}.{table_name}" if schema else table_name
            
            columns = inspector.get_columns(table_name, schema=schema)
            pk = inspector.get_pk_constraint(table_name, schema=schema)
            
            return {
                "table": full_table,
                "columns": columns,
                "primary_key": pk,
                "exists": True
            }
        except Exception as e:
            logger.warning(f"⚠️ Tabela {table_name} não encontrada: {e}")
            return {"exists": False}
    
    @staticmethod
    def execute_query(engine, query: str, params: Dict = None) -> pd.DataFrame:
        """Executa query e retorna DataFrame"""
        try:
            return pd.read_sql(query, engine, params=params)
        except Exception as e:
            logger.error(f"❌ Erro na execução da query: {e}")
            raise
