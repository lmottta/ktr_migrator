import streamlit as st
import os
import shutil
import sys
from pathlib import Path
import tempfile
import time
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
# from streamlit_autorefresh import st_autorefresh  # Removido - usando JavaScript nativo
from loguru import logger
import re

# Adicionar o diretório raiz ao sys.path para importações corretas
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flow_manager import FlowManager, Flow
from executor import FlowExecutor
from scheduler import FlowScheduler
from src.parser.ktr_parser import KTRParser
from src.generator.code_generator import CodeGenerator
from src.analyzer.pipeline_analyzer import PipelineAnalyzer

# --- Configuração da Página ---
st.set_page_config(
    page_title="KTR Platform Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS para deixar mais bonito
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    .flow-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-card { border-left: 5px solid #28a745; }
    .error-card { border-left: 5px solid #dc3545; }
    .running-card { border-left: 5px solid #ffc107; }
    .ready-card { border-left: 5px solid #007bff; }
</style>
""", unsafe_allow_html=True)

# --- Gerenciamento de Estado ---
if 'flow_manager' not in st.session_state:
    st.session_state.flow_manager = FlowManager()
if 'executor' not in st.session_state:
    st.session_state.executor = FlowExecutor(st.session_state.flow_manager)
if 'scheduler' not in st.session_state:
    st.session_state.scheduler = FlowScheduler(st.session_state.flow_manager, st.session_state.executor)
    st.session_state.scheduler.start()  # Iniciar o scheduler automaticamente
if 'view' not in st.session_state:
    st.session_state.view = 'dashboard'
if 'ktr_model' not in st.session_state:
    st.session_state.ktr_model = None
if 'selected_flow_id' not in st.session_state:
    st.session_state.selected_flow_id = None
if 'selected_flows' not in st.session_state:
    st.session_state.selected_flows = []
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False

# Acessar os gerenciadores
flow_manager = st.session_state.flow_manager
executor = st.session_state.executor
scheduler = st.session_state.scheduler

def change_view(view_name, flow_id=None):
    """Muda a visualização atual."""
    st.session_state.view = view_name
    st.session_state.selected_flow_id = flow_id
    if view_name == 'dashboard':
        st.session_state.ktr_model = None

# --- Sidebar de Navegação ---
with st.sidebar:
    st.markdown("### 🎛️ Painel de Controle")
    
    if st.button("🏠 Dashboard", use_container_width=True):
        change_view('dashboard')
        st.rerun()
    
    if st.button("➕ Importar Fluxo", use_container_width=True):
        change_view('import_flow')
        st.rerun()
    
    if st.button("⏰ Agendamentos", use_container_width=True):
        change_view('schedules')
        st.rerun()
    
    st.markdown("---")
    
    # Controles de Sistema
    st.markdown("### ⚙️ Sistema")
    
    if st.button("🔄 Atualizar Agora", use_container_width=True):
        st.rerun()
    
    # Próximos agendamentos
    st.markdown("### ⏰ Próximas Execuções")
    
    next_runs = scheduler.get_next_runs(3)
    if next_runs:
        for run in next_runs:
            st.text(f"🔹 {run['flow_name']}")
            st.caption(f"   {run['next_run_str']}")
    else:
        st.info("Nenhum agendamento ativo")

# --- Funções de UI ---

def show_global_header():
    """Header global com métricas principais visível em todas as páginas."""
    all_flows = flow_manager.get_all_flows()
    all_schedules = scheduler.get_all_schedules()
    
    total_flows = len(all_flows)
    running_flows = len([f for f in all_flows if executor.is_flow_running(f.id)])
    successful_flows = len([f for f in all_flows if f.execution_status == "Sucesso"])
    failed_flows = len([f for f in all_flows if f.execution_status in ["Falha", "Erro"]])
    total_schedules = len(all_schedules)
    scheduler_status = "🟢 Ativo" if scheduler.running else "🔴 Parado"
    
    st.markdown("""
    <div style="
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
            <h2 style="margin: 0; color: white;">🚀 KTR Platform Pro - Status Global</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas em colunas
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("📁 Total de Fluxos", total_flows)
    with col2:
        st.metric("⚡ Em Execução", running_flows, delta=f"+{running_flows}" if running_flows > 0 else None)
    with col3:
        st.metric("✅ Sucessos", successful_flows)
    with col4:
        st.metric("❌ Falhas", failed_flows, delta=f"+{failed_flows}" if failed_flows > 0 else None)
    with col5:
        st.metric("⏰ Agendamentos", total_schedules)
    with col6:
        st.metric("🤖 Scheduler", scheduler_status)
    
    st.markdown("---")

def show_dashboard():
    """Dashboard principal melhorado."""
    
    # Header global com métricas
    show_global_header()
    
    all_flows = flow_manager.get_all_flows()
    running_flows = len([f for f in all_flows if executor.is_flow_running(f.id)])
    
    # Banner de execução em tempo real
    if running_flows > 0:
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #ff6b35 0%, #f7931e 100%); padding: 1rem; border-radius: 10px; margin: 1rem 0; text-align: center; color: white; animation: pulse 2s infinite;">
            🔄 <strong>EXECUÇÃO EM TEMPO REAL</strong> - {running_flows} fluxo(s) executando
            <br><small>Monitore o progresso clicando no botão "📊 Monitorar" de cada fluxo</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Controles avançados
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    
    with col1:
        search_term = st.text_input("🔍 Buscar fluxos", placeholder="Digite o nome do fluxo...")
    
    with col2:
        status_filter = st.selectbox("📋 Filtrar por status", 
                                   ["Todos", "Pronto", "Executando", "Sucesso", "Falha", "Importando"])
    
    with col3:
        view_mode = st.radio("👁️ Visualização", ["Cards", "Tabela"], horizontal=True)
    
    with col4:
        if st.button("🔄 Atualizar", type="secondary"):
            st.rerun()
    
    # Execução em lote
    if all_flows:
        st.markdown("### 🚀 Execução em Lote")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            available_flows = [f for f in all_flows if f.status == "Pronto" and not executor.is_flow_running(f.id)]
            if available_flows:
                selected_for_batch = st.multiselect(
                    "Selecionar fluxos para execução em lote:",
                    options=[f.id for f in available_flows],
                    format_func=lambda x: next(f.name for f in available_flows if f.id == x)
                )
        
        with col2:
            if st.button("▶️ Executar Selecionados", type="primary", disabled=not selected_for_batch if 'selected_for_batch' in locals() else True):
                for flow_id in selected_for_batch:
                    executor.execute_flow(flow_id)
                st.success(f"🚀 {len(selected_for_batch)} fluxos iniciados!")
                st.rerun()
    
    st.markdown("---")
    
    # Filtrar fluxos
    filtered_flows = all_flows
    
    if search_term:
        filtered_flows = [f for f in filtered_flows if search_term.lower() in f.name.lower()]
    
    if status_filter != "Todos":
        if status_filter == "Executando":
            filtered_flows = [f for f in filtered_flows if executor.is_flow_running(f.id)]
        else:
            filtered_flows = [f for f in filtered_flows if f.execution_status == status_filter]
    
    if not filtered_flows:
        st.info("Nenhum fluxo encontrado com os filtros aplicados.")
        return
    
    # Exibir fluxos
    if view_mode == "Cards":
        show_flows_as_cards(filtered_flows)
    else:
        show_flows_as_table(filtered_flows)
    
    # Auto-refresh para fluxos em execução
    if any(executor.is_flow_running(flow.id) for flow in all_flows):
        # Auto-refresh implementado via JavaScript nativo no sistema de tempo real
        pass  # Mantém a estrutura do if


def show_flows_as_cards(flows):
    """Exibe fluxos como cards visuais."""
    st.markdown("### 📋 Meus Fluxos")
    
    # Organizar em colunas
    cols_per_row = 2
    for i in range(0, len(flows), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, flow in enumerate(flows[i:i + cols_per_row]):
            with cols[j]:
                # Determinar classe CSS baseada no status
                is_running = executor.is_flow_running(flow.id)
                
                if is_running:
                    card_class = "running-card"
                    status_emoji = "⏳"
                elif flow.execution_status == "Sucesso":
                    card_class = "success-card"
                    status_emoji = "✅"
                elif flow.execution_status in ["Falha", "Erro"]:
                    card_class = "error-card"
                    status_emoji = "❌"
                else:
                    card_class = "ready-card"
                    status_emoji = "📄"
                
                st.markdown(f"""
                <div class="flow-card {card_class}">
                    <h4>{status_emoji} {flow.name}</h4>
                    <p><strong>Status:</strong> {flow.execution_status}</p>
                    <p><strong>Última execução:</strong> {flow.last_run_at.split('T')[0] if flow.last_run_at else 'Nunca'}</p>
                    <p><strong>Duração:</strong> {f"{flow.execution_duration:.1f}s" if flow.execution_duration else "-"}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Botões de ação
                cols_actions = st.columns(5)
                
                with cols_actions[0]:
                    if is_running:
                        if st.button("⏹️", key=f"stop_card_{flow.id}", help="Parar"):
                            executor.stop_flow(flow.id)
                            st.rerun()
                    else:
                        can_execute = flow.status == "Pronto"
                        if st.button("▶️", key=f"run_card_{flow.id}", disabled=not can_execute, help="Executar"):
                            executor.execute_flow(flow.id)
                            st.rerun()
                
                with cols_actions[1]:
                    if st.button("📝", key=f"edit_card_{flow.id}", help="Editar Código"):
                        change_view('edit_code', flow.id)
                        st.rerun()
                
                with cols_actions[2]:
                    if st.button("📊", key=f"monitor_card_{flow.id}", help="Monitorar"):
                        change_view('monitor', flow.id)
                        st.rerun()
                
                with cols_actions[3]:
                    if st.button("✏️", key=f"rename_card_{flow.id}", help="Renomear"):
                        change_view('rename', flow.id)
                        st.rerun()
                
                with cols_actions[4]:
                    if st.button("🗑️", key=f"delete_card_{flow.id}", help="Excluir"):
                        change_view('delete', flow.id)
                        st.rerun()


def show_flows_as_table(flows):
    """Exibe fluxos como tabela avançada."""
    st.markdown("### 📋 Meus Fluxos")
    
    # Preparar dados para a tabela
    table_data = []
    for flow in flows:
        is_running = executor.is_flow_running(flow.id)
        table_data.append({
            'Nome': flow.name,
            'Status Importação': flow.status,
            'Status Execução': flow.execution_status,
            'Última Execução': flow.last_run_at.split('T')[0] if flow.last_run_at else '-',
            'Duração (s)': f"{flow.execution_duration:.1f}" if flow.execution_duration else '-',
            'Em Execução': '▶️' if is_running else '-',
            'ID': flow.id
        })
    
    if table_data:
        df = pd.DataFrame(table_data)
        
        # Tabela interativa
        selected_rows = st.dataframe(
            df[['Nome', 'Status Importação', 'Status Execução', 'Última Execução', 'Duração (s)', 'Em Execução']],
            use_container_width=True,
            hide_index=True
        )
        
        # Ações rápidas na tabela
        st.markdown("**Ações Rápidas:**")
        cols = st.columns(6)
        
        with cols[0]:
            if st.button("▶️ Executar Todos Prontos"):
                ready_flows = [f for f in flows if f.status == "Pronto" and not executor.is_flow_running(f.id)]
                for flow in ready_flows:
                    executor.execute_flow(flow.id)
                st.success(f"🚀 {len(ready_flows)} fluxos iniciados!")
                st.rerun()
        
        with cols[1]:
            if st.button("⏹️ Parar Todos"):
                running_flows = [f for f in flows if executor.is_flow_running(f.id)]
                for flow in running_flows:
                    executor.stop_flow(flow.id)
                st.success(f"⏹️ {len(running_flows)} fluxos parados!")
                st.rerun()


def show_detailed_ktr_analysis(ktr_model):
    """Mostra análise detalhada do fluxo KTR estilo n8n."""
    st.markdown("---")
    st.subheader("🔍 Análise Detalhada do Fluxo KTR - Visão n8n")
    
    with st.spinner("🔍 Executando análise avançada..."):
        try:
            # Usar o PipelineAnalyzer para análise completa
            analyzer = PipelineAnalyzer()
            analysis_result = analyzer.analyze_pipeline(ktr_model)
            
            # Header com informações gerais
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("🎯 Complexidade", analysis_result.complexity_score, 
                         delta="Alta" if analysis_result.complexity_score > 7 else "Média" if analysis_result.complexity_score > 4 else "Baixa")
            with col2:
                st.metric("⚡ Performance", f"{analysis_result.estimated_performance_gain}%")
            with col3:
                st.metric("🔍 Padrões", len(analysis_result.patterns))
            with col4:
                st.metric("💡 Otimizações", len(analysis_result.optimizations))
            with col5:
                st.metric("🔗 Conexões", analysis_result.metrics.get("total_hops", 0))

            # Tabs para diferentes visualizações
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🎯 Visão Geral", 
                "📊 Nodes Detalhados", 
                "🔗 Fluxo de Dados", 
                "📈 Métricas", 
                "💡 Otimizações"
            ])
            
            with tab1:
                show_flow_overview(ktr_model, analysis_result)
            
            with tab2:
                show_detailed_nodes(ktr_model)
            
            with tab3:
                show_data_flow(ktr_model, analysis_result)
            
            with tab4:
                show_detailed_metrics(analysis_result)
            
            with tab5:
                show_optimization_recommendations(analysis_result)
                
        except Exception as e:
            st.error(f"❌ Erro na análise detalhada: {e}")
            logger.error(f"Erro na análise detalhada: {e}")


def show_flow_overview(ktr_model, analysis_result):
    """Mostra visão geral do fluxo"""
    
    # Mapa visual do fluxo
    st.markdown("### 🗺️ Mapeamento Visual do Pipeline")
    
    input_steps = [step for step in ktr_model.steps if step.is_input]
    transform_steps = [step for step in ktr_model.steps if step.is_transform]
    output_steps = [step for step in ktr_model.steps if step.is_output]
    
    # Layout visual estilo flowchart
    col1, col2, col3 = st.columns([2, 3, 2])
    
    with col1:
        st.markdown("#### 📥 **ENTRADA**")
        for i, step in enumerate(input_steps):
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 0.8rem;
                border-radius: 8px;
                margin: 0.5rem 0;
                color: white;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <strong>{step.name}</strong><br>
                <small>{step.type.value}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 🔄 **TRANSFORMAÇÃO**")
        if transform_steps:
            for i, step in enumerate(transform_steps):
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    padding: 0.8rem;
                    border-radius: 8px;
                    margin: 0.5rem 0;
                    color: white;
                    text-align: center;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <strong>{step.name}</strong><br>
                    <small>{step.type.value}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhuma transformação intermediária")
    
    with col3:
        st.markdown("#### 📤 **SAÍDA**")
        for i, step in enumerate(output_steps):
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                padding: 0.8rem;
                border-radius: 8px;
                margin: 0.5rem 0;
                color: white;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <strong>{step.name}</strong><br>
                <small>{step.type.value}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Resumo estatístico
    st.markdown("---")
    st.markdown("### 📊 Resumo Estatístico")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total de Steps", len(ktr_model.steps))
    with col2:
        st.metric("🔗 Conexões", len(ktr_model.hops))
    with col3:
        st.metric("💾 Fontes de Dados", len(input_steps))
    with col4:
        st.metric("🎯 Destinos", len(output_steps))


def show_detailed_nodes(ktr_model):
    """Mostra detalhes de cada node estilo n8n"""
    st.markdown("### 🎛️ Análise Detalhada de Cada Node")
    st.markdown("*Clique em um node para ver detalhes completos*")
    
    for i, step in enumerate(ktr_model.steps):
        # Card expansível para cada step
        step_color = get_step_color(step)
        step_icon = get_step_icon(step)
        
        with st.expander(f"{step_icon} **{step.name}** - {step.type.value}", expanded=False):
            
            # Header do node
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"**🏷️ Tipo:** {step.type.value}")
                st.markdown(f"**📝 Descrição:** {step.description or 'Sem descrição'}")
            
            with col2:
                st.markdown(f"**🔖 Categoria:** {get_step_category(step)}")
                st.markdown(f"**⚡ Complexidade:** {get_step_complexity(step)}")
            
            with col3:
                st.markdown(f"""
                <div style="
                    background: {step_color};
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 24px;
                    color: white;
                    margin: auto;
                ">
                    {step_icon}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Tabs para diferentes aspectos do node
            tab1, tab2, tab3, tab4 = st.tabs(["⚙️ Configuração", "📊 Dados", "🔗 Conexões", "🚀 Performance"])
            
            with tab1:
                show_step_configuration(step)
            
            with tab2:
                show_step_data_details(step)
            
            with tab3:
                show_step_connections(step, ktr_model)
            
            with tab4:
                show_step_performance(step)


def show_step_configuration(step):
    """Mostra configuração detalhada do step"""
    st.markdown("#### ⚙️ Configuração do Node")
    
    if hasattr(step, 'config') and step.config:
        config_data = []
        for key, value in step.config.items():
            config_data.append({"Parâmetro": key, "Valor": str(value)})
        
        if config_data:
            df_config = pd.DataFrame(config_data)
            st.dataframe(df_config, use_container_width=True)
        else:
            st.info("Nenhuma configuração específica encontrada")
    else:
        st.info("Configuração padrão")
    
    # Configurações específicas por tipo
    if step.type.value == "TableInput":
        show_table_input_config(step)
    elif step.type.value == "TableOutput":
        show_table_output_config(step)
    elif step.type.value == "ExcelInput":
        show_excel_input_config(step)
    elif step.type.value == "StringOperations":
        show_string_operations_config(step)


def show_table_input_config(step):
    """Configuração específica para TableInput"""
    st.markdown("##### 📊 Configuração de Entrada de Tabela")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**🔗 Conexão:** {getattr(step, 'connection_name', 'Não definida')}")
        st.markdown(f"**📋 Tabela/Query:** {getattr(step, 'sql', 'Não definida')}")
    with col2:
        st.markdown(f"**📊 Limite:** {getattr(step, 'limit', 'Sem limite')}")
        st.markdown(f"**🔄 Lazy Conversion:** {'Sim' if getattr(step, 'lazy_conversion', False) else 'Não'}")


def show_table_output_config(step):
    """Configuração específica para TableOutput"""
    st.markdown("##### 💾 Configuração de Saída de Tabela")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**🔗 Conexão:** {getattr(step, 'connection_name', 'Não definida')}")
        st.markdown(f"**📊 Schema:** {getattr(step, 'schema', 'Padrão')}")
        st.markdown(f"**📋 Tabela:** {getattr(step, 'table', 'Não definida')}")
    with col2:
        st.markdown(f"**🗑️ Truncar:** {'Sim' if getattr(step, 'truncate', False) else 'Não'}")
        st.markdown(f"**📦 Commit Size:** {getattr(step, 'commit_size', 1000)}")


def show_excel_input_config(step):
    """Configuração específica para ExcelInput"""
    st.markdown("##### 📈 Configuração de Entrada Excel")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**📁 Arquivo:** {getattr(step, 'file_path', 'Não definido')}")
        st.markdown(f"**📄 Planilha:** {getattr(step, 'sheet_name', 'Primeira')}")
    with col2:
        st.markdown(f"**📋 Header:** {'Sim' if getattr(step, 'header', True) else 'Não'}")
        st.markdown(f"**📍 Linha Inicial:** {getattr(step, 'start_row', 0)}")


def show_string_operations_config(step):
    """Configuração específica para StringOperations"""
    st.markdown("##### 🔤 Operações de String")
    
    operations = getattr(step, 'operations', [])
    if operations:
        for i, op in enumerate(operations):
            st.markdown(f"**Operação {i+1}:** {op.get('operation_type', 'Não definida')}")
            st.markdown(f"**Campo:** {op.get('field_name', 'Não definido')}")
    else:
        st.info("Nenhuma operação específica configurada")


def show_step_data_details(step):
    """Mostra detalhes dos dados do step"""
    st.markdown("#### 📊 Estrutura de Dados")
    
    # Campos esperados (se disponível)
    if hasattr(step, 'fields') and step.fields:
        st.markdown("##### 📋 Campos Definidos")
        fields_data = []
        for field in step.fields:
            fields_data.append({
                "Campo": field.name,
                "Tipo": field.type,
                "Tamanho": field.length if field.length > 0 else "Variável",
                "Precisão": field.precision if field.precision > 0 else "N/A",
                "Formato": field.format or "Padrão"
            })
        
        df_fields = pd.DataFrame(fields_data)
        st.dataframe(df_fields, use_container_width=True)
    else:
        st.info("Estrutura de campos será determinada em tempo de execução")
    
    # Estimativas de volume
    st.markdown("##### 📈 Estimativas de Volume")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Registros Estimados", get_estimated_records(step))
    with col2:
        st.metric("💾 Tamanho Estimado", get_estimated_size(step))
    with col3:
        st.metric("⏱️ Tempo Estimado", get_estimated_time(step))


def show_step_connections(step, ktr_model):
    """Mostra conexões do step"""
    st.markdown("#### 🔗 Conectividade do Node")
    
    # Entrada (steps que conectam a este)
    incoming = [hop for hop in ktr_model.hops if hop.to_step == step.name]
    # Saída (steps para onde este conecta)
    outgoing = [hop for hop in ktr_model.hops if hop.from_step == step.name]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### ⬅️ Entradas")
        if incoming:
            for hop in incoming:
                st.markdown(f"• **{hop.from_step}** → {step.name}")
                if not hop.enabled:
                    st.caption("  ⚠️ Conexão desabilitada")
        else:
            st.info("Nenhuma entrada (step inicial)")
    
    with col2:
        st.markdown("##### ➡️ Saídas")
        if outgoing:
            for hop in outgoing:
                st.markdown(f"• {step.name} → **{hop.to_step}**")
                if not hop.enabled:
                    st.caption("  ⚠️ Conexão desabilitada")
        else:
            st.info("Nenhuma saída (step final)")
    
    # Posição no fluxo
    st.markdown("##### 🎯 Posição no Pipeline")
    position = "Início" if not incoming else "Fim" if not outgoing else "Intermediário"
    depth = calculate_step_depth(step, ktr_model)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📍 Posição", position)
    with col2:
        st.metric("📏 Profundidade", depth)


def show_step_performance(step):
    """Mostra informações de performance do step"""
    st.markdown("#### 🚀 Análise de Performance")
    
    # Métricas estimadas de performance
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("⚡ Velocidade", get_step_speed_rating(step))
        st.metric("🧠 Uso de Memória", get_memory_usage_rating(step))
    
    with col2:
        st.metric("💾 Uso de CPU", get_cpu_usage_rating(step))
        st.metric("🌐 Uso de Rede", get_network_usage_rating(step))
    
    with col3:
        st.metric("💿 Uso de I/O", get_io_usage_rating(step))
        st.metric("🔧 Complexidade", get_step_complexity(step))
    
    # Sugestões específicas
    st.markdown("##### 💡 Sugestões de Otimização")
    suggestions = get_step_optimization_suggestions(step)
    if suggestions:
        for suggestion in suggestions:
            st.info(f"💡 {suggestion}")
    else:
        st.success("✅ Step otimizado adequadamente")


def show_data_flow(ktr_model, analysis_result):
    """Mostra fluxo de dados detalhado"""
    st.markdown("### 🔗 Análise do Fluxo de Dados")
    
    # Grafo visual do pipeline
    st.markdown("#### 📊 Mapeamento de Dependências")
    
    # Criar visualização com Plotly
    fig = create_flow_diagram(ktr_model)
    st.plotly_chart(fig, use_container_width=True)
    
    # Análise de caminhos críticos
    st.markdown("#### 🎯 Caminhos Críticos")
    critical_paths = find_critical_paths(ktr_model)
    
    if critical_paths:
        for i, path in enumerate(critical_paths):
            st.markdown(f"**Caminho {i+1}:** {' → '.join(path)}")
    else:
        st.info("Pipeline linear - sem caminhos paralelos")
    
    # Pontos de gargalo
    st.markdown("#### 🚨 Análise de Gargalos")
    bottlenecks = find_bottlenecks(ktr_model)
    
    if bottlenecks:
        for bottleneck in bottlenecks:
            st.warning(f"⚠️ Possível gargalo: **{bottleneck['step']}** - {bottleneck['reason']}")
    else:
        st.success("✅ Nenhum gargalo crítico identificado")


def show_detailed_metrics(analysis_result):
    """Mostra métricas detalhadas"""
    st.markdown("### 📈 Métricas Avançadas")
    
    metrics = analysis_result.metrics
    
    # Métricas em grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Steps", metrics.get("total_steps", 0))
        st.metric("📥 Steps Entrada", metrics.get("input_steps", 0))
    
    with col2:
        st.metric("🔄 Steps Transformação", metrics.get("transform_steps", 0))
        st.metric("📤 Steps Saída", metrics.get("output_steps", 0))
    
    with col3:
        st.metric("🔗 Conexões", metrics.get("total_connections", 0))
        st.metric("🔀 Hops", metrics.get("total_hops", 0))
    
    with col4:
        st.metric("📏 Profundidade", metrics.get("graph_depth", 0))
        st.metric("📐 Largura", metrics.get("graph_width", 0))
    
    # Gráficos de análise
    if metrics:
        col1, col2 = st.columns(2)
        
        with col1:
            try:
                # Distribuição por tipo
                step_type_names = ["Entrada", "Transformação", "Saída"]
                step_type_values = [
                    metrics.get("input_steps", 0),
                    metrics.get("transform_steps", 0),
                    metrics.get("output_steps", 0)
                ]
                
                # Verificar se há dados válidos
                if sum(step_type_values) > 0:
                    fig_pie = px.pie(
                        values=step_type_values,
                        names=step_type_names,
                        title="Distribuição de Steps por Tipo"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("📊 Nenhum step encontrado para análise")
            except Exception as e:
                st.error(f"❌ Erro no gráfico de distribuição: {str(e)}")
        
        with col2:
            try:
                # Complexidade vs Performance
                complexity_score = getattr(analysis_result, 'complexity_score', 0)
                performance_gain = getattr(analysis_result, 'estimated_performance_gain', 0)
                optimizations_count = len(getattr(analysis_result, 'optimizations', []))
                
                metrics_names = ["Complexidade", "Performance", "Otimizações"]
                metrics_values = [complexity_score, performance_gain, optimizations_count]
                
                # Verificar se temos dados válidos e arrays do mesmo tamanho
                if len(metrics_names) == len(metrics_values) and any(v > 0 for v in metrics_values):
                    fig_bar = px.bar(
                        x=metrics_names,
                        y=metrics_values,
                        title="Métricas de Análise"
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("📈 Dados insuficientes para gráfico de métricas")
            except Exception as e:
                st.error(f"❌ Erro no gráfico de métricas: {str(e)}")
    else:
        st.warning("📊 Métricas não disponíveis")


def show_optimization_recommendations(analysis_result):
    """Mostra recomendações de otimização"""
    st.markdown("### 💡 Recomendações de Otimização")
    
    if not analysis_result.optimizations:
        st.success("🎉 Pipeline já está bem otimizado!")
        return
    
    # Agrupar por impacto
    high_impact = [opt for opt in analysis_result.optimizations if opt.impact == "high"]
    medium_impact = [opt for opt in analysis_result.optimizations if opt.impact == "medium"]
    low_impact = [opt for opt in analysis_result.optimizations if opt.impact == "low"]
    
    if high_impact:
        st.markdown("#### 🔴 Alto Impacto (Prioridade)")
        for opt in high_impact:
            with st.expander(f"🔴 {opt.type} - {opt.description[:50]}..."):
                st.markdown(opt.description)
                if opt.code_example:
                    st.code(opt.code_example, language="python")
    
    if medium_impact:
        st.markdown("#### 🟡 Médio Impacto")
        for opt in medium_impact:
            with st.expander(f"🟡 {opt.type} - {opt.description[:50]}..."):
                st.markdown(opt.description)
                if opt.code_example:
                    st.code(opt.code_example, language="python")
    
    if low_impact:
        st.markdown("#### 🟢 Baixo Impacto")
        for opt in low_impact:
            with st.expander(f"🟢 {opt.type} - {opt.description[:50]}..."):
                st.markdown(opt.description)
                if opt.code_example:
                    st.code(opt.code_example, language="python")


# Funções auxiliares para análise detalhada

def get_step_color(step):
    """Retorna cor para o step baseada no tipo"""
    color_map = {
        "TableInput": "#667eea",
        "ExcelInput": "#667eea", 
        "TextFileInput": "#667eea",
        "TableOutput": "#4facfe",
        "ExcelOutput": "#4facfe",
        "TextFileOutput": "#4facfe",
        "StringOperations": "#f093fb",
        "FilterRows": "#f093fb",
        "ValueMapper": "#f093fb",
        "Calculator": "#f093fb",
        "SortRows": "#f093fb",
        "GroupBy": "#f093fb",
        "SelectValues": "#f093fb"
    }
    return color_map.get(step.type.value, "#9ca3af")


def get_step_icon(step):
    """Retorna ícone para o step"""
    icon_map = {
        "TableInput": "📊",
        "ExcelInput": "📈",
        "TextFileInput": "📄",
        "TableOutput": "💾",
        "ExcelOutput": "📊",
        "TextFileOutput": "📁",
        "StringOperations": "🔤",
        "FilterRows": "🔍",
        "ValueMapper": "🗺️",
        "Calculator": "🧮",
        "SortRows": "📊",
        "GroupBy": "📋",
        "SelectValues": "✅"
    }
    return icon_map.get(step.type.value, "⚙️")


def get_step_category(step):
    """Retorna categoria do step"""
    if step.is_input:
        return "Entrada de Dados"
    elif step.is_output:
        return "Saída de Dados"
    else:
        return "Transformação"


def get_step_complexity(step):
    """Calcula complexidade do step"""
    complexity_map = {
        "TableInput": "Baixa",
        "ExcelInput": "Baixa",
        "TextFileInput": "Baixa",
        "TableOutput": "Baixa",
        "ExcelOutput": "Baixa", 
        "TextFileOutput": "Baixa",
        "StringOperations": "Média",
        "FilterRows": "Baixa",
        "ValueMapper": "Média",
        "Calculator": "Média",
        "SortRows": "Média",
        "GroupBy": "Alta",
        "SelectValues": "Baixa"
    }
    return complexity_map.get(step.type.value, "Média")


def get_estimated_records(step):
    """Estima número de registros"""
    if step.is_input:
        return "10K - 100K"
    elif step.is_transform:
        return "Variável"
    else:
        return "Conforme entrada"


def get_estimated_size(step):
    """Estima tamanho dos dados"""
    if step.is_input:
        return "1-10 MB"
    else:
        return "Conforme entrada"


def get_estimated_time(step):
    """Estima tempo de execução"""
    time_map = {
        "TableInput": "1-5s",
        "ExcelInput": "2-10s",
        "TextFileInput": "1-5s",
        "TableOutput": "2-10s",
        "ExcelOutput": "5-15s",
        "TextFileOutput": "1-5s",
        "StringOperations": "< 1s",
        "FilterRows": "< 1s",
        "ValueMapper": "< 1s",
        "Calculator": "< 1s",
        "SortRows": "1-5s",
        "GroupBy": "2-10s",
        "SelectValues": "< 1s"
    }
    return time_map.get(step.type.value, "1-5s")


def calculate_step_depth(step, ktr_model):
    """Calcula profundidade do step no pipeline"""
    def get_depth(step_name, visited=None):
        if visited is None:
            visited = set()
        
        if step_name in visited:
            return 0  # Evitar loops
        
        visited.add(step_name)
        
        incoming = [hop for hop in ktr_model.hops if hop.to_step == step_name]
        if not incoming:
            return 0
        
        max_depth = 0
        for hop in incoming:
            depth = get_depth(hop.from_step, visited.copy())
            max_depth = max(max_depth, depth + 1)
        
        return max_depth
    
    return get_depth(step.name)


def get_step_speed_rating(step):
    """Rating de velocidade do step"""
    speed_map = {
        "TableInput": "Rápido",
        "ExcelInput": "Médio",
        "TextFileInput": "Rápido",
        "TableOutput": "Médio",
        "ExcelOutput": "Lento",
        "TextFileOutput": "Rápido",
        "StringOperations": "Muito Rápido",
        "FilterRows": "Muito Rápido",
        "ValueMapper": "Rápido",
        "Calculator": "Rápido",
        "SortRows": "Médio",
        "GroupBy": "Lento",
        "SelectValues": "Muito Rápido"
    }
    return speed_map.get(step.type.value, "Médio")


def get_memory_usage_rating(step):
    """Rating de uso de memória"""
    memory_map = {
        "TableInput": "Baixo",
        "ExcelInput": "Médio",
        "TextFileInput": "Baixo",
        "TableOutput": "Baixo",
        "ExcelOutput": "Médio",
        "TextFileOutput": "Baixo",
        "StringOperations": "Baixo",
        "FilterRows": "Baixo",
        "ValueMapper": "Baixo",
        "Calculator": "Baixo",
        "SortRows": "Alto",
        "GroupBy": "Alto",
        "SelectValues": "Baixo"
    }
    return memory_map.get(step.type.value, "Médio")


def get_cpu_usage_rating(step):
    """Rating de uso de CPU"""
    cpu_map = {
        "TableInput": "Baixo",
        "ExcelInput": "Médio",
        "TextFileInput": "Baixo",
        "TableOutput": "Baixo",
        "ExcelOutput": "Médio",
        "TextFileOutput": "Baixo",
        "StringOperations": "Médio",
        "FilterRows": "Baixo",
        "ValueMapper": "Baixo",
        "Calculator": "Médio",
        "SortRows": "Alto",
        "GroupBy": "Alto",
        "SelectValues": "Baixo"
    }
    return cpu_map.get(step.type.value, "Médio")


def get_network_usage_rating(step):
    """Rating de uso de rede"""
    if step.is_input or step.is_output:
        return "Médio"
    return "Nenhum"


def get_io_usage_rating(step):
    """Rating de uso de I/O"""
    io_map = {
        "TableInput": "Alto",
        "ExcelInput": "Alto",
        "TextFileInput": "Alto",
        "TableOutput": "Alto",
        "ExcelOutput": "Alto",
        "TextFileOutput": "Alto",
        "StringOperations": "Baixo",
        "FilterRows": "Baixo",
        "ValueMapper": "Baixo",
        "Calculator": "Baixo",
        "SortRows": "Médio",
        "GroupBy": "Médio",
        "SelectValues": "Baixo"
    }
    return io_map.get(step.type.value, "Médio")


def get_step_optimization_suggestions(step):
    """Sugestões específicas para o step"""
    suggestions_map = {
        "TableInput": [
            "Use LIMIT para testes",
            "Considere índices na tabela source",
            "Avalie usar WHERE para filtrar na origem"
        ],
        "ExcelInput": [
            "Converta para CSV se possível",
            "Use apenas as colunas necessárias",
            "Considere dividir arquivos grandes"
        ],
        "TableOutput": [
            "Use batch inserts",
            "Desabilite índices durante carga",
            "Use TRUNCATE ao invés de DELETE"
        ],
        "SortRows": [
            "Considere fazer sort no banco",
            "Verifique se realmente precisa ordenar",
            "Use apenas campos necessários"
        ],
        "GroupBy": [
            "Agrupe no banco se possível",
            "Use apenas agregações necessárias",
            "Considere pré-filtrar dados"
        ]
    }
    return suggestions_map.get(step.type.value, [])


def create_flow_diagram(ktr_model):
    """Cria diagrama visual do fluxo"""
    import plotly.graph_objects as go
    try:
        import networkx as nx
    except ImportError:
        # Fallback para quando networkx não estiver disponível
        fig = go.Figure()
        fig.add_annotation(
            text="📊 Visualização de grafo requer networkx<br>Execute: pip install networkx",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Criar grafo
    G = nx.DiGraph()
    
    # Adicionar nós
    for step in ktr_model.steps:
        G.add_node(step.name, type=step.type.value)
    
    # Adicionar arestas
    for hop in ktr_model.hops:
        if hop.enabled:
            G.add_edge(hop.from_step, hop.to_step)
    
    # Layout hierárquico
    try:
        pos = nx.spring_layout(G, k=2, iterations=50)
    except:
        pos = {node: (i, 0) for i, node in enumerate(G.nodes())}
    
    # Criar traces para edges
    edge_x = []
    edge_y = []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Criar traces para nodes
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        
        # Cor baseada no tipo
        step = next(s for s in ktr_model.steps if s.name == node)
        if step.is_input:
            node_color.append('#667eea')
        elif step.is_output:
            node_color.append('#4facfe')
        else:
            node_color.append('#f093fb')
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition="middle center",
        marker=dict(
            size=50,
            color=node_color,
            line=dict(width=2, color='white')
        )
    )
    
    # Criar figura
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=dict(text='Fluxo de Dados do Pipeline', font=dict(size=16)),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="Direção do fluxo de dados",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor="left", yanchor="bottom",
                font=dict(color="#000000", size=12)
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
    )
    
    return fig


def find_critical_paths(ktr_model):
    """Encontra caminhos críticos no pipeline"""
    try:
        import networkx as nx
    except ImportError:
        return []
    
    G = nx.DiGraph()
    
    for step in ktr_model.steps:
        G.add_node(step.name)
    
    for hop in ktr_model.hops:
        if hop.enabled:
            G.add_edge(hop.from_step, hop.to_step)
    
    # Encontrar todos os caminhos simples
    start_nodes = [n for n in G.nodes() if G.in_degree(n) == 0]
    end_nodes = [n for n in G.nodes() if G.out_degree(n) == 0]
    
    paths = []
    for start in start_nodes:
        for end in end_nodes:
            try:
                for path in nx.all_simple_paths(G, start, end):
                    paths.append(path)
            except:
                pass
    
    return paths


def find_bottlenecks(ktr_model):
    """Identifica possíveis gargalos"""
    bottlenecks = []
    
    for step in ktr_model.steps:
        # Steps com múltiplas entradas podem ser gargalos
        incoming = [hop for hop in ktr_model.hops if hop.to_step == step.name]
        if len(incoming) > 1:
            bottlenecks.append({
                "step": step.name,
                "reason": f"Recebe dados de {len(incoming)} fontes diferentes"
            })
        
        # Steps de alta complexidade
        if step.type.value in ["GroupBy", "SortRows"]:
            bottlenecks.append({
                "step": step.name,
                "reason": f"Operação de alta complexidade: {step.type.value}"
            })
    
    return bottlenecks


def get_step_explanation(step) -> str:
    """Gera explicação detalhada para uma etapa específica."""
    
    # Mapeamento detalhado de explicações por tipo
    detailed_explanations = {
        "TableInput": {
            "description": "📊 **Entrada de Tabela SQL**",
            "details": [
                "• Extrai dados diretamente de tabelas no banco de dados",
                "• Suporta queries SQL complexas com WHERE, JOIN, GROUP BY",
                "• Permite controle de limite de registros para testes",
                "• Otimizado para grandes volumes de dados",
                "• Mantém tipos de dados originais (inteiros, decimais, datas)"
            ],
            "use_cases": [
                "Extração de dados transacionais",
                "Consultas a dimensões e fatos",
                "Leitura de tabelas de configuração"
            ],
            "performance": "Alta - execução direta no banco",
            "complexity": "Baixa a Média (dependendo da query)"
        },
        
        "ExcelInput": {
            "description": "📈 **Entrada de Arquivo Excel**",
            "details": [
                "• Lê dados de planilhas Excel (.xls, .xlsx)",
                "• Suporta múltiplas abas/worksheets",
                "• Detecta automaticamente cabeçalhos e tipos",
                "• Permite definir range específico de células",
                "• Converte datas e números automaticamente"
            ],
            "use_cases": [
                "Importação de dados de usuários",
                "Cargas mensais/semanais",
                "Dados de sistemas legados"
            ],
            "performance": "Média - processamento de arquivo",
            "complexity": "Baixa a Média"
        },
        
        "TextFileInput": {
            "description": "📄 **Entrada de Arquivo Texto**",
            "details": [
                "• Processa arquivos CSV, TXT, TSV delimitados",
                "• Configuração flexível de separadores",
                "• Tratamento de encoding (UTF-8, Latin1, etc.)",
                "• Suporte a escape de caracteres especiais",
                "• Validação de estrutura durante leitura"
            ],
            "use_cases": [
                "Arquivos de sistemas externos",
                "Exports de relatórios",
                "Dados de APIs em formato texto"
            ],
            "performance": "Alta - leitura otimizada",
            "complexity": "Baixa"
        },
        
        "StringOperations": {
            "description": "🔤 **Operações de String**",
            "details": [
                "• Manipulação avançada de campos de texto",
                "• Concatenação, substring, replace, trim",
                "• Conversão de case (maiúscula/minúscula)",
                "• Remoção de caracteres especiais",
                "• Formatação e padronização de dados"
            ],
            "use_cases": [
                "Limpeza de dados de entrada",
                "Formatação de códigos/IDs",
                "Normalização de nomes e endereços"
            ],
            "performance": "Muito Alta - operações em memória",
            "complexity": "Baixa a Média"
        },
        
        "Calculator": {
            "description": "🧮 **Calculadora de Campos**",
            "details": [
                "• Cria novos campos através de expressões",
                "• Operações matemáticas (+, -, *, /, %)",
                "• Funções de data (DATEDIFF, DATEADD, etc.)",
                "• Condicionais (IF, CASE WHEN)",
                "• Funções estatísticas (SUM, AVG, COUNT)"
            ],
            "use_cases": [
                "Cálculo de indicadores",
                "Transformações de medidas",
                "Criação de flags e categorias"
            ],
            "performance": "Alta - cálculos otimizados",
            "complexity": "Média a Alta"
        },
        
        "FilterRows": {
            "description": "🔍 **Filtro de Registros**",
            "details": [
                "• Filtragem baseada em condições lógicas",
                "• Operadores: =, <>, >, <, >=, <=, LIKE",
                "• Múltiplas condições com AND/OR",
                "• Suporte a expressões regulares",
                "• Filtros por valores nulos/não nulos"
            ],
            "use_cases": [
                "Seleção de período específico",
                "Filtro por status/categoria",
                "Remoção de registros inválidos"
            ],
            "performance": "Muito Alta - filtro em memória",
            "complexity": "Baixa"
        },
        
        "SortRows": {
            "description": "📊 **Ordenação de Registros**",
            "details": [
                "• Ordena registros por um ou múltiplos campos",
                "• Suporte a ordenação crescente/decrescente",
                "• Otimizado para grandes volumes",
                "• Preserva ordem original em caso de empate",
                "• Suporte a tipos diversos (texto, número, data)"
            ],
            "use_cases": [
                "Preparação para agregações",
                "Ordenação cronológica",
                "Ranking de valores"
            ],
            "performance": "Média - uso intensivo de memória",
            "complexity": "Média"
        },
        
        "GroupBy": {
            "description": "📋 **Agrupamento e Agregação**",
            "details": [
                "• Agrupa registros por campos específicos",
                "• Funções: SUM, COUNT, AVG, MIN, MAX",
                "• Múltiplos níveis de agrupamento",
                "• Criação de subtotais automáticos",
                "• Otimizado para análises estatísticas"
            ],
            "use_cases": [
                "Relatórios de totalizações",
                "Análises por período/categoria",
                "Cálculo de KPIs"
            ],
            "performance": "Baixa a Média - processamento intensivo",
            "complexity": "Alta"
        },
        
        "SelectValues": {
            "description": "✅ **Seleção de Campos**",
            "details": [
                "• Seleciona campos específicos do dataset",
                "• Renomeação de colunas",
                "• Alteração de tipos de dados",
                "• Reordenação de campos",
                "• Remoção de colunas desnecessárias"
            ],
            "use_cases": [
                "Preparação de estrutura final",
                "Otimização de performance",
                "Padronização de nomenclatura"
            ],
            "performance": "Muito Alta - operação simples",
            "complexity": "Baixa"
        },
        
        "TableOutput": {
            "description": "💾 **Saída para Tabela SQL**",
            "details": [
                "• Grava dados em tabelas do banco",
                "• Modos: INSERT, UPDATE, INSERT/UPDATE",
                "• Controle de commit por lotes",
                "• Mapeamento automático de campos",
                "• Tratamento de chaves primárias/únicas"
            ],
            "use_cases": [
                "Carga em Data Warehouse",
                "Atualização de dimensões",
                "Persistência de resultados"
            ],
            "performance": "Média - depende da rede/banco",
            "complexity": "Baixa a Média"
        },
        
        "ExcelOutput": {
            "description": "📊 **Saída para Excel**",
            "details": [
                "• Cria arquivos Excel (.xlsx) com dados",
                "• Múltiplas abas em um arquivo",
                "• Formatação automática (headers, tipos)",
                "• Controle de localização do arquivo",
                "• Preservação de formatação original"
            ],
            "use_cases": [
                "Relatórios para usuários finais",
                "Exports para análise externa",
                "Backup de dados processados"
            ],
            "performance": "Baixa - criação de arquivo",
            "complexity": "Baixa"
        },
        
        "TextFileOutput": {
            "description": "📁 **Saída para Arquivo Texto**",
            "details": [
                "• Gera arquivos CSV, TXT delimitados",
                "• Configuração de separadores e encoding",
                "• Controle de cabeçalhos",
                "• Formatação de datas e números",
                "• Otimizado para integração com outros sistemas"
            ],
            "use_cases": [
                "Interface com sistemas externos",
                "Arquivos para FTP/API",
                "Backup em formato universal"
            ],
            "performance": "Alta - escrita sequencial",
            "complexity": "Baixa"
        },
        
        "ValueMapper": {
            "description": "🗺️ **Mapeamento de Valores**",
            "details": [
                "• Substitui valores baseado em tabela de mapeamento",
                "• Suporte a valores padrão para não encontrados",
                "• Mapeamento um-para-um ou um-para-muitos",
                "• Útil para tradução de códigos",
                "• Preserva tipos de dados originais"
            ],
            "use_cases": [
                "Tradução de códigos",
                "Padronização de valores",
                "Enriquecimento de dados"
            ],
            "performance": "Alta - lookup em memória",
            "complexity": "Média"
        }
    }
    
    step_type = step.type.value if hasattr(step.type, 'value') else str(step.type)
    
    if step_type in detailed_explanations:
        info = detailed_explanations[step_type]
        
        explanation = f"""
{info['description']}

**📋 Funcionalidades:**
{chr(10).join(info['details'])}

**🎯 Casos de Uso Típicos:**
{chr(10).join(['• ' + uc for uc in info['use_cases']])}

**⚡ Performance:** {info['performance']}
**🔧 Complexidade:** {info['complexity']}
"""
    else:
        # Fallback para tipos não mapeados
        explanation = f"⚙️ **{step_type}**\n\nExecuta operação específica: {step_type}"
    
    # Adicionar informações específicas da configuração se disponíveis
    config_info = []
    
    if hasattr(step, 'config') and step.config:
        config = step.config
        
        # Informações específicas por tipo
        if step_type == "TableInput":
            if 'connection' in config:
                config_info.append(f"🔗 **Conexão:** {config['connection']}")
            if 'sql' in config:
                sql_preview = config['sql'][:100] + "..." if len(config['sql']) > 100 else config['sql']
                config_info.append(f"📝 **Query:** `{sql_preview}`")
            if 'limit' in config and config['limit'] > 0:
                config_info.append(f"📊 **Limite:** {config['limit']} registros")
                
        elif step_type == "ExcelInput":
            if 'filename' in config:
                config_info.append(f"📁 **Arquivo:** {config['filename']}")
            if 'sheet' in config:
                config_info.append(f"📄 **Planilha:** {config['sheet']}")
            if 'startrow' in config:
                config_info.append(f"📍 **Linha inicial:** {config['startrow']}")
                
        elif step_type == "TableOutput":
            if 'connection' in config:
                config_info.append(f"🔗 **Conexão:** {config['connection']}")
            if 'table' in config:
                config_info.append(f"📋 **Tabela:** {config['table']}")
            if 'commit' in config:
                config_info.append(f"📦 **Commit:** {config['commit']} registros")
    
    # Adicionar configurações específicas se encontradas
    if config_info:
        explanation += f"\n\n**⚙️ Configuração Atual:**\n{chr(10).join(config_info)}"
    
    return explanation



def show_import_flow():
    """Página de importação melhorada."""
    show_global_header()
    st.title("➕ Importar Novo Fluxo")
    st.markdown("Faça upload do seu arquivo KTR do Pentaho e converta automaticamente para Python")
    
    if st.button("⬅️ Voltar ao Dashboard"):
        change_view('dashboard')
        st.rerun()
    
    st.markdown("---")

    # Upload melhorado
    uploaded_file = st.file_uploader(
        "📁 Selecione seu arquivo KTR",
        type=['ktr'],
        help="Arquivos .ktr do Pentaho Data Integration"
    )

    if uploaded_file is None:
        st.session_state.ktr_model = None
        
        # Dicas de uso
        with st.expander("💡 Dicas de Uso"):
            st.markdown("""
            **Como usar a plataforma:**
            1. **Upload**: Selecione um arquivo .ktr do Pentaho
            2. **Análise**: O sistema analisa automaticamente o pipeline
            3. **Conversão**: Gera código Python equivalente
            4. **Execução**: Execute o fluxo diretamente na plataforma
            5. **Monitoramento**: Acompanhe logs e métricas em tempo real
            """)
        return

    # Análise automática
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ktr') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        with st.spinner("🔍 Analisando arquivo KTR..."):
            parser = KTRParser()
            ktr_model = parser.parse_file(tmp_path)
            st.session_state.ktr_model = ktr_model
            
        os.unlink(tmp_path)
        st.success(f"✅ Arquivo '{uploaded_file.name}' analisado com sucesso!")

        # Preview da análise
        with st.expander("🔍 Detalhes da Análise", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Steps Detectados", len(ktr_model.steps))
            with col2:
                st.metric("Conexões", len(ktr_model.connections))
            with col3:
                st.metric("Complexidade", "Média")  # Placeholder

        # Botão para análise detalhada do fluxo
        if st.button("🔍 Analisar Fluxo Detalhadamente", type="secondary", use_container_width=True):
            show_detailed_ktr_analysis(ktr_model)

    except Exception as e:
        st.error(f"❌ Erro na análise do KTR: {e}")
        st.session_state.ktr_model = None
        return

    if st.session_state.ktr_model:
        st.markdown("---")
        st.subheader("💾 Configurações do Fluxo")
        
        col1, col2 = st.columns(2)
        
        with col1:
            flow_name = st.text_input("Nome do Fluxo", value=st.session_state.ktr_model.name)
        
        with col2:
            auto_execute = st.checkbox("▶️ Executar automaticamente após importar")

        if st.button("💾 Salvar Fluxo", type="primary", use_container_width=True):
            if not flow_name:
                st.warning("Por favor, forneça um nome para o fluxo.")
                return

            with st.status("Processando arquivo KTR...", expanded=True) as status_ui:
                try:
                    status_ui.update(label="🔧 Criando registro do fluxo...")
                    new_flow = flow_manager.add_flow(name=flow_name)
                    
                    status_ui.update(label="🐍 Gerando código Python...")
                    generator = CodeGenerator()
                    project = generator.generate_pipeline(st.session_state.ktr_model, new_flow.project_path)
                    
                    status_ui.update(label=f"💾 Salvando {len(project.files)} arquivos...")
                    project_dir = Path(new_flow.project_path)
                    project_dir.mkdir(parents=True, exist_ok=True)
                    
                    for file_path, content in project.files.items():
                        full_path = project_dir / file_path
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(full_path, "w", encoding="utf-8") as f:
                            f.write(content)
                    
                    status_ui.update(label="✅ Finalizando importação...")
                    flow_manager.update_flow_status(new_flow.id, "Pronto")
                    
                    if auto_execute:
                        status_ui.update(label="🚀 Iniciando execução automática...")
                        executor.execute_flow(new_flow.id)

                    status_ui.update(label="🎉 Importação concluída!", state="complete", expanded=False)
                    st.success(f"🎉 Fluxo '{flow_name}' importado com sucesso!")
                    
                    if auto_execute:
                        st.info("🚀 Execução iniciada automaticamente!")
                    
                    time.sleep(2)
                    change_view('dashboard')
                    st.rerun()

                except Exception as e:
                    status_ui.update(label=f"❌ Falha: {e}", state="error")
                    st.error(f"❌ Erro ao salvar o fluxo: {e}")
                    if 'new_flow' in locals():
                        flow_manager.delete_flow(new_flow.id)
                        if Path(new_flow.project_path).exists():
                            shutil.rmtree(new_flow.project_path)

def show_monitor():
    """Página de monitoramento melhorada com progresso visual em tempo real."""
    show_global_header()
    
    flow_id = st.session_state.selected_flow_id
    flow = flow_manager.get_flow(flow_id)
    
    if not flow:
        st.error("Fluxo não encontrado!")
        return
    
    st.title(f"📊 Monitor: {flow.name}")
    
    if st.button("⬅️ Voltar ao Dashboard"):
        change_view('dashboard')
        st.rerun()
    
    st.markdown("---")
    
    # CSS para progresso visual
    st.markdown("""
    <style>
    .monitor-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .progress-step {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #007bff;
        color: #333;
    }
    .step-running {
        border-left-color: #ffc107;
        animation: pulse 2s infinite;
    }
    .step-success {
        border-left-color: #28a745;
    }
    .step-error {
        border-left-color: #dc3545;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 193, 7, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0); }
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .spinner {
        display: inline-block;
        animation: spin 1s linear infinite;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Status em tempo real
    is_running = executor.is_flow_running(flow_id)
    
    # Container principal de monitoramento
    st.markdown(f"""
    <div class="monitor-container">
        <h2>🎯 {flow.name}</h2>
        <p>Monitoramento em tempo real da execução do pipeline</p>
    </div>
    """, unsafe_allow_html=True)
    
    # SISTEMA DE TEMPO REAL COM AUTO-REFRESH INTELIGENTE
    current_time = datetime.now()
    
    # Container de status dinâmico
    status_container = st.container()
    
    with status_container:
        # Sistema de refresh automático baseado em estado
        if is_running:
            # Durante execução: atualização a cada 1 segundo
            st.markdown("""
            <script>
                setTimeout(function() {
                    window.parent.document.querySelector('[data-testid="stApp"]').click();
                }, 1000);
            </script>
            """, unsafe_allow_html=True)
            
            st.success(f"🔄 **EXECUTANDO EM TEMPO REAL** - Monitoramento ativo: {current_time.strftime('%H:%M:%S')}")
            
        elif flow.error_message or flow.execution_status in ["Falha", "Erro"]:
            # Com erro: atualização a cada 2 segundos (para detectar correções)
            st.markdown("""
            <script>
                setTimeout(function() {
                    window.parent.document.querySelector('[data-testid="stApp"]').click();
                }, 2000);
            </script>
            """, unsafe_allow_html=True)
            
            st.error(f"💥 **ERRO DETECTADO** - Sistema monitorando falhas: {current_time.strftime('%H:%M:%S')}")
            
        else:
            # Estado normal: atualização a cada 5 segundos
            st.markdown("""
            <script>
                setTimeout(function() {
                    window.parent.document.querySelector('[data-testid="stApp"]').click();
                }, 5000);
            </script>
            """, unsafe_allow_html=True)
            
            st.info(f"📊 **MONITORAMENTO ATIVO** - Última verificação: {current_time.strftime('%H:%M:%S')}")
    
    # BARRA DE PROGRESSO EM TEMPO REAL
    progress_container = st.container()
    
    with progress_container:
        # Análise de progresso baseada nos logs
        progress_steps = analyze_execution_progress(flow)
        total_steps = len(progress_steps) if progress_steps else 3  # Mínimo de 3 etapas padrão
        completed_steps = len([s for s in progress_steps if s['status'] == 'completed'])
        current_step = None
        
        # Identificar etapa atual em execução
        for step in progress_steps:
            if step['status'] == 'running':
                current_step = step
                break
        
        # Calcular progresso real
        if is_running and current_step:
            # Durante execução, mostrar progresso dinâmico
            base_progress = (completed_steps / total_steps) * 100
            # Adicionar progresso parcial da etapa atual (simulação baseada em tempo)
            execution_time = calculate_current_duration_numeric(flow)
            step_progress = min(0.8, execution_time / 30.0) * (100 / total_steps)  # Max 80% por etapa
            progress_percentage = min(95, base_progress + step_progress)  # Nunca 100% até terminar
        else:
            progress_percentage = (completed_steps / total_steps) * 100 if total_steps > 0 else 0
            
        # Barra de progresso visual com animação
        if is_running:
            # Barra animada durante execução
            st.markdown(f"""
            <div style="background-color: #f0f2f6; border-radius: 10px; padding: 5px; margin: 10px 0;">
                <div style="
                    background: linear-gradient(90deg, #4CAF50, #2196F3);
                    height: 25px;
                    border-radius: 8px;
                    width: {progress_percentage}%;
                    transition: width 0.5s ease;
                    animation: pulse 2s infinite;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                ">
                    🚀 {progress_percentage:.1f}%
                </div>
            </div>
            <style>
                @keyframes pulse {{
                    0% {{ opacity: 0.8; }}
                    50% {{ opacity: 1; }}
                    100% {{ opacity: 0.8; }}
                }}
            </style>
            """, unsafe_allow_html=True)
        else:
            # Barra estática quando não está executando
            st.progress(progress_percentage / 100)
            
        # Métricas de progresso em tempo real
        col1, col2, col3 = st.columns(3)
        with col1:
            if is_running:
                st.metric("🚀 Progresso Atual", f"{progress_percentage:.1f}%", delta="Em execução")
            else:
                st.metric("📊 Progresso Final", f"{progress_percentage:.1f}%")
        with col2:
            st.metric("✅ Etapas Concluídas", f"{completed_steps}/{total_steps}")
        with col3:
            if current_step:
                st.metric("🔄 Etapa Atual", current_step['name'])
            else:
                status_emoji = "🔄" if is_running else ("✅" if flow.execution_status == "Sucesso" else "❌")
                st.metric("📍 Status", f"{status_emoji} {flow.execution_status}")

    # DETECÇÃO E EXIBIÇÃO DE ERROS EM TEMPO REAL
    if flow.error_message:
        # Extrair a etapa do erro da mensagem
        stage_match = re.search(r'\[([^\]]+)\]', flow.error_message)
        stage = stage_match.group(1) if stage_match else "DESCONHECIDO"
        
        # Cores específicas por etapa
        stage_colors = {
            "EXTRAÇÃO": "🔴",
            "TRANSFORMAÇÃO": "🟠", 
            "CARREGAMENTO": "🟡",
            "EXECUTOR": "🔵",
            "GERAL": "⚫"
        }
        
        stage_icon = stage_colors.get(stage, "❌")
        
        st.error(f"### {stage_icon} Falha na Etapa: {stage}")
        
        # Limpar a mensagem de erro dos prefixos para exibição
        clean_error = re.sub(r'^\[[^\]]+\]\s*', '', flow.error_message)
        
        # Exibir com formatting específico
        if "Traceback" in clean_error or "File " in clean_error:
            st.code(clean_error, language='python')
        else:
            st.code(clean_error, language='bash')
            
        # Adicionar dicas de resolução baseadas na etapa
        if stage == "EXTRAÇÃO":
            with st.expander("💡 Dicas para Resolução"):
                st.write("""
                **Problemas comuns na extração:**
                - Arquivo não encontrado: Verifique se o caminho está correto
                - Erro de permissão: Verifique se o arquivo está sendo usado por outro processo
                - Formato inválido: Verifique se o arquivo Excel não está corrompido
                - Planilha não encontrada: Verifique o nome da aba no arquivo Excel
                """)
        elif stage == "TRANSFORMAÇÃO":
            with st.expander("💡 Dicas para Resolução"):
                st.write("""
                **Problemas comuns na transformação:**
                - Campo não encontrado: Verifique se as colunas existem no DataFrame
                - Tipo de dados inválido: Verifique se os tipos estão corretos
                - Valores nulos: Implemente tratamento para valores ausentes
                """)
        elif stage == "CARREGAMENTO":
            with st.expander("💡 Dicas para Resolução"):
                st.write("""
                **Problemas comuns no carregamento:**
                - Erro de conexão: Verifique credenciais e conectividade
                - Tabela não existe: Verifique se a tabela foi criada
                - Permissões insuficientes: Verifique as permissões do usuário
                - Constraint violada: Verifique duplicatas ou campos obrigatórios
                """)

    # LOGS EM TEMPO REAL - Container para logs dinâmicos
    st.markdown("---")
    
    # Logs em tempo real com scroll automático
    if flow.execution_logs:
        st.subheader("📊 Logs de Execução em Tempo Real")
        
        # Container de logs com altura fixa e auto-scroll
        logs_container = st.container()
        
        with logs_container:
            # Durante execução, mostrar apenas os últimos 20 logs para performance
            if is_running:
                recent_logs = flow.execution_logs[-20:]
                st.info("🔄 Exibindo logs em tempo real (últimas 20 entradas)")
            else:
                recent_logs = flow.execution_logs[-50:]
                st.info(f"📋 Total de {len(flow.execution_logs)} entradas de log")
            
            # Exibir logs com cores baseadas no conteúdo
            for log_entry in recent_logs:
                timestamp_now = datetime.now().strftime("%H:%M:%S")
                
                # Detectar tipo de log e aplicar cor
                if "ERROR" in log_entry or "❌" in log_entry or "Erro" in log_entry or "[ERRO]" in log_entry:
                    st.error(f"🔴 {log_entry}")
                elif "WARNING" in log_entry or "⚠️" in log_entry or "Aviso" in log_entry:
                    st.warning(f"🟡 {log_entry}")
                elif "SUCCESS" in log_entry or "✅" in log_entry or "Sucesso" in log_entry or "concluída" in log_entry:
                    st.success(f"🟢 {log_entry}")
                elif "🚀" in log_entry or "Iniciando" in log_entry or "INFO" in log_entry:
                    st.info(f"🔵 {log_entry}")
                elif "🎯" in log_entry or "Pipeline" in log_entry:
                    st.info(f"⚡ {log_entry}")
                else:
                    st.text(f"⚪ {log_entry}")
                    
        # Status de atualização dos logs
        if is_running:
            st.caption(f"🔄 Logs atualizando automaticamente... | {timestamp_now}")
        else:
            st.caption(f"📋 Logs finalizados | Última atualização: {timestamp_now}")
            
    else:
        st.info("📝 Nenhum log disponível. Os logs aparecerão aqui durante a execução.")
    
    # Timeline das etapas
    st.subheader("🔄 Timeline de Execução")
    
    for i, step in enumerate(progress_steps):
        step_class = "progress-step"
        if step['status'] == 'running':
            step_class += " step-running"
        elif step['status'] == 'completed':
            step_class += " step-success"
        elif step['status'] == 'error':
            step_class += " step-error"
            
        icon = "🔄" if step['status'] == 'running' else ("✅" if step['status'] == 'completed' else ("❌" if step['status'] == 'error' else "⏳"))
        
        spinner_html = '<span class="spinner">🔄</span>' if step['status'] == 'running' else icon
        
        st.markdown(f"""
        <div class="{step_class}">
            <strong>{spinner_html} Etapa {i+1}: {step['name']}</strong><br>
            <small>{step['description']}</small>
            {f"<br><small>⏱️ {step['timestamp']}</small>" if step['timestamp'] else ""}
        </div>
        """, unsafe_allow_html=True)
    
    # Métricas detalhadas
    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        status_color = "🟢" if flow.execution_status == "Sucesso" else "🔴" if flow.execution_status in ["Falha", "Erro"] else "🟡"
        st.metric("Status Detalhado", f"{status_color} {flow.execution_status}")
    
    with col2:
        if flow.execution_duration:
            st.metric("Duração", f"{flow.execution_duration:.2f}s")
        else:
            current_duration = calculate_current_duration(flow, is_running)
            st.metric("Duração", current_duration)
    
    with col3:
        if flow.execution_start_time:
            start_time = pd.to_datetime(flow.execution_start_time)
            st.metric("Iniciado", start_time.strftime("%H:%M:%S"))
        else:
            st.metric("Iniciado", "-")
    
    with col4:
        if flow.execution_end_time:
            end_time = pd.to_datetime(flow.execution_end_time)
            st.metric("Finalizado", end_time.strftime("%H:%M:%S"))
        else:
            st.metric("Finalizado", "-" if not is_running else "🔄 Executando...")
    
    with col5:
        logs_count = len(flow.execution_logs)
        st.metric("Logs", f"{logs_count} entradas")
    
    # Controles de execução
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if is_running:
            if st.button("⏹️ Parar Execução", type="secondary", use_container_width=True):
                executor.stop_flow(flow_id)
                st.rerun()
        else:
            if st.button("▶️ Executar Novamente", type="primary", use_container_width=True):
                executor.execute_flow(flow_id)
                st.rerun()
    
    with col2:
        if st.button("🧹 Limpar Logs", use_container_width=True):
            flow_manager.clear_execution_logs(flow_id)
            st.rerun()
    
    with col3:
        if st.button("📥 Exportar Logs", use_container_width=True):
            if flow.execution_logs:
                logs_text = "\n".join(flow.execution_logs)
                st.download_button(
                    "💾 Download",
                    logs_text,
                    f"{flow.name}_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    "text/plain"
                )
    
    with col4:
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=True)
        # Auto-refresh está implementado via JavaScript no sistema de tempo real
        if auto_refresh:
            st.caption("🔄 Refresh automático ativo")

    # Logs em tempo real com análise
    st.markdown("---")
    st.subheader("📊 Logs de Execução")
    
    # Status de refresh
    if auto_refresh:
        st.caption(f"🔄 Auto-refresh ativo - Última atualização: {datetime.now().strftime('%H:%M:%S')}")
    
    if flow.execution_logs:
        # Container para logs com altura fixa e scroll
        logs_container = st.container()
        
        with logs_container:
            # Mostrar apenas os últimos 50 logs para performance
            recent_logs = flow.execution_logs[-50:]
            
            for log_entry in recent_logs:
                # Colorir logs baseado no conteúdo
                if "ERROR" in log_entry or "❌" in log_entry or "Erro" in log_entry:
                    st.error(log_entry)
                elif "WARNING" in log_entry or "⚠️" in log_entry:
                    st.warning(log_entry)
                elif "SUCCESS" in log_entry or "✅" in log_entry or "Sucesso" in log_entry:
                    st.success(log_entry)
                elif "INFO" in log_entry or "📡" in log_entry or "🚀" in log_entry or "🎯" in log_entry:
                    st.info(log_entry)
                else:
                    st.text(log_entry)
    else:
        st.info("📝 Nenhum log disponível. Execute o fluxo para gerar logs.")

def analyze_execution_progress(flow):
    """Analisa os logs para determinar o progresso das etapas."""
    steps = [
        {"name": "Inicialização", "description": "Preparando ambiente de execução", "status": "pending", "timestamp": None},
        {"name": "Configuração", "description": "Carregando configurações e conexões", "status": "pending", "timestamp": None},
        {"name": "Extração", "description": "Extraindo dados das fontes", "status": "pending", "timestamp": None},
        {"name": "Transformação", "description": "Aplicando regras de negócio", "status": "pending", "timestamp": None},
        {"name": "Carregamento", "description": "Salvando dados processados", "status": "pending", "timestamp": None},
        {"name": "Finalização", "description": "Limpeza e relatórios", "status": "pending", "timestamp": None}
    ]
    
    if not flow.execution_logs:
        return steps
    
    current_step = 0
    
    for log in flow.execution_logs:
        # Mapear logs para etapas
        if "Iniciando execução" in log or "Iniciando pipeline" in log:
            if current_step < len(steps):
                steps[current_step]['status'] = 'completed'
                steps[current_step]['timestamp'] = extract_timestamp(log)
                current_step = 1
                
        elif "Conexão configurada" in log or "configurações" in log.lower():
            if current_step <= 1:
                if current_step == 1:
                    steps[current_step]['status'] = 'completed'
                    steps[current_step]['timestamp'] = extract_timestamp(log)
                current_step = 2
                
        elif "extração" in log.lower() or "Iniciando extração" in log:
            if current_step <= 2:
                if current_step == 2:
                    steps[current_step]['status'] = 'running' if "Iniciando" in log else 'completed'
                    steps[current_step]['timestamp'] = extract_timestamp(log)
                if "Iniciando" not in log:
                    current_step = 3
                    
        elif "transformação" in log.lower() or "transform" in log.lower():
            if current_step <= 3:
                if current_step == 3:
                    steps[current_step]['status'] = 'running' if "Iniciando" in log else 'completed'
                    steps[current_step]['timestamp'] = extract_timestamp(log)
                if "Iniciando" not in log:
                    current_step = 4
                    
        elif "carregamento" in log.lower() or "loading" in log.lower() or "salvando" in log.lower():
            if current_step <= 4:
                if current_step == 4:
                    steps[current_step]['status'] = 'running' if "Iniciando" in log else 'completed'
                    steps[current_step]['timestamp'] = extract_timestamp(log)
                if "Iniciando" not in log:
                    current_step = 5
                    
        elif "Pipeline concluído" in log or "Execução concluída" in log:
            steps[5]['status'] = 'completed'
            steps[5]['timestamp'] = extract_timestamp(log)
            
        elif "ERROR" in log or "❌" in log or "Erro" in log or "falhou" in log:
            # Marcar etapa atual como erro
            if current_step < len(steps):
                steps[current_step]['status'] = 'error'
                steps[current_step]['timestamp'] = extract_timestamp(log)
    
    return steps

def extract_timestamp(log_entry):
    """Extrai timestamp do log."""
    try:
        if "[" in log_entry and "]" in log_entry:
            timestamp_str = log_entry.split("]")[0].replace("[", "")
            return timestamp_str.split("T")[1][:8] if "T" in timestamp_str else timestamp_str
    except:
        pass
    return None

def calculate_current_duration(flow, is_running):
    """Calcula duração atual se ainda estiver executando."""
    if not is_running or not flow.execution_start_time:
        return "-"
    
    try:
        start_time = pd.to_datetime(flow.execution_start_time)
        current_time = pd.Timestamp.now()
        duration = (current_time - start_time).total_seconds()
        return f"{duration:.1f}s"
    except:
        return "-"

def calculate_current_duration_numeric(flow):
    """Calcula duração atual em segundos (numérico) para cálculos de progresso."""
    if not flow.execution_start_time:
        return 0
    
    try:
        start_time = pd.to_datetime(flow.execution_start_time)
        
        if flow.execution_end_time:
            end_time = pd.to_datetime(flow.execution_end_time)
            return (end_time - start_time).total_seconds()
        else:
            current_time = pd.Timestamp.now()
            return (current_time - start_time).total_seconds()
    except:
        return 0

def show_rename():
    """Página de renomeação melhorada."""
    flow_id = st.session_state.selected_flow_id
    flow = flow_manager.get_flow(flow_id)
    
    if not flow:
        st.error("Fluxo não encontrado!")
        return
    
    st.title("✏️ Renomear Fluxo")
    
    if st.button("⬅️ Voltar ao Dashboard"):
        change_view('dashboard')
        st.rerun()
    
    st.markdown("---")
    
    st.info(f"📝 Renomeando: **{flow.name}**")
    
    new_name = st.text_input("Novo nome do fluxo", value=flow.name, placeholder="Digite o novo nome...")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Salvar Alterações", type="primary", use_container_width=True):
            if new_name and new_name != flow.name:
                flow_manager.rename_flow(flow_id, new_name)
                st.success(f"✅ Fluxo renomeado para '{new_name}'!")
                time.sleep(1)
                change_view('dashboard')
                st.rerun()
            elif not new_name:
                st.warning("⚠️ Por favor, forneça um nome.")
            else:
                st.info("ℹ️ O nome não foi alterado.")
    
    with col2:
        if st.button("❌ Cancelar", use_container_width=True):
            change_view('dashboard')
            st.rerun()


def show_delete():
    """Página de exclusão melhorada."""
    flow_id = st.session_state.selected_flow_id
    flow = flow_manager.get_flow(flow_id)
    
    if not flow:
        st.error("Fluxo não encontrado!")
        return
    
    st.title("🗑️ Excluir Fluxo")
    
    if st.button("⬅️ Voltar ao Dashboard"):
        change_view('dashboard')
        st.rerun()
    
    st.markdown("---")
    
    st.error(f"⚠️ **ATENÇÃO:** Você está prestes a excluir o fluxo **{flow.name}**")
    
    st.markdown("""
    **Esta ação é irreversível e removerá:**
    - ✂️ Todos os arquivos do projeto Python gerado
    - 📊 Todo o histórico de execuções
    - 📋 Todos os logs de execução
    - ⚙️ Todas as configurações do fluxo
    """)
    
    # Confirmação extra
    confirmation = st.text_input(
        f"Digite **{flow.name}** para confirmar a exclusão:",
        placeholder="Nome do fluxo para confirmar..."
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        can_delete = confirmation == flow.name
        if st.button("🗑️ Confirmar Exclusão", 
                    type="primary", 
                    disabled=not can_delete,
                    use_container_width=True):
            
            with st.spinner("🗑️ Excluindo fluxo..."):
                # Parar execução se estiver rodando
                if executor.is_flow_running(flow_id):
                    executor.stop_flow(flow_id)
                
                # Remover arquivos do projeto
                project_path = Path(flow.project_path)
                if project_path.exists():
                    shutil.rmtree(project_path)
                
                # Remover do gerenciador
                flow_manager.delete_flow(flow_id)
            
            st.success(f"🎉 Fluxo '{flow.name}' excluído com sucesso!")
            time.sleep(2)
            change_view('dashboard')
            st.rerun()
    
    with col2:
        if st.button("❌ Cancelar", use_container_width=True):
            change_view('dashboard')
            st.rerun()


def show_edit_code():
    """Página para editar código do fluxo com informações específicas sobre cada arquivo."""
    flow_id = st.session_state.selected_flow_id
    flow = flow_manager.get_flow(flow_id)
    
    if not flow:
        st.error("Fluxo não encontrado!")
        return
    
    st.title(f"📝 Editor de Código: {flow.name}")
    
    if st.button("⬅️ Voltar ao Dashboard"):
        change_view('dashboard')
        st.rerun()
    
    st.markdown("---")
    
    # Verificar se o projeto existe
    project_path = Path(flow.project_path)
    if not project_path.exists():
        st.error("❌ Projeto não encontrado! Verifique se o fluxo foi importado corretamente.")
        return

    # Definir tipos de arquivos com suas funções específicas
    file_types_info = {
        "Pipeline Principal": {
            "icon": "🔄",
            "description": "Arquivo principal que contém a lógica de ETL do pipeline",
            "impact": "Alterações aqui afetam diretamente o processamento de dados",
            "etapas": ["Extração de dados", "Transformações", "Carga de dados"],
            "pattern": f"{flow.name.lower().replace(' ', '_')}_pipeline.py",
            "folder": "src/pipelines/"
        },
        "Configurações": {
            "icon": "⚙️", 
            "description": "Configurações de conexões de banco, variáveis de ambiente e parâmetros",
            "impact": "Alterações aqui afetam conexões e comportamento global do pipeline",
            "etapas": ["Configuração de DB", "Variáveis de ambiente", "Parâmetros gerais"],
            "pattern": "settings.py",
            "folder": "config/"
        },
        "Testes Unitários": {
            "icon": "🧪",
            "description": "Testes automatizados para validar o funcionamento do pipeline",
            "impact": "Alterações aqui afetam a validação e qualidade do código",
            "etapas": ["Testes de conexão", "Validação de dados", "Testes de transformação"],
            "pattern": f"test_{flow.name.lower().replace(' ', '_')}_pipeline.py",
            "folder": "tests/"
        },
        "Extratores": {
            "icon": "📥",
            "description": "Módulos responsáveis pela extração de dados de fontes",
            "impact": "Alterações aqui afetam como os dados são extraídos das origens",
            "etapas": ["Conexão com fonte", "Consultas SQL", "Validação de entrada"],
            "pattern": "*.py",
            "folder": "src/extractors/"
        },
        "Transformadores": {
            "icon": "🔧",
            "description": "Módulos para transformação e limpeza de dados",
            "impact": "Alterações aqui afetam como os dados são processados e transformados",
            "etapas": ["Limpeza de dados", "Aplicação de regras", "Validações"],
            "pattern": "*.py", 
            "folder": "src/transformers/"
        },
        "Carregadores": {
            "icon": "📤",
            "description": "Módulos responsáveis pela carga de dados no destino",
            "impact": "Alterações aqui afetam como os dados são carregados no destino",
            "etapas": ["Conexão de destino", "Inserção de dados", "Validação de carga"],
            "pattern": "*.py",
            "folder": "src/loaders/"
        },
        "Utilitários": {
            "icon": "🛠️",
            "description": "Funções auxiliares e utilitários compartilhados",
            "impact": "Alterações aqui afetam funcionalidades compartilhadas entre módulos",
            "etapas": ["Funções auxiliares", "Helpers", "Validadores"],
            "pattern": "*.py",
            "folder": "src/utils/"
        }
    }
    
    # Encontrar arquivos por categoria
    categorized_files = {}
    
    for category, info in file_types_info.items():
        folder_path = project_path / info["folder"]
        files_found = []
        
        if folder_path.exists():
            if info["pattern"] == "*.py":
                files_found = list(folder_path.glob("*.py"))
            else:
                specific_file = folder_path / info["pattern"]
                if specific_file.exists():
                    files_found = [specific_file]
        
        if files_found:
            categorized_files[category] = {
                "info": info,
                "files": files_found
            }
    
    if not categorized_files:
        st.warning("⚠️ Nenhum arquivo Python encontrado no projeto.")
        return
    
    # Seletor de categoria e arquivo
    st.subheader("📂 Selecionar Arquivo para Editar")
    
    # Primeiro, selecionar categoria
    categories = list(categorized_files.keys())
    selected_category = st.selectbox(
        "1️⃣ Escolha a categoria:",
        options=categories,
        format_func=lambda x: f"{categorized_files[x]['info']['icon']} {x}",
        index=0
    )
    
    # Mostrar informações da categoria selecionada
    if selected_category:
        category_info = categorized_files[selected_category]["info"]
        
        with st.expander(f"ℹ️ Sobre {selected_category}", expanded=True):
            st.markdown(f"**Função:** {category_info['description']}")
            st.markdown(f"**Impacto das alterações:** {category_info['impact']}")
            
            if category_info['etapas']:
                st.markdown("**Etapas que afeta:**")
                for etapa in category_info['etapas']:
                    st.markdown(f"  • {etapa}")
        
        # Segundo, selecionar arquivo específico da categoria
        available_files = categorized_files[selected_category]["files"]
        
        if len(available_files) > 1:
            file_options = {}
            for file_path in available_files:
                relative_path = file_path.relative_to(project_path)
                file_options[str(relative_path)] = str(file_path)
            
            selected_file_display = st.selectbox(
                "2️⃣ Escolha o arquivo específico:",
                options=list(file_options.keys())
            )
            selected_file_path = file_options[selected_file_display]
        else:
            selected_file_path = str(available_files[0])
            selected_file_display = available_files[0].relative_to(project_path)
    
    if not selected_file_path:
        st.error("Arquivo não encontrado!")
        return
    
    try:
        # Ler conteúdo do arquivo
        with open(selected_file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Informações detalhadas do arquivo
        st.markdown("---")
        st.subheader(f"✏️ Editando: {selected_file_display}")
        
        # Métricas do arquivo
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            file_size = len(original_content.encode('utf-8'))
            st.metric("📏 Tamanho", f"{file_size:,} bytes")
        with col2:
            line_count = len(original_content.splitlines())
            st.metric("📄 Linhas", f"{line_count:,}")
        with col3:
            st.metric("🐍 Tipo", "Python")
        with col4:
            # Calcular complexidade básica (imports, funções, classes)
            imports = len([line for line in original_content.splitlines() if line.strip().startswith(('import ', 'from '))])
            functions = len([line for line in original_content.splitlines() if line.strip().startswith('def ')])
            classes = len([line for line in original_content.splitlines() if line.strip().startswith('class ')])
            complexity = imports + functions * 2 + classes * 3
            st.metric("🧠 Complexidade", complexity)
        
        # Editor de código com melhor interface
        st.markdown("### 💻 Editor de Código")
        
        # Dicas específicas por tipo de arquivo
        if selected_category == "Pipeline Principal":
            st.info("💡 **Dica:** Este é o coração do seu pipeline. Altere com cuidado as funções de extração, transformação e carga.")
        elif selected_category == "Configurações":
            st.warning("⚠️ **Atenção:** Mudanças aqui afetam todas as operações. Certifique-se de que as configurações de conexão estão corretas.")
        elif selected_category == "Testes Unitários":
            st.success("✅ **Boa prática:** Sempre execute os testes após fazer alterações para garantir que tudo funciona.")
        
        # Text area para edição com altura maior
        edited_content = st.text_area(
            "Código Python:",
            value=original_content,
            height=600,
            help="💡 Use Ctrl+A para selecionar tudo, Ctrl+Z para desfazer, Ctrl+S para salvar (apenas no navegador)"
        )
        
        # Verificar se houve mudanças
        has_changes = edited_content != original_content
        
        if has_changes:
            st.info("💡 Você fez alterações no código!")
            
            # Análise básica das mudanças
            original_lines = original_content.splitlines()
            edited_lines = edited_content.splitlines()
            
            lines_added = len(edited_lines) - len(original_lines)
            if lines_added > 0:
                st.success(f"➕ {lines_added} linhas adicionadas")
            elif lines_added < 0:
                st.warning(f"➖ {abs(lines_added)} linhas removidas")
        
        # Botões de ação principais
        st.markdown("---")
        st.subheader("💾 Ações de Arquivo")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("💾 Salvar Alterações", type="primary", disabled=not has_changes):
                try:
                    # Verificar permissões de escrita
                    file_path = Path(selected_file_path)
                    if not file_path.parent.exists():
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Fazer backup do arquivo original com timestamp
                    import datetime
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_path = f"{selected_file_path}.backup_{timestamp}"
                    
                    # Criar backup
                    with open(backup_path, 'w', encoding='utf-8', newline='') as f:
                        f.write(original_content)
                    
                    # Salvar o novo conteúdo
                    with open(selected_file_path, 'w', encoding='utf-8', newline='') as f:
                        f.write(edited_content)
                    
                    st.success("✅ Arquivo salvo com sucesso!")
                    st.info(f"📁 Backup criado: {Path(backup_path).name}")
                    
                    # Mostrar estatísticas da operação
                    bytes_saved = len(edited_content.encode('utf-8'))
                    st.metric("📊 Dados salvos", f"{bytes_saved:,} bytes")
                    
                    time.sleep(1.5)
                    st.rerun()
                    
                except PermissionError:
                    st.error("❌ Erro de permissão! Verifique se o arquivo não está sendo usado por outro programa.")
                except UnicodeError:
                    st.error("❌ Erro de codificação! Verifique se o código contém caracteres especiais válidos.")
                except Exception as e:
                    st.error(f"❌ Erro ao salvar arquivo: {type(e).__name__}: {e}")
                    st.code(f"Caminho: {selected_file_path}")
        
        with col2:
            if st.button("🔄 Recarregar Original"):
                st.info("🔄 Recarregando conteúdo original...")
                time.sleep(0.5)
                st.rerun()
        
        with col3:
            if st.button("📋 Copiar Código"):
                # Implementar BEP (notificação especial) para código copiado
                st.markdown("### 🚨 BEP - CÓDIGO COPIADO")
                st.markdown("---")
                
                # Informações do BEP
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("**📄 Arquivo:** " + str(selected_file_display))
                    st.markdown("**📁 Categoria:** " + selected_category)
                    st.markdown("**📏 Linhas:** " + str(len(edited_content.splitlines())))
                
                with col_b:
                    import datetime
                    timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    st.markdown("**🕐 Timestamp:** " + timestamp)
                    st.markdown("**👤 Usuário:** Sistema")
                    st.markdown("**🔗 Flow ID:** " + flow_id)
                
                st.markdown("**📋 Código para Cópia:**")
                st.code(edited_content, language="python")
                
                st.success("✅ **BEP Gerado!** Use Ctrl+A no código acima, depois Ctrl+C para copiar")
                st.info("💡 Este BEP registra que o código foi acessado para cópia conforme procedimentos de auditoria")
        
        with col4:
            # Verificar se existem backups
            backup_files = list(Path(selected_file_path).parent.glob(f"{Path(selected_file_path).name}.backup_*"))
            if backup_files:
                if st.button("↩️ Restaurar Backup"):
                    # Selecionar o backup mais recente
                    latest_backup = max(backup_files, key=os.path.getctime)
                    
                    try:
                        with open(latest_backup, 'r', encoding='utf-8') as f:
                            backup_content = f.read()
                        
                        with open(selected_file_path, 'w', encoding='utf-8', newline='') as f:
                            f.write(backup_content)
                        
                        st.success(f"✅ Backup restaurado: {latest_backup.name}")
                        time.sleep(1)
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao restaurar backup: {e}")
        
        # Validação do código
        if has_changes:
            st.markdown("---")
            st.subheader("🔍 Validação e Análise")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🐍 Sintaxe Python:**")
                try:
                    compile(edited_content, selected_file_path, 'exec')
                    st.success("✅ Sintaxe válida!")
                except SyntaxError as e:
                    st.error(f"❌ Erro de sintaxe na linha {e.lineno}")
                    if e.text:
                        st.code(f"Linha {e.lineno}: {e.text.strip()}")
                    st.error(f"Erro: {e.msg}")
                except Exception as e:
                    st.warning(f"⚠️ Aviso na validação: {e}")
            
            with col2:
                st.markdown("**📊 Análise de Mudanças:**")
                
                # Comparar imports
                original_imports = len([line for line in original_content.splitlines() if line.strip().startswith(('import ', 'from '))])
                edited_imports = len([line for line in edited_content.splitlines() if line.strip().startswith(('import ', 'from '))])
                
                if edited_imports != original_imports:
                    diff_imports = edited_imports - original_imports
                    emoji = "➕" if diff_imports > 0 else "➖"
                    st.info(f"{emoji} {abs(diff_imports)} imports alterados")
                
                # Comparar funções
                original_functions = len([line for line in original_content.splitlines() if line.strip().startswith('def ')])
                edited_functions = len([line for line in edited_content.splitlines() if line.strip().startswith('def ')])
                
                if edited_functions != original_functions:
                    diff_functions = edited_functions - original_functions
                    emoji = "➕" if diff_functions > 0 else "➖"
                    st.info(f"{emoji} {abs(diff_functions)} funções alteradas")
            
            # Mostrar diff das mudanças
            with st.expander("👀 Ver Diferenças Detalhadas"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**📄 Antes:**")
                    preview_original = original_content[:2000] + "\n..." if len(original_content) > 2000 else original_content
                    st.code(preview_original, language="python")
                with col2:
                    st.markdown("**📝 Depois:**")
                    preview_edited = edited_content[:2000] + "\n..." if len(edited_content) > 2000 else edited_content
                    st.code(preview_edited, language="python")
        
        # Ações adicionais específicas por categoria
        st.markdown("---")
        st.subheader("🛠️ Ações Específicas")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧪 Testar Código"):
                if has_changes:
                    st.warning("⚠️ Salve as alterações antes de testar!")
                else:
                    if selected_category == "Testes Unitários":
                        st.info("🧪 Executando testes unitários...")
                        # Aqui você pode integrar com pytest ou unittest
                        st.code(f"python -m pytest {selected_file_path}")
                    else:
                        st.info("🚀 Iniciando teste do pipeline...")
                        executor.execute_flow(flow.id)
                        change_view('monitor', flow.id)
                        st.rerun()
        
        with col2:
            if st.button("📁 Abrir Pasta"):
                folder_path = Path(selected_file_path).parent
                st.code(f"📂 Pasta: {folder_path}")
                st.info("💡 Copie o caminho acima para abrir no explorador")
        
        with col3:
            if st.button("📋 Listar Arquivos"):
                st.markdown("**📁 Arquivos da categoria:**")
                category_files = categorized_files[selected_category]["files"]
                for file_path in category_files:
                    relative = file_path.relative_to(project_path)
                    size = file_path.stat().st_size
                    st.write(f"📄 {relative} ({size:,} bytes)")
    
    except FileNotFoundError:
        st.error(f"❌ Arquivo não encontrado: {selected_file_path}")
    except PermissionError:
        st.error(f"❌ Sem permissão para acessar: {selected_file_path}")
    except UnicodeDecodeError:
        st.error(f"❌ Erro de codificação no arquivo: {selected_file_path}")
        st.info("💡 O arquivo pode conter caracteres especiais ou estar corrompido")
    except Exception as e:
        st.error(f"❌ Erro inesperado ao ler arquivo: {type(e).__name__}: {e}")
        st.code(f"Arquivo: {selected_file_path}")


def show_schedules():
    """Página de gerenciamento de agendamentos."""
    show_global_header()
    st.title("⏰ Gerenciamento de Agendamentos")
    
    if st.button("⬅️ Voltar ao Dashboard"):
        change_view('dashboard')
        st.rerun()
    
    st.markdown("---")
    
    # Tabs para organizar funcionalidades
    tab1, tab2, tab3 = st.tabs(["➕ Criar Agendamento", "📋 Agendamentos Ativos", "📅 Próximas Execuções"])
    
    with tab1:
        create_schedule_tab()
    
    with tab2:
        show_active_schedules()
    
    with tab3:
        show_next_executions()


def create_schedule_tab():
    """Aba para criar novos agendamentos."""
    st.header("🆕 Criar Novo Agendamento")
    
    flows = flow_manager.get_all_flows()
    available_flows = [f for f in flows if f.status == "Pronto"]
    
    if not available_flows:
        st.warning("Nenhum fluxo disponível. Carregue alguns fluxos primeiro.")
        return
    
    with st.form("create_schedule"):
        # Seleção do fluxo
        flow_options = {f"{flow.name} ({flow.id})": flow.id for flow in available_flows}
        selected_flow = st.selectbox("Fluxo", list(flow_options.keys()))
        flow_id = flow_options[selected_flow]
        
        # Tipos de agendamento
        schedule_types = {
            "📅 Diário": "daily",
            "📆 Semanal": "weekly", 
            "🗓️ Datas Específicas": "specific_dates",
            "⚙️ Personalizado": "custom",
            "🕐 Múltiplos Horários": "multiple_times",
            "📋 Horários por Dia": "day_specific",
            "⏱️ Por Intervalo": "interval"
        }
        
        schedule_type_display = st.selectbox("Tipo de Agendamento", list(schedule_types.keys()))
        schedule_type = schedule_types[schedule_type_display]
        
        # Descrição personalizada
        description = st.text_input("Descrição (opcional)", placeholder="Ex: Backup diário do sistema")
        
        # Configurações específicas por tipo
        if schedule_type == "multiple_times":
            st.subheader("🕐 Múltiplos Horários")
            st.info("Configure múltiplos horários de execução para o mesmo tipo de agendamento")
            
            # Sub-tipo para múltiplos horários
            multi_type = st.radio("Executar:", ["Todos os dias", "Dias específicos da semana"])
            
            # Configuração de horários
            col1, col2 = st.columns(2)
            with col1:
                num_times = st.number_input("Quantos horários?", min_value=1, max_value=10, value=2)
            
            times = []
            days = None
            
            # Entrada de horários
            st.write("**Horários de Execução:**")
            cols = st.columns(min(num_times, 3))
            for i in range(num_times):
                with cols[i % 3]:
                    time_input = st.time_input(f"Horário {i+1}", key=f"multi_time_{i}")
                    times.append(time_input.strftime("%H:%M"))
            
            # Dias da semana se necessário
            if multi_type == "Dias específicos da semana":
                days = st.multiselect("Dias da Semana", 
                                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
                if not days:
                    st.warning("Selecione pelo menos um dia da semana")
            
            if st.form_submit_button("Criar Agendamento Múltiplos Horários"):
                try:
                    sched_type = "daily" if multi_type == "Todos os dias" else "weekly"
                    schedule_id = scheduler.create_multiple_times_schedule(
                        flow_id=flow_id,
                        times=times,
                        schedule_type=sched_type,
                        days=days,
                        description=description
                    )
                    st.success(f"Agendamento criado com sucesso! ID: {schedule_id}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao criar agendamento: {e}")
        
        elif schedule_type == "day_specific":
            st.subheader("📋 Horários Específicos por Dia")
            st.info("Configure horários diferentes para cada dia da semana")
            
            day_times = {}
            weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            
            for day in weekdays:
                with st.expander(f"📅 {day}"):
                    enable_day = st.checkbox(f"Ativar {day}", key=f"enable_{day}")
                    if enable_day:
                        num_times = st.number_input(f"Quantos horários para {day}?", 
                                                  min_value=1, max_value=5, value=1, key=f"num_{day}")
                        day_schedule = []
                        for i in range(num_times):
                            time_input = st.time_input(f"Horário {i+1}", key=f"{day}_time_{i}")
                            day_schedule.append(time_input.strftime("%H:%M"))
                        day_times[day] = day_schedule
            
            if st.form_submit_button("Criar Agendamento por Dia"):
                if not day_times:
                    st.warning("Configure pelo menos um dia com horários")
                else:
                    try:
                        schedule_id = scheduler.create_day_specific_times_schedule(
                            flow_id=flow_id,
                            day_times=day_times,
                            description=description
                        )
                        st.success(f"Agendamento criado com sucesso! ID: {schedule_id}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao criar agendamento: {e}")
        
        elif schedule_type == "interval":
            st.subheader("⏱️ Execução por Intervalo")
            st.info("Execute o fluxo a cada X minutos dentro de um período específico")
            
            col1, col2 = st.columns(2)
            with col1:
                interval_minutes = st.number_input("Intervalo (minutos)", min_value=1, max_value=1440, value=60)
            with col2:
                interval_type = st.radio("Período:", ["Todo o dia", "Horário específico", "Dias específicos"])
            
            start_time = "00:00"
            end_time = "23:59"
            days = None
            
            if interval_type == "Horário específico":
                col3, col4 = st.columns(2)
                with col3:
                    start_input = st.time_input("Início", value=datetime.strptime("08:00", "%H:%M").time())
                    start_time = start_input.strftime("%H:%M")
                with col4:
                    end_input = st.time_input("Fim", value=datetime.strptime("18:00", "%H:%M").time())
                    end_time = end_input.strftime("%H:%M")
            
            elif interval_type == "Dias específicos":
                days = st.multiselect("Dias da Semana", 
                                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                    default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
                col3, col4 = st.columns(2)
                with col3:
                    start_input = st.time_input("Início", value=datetime.strptime("08:00", "%H:%M").time())
                    start_time = start_input.strftime("%H:%M")
                with col4:
                    end_input = st.time_input("Fim", value=datetime.strptime("18:00", "%H:%M").time())
                    end_time = end_input.strftime("%H:%M")
            
            # Exibir informações do agendamento
            executions_per_hour = 60 // interval_minutes
            if interval_type == "Todo o dia":
                executions_per_day = 24 * executions_per_hour
            else:
                start_dt = datetime.strptime(start_time, "%H:%M")
                end_dt = datetime.strptime(end_time, "%H:%M")
                if end_dt < start_dt:
                    end_dt += timedelta(days=1)
                duration_hours = (end_dt - start_dt).total_seconds() / 3600
                executions_per_day = int(duration_hours * executions_per_hour)
            
            st.info(f"**Previsão:** ~{executions_per_hour} execuções/hora, ~{executions_per_day} execuções/dia")
            
            if st.form_submit_button("Criar Agendamento por Intervalo"):
                try:
                    schedule_id = scheduler.create_interval_schedule(
                        flow_id=flow_id,
                        interval_minutes=interval_minutes,
                        start_time=start_time,
                        end_time=end_time,
                        days=days,
                        description=description
                    )
                    st.success(f"Agendamento criado com sucesso! ID: {schedule_id}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao criar agendamento: {e}")
        
        # Tipos de agendamento originais
        elif schedule_type == "daily":
            time_input = st.time_input("Horário", value=datetime.now().time())
            
            if st.form_submit_button("Criar Agendamento Diário"):
                try:
                    schedule_id = scheduler.create_daily_schedule(
                        flow_id=flow_id,
                        time=time_input.strftime("%H:%M"),
                        description=description
                    )
                    st.success(f"Agendamento criado com sucesso! ID: {schedule_id}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao criar agendamento: {e}")
        
        elif schedule_type == "weekly":
            col1, col2 = st.columns(2)
            with col1:
                days = st.multiselect("Dias da Semana", 
                                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
            with col2:
                time_input = st.time_input("Horário", value=datetime.now().time())
            
            if st.form_submit_button("Criar Agendamento Semanal"):
                if not days:
                    st.warning("Selecione pelo menos um dia da semana")
                else:
                    try:
                        schedule_id = scheduler.create_weekly_schedule(
                            flow_id=flow_id,
                            days=days,
                            time=time_input.strftime("%H:%M"),
                            description=description
                        )
                        st.success(f"Agendamento criado com sucesso! ID: {schedule_id}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao criar agendamento: {e}")
        
        elif schedule_type == "specific_dates":
            st.subheader("Selecionar Datas")
            
            # Calendário para seleção múltipla
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Data inicial", value=datetime.now().date())
            with col2:
                end_date = st.date_input("Data final", value=datetime.now().date() + timedelta(days=30))
            
            time_input = st.time_input("Horário", value=datetime.now().time())
            
            # Seleção de datas específicas
            st.write("**Selecione as datas específicas:**")
            
            selected_dates = []
            current_date = start_date
            cols_per_row = 7
            
            while current_date <= end_date:
                if (current_date - start_date).days % cols_per_row == 0:
                    cols = st.columns(cols_per_row)
                
                col_index = (current_date - start_date).days % cols_per_row
                
                with cols[col_index]:
                    if st.checkbox(current_date.strftime("%d/%m"), key=f"date_{current_date}"):
                        selected_dates.append(current_date.isoformat())
                
                current_date += timedelta(days=1)
            
            if st.form_submit_button("Criar Agendamento para Datas Específicas"):
                if not selected_dates:
                    st.warning("Selecione pelo menos uma data")
                else:
                    try:
                        schedule_id = scheduler.create_specific_dates_schedule(
                            flow_id=flow_id,
                            dates=selected_dates,
                            time=time_input.strftime("%H:%M"),
                            description=description
                        )
                        st.success(f"Agendamento criado com sucesso! ID: {schedule_id}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao criar agendamento: {e}")
        
        elif schedule_type == "custom":
            st.subheader("Agendamento Personalizado")
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Data de início", value=datetime.now().date())
                days = st.multiselect("Dias da Semana", 
                                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                    default=["Monday", "Wednesday", "Friday"])
            with col2:
                end_date = st.date_input("Data de fim", value=datetime.now().date() + timedelta(days=30))
                time_input = st.time_input("Horário", value=datetime.now().time())
            
            if st.form_submit_button("Criar Agendamento Personalizado"):
                if not days:
                    st.warning("Selecione pelo menos um dia da semana")
                elif start_date >= end_date:
                    st.warning("A data de fim deve ser posterior à data de início")
                else:
                    try:
                        schedule_id = scheduler.create_custom_schedule(
                            flow_id=flow_id,
                            days=days,
                            time=time_input.strftime("%H:%M"),
                            start_date=start_date.isoformat(),
                            end_date=end_date.isoformat(),
                            description=description
                        )
                        st.success(f"Agendamento criado com sucesso! ID: {schedule_id}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao criar agendamento: {e}")


def show_active_schedules():
    """Exibe e gerencia agendamentos ativos."""
    st.header("📋 Agendamentos Ativos")
    
    schedules = scheduler.get_all_schedules()
    active_schedules = [s for s in schedules if s.active]
    
    if not active_schedules:
        st.info("Nenhum agendamento ativo encontrado.")
        return
    
    # Estatísticas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Ativos", len(active_schedules))
    with col2:
        daily_count = len([s for s in active_schedules if s.schedule_type == 'daily'])
        st.metric("Diários", daily_count)
    with col3:
        weekly_count = len([s for s in active_schedules if s.schedule_type == 'weekly'])
        st.metric("Semanais", weekly_count)
    with col4:
        other_count = len([s for s in active_schedules if s.schedule_type not in ['daily', 'weekly']])
        st.metric("Outros", other_count)
    
    st.divider()
    
    # Lista de agendamentos
    for schedule in active_schedules:
        with st.expander(f"🔄 {schedule.flow_name} - {get_schedule_type_display(schedule)}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Informações básicas
                st.markdown(f"**ID:** `{schedule.id}`")
                st.markdown(f"**Fluxo:** {schedule.flow_name}")
                st.markdown(f"**Tipo:** {get_schedule_type_display(schedule)}")
                
                if schedule.description:
                    st.markdown(f"**Descrição:** {schedule.description}")
                
                # Configuração específica por tipo
                display_schedule_config(schedule)
                
                # Estatísticas de execução
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    st.metric("Execuções", schedule.run_count)
                with col_stat2:
                    if schedule.last_run:
                        last_run = datetime.fromisoformat(schedule.last_run)
                        st.metric("Última Execução", last_run.strftime("%d/%m %H:%M"))
                    else:
                        st.metric("Última Execução", "Nunca")
                with col_stat3:
                    if schedule.next_run:
                        next_run = datetime.fromisoformat(schedule.next_run)
                        time_until = next_run - datetime.now()
                        if time_until.total_seconds() > 0:
                            if time_until.days > 0:
                                time_str = f"{time_until.days}d {time_until.seconds//3600}h"
                            else:
                                hours = time_until.seconds // 3600
                                minutes = (time_until.seconds % 3600) // 60
                                time_str = f"{hours}h {minutes}m"
                            st.metric("Próxima em", time_str)
                        else:
                            st.metric("Próxima em", "Agora")
                    else:
                        st.metric("Próxima Execução", "N/A")
            
            with col2:
                st.markdown("#### Ações")
                
                # Botão de execução manual
                if st.button("▶️ Executar Agora", key=f"run_{schedule.id}"):
                    try:
                        # Executar o fluxo manualmente
                        flow = flow_manager.get_flow(schedule.flow_id)
                        if flow:
                            result = executor.execute_flow(schedule.flow_id)
                            if result:
                                st.success("Fluxo executado com sucesso!")
                            else:
                                st.error("Erro ao executar fluxo")
                        else:
                            st.error("Fluxo não encontrado")
                    except Exception as e:
                        st.error(f"Erro: {e}")
                
                # Botão de pausar/ativar
                if st.button("⏸️ Pausar" if schedule.active else "▶️ Ativar", key=f"toggle_{schedule.id}"):
                    try:
                        scheduler.update_schedule(schedule.id, active=not schedule.active)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
                
                # Botão de editar
                if st.button("✏️ Editar", key=f"edit_{schedule.id}"):
                    st.session_state[f"editing_{schedule.id}"] = True
                    st.rerun()
                
                # Botão de remover
                if st.button("🗑️ Remover", key=f"delete_{schedule.id}", type="secondary"):
                    if st.session_state.get(f"confirm_delete_{schedule.id}", False):
                        try:
                            scheduler.delete_schedule(schedule.id)
                            st.success("Agendamento removido!")
                            if f"confirm_delete_{schedule.id}" in st.session_state:
                                del st.session_state[f"confirm_delete_{schedule.id}"]
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
                    else:
                        st.session_state[f"confirm_delete_{schedule.id}"] = True
                        st.warning("Clique novamente para confirmar a remoção")
                        st.rerun()
            
            # Formulário de edição (se ativo)
            if st.session_state.get(f"editing_{schedule.id}", False):
                show_edit_schedule_form(schedule)

def get_schedule_type_display(schedule):
    """Retorna a exibição formatada do tipo de agendamento."""
    if schedule.schedule_type == 'daily':
        if schedule.times:
            return f"📅 Diário ({len(schedule.times)} horários)"
        else:
            return f"📅 Diário às {schedule.time}"
    elif schedule.schedule_type == 'weekly':
        if schedule.day_times:
            total_executions = sum(len(times) for times in schedule.day_times.values())
            return f"📆 Semanal ({total_executions} execuções/semana)"
        elif schedule.times:
            return f"📆 Semanal ({len(schedule.times)} horários)"
        else:
            days_str = ", ".join(schedule.days) if schedule.days else "Todos os dias"
            return f"📆 Semanal - {days_str} às {schedule.time}"
    elif schedule.schedule_type == 'specific_dates':
        return f"🗓️ Datas Específicas ({len(schedule.specific_dates or [])} datas)"
    elif schedule.schedule_type == 'custom':
        return "⚙️ Personalizado"
    elif schedule.schedule_type == 'interval':
        return f"⏱️ Intervalo ({schedule.interval_minutes}min)"
    else:
        return schedule.schedule_type

def display_schedule_config(schedule):
    """Exibe a configuração detalhada do agendamento."""
    
    if schedule.schedule_type == 'daily':
        if schedule.times:
            st.markdown(f"**Horários:** {', '.join(schedule.times)}")
        else:
            st.markdown(f"**Horário:** {schedule.time}")
    
    elif schedule.schedule_type == 'weekly':
        if schedule.day_times:
            st.markdown("**Horários por Dia:**")
            for day, times in schedule.day_times.items():
                st.markdown(f"- **{day}:** {', '.join(times)}")
        elif schedule.times:
            st.markdown(f"**Dias:** {', '.join(schedule.days)}")
            st.markdown(f"**Horários:** {', '.join(schedule.times)}")
        else:
            st.markdown(f"**Dias:** {', '.join(schedule.days)}")
            st.markdown(f"**Horário:** {schedule.time}")
    
    elif schedule.schedule_type == 'specific_dates':
        if schedule.specific_dates:
            st.markdown(f"**Datas:** {len(schedule.specific_dates)} data(s) configurada(s)")
            if schedule.specific_date_times:
                st.markdown("**Horários por Data:**")
                for date, times in schedule.specific_date_times.items():
                    date_obj = datetime.fromisoformat(date)
                    st.markdown(f"- **{date_obj.strftime('%d/%m/%Y')}:** {', '.join(times)}")
            else:
                st.markdown(f"**Horário:** {schedule.time}")
            
            # Mostrar próximas 3 datas
            future_dates = []
            now = datetime.now().date()
            for date_str in schedule.specific_dates:
                try:
                    date_obj = datetime.fromisoformat(date_str).date()
                    if date_obj >= now:
                        future_dates.append(date_obj)
                except:
                    continue
            
            if future_dates:
                future_dates.sort()
                st.markdown("**Próximas Datas:**")
                for date in future_dates[:3]:
                    st.markdown(f"- {date.strftime('%d/%m/%Y')}")
    
    elif schedule.schedule_type == 'custom':
        st.markdown(f"**Período:** {schedule.start_date} até {schedule.end_date}")
        if schedule.days:
            st.markdown(f"**Dias:** {', '.join(schedule.days)}")
        st.markdown(f"**Horário:** {schedule.time}")
    
    elif schedule.schedule_type == 'interval':
        st.markdown(f"**Intervalo:** A cada {schedule.interval_minutes} minutos")
        st.markdown(f"**Período:** {schedule.interval_start_time} - {schedule.interval_end_time}")
        if schedule.days:
            st.markdown(f"**Dias:** {', '.join(schedule.days)}")
    
    # Próxima execução
    if schedule.next_run:
        try:
            next_run = datetime.fromisoformat(schedule.next_run)
            st.markdown(f"**Próxima Execução:** {next_run.strftime('%d/%m/%Y às %H:%M')}")
        except:
            pass

def show_edit_schedule_form(schedule):
    """Exibe formulário de edição para um agendamento."""
    st.subheader(f"✏️ Editando: {schedule.flow_name}")
    
    with st.form(f"edit_schedule_{schedule.id}"):
        # Descrição
        new_description = st.text_input("Descrição", value=schedule.description or "")
        
        # Configurações específicas por tipo
        if schedule.schedule_type in ['daily', 'weekly'] and schedule.times:
            # Múltiplos horários
            st.markdown("**Horários Atuais:**")
            new_times = []
            for i, time_str in enumerate(schedule.times):
                time_obj = datetime.strptime(time_str, "%H:%M").time()
                new_time = st.time_input(f"Horário {i+1}", value=time_obj, key=f"edit_time_{schedule.id}_{i}")
                new_times.append(new_time.strftime("%H:%M"))
            
            # Opção para adicionar mais horários
            if st.checkbox("Adicionar novo horário", key=f"add_time_{schedule.id}"):
                new_time = st.time_input("Novo horário", key=f"new_time_{schedule.id}")
                new_times.append(new_time.strftime("%H:%M"))
        
        elif schedule.schedule_type == 'weekly' and schedule.day_times:
            # Horários por dia
            st.markdown("**Horários por Dia:**")
            new_day_times = {}
            for day, times in schedule.day_times.items():
                with st.expander(f"{day}"):
                    day_schedule = []
                    for i, time_str in enumerate(times):
                        time_obj = datetime.strptime(time_str, "%H:%M").time()
                        time_input = st.time_input(f"Horário {i+1}", value=time_obj, key=f"edit_{schedule.id}_{day}_{i}")
                        day_schedule.append(time_input.strftime("%H:%M"))
                    new_day_times[day] = day_schedule
        
        elif schedule.schedule_type == 'interval':
            # Intervalo
            new_interval = st.number_input("Intervalo (minutos)", 
                                         min_value=1, max_value=1440, 
                                         value=schedule.interval_minutes)
            
            col1, col2 = st.columns(2)
            with col1:
                start_time_obj = datetime.strptime(schedule.interval_start_time, "%H:%M").time()
                new_start_time = st.time_input("Horário de início", value=start_time_obj)
            with col2:
                end_time_obj = datetime.strptime(schedule.interval_end_time, "%H:%M").time()
                new_end_time = st.time_input("Horário de fim", value=end_time_obj)
        
        elif schedule.schedule_type in ['daily', 'weekly', 'custom'] and schedule.time:
            # Horário único
            time_obj = datetime.strptime(schedule.time, "%H:%M").time()
            new_time = st.time_input("Horário", value=time_obj)
        
        # Botões de ação
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Salvar Alterações", type="primary"):
                try:
                    updates = {"description": new_description}
                    
                    # Aplicar mudanças específicas por tipo
                    if schedule.schedule_type in ['daily', 'weekly'] and schedule.times:
                        updates["times"] = new_times
                    elif schedule.schedule_type == 'weekly' and schedule.day_times:
                        updates["day_times"] = new_day_times
                    elif schedule.schedule_type == 'interval':
                        updates.update({
                            "interval_minutes": new_interval,
                            "interval_start_time": new_start_time.strftime("%H:%M"),
                            "interval_end_time": new_end_time.strftime("%H:%M")
                        })
                    elif schedule.schedule_type in ['daily', 'weekly', 'custom'] and schedule.time:
                        updates["time"] = new_time.strftime("%H:%M")
                    
                    scheduler.update_schedule(schedule.id, **updates)
                    st.success("Agendamento atualizado com sucesso!")
                    st.session_state[f"editing_{schedule.id}"] = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao atualizar: {e}")
        
        with col2:
            if st.form_submit_button("❌ Cancelar"):
                st.session_state[f"editing_{schedule.id}"] = False
                st.rerun()


def show_next_executions():
    """Mostra as próximas execuções agendadas."""
    st.subheader("📅 Próximas Execuções")
    
    next_runs = scheduler.get_next_runs(20)
    
    if not next_runs:
        st.info("📝 Nenhuma execução agendada.")
        return
    
    # Criar dataframe para exibição
    df_data = []
    type_icons = {
        'daily': '📅',
        'weekly': '📆', 
        'specific_dates': '🗓️',
        'custom': '⚙️'
    }
    
    type_names = {
        'daily': 'Diário',
        'weekly': 'Semanal',
        'specific_dates': 'Datas Específicas', 
        'custom': 'Personalizado'
    }
    
    for run in next_runs:
        schedule_type = run['schedule_type']
        icon = type_icons.get(schedule_type, '📋')
        type_name = type_names.get(schedule_type, 'Desconhecido')
        
        # Informações específicas por tipo
        details = ""
        if schedule_type == 'weekly' and run.get('days'):
            weekdays = {
                'Monday': 'Seg', 'Tuesday': 'Ter', 'Wednesday': 'Qua',
                'Thursday': 'Qui', 'Friday': 'Sex', 'Saturday': 'Sáb', 'Sunday': 'Dom'
            }
            days_str = ", ".join([weekdays.get(day, day) for day in run['days']])
            details = f"({days_str})"
        elif schedule_type == 'custom' and run.get('days'):
            weekdays = {
                'Monday': 'Seg', 'Tuesday': 'Ter', 'Wednesday': 'Qua',
                'Thursday': 'Qui', 'Friday': 'Sex', 'Saturday': 'Sáb', 'Sunday': 'Dom'
            }
            days_str = ", ".join([weekdays.get(day, day) for day in run['days']])
            details = f"({days_str})"
        
        df_data.append({
            'Fluxo': run['flow_name'],
            'Data/Hora': run['next_run_str'],
            'Tipo': f"{icon} {type_name}",
            'Horário': run['time'],
            'Detalhes': details or '-'
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True)
    
    # Estatísticas por tipo
    st.markdown("#### 📊 Estatísticas por Tipo")
    col1, col2, col3, col4 = st.columns(4)
    
    type_counts = {}
    for run in next_runs:
        schedule_type = run['schedule_type']
        type_counts[schedule_type] = type_counts.get(schedule_type, 0) + 1
    
    with col1:
        daily_count = type_counts.get('daily', 0)
        st.metric("📅 Diários", daily_count)
    
    with col2:
        weekly_count = type_counts.get('weekly', 0)
        st.metric("📆 Semanais", weekly_count)
    
    with col3:
        specific_count = type_counts.get('specific_dates', 0)
        st.metric("🗓️ Datas Específicas", specific_count)
    
    with col4:
        custom_count = type_counts.get('custom', 0)
        st.metric("⚙️ Personalizados", custom_count)
    
    # Gráfico das próximas execuções
    if len(next_runs) > 1:
        st.markdown("#### 📈 Timeline das Próximas Execuções")
        
        # Preparar dados para o gráfico
        chart_data = []
        for run in next_runs[:10]:  # Limitar a 10 para não poluir o gráfico
            schedule_type = run['schedule_type']
            type_name = type_names.get(schedule_type, 'Desconhecido')
            
            chart_data.append({
                'Fluxo': run['flow_name'],
                'Inicio': run['next_run'],
                'Fim': run['next_run'] + timedelta(minutes=30),  # Duração estimada
                'Tipo': type_name,
                'Horário': run['time']
            })
        
        if chart_data:
            fig = px.timeline(
                chart_data,
                x_start='Inicio',
                x_end='Fim',
                y='Fluxo',
                color='Tipo',
                title="Timeline das Próximas 10 Execuções",
                hover_data=['Horário']
            )
            
            fig.update_layout(
                height=400,
                xaxis_title="Data/Hora",
                yaxis_title="Fluxos"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Alertas e informações importantes
    st.markdown("#### ⚠️ Informações Importantes")
    
    # Verificar agendamentos que expiram em breve
    expiring_soon = []
    schedules = scheduler.get_all_schedules()
    
    for schedule in schedules:
        if schedule.schedule_type == 'specific_dates' and schedule.specific_dates:
            remaining = len(schedule.specific_dates)
            if remaining <= 3:
                expiring_soon.append(f"🗓️ **{schedule.flow_name}**: apenas {remaining} execução(ões) restante(s)")
        
        elif schedule.schedule_type == 'custom' and schedule.end_date:
            end_date = datetime.fromisoformat(schedule.end_date)
            days_to_end = (end_date.date() - datetime.now().date()).days
            if 0 <= days_to_end <= 7:
                expiring_soon.append(f"⚙️ **{schedule.flow_name}**: expira em {days_to_end} dia(s)")
    
    if expiring_soon:
        st.warning("Agendamentos que expiram em breve:")
        for alert in expiring_soon:
            st.write(f"• {alert}")
    else:
        st.success("✅ Todos os agendamentos estão ativos e dentro do prazo.")




# --- Roteador Principal ---
if st.session_state.view == 'dashboard':
    show_dashboard()
elif st.session_state.view == 'import_flow':
    show_import_flow()
elif st.session_state.view == 'schedules':
    show_schedules()
elif st.session_state.view == 'monitor':
    show_monitor()
elif st.session_state.view == 'edit_code':
    show_edit_code()
elif st.session_state.view == 'rename':
    show_rename()
elif st.session_state.view == 'delete':
    show_delete() 