"""
KTR Migrator - Interface Web Principal
Aplicação Streamlit para conversão de pipelines Pentaho
"""

import streamlit as st
import tempfile
import os
import zipfile
import io
from pathlib import Path
import sys

# Configurar path para imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "src"))

# Imports dos módulos do projeto
try:
    from src.parser.ktr_parser import KTRParser
    from src.generator.code_generator import CodeGenerator
    from src.analyzer.pipeline_analyzer import PipelineAnalyzer
except ImportError as e:
    st.error(f"❌ Erro ao importar módulos: {e}")
    st.error("Certifique-se de que está executando no diretório raiz do projeto.")
    st.stop()

# Configuração da página
st.set_page_config(
    page_title="KTR Migrator",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .header-container {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1e3c72;
        margin: 0.5rem 0;
    }
    
    .success-box {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    
    .progress-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin: 1rem 0;
    }
    
    .progress-step {
        display: flex;
        align-items: center;
        padding: 0.75rem 0;
        border-bottom: 1px solid #e9ecef;
    }
    
    .progress-step:last-child {
        border-bottom: none;
    }
    
    .progress-icon {
        font-size: 1.5rem;
        margin-right: 1rem;
        min-width: 2rem;
        text-align: center;
    }
    
    .progress-content {
        flex: 1;
    }
    
    .progress-title {
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    
    .progress-description {
        font-size: 0.875rem;
        color: #6c757d;
        margin: 0;
    }
    
    .running {
        color: #007bff;
    }
    
    .completed {
        color: #28a745;
    }
    
    .pending {
        color: #6c757d;
    }
    
    .error {
        color: #dc3545;
    }
    
    /* Animação para ícone de loading */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .spinning {
        animation: spin 1s linear infinite;
    }
    
    /* Animação para progresso */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    .pulsing {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Estilo para métricas */
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        transition: transform 0.2s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

def create_progress_step(step_num, total_steps, title, description, status="running"):
    """Cria um componente visual para acompanhar uma etapa do progresso"""
    
    # Ícones baseados no status
    icons = {
        "pending": "⏳",
        "running": "🔄", 
        "completed": "✅",
        "error": "❌"
    }
    
    # Cores baseadas no status
    colors = {
        "pending": "#6c757d",
        "running": "#007bff",
        "completed": "#28a745", 
        "error": "#dc3545"
    }
    
    progress_percent = (step_num / total_steps) * 100
    
    col1, col2 = st.columns([1, 6])
    
    with col1:
        st.markdown(f"<div style='font-size: 1.5rem; text-align: center;'>{icons[status]}</div>", 
                   unsafe_allow_html=True)
    
    with col2:
        if status == "running":
            st.markdown(f"**{title}** 🔄")
            st.markdown(f"<small style='color: {colors[status]};'>{description}</small>", 
                       unsafe_allow_html=True)
        elif status == "completed":
            st.markdown(f"**{title}** ✅")
            st.markdown(f"<small style='color: {colors[status]};'>{description}</small>", 
                       unsafe_allow_html=True)
        else:
            st.markdown(f"**{title}**")
            st.markdown(f"<small style='color: {colors[status]};'>{description}</small>", 
                       unsafe_allow_html=True)

def main():
    """Função principal da aplicação"""
    
    # Header
    st.markdown("""
    <div class="header-container">
        <h1>🔄 KTR Migrator</h1>
        <p>Migração Inteligente de Pipelines Pentaho para Python</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Controles")
        
        # Upload de arquivo
        uploaded_file = st.file_uploader(
            "📁 Arquivo KTR",
            type=['ktr'],
            help="Selecione um arquivo .ktr do Pentaho"
        )
        
        if uploaded_file:
            st.success(f"✅ {uploaded_file.name}")
            
            # Botões de ação
            st.markdown("### 🚀 Ações")
            
            col1, col2 = st.columns(2)
            
            with col1:
                analyze_btn = st.button("🔍 Analisar", type="primary", key="analyze")
            
            with col2:
                convert_btn = st.button("🔄 Converter", type="secondary", key="convert")
            
            # Opções avançadas
            with st.expander("⚙️ Opções"):
                optimize = st.checkbox("🚀 Otimizações", value=True)
                format_code = st.checkbox("🎨 Formatar código", value=True)
                generate_tests = st.checkbox("🧪 Gerar testes", value=True)
        else:
            st.info("📁 Selecione um arquivo KTR para começar")
    
    # Área principal
    if uploaded_file:
        if analyze_btn:
            analyze_pipeline(uploaded_file)
        
        if convert_btn:
            convert_pipeline(uploaded_file)
        
        # Mostrar resultados salvos
        if 'analysis_results' in st.session_state:
            show_analysis_results()
        
        if 'conversion_results' in st.session_state:
            show_conversion_results()
    
    else:
        show_welcome_screen()

def show_welcome_screen():
    """Tela de boas-vindas"""
    
    st.markdown("## 👋 Bem-vindo ao KTR Migrator!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🔍 Análise Inteligente
        - Detecta padrões ETL automaticamente
        - Calcula complexidade do pipeline
        - Sugere otimizações específicas
        """)
    
    with col2:
        st.markdown("""
        ### 🐍 Código Python
        - Pipelines modernos com Pandas
        - Conexões SQLAlchemy
        - Logging estruturado
        """)
    
    with col3:
        st.markdown("""
        ### 📊 Interface Visual
        - Upload intuitivo
        - Preview de resultados
        - Download instantâneo
        """)
    
    st.markdown("---")
    
    # Instruções de uso
    st.markdown("## 📖 Como usar")
    
    st.markdown("""
    1. **📁 Upload**: Selecione seu arquivo .ktr na barra lateral
    2. **🔍 Analisar**: Clique no botão "Analisar" para ver detalhes
    3. **🔄 Converter**: Clique em "Converter" para gerar código Python
    4. **📥 Download**: Baixe o projeto Python gerado
    """)
    
    # Exemplo de métricas
    st.markdown("## 📊 Exemplo de Análise")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Complexidade", "44/100", "baixa")
    with col2:
        st.metric("⚡ Performance", "80%", "+30%")
    with col3:
        st.metric("🔧 Steps", "3", "detectados")
    with col4:
        st.metric("🚀 Otimizações", "4", "sugestões")

def analyze_pipeline(uploaded_file):
    """Analisa o pipeline KTR com progresso detalhado"""
    
    try:
        # Container para progresso detalhado
        progress_container = st.container()
        
        with progress_container:
            st.markdown("### 🔍 Analisando Pipeline KTR")
            
            # Barra de progresso principal
            main_progress = st.progress(0)
            status_container = st.container()
            
            # Etapa 1: Preparação do arquivo
            with status_container:
                current_step = st.empty()
                current_step.markdown("🔄 **Etapa 1/5:** Preparando arquivo para análise...")
                main_progress.progress(20)
                
                # Salvar arquivo temporário
                with tempfile.NamedTemporaryFile(delete=False, suffix='.ktr') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                current_step.markdown("✅ **Etapa 1/5:** Arquivo preparado com sucesso")
            
            # Etapa 2: Parse do XML
            current_step.markdown("🔄 **Etapa 2/5:** Analisando estrutura XML do KTR...")
            main_progress.progress(40)
            
            parser = KTRParser()
            ktr_model = parser.parse_file(tmp_path)
            
            current_step.markdown(f"✅ **Etapa 2/5:** Estrutura analisada - {len(ktr_model.steps)} steps, {len(ktr_model.connections)} conexões")
            
            # Etapa 3: Identificação de componentes
            current_step.markdown("🔄 **Etapa 3/5:** Identificando extractors, transformers e loaders...")
            main_progress.progress(60)
            
            # Classificar steps
            extractors = [step for step in ktr_model.steps if step.is_input]
            transformers = [step for step in ktr_model.steps if step.is_transform]
            loaders = [step for step in ktr_model.steps if step.is_output]
            
            current_step.markdown(f"✅ **Etapa 3/5:** Componentes identificados - {len(extractors)} extractors, {len(transformers)} transformers, {len(loaders)} loaders")
            
            # Etapa 4: Análise avançada
            current_step.markdown("🔄 **Etapa 4/5:** Executando análise de complexidade e padrões...")
            main_progress.progress(80)
            
            analyzer = PipelineAnalyzer()
            analysis = analyzer.analyze_pipeline(ktr_model)
            
            current_step.markdown(f"✅ **Etapa 4/5:** Análise concluída - Complexidade: {analysis.complexity_score}/100")
            
            # Etapa 5: Finalização
            current_step.markdown("🔄 **Etapa 5/5:** Finalizando análise...")
            main_progress.progress(95)
            
            # Salvar resultados
            st.session_state.ktr_model = ktr_model
            st.session_state.analysis = analysis
            st.session_state.analysis_results = True
            
            # Cleanup
            os.unlink(tmp_path)
            
            current_step.markdown("✅ **Etapa 5/5:** Análise finalizada com sucesso!")
            main_progress.progress(100)
            
            # Mostrar resumo final
            st.success(f"🎉 **Análise concluída!** Pipeline '{ktr_model.name}' analisado com sucesso.")
            
            # Pequeno delay para mostrar o resultado
            import time
            time.sleep(0.5)
            st.rerun()
        
    except Exception as e:
        st.error(f"❌ Erro na análise: {str(e)}")

def show_analysis_results():
    """Mostra resultados da análise"""
    
    if 'analysis' not in st.session_state:
        return
    
    ktr_model = st.session_state.ktr_model
    analysis = st.session_state.analysis
    
    st.markdown("## 📊 Resultados da Análise")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Complexidade", f"{analysis.complexity_score}/100")
    with col2:
        st.metric("⚡ Performance", f"{analysis.estimated_performance_gain}%")
    with col3:
        st.metric("🔧 Steps", len(ktr_model.steps))
    with col4:
        st.metric("🔗 Conexões", len(ktr_model.connections))
    
    # Informações do pipeline
    with st.container():
        st.markdown("### 📋 Informações do Pipeline")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Nome:** {ktr_model.name}")
            st.write(f"**Steps detectados:** {len(ktr_model.steps)}")
        
        with col2:
            st.write(f"**Conexões:** {len(ktr_model.connections)}")
            st.write(f"**Hops:** {len(ktr_model.hops)}")
    
    # Detalhes dos steps
    if ktr_model.steps:
        st.markdown("### 🔧 Steps Detectados")
        
        for i, step in enumerate(ktr_model.steps):
            with st.expander(f"📌 {step.name} ({step.type.value})"):
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Tipo:** {step.type.value}")
                    category = "Input" if step.is_input else "Output" if step.is_output else "Transform"
                    st.write(f"**Categoria:** {category}")
                
                with col2:
                    if hasattr(step, 'connection_name') and step.connection_name:
                        st.write(f"**Conexão:** {step.connection_name}")
                    
                    if hasattr(step, 'table') and step.table:
                        st.write(f"**Tabela:** {step.table}")
                
                # SQL preview
                if hasattr(step, 'sql') and step.sql:
                    st.markdown("**SQL:**")
                    sql_preview = step.sql[:200] + "..." if len(step.sql) > 200 else step.sql
                    st.code(sql_preview, language="sql")
    
    # Padrões detectados
    if analysis.patterns:
        st.markdown("### 🎯 Padrões Detectados")
        
        for pattern in analysis.patterns:
            st.success(f"**{pattern.name}**: {pattern.description} (Confiança: {pattern.confidence:.1%})")
    
    # Otimizações sugeridas
    if analysis.optimizations:
        st.markdown("### 🚀 Otimizações Sugeridas")
        
        for opt in analysis.optimizations:
            impact_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            
            with st.container():
                st.markdown(f"{impact_emoji.get(opt.impact, '🔵')} **{opt.type.replace('_', ' ').title()}**")
                st.write(opt.description)
                
                if opt.code_example:
                    with st.expander("👀 Ver exemplo de código"):
                        st.code(opt.code_example, language="python")

def convert_pipeline(uploaded_file):
    """Converte pipeline para Python com progresso detalhado"""
    
    try:
        # Container para progresso detalhado
        progress_container = st.container()
        
        with progress_container:
            st.markdown("### 🏗️ Convertendo Pipeline para Python")
            
            # Barra de progresso principal
            main_progress = st.progress(0)
            status_container = st.container()
            
            # Etapa 1: Verificação ou Parse inicial
            with status_container:
                current_step = st.empty()
                current_step.markdown("🔄 **Etapa 1/7:** Preparando dados do pipeline...")
                main_progress.progress(14)
                
                # Verificar se já foi analisado
                if 'ktr_model' not in st.session_state:
                    current_step.markdown("🔄 **Etapa 1/7:** Fazendo análise rápida do KTR...")
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.ktr') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    parser = KTRParser()
                    ktr_model = parser.parse_file(tmp_path)
                    os.unlink(tmp_path)
                else:
                    ktr_model = st.session_state.ktr_model
                
                current_step.markdown(f"✅ **Etapa 1/7:** Dados preparados - Pipeline '{ktr_model.name}'")
            
            # Etapa 2: Inicialização e geração completa do projeto
            current_step.markdown("🔄 **Etapa 2/4:** Inicializando gerador de código Python...")
            main_progress.progress(25)
            
            generator = CodeGenerator()
            
            current_step.markdown("✅ **Etapa 2/4:** Gerador inicializado")
            
            # Etapa 3: Geração completa do projeto com todos os componentes ETL
            current_step.markdown("🔄 **Etapa 3/4:** Gerando projeto completo (pipeline, extractors, transformers, loaders, utils)...")
            main_progress.progress(50)
            
            # Usar diretório temporário para geração completa
            with tempfile.TemporaryDirectory() as temp_dir:
                # Gerar projeto completo usando o método corrigido
                project = generator.generate_pipeline(ktr_model, temp_dir)
                
                # Ler todos os arquivos gerados
                project_files = {}
                for file_path, content in project.files.items():
                    if isinstance(content, str):
                        project_files[file_path] = content
                    else:
                        # Se for um caminho de arquivo, ler o conteúdo
                        full_path = Path(temp_dir) / file_path
                        if full_path.exists():
                            with open(full_path, 'r', encoding='utf-8') as f:
                                project_files[file_path] = f.read()
                
                # Atualizar o projeto com todos os arquivos
                project.files = project_files
            
            current_step.markdown(f"✅ **Etapa 3/4:** Projeto completo gerado - {len(project.files)} arquivos criados")
            
            # Etapa 4: Finalização
            current_step.markdown("🔄 **Etapa 4/4:** Finalizando conversão...")
            main_progress.progress(75)
            
            # Salvar resultados
            st.session_state.project = project
            st.session_state.conversion_results = True
            
            current_step.markdown("✅ **Etapa 4/4:** Conversão finalizada com sucesso!")
            main_progress.progress(100)
            
            # Calcular estatísticas finais
            total_lines = sum(len(content.split('\n')) for content in project.files.values())
            total_size = sum(len(content) for content in project.files.values())
            
            # Mostrar resumo final
            st.success(f"🎉 **Conversão concluída!** {len(project.files)} arquivos gerados, {total_lines} linhas de código, {total_size/1024:.1f} KB")
            
            # Pequeno delay para mostrar o resultado
            import time
            time.sleep(0.5)
            st.rerun()
        
    except Exception as e:
        st.error(f"❌ Erro na conversão: {str(e)}")
        import traceback
        st.code(traceback.format_exc(), language="python")

def show_conversion_results():
    """Mostra resultados da conversão"""
    
    if 'project' not in st.session_state:
        return
    
    project = st.session_state.project
    
    st.markdown("## 🐍 Projeto Python Gerado")
    
    # Métricas do projeto
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📄 Arquivos", len(project.files))
    with col2:
        st.metric("📦 Dependências", len(project.dependencies))
    with col3:
        total_lines = sum(len(content.split('\n')) for content in project.files.values())
        st.metric("🐍 Linhas", total_lines)
    with col4:
        total_size = sum(len(content) for content in project.files.values())
        st.metric("📏 Tamanho", f"{total_size / 1024:.1f} KB")
    
    # Lista de arquivos
    st.markdown("### 📁 Arquivos Gerados")
    
    file_types = {
        '.py': '🐍',
        '.md': '📄', 
        '.txt': '📝',
        '.env': '⚙️'
    }
    
    for file_path in project.files.keys():
        ext = Path(file_path).suffix
        icon = file_types.get(ext, '📄')
        st.write(f"{icon} `{file_path}`")
    
    # Preview dos arquivos principais
    st.markdown("### 👀 Preview dos Arquivos")
    
    for file_path, content in project.files.items():
        with st.expander(f"📄 {file_path}"):
            
            # Detectar linguagem
            if file_path.endswith('.py'):
                language = "python"
            elif file_path.endswith('.md'):
                language = "markdown"
            elif file_path.endswith('.sql'):
                language = "sql"
            else:
                language = "text"
            
            # Limitar preview
            preview_length = 1000
            if len(content) > preview_length:
                preview = content[:preview_length] + "\n\n... (arquivo truncado para preview)"
            else:
                preview = content
            
            st.code(preview, language=language)
    
    # Botão de download
    st.markdown("### 📥 Download")
    
    zip_data = create_zip_download(project.files)
    
    if zip_data:
        st.download_button(
            label="📦 Download Projeto Python",
            data=zip_data,
            file_name=f"{project.name}_python_pipeline.zip",
            mime="application/zip",
            type="primary"
        )
        
        st.success("✅ Projeto pronto para download!")
    else:
        st.error("❌ Erro ao preparar download")

def create_zip_download(files_dict):
    """Cria arquivo ZIP para download"""
    
    try:
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path, content in files_dict.items():
                zipf.writestr(file_path, content)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
        
    except Exception as e:
        st.error(f"Erro ao criar ZIP: {e}")
        return None

if __name__ == "__main__":
    main() 