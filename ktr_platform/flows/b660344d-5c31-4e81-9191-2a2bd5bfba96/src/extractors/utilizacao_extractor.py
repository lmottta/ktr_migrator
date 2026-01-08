"""
Extração de dados - Utilizacao
Gerado automaticamente do KTR: importatabelas.ktr
"""
import pandas as pd
from sqlalchemy import create_engine, text
from loguru import logger
from typing import Dict, Any, Optional
from ..utils.database_utils import DatabaseUtils
from ..utils.validation_utils import ValidationUtils

class UtilizacaoPipelineExtractor:
    """
    Extractor para: Utilizacao
    Tipo: TableInput
    """
    
    def __init__(self, connections: Dict[str, Any]):
        self.connections = connections
        self.validator = ValidationUtils()
        
    def extract(self) -> pd.DataFrame:
        """
        Executa a extração de dados
        """
        logger.info(f"🔄 Iniciando extração: Utilizacao")
        
        try:
                         # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT cast(uti_nu_rip as bigint) uti_nu_rip , cast(uti_nu_rip_imovel as bigint) uti_nu_rip_imovel , cast(rtrim(uti_in_certificado) as varchar(1)) uti_in_certificado , cast(rtrim(uti_in_valornormalizadosiafi) as varchar(1)) uti_in_valornormalizadosiafi , cast(uti_co_ug as bigint) uti_co_ug , cast(uti_co_gestao as bigint) uti_co_gestao , cast(uti_nu_processo as varchar(17)) uti_nu_processo , cast(uti_co_motivocancelamentoutilizacao as bigint) uti_co_motivocancelamentoutilizacao , cast(uti_co_regime as bigint) uti_co_regime , cast(uti_co_situacaoregime as bigint) uti_co_situacaoregime , cast(uti_da_inicio as timestamp) uti_da_inicio , cast(uti_da_fim as timestamp) uti_da_fim , uti_ed_complemento , uti_mq_areaterreno , uti_va_metroquadrado , uti_va_terreno , uti_op_fracaoideal , uti_op_fatorcorretivo , uti_va_utilizacao , cast(uti_da_avaliacao as timestamp) uti_da_avaliacao , cast(uti_co_nivelrigoravaliacao as bigint) uti_co_nivelrigoravaliacao , cast(uti_da_prazovalidadeavaliacao as timestamp) uti_da_prazovalidadeavaliacao , cast(uti_co_tipodestinacao as bigint) uti_co_tipodestinacao , uti_no_destinacao , uti_no_vocacao , uti_no_averbacaoratificacao , cast(uti_da_averbacaoratificacao as timestamp) uti_da_averbacaoratificacao , uti_nu_livro , uti_nu_folha , uti_no_beneficiario , uti_no_objetivocessao , uti_no_encargocessao , uti_no_embasamentolegal , cast(rtrim(uti_in_cpfcnpjbeneficiario) as varchar(1)) uti_in_cpfcnpjbeneficiario , uti_nu_cpfcnpjbeneficiario , cast(uti_co_formacobranca as bigint) uti_co_formacobranca , uti_va_beneficio , uti_da_diavencimento , uti_no_grupoindigena , uti_nu_habitanteindigena , uti_co_formaaquisicao , uti_co_tipodominio , uti_co_formapagamento , uti_qt_parcela , uti_co_tipocontrato , cast(uti_da_iniciocontrato as timestamp) uti_da_iniciocontrato , cast(uti_da_fimcontrato as timestamp) uti_da_fimcontrato , cast(uti_da_prazocarencia as timestamp) uti_da_prazocarencia , cast(uti_da_outorga as timestamp) uti_da_outorga , cast(uti_da_vistoria as timestamp) uti_da_vistoria , uti_nu_edital , cast(uti_da_publicacaoedital as timestamp) uti_da_publicacaoedital , cast(uti_da_avaliacaoalienacao as timestamp) uti_da_avaliacaoalienacao , uti_va_efetivoalienacao , uti_co_formalizadornegocio , uti_co_situacaoocupacao , cast(uti_da_validacao as timestamp) uti_da_validacao , cast(uti_in_alteracaovalor as varchar(1)) as uti_in_alteracaovalor , uti_co_finalidade , uti_co_indicereajuste , uti_no_outrosindicereajuste , uti_nu_prazoreajuste , uti_nu_prazocarencia , uti_co_tipoinstrumento , uti_nu_instrumento , cast(uti_da_instrumento as timestamp) uti_da_instrumento , uti_co_orgaolotacao , cast(rtrim(uti_in_endcorrespondencia) as varchar(1)) uti_in_endcorrespondencia , uti_ed_tipologradouro_corr , uti_ed_logradouro_corr , uti_ed_numero_corr , uti_ed_complemento_corr , uti_ed_bairro_corr , uti_ed_cep_corr , uti_co_municipio_corr , uti_sg_uf_corr , cast(uti_da_publicacaoinstrumento as timestamp) uti_da_publicacaoinstrumento , uti_co_objetivoempreendimentossociais , uti_no_outrosobjetivo , uti_nu_familiasbeneficiadas , cast(uti_da_assinaturatermo as timestamp) uti_da_assinaturatermo , uti_co_direitoadquirido , uti_nu_inscricaogenericafrgps , uti_nu_contacontabilanteriorfrgps , uti_co_uganteriorfrgps , uti_co_ugemitentefrgps , uti_co_gestaoemitentefrgps , uti_co_gestaoanteriorfrgps FROM dbp_29321_spiunet_VBL.utilizacao""", connection)
            
            # Validação dos dados extraídos
            if self.validator.validate_dataframe(df):
                logger.info(f"✅ Extração concluída: {len(df)} registros")
                return df
            else:
                logger.warning("⚠️ Dados extraídos não passaram na validação")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"❌ Erro na extração Utilizacao: {e}")
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
