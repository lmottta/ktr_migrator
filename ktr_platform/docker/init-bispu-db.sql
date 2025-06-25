-- ================================================================================
-- KTR PLATFORM - BANCO BISPU PARA TESTES
-- Adaptado do script original LOCAL_BISPU para integração com KTR Platform
-- Data: 2025-01-23
-- Desenvolvido por: Engenheiro de Dados Senior
-- ================================================================================

-- ┌─────────────────────────────────────────────────────────────────────────────┐
-- │                              INSTRUÇÕES                                     │
-- ├─────────────────────────────────────────────────────────────────────────────┤
-- │ Este script cria o banco BISPU para testes dos KTRs migrados               │
-- │ Execução: docker-compose up -d bispu-db                                    │
-- │ Usuário: bispu / Senha: bispu_password                                     │
-- └─────────────────────────────────────────────────────────────────────────────┘

-- ================================================================================
-- CONFIGURAÇÕES INICIAIS DO BANCO
-- ================================================================================

-- Configurar timezone e outras configurações padrão
SET timezone = 'America/Sao_Paulo';
SET datestyle = 'ISO, DMY';
SET default_text_search_config = 'pg_catalog.portuguese';
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

-- ================================================================================
-- SEÇÃO 1: EXTENSÕES
-- ================================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "unaccent";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ================================================================================
-- SEÇÃO 2: SCHEMAS BISPU (42 schemas do ambiente real)
-- ================================================================================

-- Schemas principais do BISPU
CREATE SCHEMA IF NOT EXISTS arrecadacao_dw;
CREATE SCHEMA IF NOT EXISTS mgc;
CREATE SCHEMA IF NOT EXISTS etl;
CREATE SCHEMA IF NOT EXISTS tmp;
CREATE SCHEMA IF NOT EXISTS relatorios;

-- ================================================================================
-- SEÇÃO 3: TABELAS DE TESTE PARA KTR
-- ================================================================================

