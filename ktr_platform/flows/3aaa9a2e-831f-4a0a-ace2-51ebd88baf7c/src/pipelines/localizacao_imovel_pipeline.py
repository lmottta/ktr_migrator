"""
Pipeline: localizacao_imovel
Gerado automaticamente do KTR: localizacao_imovel.ktr
Data: 2025-06-17 22:54:27

Este arquivo foi gerado pelo KTR Migrator
Autor: Engenheiro de Dados
"""

import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine
from loguru import logger
from typing import Dict, Any, Optional
from datetime import datetime
import os
from sqlalchemy import text
from sqlalchemy import text

class LocalizacaoImovelPipeline:
    """
    Pipeline gerado do KTR localizacao_imovel
    
    Pipeline ETL gerado automaticamente a partir do KTR: localizacao_imovel.ktr
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Inicializa o pipeline com configurações"""
        self.config = config or {}
        self.connections = {}
        self.metrics = {
            "records_processed": 0,
            "execution_time": 0,
            "errors": 0
        }
        self.setup_logging()
        self.setup_connections()
    
    def setup_logging(self):
        """Configura logging estruturado"""
        log_level = self.config.get("log_level", "INFO")
        log_file = self.config.get("log_file", f"logs/localizacao_imovel_{datetime.now().strftime('%Y%m%d')}.log")
        
        logger.add(
            log_file,
            rotation="1 day",
            retention="30 days",
            format="{time} | {level} | {message}",
            level=log_level
        )
        
        logger.info(f"🚀 Iniciando pipeline: localizacao_imovel")
    
    def setup_connections(self):
        """Configura conexões com bancos de dados"""
        # Conexão: local
        local_url = "postgresql://postgres:Encrypted 2be98afc86aa7f2e4cb79a3608fc0fc8e@localhost:5432/bispu"
        self.connections["local"] = create_engine(local_url)
        logger.info(f"📡 Conexão configurada: local (POSTGRESQL)")
        # Conexão: PRODUCAO
        producao_url = "postgresql://postgres:Encrypted 2be98afc86aa7c683ea53be7fd0c282ea@10.209.9.227:5432/bispu"
        self.connections["PRODUCAO"] = create_engine(producao_url)
        logger.info(f"📡 Conexão configurada: PRODUCAO (POSTGRESQL)")
    
    def extract_data(self) -> pd.DataFrame:
        """
        Extração de dados - Stage 1
        """
        logger.info("🔄 Iniciando extração de dados...")
        start_time = datetime.now()
        
        try:
            # Extração de dados - Excel_input_localizacao_imovel
            # Extração de Excel
            df = pd.read_excel(
                "C:\biserver-ce\ktr\Geo\723104_Localizacao_imovel_CGDAI_Marco_25.xlsx",
                sheet_name="Localizacao_imovel_Brasil - Atu",
                header=0
            )
            # Extração de dados - Excel_input_localizacao_imovel 2
            # Extração de Excel
            df = pd.read_excel(
                "C:\biserver-ce\ktr\Geo\723104_Localizacao_imovel_CGDAI_Marco_25.xlsx",
                sheet_name="Localizacao_imovel_Brasil - Atu",
                header=0
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Extração concluída em {execution_time:.2f}s - {len(df)} registros")
            self.metrics["records_processed"] = len(df)
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Erro na extração: {e}")
            self.metrics["errors"] += 1
            raise
    
    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transformação de dados - Stage 2
        """
        logger.info("🔄 Aplicando transformações...")
        start_time = datetime.now()
        
        try:
            # Transformação de dados - String operations
            df['fonte'] = df['fonte'].str.strip()
            df['Nivel de Precisao - Por extenso'] = df['Nivel de Precisao - Por extenso'].str.strip()
            # Transformação de dados - String operations 2
            df['fonte'] = df['fonte'].str.strip()
            df['Nivel de Precisao - Por extenso'] = df['Nivel de Precisao - Por extenso'].str.strip()
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Transformações aplicadas em {execution_time:.2f}s")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Erro na transformação: {e}")
            self.metrics["errors"] += 1
            raise
    
    def load_data(self, df: pd.DataFrame) -> None:
        """
        Carga de dados - Stage 3
        """
        logger.info("🔄 Carregando dados...")
        start_time = datetime.now()
        
        try:
            # Carga de dados - Table output
            # Carga para PostgreSQL
            connection = self.connections["local"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE public.tb_carga_qualificageo"))
                logger.info("🗑️ Tabela truncada: public.tb_carga_qualificageo")

            df.to_sql(
                name="tb_carga_qualificageo",
                schema="public" if "public" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - Table output PRODUCAO
            # Carga para PostgreSQL
            connection = self.connections["PRODUCAO"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE public.tb_carga_qualificageo"))
                logger.info("🗑️ Tabela truncada: public.tb_carga_qualificageo")

            df.to_sql(
                name="tb_carga_qualificageo",
                schema="public" if "public" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Carga concluída em {execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Erro na carga: {e}")
            self.metrics["errors"] += 1
            raise
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validações de qualidade de dados
        """
        logger.info("🔍 Validando qualidade dos dados...")
        
        # Validações básicas
        if df.empty:
            logger.warning("⚠️ DataFrame vazio")
            return False
        
        # Verificar campos obrigatórios
        required_fields = []
        for field in required_fields:
            if field not in df.columns:
                logger.error(f"❌ Campo obrigatório ausente: {field}")
                return False
            
            if df[field].isnull().any():
                null_count = df[field].isnull().sum()
                logger.warning(f"⚠️ Campo {field} tem {null_count} valores nulos")
        
        # Verificar duplicatas
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            logger.warning(f"⚠️ {duplicates} registros duplicados encontrados")
        
        logger.info("✅ Validação de dados concluída")
        return True
    
    def run_pipeline(self) -> Dict[str, Any]:
        """
        Executa pipeline completo
        """
        pipeline_start = datetime.now()
        logger.info("🎯 Executando pipeline localizacao_imovel")
        
        try:
            # Extract
            df = self.extract_data()
            
            # Validate
            if not self.validate_data(df):
                raise ValueError("Falha na validação de dados")
            
            # Transform
            df_transformed = self.transform_data(df)
            
            # Load
            self.load_data(df_transformed)
            
            # Calcular métricas finais
            pipeline_end = datetime.now()
            total_time = (pipeline_end - pipeline_start).total_seconds()
            
            self.metrics.update({
                "status": "success",
                "total_execution_time": total_time,
                "start_time": pipeline_start.isoformat(),
                "end_time": pipeline_end.isoformat(),
                "records_processed": len(df_transformed)
            })
            
            logger.info(f"🎉 Pipeline concluído com sucesso: {self.metrics}")
            return self.metrics
            
        except Exception as e:
            pipeline_end = datetime.now()
            total_time = (pipeline_end - pipeline_start).total_seconds()
            
            self.metrics.update({
                "status": "failed",
                "error": str(e),
                "total_execution_time": total_time,
                "end_time": pipeline_end.isoformat()
            })
            
            logger.error(f"💥 Pipeline falhou: {self.metrics}")
            return self.metrics
            
        finally:
            # Cleanup das conexões
            for name, engine in self.connections.items():
                engine.dispose()
                logger.debug(f"🔌 Conexão fechada: {name}")

if __name__ == "__main__":
    # Exemplo de execução
    config = {
        "log_level": "INFO",
        "environment": "development"
    }
    
    pipeline = LocalizacaoImovelPipeline(config)
    result = pipeline.run_pipeline()
    
    if result["status"] == "success":
        print(f"✅ Pipeline executado com sucesso! Processados {result['records_processed']} registros")
    else:
        print(f"❌ Pipeline falhou: {result.get('error', 'Erro desconhecido')}")
        exit(1) 