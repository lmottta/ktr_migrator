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
from streamlit_autorefresh import st_autorefresh

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
    st.image("https://via.placeholder.com/200x80/1e3c72/ffffff?text=KTR+Platform", width=200)
    
    st.markdown("### 🎛️ Painel de Controle")
    
    if st.button("🏠 Dashboard", use_container_width=True):
        change_view('dashboard')
        st.rerun()
    
    if st.button("➕ Importar Fluxo", use_container_width=True):
        change_view('import_flow')
        st.rerun()
    
    if st.button("📊 Analytics", use_container_width=True):
        change_view('analytics')
        st.rerun()
    
    if st.button("⏰ Agendamentos", use_container_width=True):
        change_view('schedules')
        st.rerun()
    
    st.markdown("---")
    
    # Controles de Sistema
    st.markdown("### ⚙️ Sistema")
    
    if st.button("🔄 Atualizar Agora", use_container_width=True):
        st.rerun()
    
    # Status do Scheduler
    scheduler_status = "🟢 Ativo" if scheduler.running else "🔴 Inativo"
    st.metric("Status do Scheduler", scheduler_status)
    
    # Próximos agendamentos
    st.markdown("---")
    st.markdown("### ⏰ Próximas Execuções")
    
    next_runs = scheduler.get_next_runs(3)
    if next_runs:
        for run in next_runs:
            st.text(f"🔹 {run['flow_name']}")
            st.caption(f"   {run['next_run_str']}")
    else:
        st.info("Nenhum agendamento ativo")
    
    # Estatísticas gerais
    st.markdown("---")
    st.markdown("### 📈 Status Rápido")
    
    all_flows = flow_manager.get_all_flows()
    total_flows = len(all_flows)
    running_flows = len([f for f in all_flows if executor.is_flow_running(f.id)])
    successful_flows = len([f for f in all_flows if f.execution_status == "Sucesso"])
    total_schedules = len(scheduler.get_all_schedules())
    
    st.metric("Total de Fluxos", total_flows)
    st.metric("Em Execução", running_flows)
    st.metric("Sucessos", successful_flows)
    st.metric("Agendamentos", total_schedules)

# --- Funções de UI ---

