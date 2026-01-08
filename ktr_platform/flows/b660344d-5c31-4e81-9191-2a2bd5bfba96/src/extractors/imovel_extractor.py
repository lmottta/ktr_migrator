"""
Extração de dados - Imovel
Gerado automaticamente do KTR: importatabelas.ktr
"""
import pandas as pd
from sqlalchemy import create_engine, text
from loguru import logger
from typing import Dict, Any, Optional
from ..utils.database_utils import DatabaseUtils
from ..utils.validation_utils import ValidationUtils

class ImovelPipelineExtractor:
    """
    Extractor para: Imovel
    Tipo: TableInput
    """
    
    def __init__(self, connections: Dict[str, Any]):
        self.connections = connections
        self.validator = ValidationUtils()
        
    def extract(self) -> pd.DataFrame:
        """
        Executa a extração de dados
        """
        logger.info(f"🔄 Iniciando extração: Imovel")
        
        try:
                         # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT cast(imv_nu_rip as bigint) imv_nu_rip, cast(rtrim(imv_in_certificado) as varchar(1)) imv_in_certificado, imv_co_motivocancelamentoimovel, imv_ed_tipologradouro, imv_ed_logradouro, imv_ed_numero, imv_ed_complemento, imv_ed_bairro, imv_ed_cep, imv_co_municipio, imv_sg_uf, imv_sg_pais, imv_no_cidadeexterior, imv_nu_codigopostal, imv_co_conceituacaoterreno, imv_mq_areaterreno, imv_co_naturezaterreno, imv_va_metroquadrado, imv_va_terreno, imv_va_somabenfeitoriautilizacao, imv_op_fracaoideal, imv_co_tipoimovel, imv_op_fatorcorretivo, imv_va_imovel, imv_va_imoveldolar, cast(imv_da_avaliacao as timestamp) imv_da_avaliacao, imv_co_nivelrigoravaliacao, cast(imv_da_prazovalidadeavaliacao as timestamp) imv_da_prazovalidadeavaliacao, imv_co_tipovocacao, imv_no_tomboarquivamento, imv_no_cartoriooficio, imv_nu_matriculacartorio, imv_nu_livrocartorio, imv_nu_folhacartorio, cast(imv_da_registrocartorio as timestamp) imv_da_registrocartorio, imv_co_formaaquisicao, imv_no_proprietarioanterior, imv_no_fundamentoincorporacao, imv_no_encargoaquisicao, cast(rtrim(imv_in_imovelsubjudice) as varchar(1)) imv_in_imovelsubjudice, imv_no_acao, imv_no_processoapenso, imv_nu_processoprincipal, imv_no_latitudelongitude, imv_co_tipodominio, imv_no_proprietariooficial, imv_co_proprietariooficial, cast(imv_da_validacao as timestamp) imv_da_validacao, imv_no_situacaoincorporacao, cast(imv_da_cadastro as timestamp) imv_da_cadastro, cast(imv_da_incorporacao as timestamp) imv_da_incorporacao, imv_co_orgaoextinto, imv_co_direitoadquirido, cast(rtrim(imv_in_enderecovalidado) as varchar(1)) imv_in_enderecovalidado, cast(rtrim(imv_in_migracaospunet) as varchar(1)) imv_in_migracaospunet, imv_id_imovelspunet FROM dbp_29321_spiunet_VBL.imovel;""", connection)
            
            # Validação dos dados extraídos
            if self.validator.validate_dataframe(df):
                logger.info(f"✅ Extração concluída: {len(df)} registros")
                return df
            else:
                logger.warning("⚠️ Dados extraídos não passaram na validação")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"❌ Erro na extração Imovel: {e}")
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
