"""
Interface Web para KTR Migrator
Streamlit App para upload e conversão de arquivos KTR
"""

import streamlit as st
import pandas as pd
import tempfile
import os
import json
import zipfile
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List
import sys

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.parser.ktr_parser import KTRParser
from src.generator.code_generator import CodeGenerator
from src.analyzer.pipeline_analyzer import PipelineAnalyzer
from src.models.ktr_models import KTRModel, Step

# Configuração da página
st.set_page_config(
    page_title="KTR Migrator",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    
    .step-card {
        background: #fff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
    }
    
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Função principal da interface"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔄 KTR Migrator</h1>
        <p>Migração Inteligente de Pipelines Pentaho para Python</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Controles")
        
        # Upload de arquivo
        uploaded_file = st.file_uploader(
            "📁 Selecione seu arquivo KTR",
            type=['ktr'],
            help="Faça upload do arquivo .ktr que deseja converter"
        )
        
        if uploaded_file:
            st.success(f"✅ Arquivo carregado: {uploaded_file.name}")
            
            # Opções de conversão
            st.subheader("⚙️ Opções")
            
            optimize = st.checkbox("🚀 Aplicar otimizações", value=True)
            format_code = st.checkbox("🎨 Formatar código", value=True)
            generate_tests = st.checkbox("🧪 Gerar testes", value=True)
            
            # Botão de análise
            if st.button("🔍 Analisar KTR", type="primary"):
                analyze_ktr(uploaded_file)
            
            # Botão de conversão
            if st.button("🔄 Converter para Python", type="secondary"):
                convert_ktr(uploaded_file, optimize, format_code, generate_tests)
    
    # Área principal
    if not uploaded_file:
        show_welcome_screen()
    else:
        show_file_info(uploaded_file)

def show_welcome_screen():
    """Tela de boas-vindas"""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🔍 Análise Inteligente</h3>
            <p>Detecta padrões ETL e sugere otimizações automaticamente</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🐍 Código Python</h3>
            <p>Gera pipelines Python modernos com pandas e SQLAlchemy</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Visualização</h3>
            <p>Interface gráfica para acompanhar todo o processo</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Exemplo de uso
    st.subheader("📖 Como usar")
    
    st.markdown("""
    1. **📁 Upload**: Faça upload do seu arquivo .ktr na barra lateral
    2. **🔍 Análise**: Clique em "Analisar KTR" para ver detalhes do pipeline
    3. **⚙️ Configurar**: Escolha as opções de conversão desejadas
    4. **🔄 Converter**: Clique em "Converter para Python" para gerar o código
    5. **📥 Download**: Baixe o projeto Python gerado
    """)
    
    # Estatísticas do exemplo
    st.subheader("📊 Exemplo de Análise")
    
    example_data = {
        "Métrica": ["Complexidade", "Performance Estimada", "Steps Detectados", "Otimizações"],
        "Valor": [44, "80%", 3, 4],
        "Status": ["🟡 Médio", "🟢 Alto", "🟢 Bom", "🟢 Disponível"]
    }
    
    df_example = pd.DataFrame(example_data)
    st.dataframe(df_example, use_container_width=True)

def show_file_info(uploaded_file):
    """Mostra informações do arquivo carregado"""
    
    st.subheader(f"📄 Arquivo: {uploaded_file.name}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.metric("📊 Tamanho", f"{uploaded_file.size / 1024:.1f} KB")
    
    with col2:
        st.metric("📝 Tipo", uploaded_file.type or "application/xml")

def analyze_ktr(uploaded_file):
    """Analisa o arquivo KTR e mostra resultados"""
    
    try:
        # Salvar arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ktr') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        # Parse do KTR
        with st.spinner("🔍 Analisando arquivo KTR..."):
            parser = KTRParser()
            ktr_model = parser.parse_file(tmp_path)
        
        # Análise avançada
        with st.spinner("📊 Executando análise avançada..."):
            analyzer = PipelineAnalyzer()
            analysis = analyzer.analyze_pipeline(ktr_model)
        
        # Guardar resultados no session state
        st.session_state.ktr_model = ktr_model
        st.session_state.analysis = analysis
        
        # Mostrar resultados
        show_analysis_results(ktr_model, analysis)
        
        # Cleanup
        os.unlink(tmp_path)
        
    except Exception as e:
        st.error(f"❌ Erro na análise: {str(e)}")

def show_analysis_results(ktr_model: KTRModel, analysis):
    """Mostra resultados da análise"""
    
    st.success("✅ Análise concluída!")
    
    # Métricas principais
    st.subheader("📊 Métricas do Pipeline")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Complexidade", f"{analysis.complexity_score}/100")
    
    with col2:
        st.metric("⚡ Performance", f"{analysis.estimated_performance_gain}%")
    
    with col3:
        st.metric("🔧 Steps", len(ktr_model.steps))
    
    with col4:
        st.metric("🚀 Otimizações", len(analysis.optimizations))
    
    # Visualização do fluxo
    st.subheader("🔄 Fluxo do Pipeline")
    show_pipeline_flow(ktr_model)
    
    # Detalhes dos steps
    st.subheader("🔧 Detalhes dos Steps")
    show_steps_details(ktr_model)
    
    # Padrões detectados
    if analysis.patterns:
        st.subheader("🎯 Padrões Detectados")
        for pattern in analysis.patterns:
            st.markdown(f"""
            <div class="step-card">
                <h4>📋 {pattern.name}</h4>
                <p>{pattern.description}</p>
                <p><strong>Confiança:</strong> {pattern.confidence:.1%}</p>
                <p><strong>Steps envolvidos:</strong> {', '.join(pattern.steps_involved)}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Otimizações sugeridas
    if analysis.optimizations:
        st.subheader("🚀 Otimizações Sugeridas")
        for opt in analysis.optimizations:
            impact_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            st.markdown(f"""
            <div class="step-card">
                <h4>{impact_color.get(opt.impact, '🔵')} {opt.type.replace('_', ' ').title()}</h4>
                <p>{opt.description}</p>
                <p><strong>Impacto:</strong> {opt.impact.title()}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if opt.code_example:
                with st.expander("👀 Ver exemplo de código"):
                    st.code(opt.code_example, language="python")

def show_pipeline_flow(ktr_model: KTRModel):
    """Visualiza o fluxo do pipeline"""
    
    # Criar grafo do pipeline
    fig = go.Figure()
    
    # Posições dos nodes
    positions = {}
    y_pos = 0
    
    for i, step in enumerate(ktr_model.steps):
        positions[step.name] = (i * 2, y_pos)
    
    # Adicionar edges (hops)
    for hop in ktr_model.hops:
        if hop.from_step in positions and hop.to_step in positions:
            x_from, y_from = positions[hop.from_step]
            x_to, y_to = positions[hop.to_step]
            
            fig.add_trace(go.Scatter(
                x=[x_from, x_to],
                y=[y_from, y_to],
                mode='lines',
                line=dict(color='#667eea', width=2),
                showlegend=False,
                hoverinfo='none'
            ))
    
    # Adicionar nodes (steps)
    for step in ktr_model.steps:
        x, y = positions[step.name]
        
        color = '#28a745' if step.is_input else '#dc3545' if step.is_output else '#ffc107'
        
        fig.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers+text',
            marker=dict(size=30, color=color),
            text=[step.name],
            textposition="bottom center",
            showlegend=False,
            hovertemplate=f"<b>{step.name}</b><br>Tipo: {step.type.value}<extra></extra>"
        ))
    
    fig.update_layout(
        title="🔄 Fluxo do Pipeline",
        showlegend=False,
        height=400,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_steps_details(ktr_model: KTRModel):
    """Mostra detalhes dos steps"""
    
    for step in ktr_model.steps:
        
        # Ícone baseado no tipo
        icon = "📥" if step.is_input else "📤" if step.is_output else "⚙️"
        
        with st.expander(f"{icon} {step.name} ({step.type.value})"):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Tipo:** {step.type.value}")
                st.write(f"**Categoria:** {'Input' if step.is_input else 'Output' if step.is_output else 'Transform'}")
            
            with col2:
                if hasattr(step, 'connection_name') and step.connection_name:
                    st.write(f"**Conexão:** {step.connection_name}")
                
                if hasattr(step, 'sql') and step.sql:
                    st.write("**SQL:**")
                    st.code(step.sql[:200] + "..." if len(step.sql) > 200 else step.sql, language="sql")

def convert_ktr(uploaded_file, optimize: bool, format_code: bool, generate_tests: bool):
    """Converte KTR para Python"""
    
    try:
        # Verificar se já foi analisado
        if 'ktr_model' not in st.session_state:
            st.warning("⚠️ Faça a análise primeiro!")
            return
        
        ktr_model = st.session_state.ktr_model
        
        # Gerar código
        with st.spinner("🐍 Gerando código Python..."):
            generator = CodeGenerator()
            
            # Criar diretório temporário
            with tempfile.TemporaryDirectory() as temp_dir:
                project = generator.generate_pipeline(ktr_model, temp_dir)
                
                # Mostrar resultados
                show_conversion_results(project, temp_dir)
        
    except Exception as e:
        st.error(f"❌ Erro na conversão: {str(e)}")

def show_conversion_results(project, temp_dir: str):
    """Mostra resultados da conversão"""
    
    st.success("✅ Conversão concluída!")
    
    # Métricas do projeto
    st.subheader("📊 Projeto Gerado")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📄 Arquivos", len(project.files))
    
    with col2:
        st.metric("📦 Dependências", len(project.dependencies))
    
    with col3:
        st.metric("🐍 Linhas", sum(len(content.split('\n')) for content in project.files.values()))
    
    with col4:
        st.metric("📁 Tamanho", f"{sum(len(content) for content in project.files.values()) / 1024:.1f} KB")
    
    # Preview dos arquivos
    st.subheader("👀 Preview dos Arquivos")
    
    for file_path, content in project.files.items():
        with st.expander(f"📄 {file_path}"):
            
            # Detectar linguagem para highlight
            language = "python" if file_path.endswith('.py') else "markdown" if file_path.endswith('.md') else "text"
            
            st.code(content[:2000] + "..." if len(content) > 2000 else content, language=language)
    
    # Botão de download
    zip_file = create_download_zip(project, temp_dir)
    
    if zip_file:
        with open(zip_file, 'rb') as f:
            st.download_button(
                label="📥 Download Projeto Python",
                data=f.read(),
                file_name=f"{project.name}_python_pipeline.zip",
                mime="application/zip",
                type="primary"
            )

def create_download_zip(project, temp_dir: str) -> str:
    """Cria arquivo ZIP para download"""
    
    zip_path = os.path.join(temp_dir, "pipeline_project.zip")
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path, content in project.files.items():
            zipf.writestr(file_path, content)
    
    return zip_path

if __name__ == "__main__":
    main() 