def show_dashboard():
    """Dashboard principal melhorado."""
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🚀 KTR Platform Pro - Central de Jobs</h1>
        <p>Gerencie, execute e monitore seus fluxos de dados migrados do Pentaho</p>
    </div>
    """, unsafe_allow_html=True)
    
    all_flows = flow_manager.get_all_flows()
    
    # Métricas principais
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_flows = len(all_flows)
    running_flows = len([f for f in all_flows if executor.is_flow_running(f.id)])
    ready_flows = len([f for f in all_flows if f.status == "Pronto"])
    successful_flows = len([f for f in all_flows if f.execution_status == "Sucesso"])
    failed_flows = len([f for f in all_flows if f.execution_status in ["Falha", "Erro"]])
    
    with col1:
        st.metric("🗂️ Total", total_flows)
    with col2:
        st.metric("▶️ Executando", running_flows, delta=None)
    with col3:
        st.metric("✅ Prontos", ready_flows)
    with col4:
        st.metric("🎯 Sucessos", successful_flows)
    with col5:
        st.metric("❌ Falhas", failed_flows)
    
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
                cols_actions = st.columns(4)
                
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
                    if st.button("📊", key=f"monitor_card_{flow.id}", help="Monitorar"):
                        change_view('monitor', flow.id)
                        st.rerun()
                
                with cols_actions[2]:
                    if st.button("✏️", key=f"rename_card_{flow.id}", help="Renomear"):
                        change_view('rename', flow.id)
                        st.rerun()
                
                with cols_actions[3]:
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


def show_analytics():
    """Página de analytics com gráficos."""
    st.title("📊 Analytics & Insights")
    
    all_flows = flow_manager.get_all_flows()
    
    if not all_flows:
        st.info("Nenhum fluxo disponível para análise.")
        return
    
    # Métricas de desempenho
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de status
        status_counts = {}
        for flow in all_flows:
            status = flow.execution_status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        fig_status = px.pie(
            values=list(status_counts.values()),
            names=list(status_counts.keys()),
            title="Distribuição de Status de Execução"
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Gráfico de durações
        durations = [f.execution_duration for f in all_flows if f.execution_duration]
        names = [f.name for f in all_flows if f.execution_duration]
        
        if durations:
            fig_duration = px.bar(
                x=names,
                y=durations,
                title="Duração das Últimas Execuções (segundos)",
                labels={'x': 'Fluxos', 'y': 'Duração (s)'}
            )
            fig_duration.update_xaxes(tickangle=45)
            st.plotly_chart(fig_duration, use_container_width=True)
        else:
            st.info("Nenhuma execução finalizada para análise de duração.")
    
    # Timeline de execuções
    st.markdown("### 📈 Timeline de Execuções")
    
    executions = []
    for flow in all_flows:
        if flow.execution_start_time and flow.execution_end_time:
            executions.append({
                'Fluxo': flow.name,
                'Início': pd.to_datetime(flow.execution_start_time),
                'Fim': pd.to_datetime(flow.execution_end_time),
                'Status': flow.execution_status
            })
    
    if executions:
        df_exec = pd.DataFrame(executions)
        
        # Gráfico de timeline
        fig_timeline = px.timeline(
            df_exec,
            x_start="Início",
            x_end="Fim",
            y="Fluxo",
            color="Status",
            title="Timeline das Execuções"
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("Nenhuma execução finalizada para timeline.")


def show_import_flow():
    """Página de importação melhorada."""
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
    """Página de monitoramento melhorada."""
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
    
    # Status em tempo real
    is_running = executor.is_flow_running(flow_id)
    
    if is_running:
        st.markdown("🔴 **EXECUTANDO EM TEMPO REAL**")
    
    # Métricas detalhadas
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        status_color = "🟢" if flow.execution_status == "Sucesso" else "🔴" if flow.execution_status in ["Falha", "Erro"] else "🟡"
        st.metric("Status", f"{status_color} {flow.execution_status}")
    
    with col2:
        if flow.execution_duration:
            st.metric("Duração", f"{flow.execution_duration:.2f}s")
        else:
            st.metric("Duração", "-")
    
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
            st.metric("Finalizado", "-" if not is_running else "Executando...")
    
    with col5:
        logs_count = len(flow.execution_logs)
        st.metric("Logs", f"{logs_count} entradas")
    
    # Controles de execução
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
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
    
    # Logs em tempo real
    st.markdown("---")
    st.subheader("📋 Logs de Execução")
    
    if flow.execution_logs:
        # Container para logs com altura fixa e scroll
        logs_container = st.container()
        
        with logs_container:
            # Mostrar apenas os últimos 100 logs para performance
            recent_logs = flow.execution_logs[-100:]
            
            for log_entry in recent_logs:
                # Colorir logs baseado no conteúdo
                if "ERROR" in log_entry or "❌" in log_entry:
                    st.error(log_entry)
                elif "WARNING" in log_entry or "⚠️" in log_entry:
                    st.warning(log_entry)
                elif "SUCCESS" in log_entry or "✅" in log_entry:
                    st.success(log_entry)
                else:
                    st.text(log_entry)
    else:
        st.info("📝 Nenhum log disponível. Execute o fluxo para gerar logs.")


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


def show_schedules():
    """Página de gerenciamento de agendamentos."""
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
elif st.session_state.view == 'analytics':
    show_analytics()
elif st.session_state.view == 'schedules':
    show_schedules()
elif st.session_state.view == 'monitor':
    show_monitor()
elif st.session_state.view == 'rename':
    show_rename()
elif st.session_state.view == 'delete':
    show_delete() 