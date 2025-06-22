-- =============================================================================
-- KTR PLATFORM - INICIALIZAÇÃO DO BANCO DE DADOS
-- =============================================================================
-- Script de inicialização para PostgreSQL
-- Data: 2025-06-19
-- Desenvolvido por: Engenheiro de Dados Senior

-- Configurações iniciais
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET default_tablespace = '';
SET default_table_access_method = heap;

-- =============================================================================
-- EXTENSÕES
-- =============================================================================

-- UUID para IDs únicos
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Funções criptográficas
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Full text search em português
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- =============================================================================
-- SCHEMAS
-- =============================================================================

-- Schema principal da aplicação
CREATE SCHEMA IF NOT EXISTS ktr_platform;

-- Schema para auditoria
CREATE SCHEMA IF NOT EXISTS audit;

-- Schema para logs
CREATE SCHEMA IF NOT EXISTS logs;

-- Configurar search_path padrão
ALTER DATABASE ktr_platform SET search_path TO ktr_platform, public;

-- =============================================================================
-- FUNÇÕES AUXILIARES
-- =============================================================================

-- Função para atualizar timestamp de modificação
CREATE OR REPLACE FUNCTION ktr_platform.update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Função para gerar slug
CREATE OR REPLACE FUNCTION ktr_platform.generate_slug(input_text TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN lower(regexp_replace(
        unaccent(input_text), 
        '[^a-zA-Z0-9]+', 
        '-', 
        'g'
    ));
END;
$$ language 'plpgsql';

-- =============================================================================
-- TABELA: flows
-- =============================================================================

CREATE TABLE IF NOT EXISTS ktr_platform.flows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE,
    description TEXT,
    
    -- Configuração
    project_path TEXT NOT NULL,
    pipeline_file TEXT,
    status VARCHAR(50) DEFAULT 'Pronto' CHECK (status IN ('Pronto', 'Executando', 'Sucesso', 'Falha', 'Erro')),
    
    -- Execução
    execution_status VARCHAR(50),
    execution_logs TEXT[],
    execution_start_time TIMESTAMP WITH TIME ZONE,
    execution_end_time TIMESTAMP WITH TIME ZONE,
    execution_duration INTERVAL,
    error_message TEXT,
    
    -- Metadados
    tags TEXT[],
    priority INTEGER DEFAULT 0,
    enabled BOOLEAN DEFAULT true,
    
    -- Auditoria
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    modified_by VARCHAR(100),
    
    -- Índices
    CONSTRAINT flows_name_check CHECK (char_length(name) >= 3),
    CONSTRAINT flows_priority_check CHECK (priority >= 0 AND priority <= 10)
);

-- Trigger para slug automático
CREATE OR REPLACE FUNCTION ktr_platform.flows_slug_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.slug IS NULL OR NEW.slug = '' THEN
        NEW.slug = ktr_platform.generate_slug(NEW.name);
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER flows_slug_auto_update
    BEFORE INSERT OR UPDATE ON ktr_platform.flows
    FOR EACH ROW
    EXECUTE FUNCTION ktr_platform.flows_slug_trigger();

-- Trigger para timestamp de modificação
CREATE TRIGGER flows_update_modified_time
    BEFORE UPDATE ON ktr_platform.flows
    FOR EACH ROW
    EXECUTE FUNCTION ktr_platform.update_modified_column();

-- =============================================================================
-- TABELA: schedules
-- =============================================================================

CREATE TABLE IF NOT EXISTS ktr_platform.schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flow_id UUID NOT NULL REFERENCES ktr_platform.flows(id) ON DELETE CASCADE,
    
    -- Agendamento
    name VARCHAR(255) NOT NULL,
    cron_expression VARCHAR(100) NOT NULL,
    timezone VARCHAR(50) DEFAULT 'America/Sao_Paulo',
    
    -- Status
    enabled BOOLEAN DEFAULT true,
    last_run TIMESTAMP WITH TIME ZONE,
    next_run TIMESTAMP WITH TIME ZONE,
    
    -- Configurações
    max_retries INTEGER DEFAULT 3,
    retry_delay_seconds INTEGER DEFAULT 300,
    timeout_seconds INTEGER DEFAULT 3600,
    
    -- Auditoria
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    modified_by VARCHAR(100),
    
    CONSTRAINT schedules_name_check CHECK (char_length(name) >= 3),
    CONSTRAINT schedules_max_retries_check CHECK (max_retries >= 0 AND max_retries <= 10),
    CONSTRAINT schedules_timeout_check CHECK (timeout_seconds > 0)
);