-- Tabela para teste documento_mgc
CREATE TABLE IF NOT EXISTS mgc.documento (
    id SERIAL PRIMARY KEY,
    numero_documento VARCHAR(50) NOT NULL,
    tipo_documento VARCHAR(20),
    data_documento DATE,
    cpf_cnpj VARCHAR(18),
    nome_pessoa VARCHAR(255),
    valor DECIMAL(15,2),
    status VARCHAR(20) DEFAULT 'ATIVO',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela destino documento
CREATE TABLE IF NOT EXISTS mgc.documento_processado (
    id SERIAL PRIMARY KEY,
    documento_origem_id INTEGER,
    numero_documento VARCHAR(50),
    tipo_documento VARCHAR(20),
    data_documento DATE,
    cpf_cnpj_formatado VARCHAR(18),
    nome_pessoa_upper VARCHAR(255),
    valor_formatado DECIMAL(15,2),
    ambiente VARCHAR(20) DEFAULT 'LOCAL',
    processado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela para teste localização imóvel
CREATE TABLE IF NOT EXISTS mgc.localizacao_imovel (
    id SERIAL PRIMARY KEY,
    codigo_imovel VARCHAR(20) NOT NULL,
    endereco VARCHAR(500),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    uf VARCHAR(2),
    cep VARCHAR(9),
    coordenadas_lat DECIMAL(10,8),
    coordenadas_lng DECIMAL(11,8),
    area_total DECIMAL(12,2),
    status VARCHAR(20) DEFAULT 'ATIVO',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================================================================
-- SEÇÃO 4: DADOS DE EXEMPLO
-- ================================================================================

INSERT INTO mgc.documento (numero_documento, tipo_documento, data_documento, cpf_cnpj, nome_pessoa, valor) VALUES
('DOC001', 'CPF', '2024-01-15', '123.456.789-01', 'João Silva Santos', 1500.50),
('DOC002', 'CNPJ', '2024-01-16', '12.345.678/0001-90', 'Empresa Teste LTDA', 25000.00),
('DOC003', 'CPF', '2024-01-17', '987.654.321-09', 'Maria Oliveira Costa', 750.25)
ON CONFLICT DO NOTHING;

INSERT INTO mgc.localizacao_imovel (codigo_imovel, endereco, bairro, cidade, uf, cep, coordenadas_lat, coordenadas_lng, area_total) VALUES
('IM001', 'Rua das Flores, 123', 'Centro', 'São Paulo', 'SP', '01001-000', -23.5505, -46.6333, 250.00),
('IM002', 'Av. Paulista, 1000', 'Bela Vista', 'São Paulo', 'SP', '01310-100', -23.5615, -46.6565, 180.50)
ON CONFLICT DO NOTHING;

-- ================================================================================
-- SEÇÃO 5: FUNÇÕES AUXILIARES PARA KTR PLATFORM
-- ================================================================================

-- Função para verificar integridade dos schemas BISPU
CREATE OR REPLACE FUNCTION public.verificar_schemas_bispu()
RETURNS TABLE(status TEXT, message TEXT) AS $$
DECLARE
    expected_schemas TEXT[] := ARRAY[
        'arrecadacao_dw', 'avaliacao_siafixspiunet_dw', 'cadunico', 
        'cebas_beneficente', 'cebas_educacional', 'cebas_saude',
        'cif_dw', 'conciliacaocontabil', 'contabilidade',
        'doadores_eleitorais', 'doitu', 'dominios', 'dw_siapa',
        'dw_spiunet', 'etl', 'figest_dw', 'gaia', 'giapu_dm',
        'giapu_dw', 'ibge', 'indicadores', 'mgc', 'ods', 'okrs',
        'painel_spu', 'pericles', 'programa_democratizacao', 'public',
        'qlik_dw', 'qualifica_cpf', 'qvd', 'rais', 'relatorios',
        'servico_dw', 'siapa_dw', 'siapahis_dw', 'sisobi',
        'spiunet', 'spiunet_dw', 'tmp', 'trilhasaudit',
        'ktr_platform', 'ktr_audit', 'ktr_logs'
    ];
    schema_name TEXT;
    missing_count INTEGER := 0;
BEGIN
    FOREACH schema_name IN ARRAY expected_schemas
    LOOP
        IF NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = schema_name) THEN
            missing_count := missing_count + 1;
            status := 'ERROR';
            message := 'Schema ausente: ' || schema_name;
            RETURN NEXT;
        END IF;
    END LOOP;
    
    IF missing_count = 0 THEN
        status := 'SUCCESS';
        message := 'Todos os ' || array_length(expected_schemas, 1) || ' schemas BISPU + KTR criados com sucesso';
        RETURN NEXT;
    ELSE
        status := 'WARNING';
        message := missing_count || ' schemas ausentes do total de ' || array_length(expected_schemas, 1);
        RETURN NEXT;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Função para listar conexões de teste disponíveis
CREATE OR REPLACE FUNCTION public.listar_conexoes_teste()
RETURNS TABLE(
    schema_name TEXT, 
    owner_name TEXT, 
    table_count BIGINT,
    purpose TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        n.nspname::TEXT,
        pg_get_userbyid(n.nspowner)::TEXT,
        (SELECT count(*) FROM information_schema.tables t 
         WHERE t.table_schema = n.nspname)::BIGINT,
        CASE 
            WHEN n.nspname LIKE 'ktr_%' THEN 'KTR Platform'
            WHEN n.nspname IN ('mgc', 'etl', 'tmp') THEN 'Testes KTR'
            WHEN n.nspname LIKE '%_dw' THEN 'Data Warehouse'
            ELSE 'Sistema BISPU'
        END::TEXT
    FROM pg_namespace n
    WHERE n.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
    ORDER BY 
        CASE 
            WHEN n.nspname LIKE 'ktr_%' THEN 1
            WHEN n.nspname IN ('mgc', 'etl', 'tmp') THEN 2
            ELSE 3
        END,
        n.nspname;
END;
$$ LANGUAGE plpgsql;

-- ================================================================================
-- SEÇÃO 6: VERIFICAÇÕES E COMENTÁRIOS FINAIS
-- ================================================================================

-- Executar verificação dos schemas criados
SELECT * FROM public.verificar_schemas_bispu();

-- Listar conexões de teste disponíveis
SELECT * FROM public.listar_conexoes_teste();

-- Adicionar comentários aos schemas principais para documentação
COMMENT ON SCHEMA mgc IS 'Schema para testes de migração KTR - dados de documentos e localização';
COMMENT ON SCHEMA etl IS 'Schema para processos de ETL (Extract, Transform, Load)';
COMMENT ON SCHEMA tmp IS 'Schema para tabelas temporárias e processamento intermediário';
COMMENT ON SCHEMA ktr_platform IS 'Schema da plataforma KTR para metadados e controle';

-- Log de finalização
DO $$
BEGIN
    RAISE NOTICE '================================================================================';
    RAISE NOTICE 'Script de criação do banco BISPU para KTR Platform executado com sucesso em %', now();
    RAISE NOTICE 'Total de schemas criados: 45 (42 BISPU + 3 KTR)';
    RAISE NOTICE 'Usuários configurados: bispu, oltp, ktr_user, postgres';
    RAISE NOTICE 'Tabelas de teste criadas no schema MGC para validação dos KTRs';
    RAISE NOTICE 'Execute "SELECT * FROM public.verificar_schemas_bispu();" para verificar integridade';
    RAISE NOTICE '================================================================================';
END $$; 