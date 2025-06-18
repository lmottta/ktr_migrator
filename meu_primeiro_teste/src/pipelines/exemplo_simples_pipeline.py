"""
Pipeline: exemplo_simples
Gerado automaticamente do KTR: exemplo_simples.ktr
Data: 2025-06-17 22:22:02

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


class ExemploSimplesPipeline:
    """
    Pipeline ETL simples para demonstração do KTR Migrator

    Pipeline ETL gerado automaticamente a partir do KTR: exemplo_simples.ktr
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Inicializa o pipeline com configurações"""
        self.config = config or {}
        self.connections = {}
        self.metrics = {"records_processed": 0, "execution_time": 0, "errors": 0}
        self.setup_logging()
        self.setup_connections()

    def setup_logging(self):
        """Configura logging estruturado"""
        log_level = self.config.get("log_level", "INFO")
        log_file = self.config.get(
            "log_file", f"logs/exemplo_simples_{datetime.now().strftime('%Y%m%d')}.log"
        )

        logger.add(
            log_file,
            rotation="1 day",
            retention="30 days",
            format="{time} | {level} | {message}",
            level=log_level,
        )

        logger.info(f"🚀 Iniciando pipeline: exemplo_simples")

    def setup_connections(self):
        """Configura conexões com bancos de dados"""
        # Conexão: fonte
        fonte_url = "postgresql://user_fonte:Encrypted 2be98afc86aa7f2e4cb79ce71da9fa6d4@localhost:5432/dados_fonte"
        self.connections["fonte"] = create_engine(fonte_url)
        logger.info(f"📡 Conexão configurada: fonte (POSTGRESQL)")
        # Conexão: destino
        destino_url = "postgresql://user_destino:Encrypted 2be98afc86aa7f2e4cb79ce71da9fa6d4@localhost:5432/dados_destino"
        self.connections["destino"] = create_engine(destino_url)
        logger.info(f"📡 Conexão configurada: destino (POSTGRESQL)")

    def extract_data(self) -> pd.DataFrame:
        """
        Extração de dados - Stage 1
        """
        logger.info("🔄 Iniciando extração de dados...")
        start_time = datetime.now()

        try:
            # Extração de dados - Table input usuarios
            # Extração via SQL
            connection = self.connections["fonte"]
            df = pd.read_sql(
                """SELECT id, nome, email, data_cadastro, status FROM public.usuarios WHERE data_cadastro >= CURRENT_DATE - INTERVAL '30 days' AND status = 'ativo' ORDER BY data_cadastro DESC""",
                connection,
            )

            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"✅ Extração concluída em {execution_time:.2f}s - {len(df)} registros"
            )
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
            # Transformação de dados - String operations limpeza
            df["nome"] = df["nome"].str.strip()
            df["email"] = df["email"].str.strip()
            df["email"] = df["email"].str.lower()

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
            # Carga de dados - Table output usuarios limpos
            # Carga para PostgreSQL
            connection = self.connections["destino"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE public.usuarios_limpos"))
                logger.info("🗑️ Tabela truncada: public.usuarios_limpos")

            df.to_sql(
                name="usuarios_limpos",
                schema="public" if "public" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000,
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
        logger.info("🎯 Executando pipeline exemplo_simples")

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

            self.metrics.update(
                {
                    "status": "success",
                    "total_execution_time": total_time,
                    "start_time": pipeline_start.isoformat(),
                    "end_time": pipeline_end.isoformat(),
                    "records_processed": len(df_transformed),
                }
            )

            logger.info(f"🎉 Pipeline concluído com sucesso: {self.metrics}")
            return self.metrics

        except Exception as e:
            pipeline_end = datetime.now()
            total_time = (pipeline_end - pipeline_start).total_seconds()

            self.metrics.update(
                {
                    "status": "failed",
                    "error": str(e),
                    "total_execution_time": total_time,
                    "end_time": pipeline_end.isoformat(),
                }
            )

            logger.error(f"💥 Pipeline falhou: {self.metrics}")
            return self.metrics

        finally:
            # Cleanup das conexões
            for name, engine in self.connections.items():
                engine.dispose()
                logger.debug(f"🔌 Conexão fechada: {name}")


if __name__ == "__main__":
    # Exemplo de execução
    config = {"log_level": "INFO", "environment": "development"}

    pipeline = ExemploSimplesPipeline(config)
    result = pipeline.run_pipeline()

    if result["status"] == "success":
        print(
            f"✅ Pipeline executado com sucesso! Processados {result['records_processed']} registros"
        )
    else:
        print(f"❌ Pipeline falhou: {result.get('error', 'Erro desconhecido')}")
        exit(1)