-- Trigger para timestamp de modificação
CREATE TRIGGER schedules_update_modified_time
    BEFORE UPDATE ON ktr_platform.schedules
    FOR EACH ROW
    EXECUTE FUNCTION ktr_platform.update_modified_column();

-- =============================================================================
-- TABELA: execution_history
-- =============================================================================

CREATE TABLE IF NOT EXISTS ktr_platform.execution_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flow_id UUID NOT NULL REFERENCES ktr_platform.flows(id) ON DELETE CASCADE,
    schedule_id UUID REFERENCES ktr_platform.schedules(id) ON DELETE SET NULL,
    
    -- Execução
    execution_id VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('Iniciado', 'Executando', 'Sucesso', 'Falha', 'Erro', 'Cancelado')),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    duration INTERVAL,
    
    -- Logs e erros
    logs TEXT,
    error_message TEXT,
    error_stack TEXT,
    
    -- Métricas
    records_processed INTEGER DEFAULT 0,
    memory_usage_mb INTEGER,
    cpu_usage_percent DECIMAL(5,2),
    
    -- Contexto
    triggered_by VARCHAR(50) DEFAULT 'manual' CHECK (triggered_by IN ('manual', 'schedule', 'api', 'webhook')),
    triggered_by_user VARCHAR(100),
    environment VARCHAR(50) DEFAULT 'production',
    
    -- Auditoria
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- TABELA: system_config
-- =============================================================================

CREATE TABLE IF NOT EXISTS ktr_platform.system_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    value_type VARCHAR(20) DEFAULT 'string' CHECK (value_type IN ('string', 'integer', 'boolean', 'json')),
    description TEXT,
    
    -- Configurações
    is_secret BOOLEAN DEFAULT false,
    is_required BOOLEAN DEFAULT false,
    default_value TEXT,
    
    -- Auditoria
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    modified_by VARCHAR(100)
);

-- Trigger para timestamp de modificação
CREATE TRIGGER system_config_update_modified_time
    BEFORE UPDATE ON ktr_platform.system_config
    FOR EACH ROW
    EXECUTE FUNCTION ktr_platform.update_modified_column();

-- =============================================================================
-- TABELA: users (básica)
-- =============================================================================

CREATE TABLE IF NOT EXISTS ktr_platform.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    
    -- Perfil
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('admin', 'editor', 'viewer', 'user')),
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE,
    
    -- Auditoria
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT users_username_check CHECK (char_length(username) >= 3),
    CONSTRAINT users_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Trigger para timestamp de modificação
CREATE TRIGGER users_update_modified_time
    BEFORE UPDATE ON ktr_platform.users
    FOR EACH ROW
    EXECUTE FUNCTION ktr_platform.update_modified_column();

-- =============================================================================
-- ÍNDICES PARA PERFORMANCE
-- =============================================================================

-- Flows
CREATE INDEX IF NOT EXISTS idx_flows_status ON ktr_platform.flows(status);
CREATE INDEX IF NOT EXISTS idx_flows_enabled ON ktr_platform.flows(enabled);
CREATE INDEX IF NOT EXISTS idx_flows_tags ON ktr_platform.flows USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_flows_created_at ON ktr_platform.flows(created_at);

-- Schedules
CREATE INDEX IF NOT EXISTS idx_schedules_flow_id ON ktr_platform.schedules(flow_id);
CREATE INDEX IF NOT EXISTS idx_schedules_enabled ON ktr_platform.schedules(enabled);
CREATE INDEX IF NOT EXISTS idx_schedules_next_run ON ktr_platform.schedules(next_run);

