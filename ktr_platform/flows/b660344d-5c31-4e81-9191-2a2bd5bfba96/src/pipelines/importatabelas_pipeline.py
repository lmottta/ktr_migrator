"""
Pipeline: importatabelas
Gerado automaticamente do KTR: importatabelas.ktr
Data: 2025-08-26 14:45:03

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
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text
from sqlalchemy import text

class ImportatabelasPipeline:
    """
    Pipeline gerado do KTR importatabelas
    
    Pipeline ETL gerado automaticamente a partir do KTR: importatabelas.ktr
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
        log_file = self.config.get("log_file", f"logs/importatabelas_{datetime.now().strftime('%Y%m%d')}.log")
        
        logger.add(
            log_file,
            rotation="1 day",
            retention="30 days",
            format="{time} | {level} | {message}",
            level=log_level
        )
        
        logger.info(f"🚀 Iniciando pipeline: importatabelas")
    
    def setup_connections(self):
        """Configura conexões com bancos de dados"""
        # Conexão: DAAS
        daas_url = "generic://41728130115:Encrypted 2be98afc86ae4d3a4be3bfd629fcbf982@:1521/"
        self.connections["DAAS"] = create_engine(daas_url)
        logger.info(f"📡 Conexão configurada: DAAS (GENERIC)")
        # Conexão: oltp
        oltp_url = "postgresql://postgres:Encrypted 2be98afc86aa7c683ea53be7fd0c282ea@10.209.9.227:5432/oltp"
        self.connections["oltp"] = create_engine(oltp_url)
        logger.info(f"📡 Conexão configurada: oltp (POSTGRESQL)")
    
    def extract_data(self) -> pd.DataFrame:
        """
        Extração de dados - Stage 1
        """
        logger.info("🔄 Iniciando extração de dados...")
        start_time = datetime.now()
        
        try:
            # Extração de dados - Benfeitoria
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT cast(bnf_nu_benfeitoria as bigint) bnf_nu_benfeitoria , cast(bnf_nu_rip_imovel as bigint) bnf_nu_rip_imovel , cast(bnf_nu_rip_utilizacao as bigint) bnf_nu_rip_utilizacao , bnf_mq_areaconstruida , bnf_op_cub , cast(bnf_co_estadoconservacao as bigint) bnf_co_estadoconservacao , cast(bnf_co_tipoestrutura as bigint) bnf_co_tipoestrutura , cast(bnf_co_idadeaparente as bigint) bnf_co_idadeaparente , bnf_op_fatorkp , bnf_va_benfeitoria , cast(bnf_co_uso as bigint) bnf_co_uso , cast(bnf_co_padraoacabamento as bigint) bnf_co_padraoacabamento , bnf_qt_pavimento , bnf_no_denominacaopredio , bnf_mq_areautil , bnf_mq_areaindividualprivativaescritorio , bnf_mq_areacoletivaprivativaescritorio , bnf_mq_areacoletivacomumescritorio , bnf_mq_areaprivativaapoio , bnf_mq_areacomumapoio , bnf_mq_areaestacionamento , bnf_qt_vagascomunsestacionamento , bnf_qt_vagasprivativasestacionamento , bnf_mq_areaoutros , bnf_mq_areaespecifica FROM benfeitoria""", connection)
            # Extração de dados - GrupoUG
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT co_ug , co_grupoug FROM ug_grupoug""", connection)
            # Extração de dados - GrupoUG 2
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT co_ug , co_grupoug FROM ug_grupoug""", connection)
            # Extração de dados - Imovel
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT cast(imv_nu_rip as bigint) imv_nu_rip, cast(rtrim(imv_in_certificado) as varchar(1)) imv_in_certificado, imv_co_motivocancelamentoimovel, imv_ed_tipologradouro, imv_ed_logradouro, imv_ed_numero, imv_ed_complemento, imv_ed_bairro, imv_ed_cep, imv_co_municipio, imv_sg_uf, imv_sg_pais, imv_no_cidadeexterior, imv_nu_codigopostal, imv_co_conceituacaoterreno, imv_mq_areaterreno, imv_co_naturezaterreno, imv_va_metroquadrado, imv_va_terreno, imv_va_somabenfeitoriautilizacao, imv_op_fracaoideal, imv_co_tipoimovel, imv_op_fatorcorretivo, imv_va_imovel, imv_va_imoveldolar, cast(imv_da_avaliacao as timestamp) imv_da_avaliacao, imv_co_nivelrigoravaliacao, cast(imv_da_prazovalidadeavaliacao as timestamp) imv_da_prazovalidadeavaliacao, imv_co_tipovocacao, imv_no_tomboarquivamento, imv_no_cartoriooficio, imv_nu_matriculacartorio, imv_nu_livrocartorio, imv_nu_folhacartorio, cast(imv_da_registrocartorio as timestamp) imv_da_registrocartorio, imv_co_formaaquisicao, imv_no_proprietarioanterior, imv_no_fundamentoincorporacao, imv_no_encargoaquisicao, cast(rtrim(imv_in_imovelsubjudice) as varchar(1)) imv_in_imovelsubjudice, imv_no_acao, imv_no_processoapenso, imv_nu_processoprincipal, imv_no_latitudelongitude, imv_co_tipodominio, imv_no_proprietariooficial, imv_co_proprietariooficial, cast(imv_da_validacao as timestamp) imv_da_validacao, imv_no_situacaoincorporacao, cast(imv_da_cadastro as timestamp) imv_da_cadastro, cast(imv_da_incorporacao as timestamp) imv_da_incorporacao, imv_co_orgaoextinto, imv_co_direitoadquirido, cast(rtrim(imv_in_enderecovalidado) as varchar(1)) imv_in_enderecovalidado, cast(rtrim(imv_in_migracaospunet) as varchar(1)) imv_in_migracaospunet, imv_id_imovelspunet FROM dbp_29321_spiunet_VBL.imovel;""", connection)
            # Extração de dados - Municipio
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT co_municipio , no_municipio , nu_cepinicial , nu_cepfinal , sg_uf , cast(da_atualizacaomunicipio as timestamp) as da_atualizacaomunicipio FROM dbp_29321_spiunet_VBL.municipio""", connection)
            # Extração de dados - TpDestinacao
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT co_tipodestinacao , no_tipodestinacao , co_classificacaosiafi FROM tipodestinacao""", connection)
            # Extração de dados - UG
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT co_ug , no_ug , co_ugsetorialcontabil , co_gestaoprincipal , cast(da_atualizacaoug_siafi as timestamp) as da_atualizacaoug_siafi , rtrim(in_ugativa) in_ugativa , rtrim(in_uggrpu) in_uggrpu FROM ug""", connection)
            # Extração de dados - UG_Gestao
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT co_ug , co_gestao , cast(da_atualizacaouggestao as timestamp) as da_atualizacaouggestao , rtrim(in_uggestaoativa) as in_uggestaoativa FROM ug_gestao""", connection)
            # Extração de dados - Usuario
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT usu_nu_chave , usu_nu_cpf , usu_no_senha , usu_no_usuario , usu_nu_telefone , usu_no_email , usu_sg_uf , usu_co_ug , usu_co_grupoug , usu_co_perfil , usu_nu_cpfusuariocadastrador , cast(usu_da_ultimologin as timestamp) usu_da_ultimologin , cast(rtrim(usu_nu_situacao) as varchar(1)) usu_nu_situacao , cast(rtrim(usu_nu_statussenha) as varchar(1)) usu_nu_statussenha , cast(usu_da_atualizacaousuario as timestamp) usu_da_atualizacaousuario , usu_qt_tentativas FROM dbp_29321_spiunet_VBL.usuario""", connection)
            # Extração de dados - Utilizacao
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT cast(uti_nu_rip as bigint) uti_nu_rip , cast(uti_nu_rip_imovel as bigint) uti_nu_rip_imovel , cast(rtrim(uti_in_certificado) as varchar(1)) uti_in_certificado , cast(rtrim(uti_in_valornormalizadosiafi) as varchar(1)) uti_in_valornormalizadosiafi , cast(uti_co_ug as bigint) uti_co_ug , cast(uti_co_gestao as bigint) uti_co_gestao , cast(uti_nu_processo as varchar(17)) uti_nu_processo , cast(uti_co_motivocancelamentoutilizacao as bigint) uti_co_motivocancelamentoutilizacao , cast(uti_co_regime as bigint) uti_co_regime , cast(uti_co_situacaoregime as bigint) uti_co_situacaoregime , cast(uti_da_inicio as timestamp) uti_da_inicio , cast(uti_da_fim as timestamp) uti_da_fim , uti_ed_complemento , uti_mq_areaterreno , uti_va_metroquadrado , uti_va_terreno , uti_op_fracaoideal , uti_op_fatorcorretivo , uti_va_utilizacao , cast(uti_da_avaliacao as timestamp) uti_da_avaliacao , cast(uti_co_nivelrigoravaliacao as bigint) uti_co_nivelrigoravaliacao , cast(uti_da_prazovalidadeavaliacao as timestamp) uti_da_prazovalidadeavaliacao , cast(uti_co_tipodestinacao as bigint) uti_co_tipodestinacao , uti_no_destinacao , uti_no_vocacao , uti_no_averbacaoratificacao , cast(uti_da_averbacaoratificacao as timestamp) uti_da_averbacaoratificacao , uti_nu_livro , uti_nu_folha , uti_no_beneficiario , uti_no_objetivocessao , uti_no_encargocessao , uti_no_embasamentolegal , cast(rtrim(uti_in_cpfcnpjbeneficiario) as varchar(1)) uti_in_cpfcnpjbeneficiario , uti_nu_cpfcnpjbeneficiario , cast(uti_co_formacobranca as bigint) uti_co_formacobranca , uti_va_beneficio , uti_da_diavencimento , uti_no_grupoindigena , uti_nu_habitanteindigena , uti_co_formaaquisicao , uti_co_tipodominio , uti_co_formapagamento , uti_qt_parcela , uti_co_tipocontrato , cast(uti_da_iniciocontrato as timestamp) uti_da_iniciocontrato , cast(uti_da_fimcontrato as timestamp) uti_da_fimcontrato , cast(uti_da_prazocarencia as timestamp) uti_da_prazocarencia , cast(uti_da_outorga as timestamp) uti_da_outorga , cast(uti_da_vistoria as timestamp) uti_da_vistoria , uti_nu_edital , cast(uti_da_publicacaoedital as timestamp) uti_da_publicacaoedital , cast(uti_da_avaliacaoalienacao as timestamp) uti_da_avaliacaoalienacao , uti_va_efetivoalienacao , uti_co_formalizadornegocio , uti_co_situacaoocupacao , cast(uti_da_validacao as timestamp) uti_da_validacao , cast(uti_in_alteracaovalor as varchar(1)) as uti_in_alteracaovalor , uti_co_finalidade , uti_co_indicereajuste , uti_no_outrosindicereajuste , uti_nu_prazoreajuste , uti_nu_prazocarencia , uti_co_tipoinstrumento , uti_nu_instrumento , cast(uti_da_instrumento as timestamp) uti_da_instrumento , uti_co_orgaolotacao , cast(rtrim(uti_in_endcorrespondencia) as varchar(1)) uti_in_endcorrespondencia , uti_ed_tipologradouro_corr , uti_ed_logradouro_corr , uti_ed_numero_corr , uti_ed_complemento_corr , uti_ed_bairro_corr , uti_ed_cep_corr , uti_co_municipio_corr , uti_sg_uf_corr , cast(uti_da_publicacaoinstrumento as timestamp) uti_da_publicacaoinstrumento , uti_co_objetivoempreendimentossociais , uti_no_outrosobjetivo , uti_nu_familiasbeneficiadas , cast(uti_da_assinaturatermo as timestamp) uti_da_assinaturatermo , uti_co_direitoadquirido , uti_nu_inscricaogenericafrgps , uti_nu_contacontabilanteriorfrgps , uti_co_uganteriorfrgps , uti_co_ugemitentefrgps , uti_co_gestaoemitentefrgps , uti_co_gestaoanteriorfrgps FROM dbp_29321_spiunet_VBL.utilizacao""", connection)
            # Extração de dados - bloqueiospiunet
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT cast(rtrim(bsn_co_recurso) as varchar(1)) bsn_co_recurso , bsn_nu_rip_imovel , bsn_nu_rip_utilizacao , bsn_nu_cpf_alteracao , bsn_nu_cpf_usuario , cast(bsn_da_atualizacao as timestamp) bsn_da_atualizacao FROM bloqueiospiunet""", connection)
            # Extração de dados - classificacaoimovel
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT co_classificacaoimovel , no_classificacaoimovel FROM classificacaoimovel""", connection)
            # Extração de dados - conceituacaoterreno
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT co_conceituacaoterreno , no_conceituacaoterreno FROM conceituacaoterreno""", connection)
            # Extração de dados - credito
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT cred_nu_chavecredito , cred_nu_riputilizacao , cast(rtrim(cred_in_creditoidentificado) as varchar(1)) cred_in_creditoidentificado , cred_sg_grpu , cred_sg_ufriputilizacao , cred_co_receita , cred_nu_pagamentosrf , cast(cred_da_arrecadacao as timestamp) cred_da_arrecadacao , cred_va_totalpago , cred_nu_banco , cred_nu_agencia , cred_nu_municipiopagamento , cast(rtrim(cred_in_cpfcnpjresponsavel) as varchar(1)) cred_in_cpfcnpjresponsavel , cred_nu_cpfcnpjresponsavel , cred_co_origemcredito , cast(cred_da_anomesdecendiosrf as timestamp) cred_da_anomesdecendiosrf , cred_co_unidademonetaria , cast(cred_da_inclusaocredito as timestamp) cred_da_inclusaocredito FROM credito""", connection)
            # Extração de dados - criticasimagens
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT descricao FROM criticasimagens""", connection)
            # Extração de dados - debito
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT deb_nu_chavedebito , deb_nu_riputilizacao , deb_sg_grpu , deb_co_receita , cast(deb_da_referenciadebito as timestamp) deb_da_referenciadebito , cast(deb_da_vencimentodebito as timestamp) deb_da_vencimentodebito , deb_va_debito , deb_co_unidademonetaria , cast(deb_da_inclusaodebito as timestamp) deb_da_inclusaodebito , cast(rtrim(deb_in_cpfcnpjresponsavel) as varchar(1)) deb_in_cpfcnpjresponsavel , deb_nu_cpfcnpjresponsavel FROM debito""", connection)
            # Extração de dados - evento
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT eve_nu_chave , eve_nu_cpfusuario , eve_nu_rip_imovel , eve_nu_rip_utilizacao , eve_nu_cpfusuarioatualizado , eve_co_tipo , CAST(eve_da_evento AS TIMESTAMP) eve_da_evento , eve_tx_descricao FROM evento""", connection)
            # Extração de dados - finalidade
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT co_finalidade , no_finalidade FROM finalidade""", connection)
            # Extração de dados - formaaquisicao
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT co_formaaquisicao , no_formaaquisicao FROM formaaquisicao""", connection)
            # Extração de dados - formacobranca
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT co_formacobranca , no_formacobranca FROM formacobranca""", connection)
            # Extração de dados - mcimovel
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT co_motivocancelamentoimovel , no_motivocancelamentoimovel , co_eventosiafi , cast(rtrim(in_opcaodisponivelonline) as varchar(1)) in_opcaodisponivelonline FROM motivocancelamentoimovel""", connection)
            # Extração de dados - mcimovel 2
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT co_motivocancelamentoutilizacao , no_motivocancelamentoutilizacao , co_eventosiafi , cast(rtrim(in_opcaodisponivelonline) as varchar(1)) in_opcaodisponivelonline FROM motivocancelamentoutilizacao""", connection)
            # Extração de dados - orgaoextinto
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT co_orgaoextinto , no_orgaoextinto , sg_orgaoextinto , no_fundamentolegal FROM orgaoextinto""", connection)
            # Extração de dados - populacao
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT pop_nu_rip_imovel , pop_nu_rip_utilizacao , pop_qt_postostrabalhointegral , pop_qt_postostrabalhoreduzido , pop_qt_apoio , pop_qt_especifica FROM populacao""", connection)
            # Extração de dados - proprietariooficial
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT co_proprietariooficial , no_proprietariooficial FROM proprietariooficial""", connection)
            # Extração de dados - receita
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT co_receitaprincipal , rtrim(no_receitaprincipal) no_receitaprincipal , co_receitamulta , co_receitajuros FROM receita""", connection)
            # Extração de dados - regime
            # Extração via SQL
            connection = self.connections["DAAS"]
            df = pd.read_sql("""SELECT co_regimeutilizacao , no_regimeutilizacao FROM regimeutilizacao""", connection)
            
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
            # Transformação de dados - campos1
            # Transformação genérica
            # Transformação de dados - campos3
            # Transformação genérica
            # Transformação de dados - campos4
            # Transformação genérica
            # Transformação de dados - campos5
            # Transformação genérica
            # Transformação de dados - campos6
            # Transformação genérica
            # Transformação de dados - campos7
            # Transformação genérica
            # Transformação de dados - campos7 2
            # Transformação genérica
            # Transformação de dados - campos8
            # Transformação genérica
            # Transformação de dados - values
            # Transformação genérica
            # Transformação de dados - values1
            # Transformação genérica
            # Transformação de dados - values10
            # Transformação genérica
            # Transformação de dados - values2
            # Transformação genérica
            # Transformação de dados - values3
            # Transformação genérica
            # Transformação de dados - values3 2
            # Transformação genérica
            # Transformação de dados - values3 2 2
            # Transformação genérica
            # Transformação de dados - values3 2 2 2
            # Transformação genérica
            # Transformação de dados - values3 2 2 2 2
            # Transformação genérica
            # Transformação de dados - values6
            # Transformação genérica
            # Transformação de dados - values6 2
            # Transformação genérica
            # Transformação de dados - values6 2 2
            # Transformação genérica
            # Transformação de dados - values6 2 2 2
            # Transformação genérica
            # Transformação de dados - values6 2 2 2 2
            # Transformação genérica
            # Transformação de dados - values6 2 2 2 2 2
            # Transformação genérica
            # Transformação de dados - values6 2 2 2 2 2 2
            # Transformação genérica
            # Transformação de dados - values7
            # Transformação genérica
            # Transformação de dados - values8
            # Transformação genérica
            # Transformação de dados - values9
            # Transformação genérica
            
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
            # Carga de dados - o_ conceituacaoterreno
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.conceituacaoterreno"))
                logger.info("🗑️ Tabela truncada: spiunet.conceituacaoterreno")

            df.to_sql(
                name="conceituacaoterreno",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - o_classificacaoimovel
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.classificacaoimovel"))
                logger.info("🗑️ Tabela truncada: spiunet.classificacaoimovel")

            df.to_sql(
                name="classificacaoimovel",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - o_credito
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.credito"))
                logger.info("🗑️ Tabela truncada: spiunet.credito")

            df.to_sql(
                name="credito",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - o_criticasimagens
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.criticasimagens"))
                logger.info("🗑️ Tabela truncada: spiunet.criticasimagens")

            df.to_sql(
                name="criticasimagens",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - o_debito
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.debito"))
                logger.info("🗑️ Tabela truncada: spiunet.debito")

            df.to_sql(
                name="debito",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - o_evento
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.evento"))
                logger.info("🗑️ Tabela truncada: spiunet.evento")

            df.to_sql(
                name="evento",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - o_finalidade
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.finalidade"))
                logger.info("🗑️ Tabela truncada: spiunet.finalidade")

            df.to_sql(
                name="finalidade",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - o_formaaquisicao
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.formaaquisicao"))
                logger.info("🗑️ Tabela truncada: spiunet.formaaquisicao")

            df.to_sql(
                name="formaaquisicao",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - o_formacobranca
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.formacobranca"))
                logger.info("🗑️ Tabela truncada: spiunet.formacobranca")

            df.to_sql(
                name="formacobranca",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - o_mcimovel
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.motivocancelamentoimovel"))
                logger.info("🗑️ Tabela truncada: spiunet.motivocancelamentoimovel")

            df.to_sql(
                name="motivocancelamentoimovel",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - o_mcimovel 2
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.motivocancelamentoutilizacao"))
                logger.info("🗑️ Tabela truncada: spiunet.motivocancelamentoutilizacao")

            df.to_sql(
                name="motivocancelamentoutilizacao",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - o_oe
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.orgaoextinto"))
                logger.info("🗑️ Tabela truncada: spiunet.orgaoextinto")

            df.to_sql(
                name="orgaoextinto",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - o_po
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
            # Carga de dados - o_populacao
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.populacao"))
                logger.info("🗑️ Tabela truncada: spiunet.populacao")

            df.to_sql(
                name="populacao",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - o_regime
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.regimeutilizacao"))
                logger.info("🗑️ Tabela truncada: spiunet.regimeutilizacao")

            df.to_sql(
                name="regimeutilizacao",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - output2
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.ug_grupoug"))
                logger.info("🗑️ Tabela truncada: spiunet.ug_grupoug")

            df.to_sql(
                name="ug_grupoug",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - output3
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.ug_gestao"))
                logger.info("🗑️ Tabela truncada: spiunet.ug_gestao")

            df.to_sql(
                name="ug_gestao",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - output4
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.ug"))
                logger.info("🗑️ Tabela truncada: spiunet.ug")

            df.to_sql(
                name="ug",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - output5
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.municipio"))
                logger.info("🗑️ Tabela truncada: spiunet.municipio")

            df.to_sql(
                name="municipio",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - output6
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.ug_grupoug"))
                logger.info("🗑️ Tabela truncada: spiunet.ug_grupoug")

            df.to_sql(
                name="ug_grupoug",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - output6 2
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.usuario"))
                logger.info("🗑️ Tabela truncada: spiunet.usuario")

            df.to_sql(
                name="usuario",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - output6 2 2
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.tipodestinacao"))
                logger.info("🗑️ Tabela truncada: spiunet.tipodestinacao")

            df.to_sql(
                name="tipodestinacao",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - output6 2 2 2
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.bloqueiospiunet"))
                logger.info("🗑️ Tabela truncada: spiunet.bloqueiospiunet")

            df.to_sql(
                name="bloqueiospiunet",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - saida_benfeitoria
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.benfeitoria"))
                logger.info("🗑️ Tabela truncada: spiunet.benfeitoria")

            df.to_sql(
                name="benfeitoria",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - saida_imovel
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.imovel"))
                logger.info("🗑️ Tabela truncada: spiunet.imovel")

            df.to_sql(
                name="imovel",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - saida_receita
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.receita"))
                logger.info("🗑️ Tabela truncada: spiunet.receita")

            df.to_sql(
                name="receita",
                schema="spiunet" if "spiunet" else None,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            # Carga de dados - saida_utilizaca
            # Carga para PostgreSQL
            connection = self.connections["oltp"]

            # Truncar tabela antes da carga
            with connection.begin() as conn:
                conn.execute(sa.text("TRUNCATE TABLE spiunet.utilizacao"))
                logger.info("🗑️ Tabela truncada: spiunet.utilizacao")

            df.to_sql(
                name="utilizacao",
                schema="spiunet" if "spiunet" else None,
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
        logger.info("🎯 Executando pipeline importatabelas")
        
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
    
    pipeline = ImportatabelasPipeline(config)
    result = pipeline.run_pipeline()
    
    if result["status"] == "success":
        print(f"✅ Pipeline executado com sucesso! Processados {result['records_processed']} registros")
    else:
        print(f"❌ Pipeline falhou: {result.get('error', 'Erro desconhecido')}")
        exit(1) 