-- Execution History
CREATE INDEX IF NOT EXISTS idx_execution_history_flow_id ON ktr_platform.execution_history(flow_id);
CREATE INDEX IF NOT EXISTS idx_execution_history_status ON ktr_platform.execution_history(status);
CREATE INDEX IF NOT EXISTS idx_execution_history_start_time ON ktr_platform.execution_history(start_time);
CREATE INDEX IF NOT EXISTS idx_execution_history_execution_id ON ktr_platform.execution_history(execution_id);

-- System Config
CREATE INDEX IF NOT EXISTS idx_system_config_key ON ktr_platform.system_config(key);

-- Users
CREATE INDEX IF NOT EXISTS idx_users_username ON ktr_platform.users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON ktr_platform.users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON ktr_platform.users(role);

-- =============================================================================
-- DADOS INICIAIS
-- =============================================================================

-- Configurações do sistema
INSERT INTO ktr_platform.system_config (key, value, value_type, description, is_required) VALUES
('app_name', 'KTR Platform', 'string', 'Nome da aplicação', true),
('app_version', '1.0.0', 'string', 'Versão da aplicação', true),
('max_concurrent_flows', '5', 'integer', 'Máximo de fluxos simultâneos', true),
('default_timeout', '3600', 'integer', 'Timeout padrão em segundos', true),
('log_retention_days', '30', 'integer', 'Dias de retenção de logs', true),
('enable_monitoring', 'true', 'boolean', 'Habilitar monitoramento', false),
('enable_notifications', 'false', 'boolean', 'Habilitar notificações', false)
ON CONFLICT (key) DO NOTHING;

-- Usuário administrador padrão (senha: admin123)
INSERT INTO ktr_platform.users (username, email, password_hash, full_name, role) VALUES
('admin', 'admin@ktr-platform.com', crypt('admin123', gen_salt('bf')), 'Administrador', 'admin')
ON CONFLICT (username) DO NOTHING;

-- =============================================================================
-- VIEWS ÚTEIS
-- =============================================================================

-- View para status dos fluxos
CREATE OR REPLACE VIEW ktr_platform.v_flows_status AS
SELECT 
    f.id,
    f.name,
    f.status,
    f.execution_status,
    f.execution_start_time,
    f.execution_duration,
    f.error_message IS NOT NULL as has_error,
    f.enabled,
    COUNT(eh.id) as total_executions,
    COUNT(CASE WHEN eh.status = 'Sucesso' THEN 1 END) as successful_executions,
    COUNT(CASE WHEN eh.status IN ('Falha', 'Erro') THEN 1 END) as failed_executions,
    MAX(eh.end_time) as last_execution,
    f.created_at,
    f.modified_at
FROM ktr_platform.flows f
LEFT JOIN ktr_platform.execution_history eh ON f.id = eh.flow_id
GROUP BY f.id, f.name, f.status, f.execution_status, f.execution_start_time, 
         f.execution_duration, f.error_message, f.enabled, f.created_at, f.modified_at;

-- View para próximas execuções agendadas
CREATE OR REPLACE VIEW ktr_platform.v_upcoming_schedules AS
SELECT 
    s.id as schedule_id,
    f.id as flow_id,
    f.name as flow_name,
    s.name as schedule_name,
    s.cron_expression,
    s.next_run,
    s.enabled,
    s.timezone
FROM ktr_platform.schedules s
JOIN ktr_platform.flows f ON s.flow_id = f.id
WHERE s.enabled = true AND f.enabled = true
ORDER BY s.next_run ASC;

-- =============================================================================
-- PERMISSÕES
-- =============================================================================

-- Garantir que o usuário da aplicação tenha acesso completo
GRANT ALL PRIVILEGES ON SCHEMA ktr_platform TO ktr_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ktr_platform TO ktr_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA ktr_platform TO ktr_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA ktr_platform TO ktr_user;

-- Concluído
SELECT 'KTR Platform database initialized successfully!' as message; 