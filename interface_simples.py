"""
Interface Simples para KTR Migrator
Versão básica e funcional
"""

import streamlit as st
import tempfile
import os
import json
import zipfile
from pathlib import Path
import sys

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from src.parser.ktr_parser import KTRParser
    from src.generator.code_generator import CodeGenerator
    from src.analyzer.pipeline_analyzer import PipelineAnalyzer
    from src.models.ktr_models import KTRModel, Step
except ImportError as e:
    st.error(f"Erro ao importar módulos: {e}")
    st.stop()

# Configuração da página
st.set_page_config(
    page_title="KTR Migrator",
    page_icon="🔄",
    layout="wide"
)

def main():
    """Função principal"""
    
    # Header
    st.title("🔄 KTR Migrator - Interface Web")
    st.markdown("**Migração de Pipelines Pentaho para Python**")
    st.markdown("---")
    
    # Upload de arquivo
    uploaded_file = st.file_uploader(
        "📁 Selecione seu arquivo KTR",
        type=['ktr'],
        help="Faça upload do arquivo .ktr que deseja converter"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ Arquivo carregado: {uploaded_file.name}")
        
        # Opções
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔍 Analisar KTR", type="primary"):
                analyze_ktr(uploaded_file)
        
        with col2:
            if st.button("🔄 Converter para Python"):
                convert_ktr(uploaded_file)
    
    else:
        # Instruções
        st.info("👆 Faça upload de um arquivo .ktr para começar")
        
        # Exemplo
        with st.expander("📖 Como usar"):
            st.markdown("""
            1. **Upload**: Selecione seu arquivo .ktr
            2. **Analisar**: Veja detalhes do pipeline
            3. **Converter**: Gere o código Python
            4. **Download**: Baixe o projeto gerado
            """)

def analyze_ktr(uploaded_file):
    """Analisa o arquivo KTR"""
    
    try:
        # Salvar arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ktr') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        # Parse
        with st.spinner("🔍 Analisando..."):
            parser = KTRParser()
            ktr_model = parser.parse_file(tmp_path)
            
            analyzer = PipelineAnalyzer()
            analysis = analyzer.analyze_pipeline(ktr_model)
        
        # Resultados
        st.success("✅ Análise concluída!")
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🎯 Complexidade", f"{analysis.complexity_score}/100")
        with col2:
            st.metric("⚡ Performance", f"{analysis.estimated_performance_gain}%")
        with col3:
            st.metric("🔧 Steps", len(ktr_model.steps))
        with col4:
            st.metric("🔗 Conexões", len(ktr_model.connections))
        
        # Detalhes
        st.subheader("📋 Detalhes do Pipeline")
        
        st.write(f"**Nome:** {ktr_model.name}")
        st.write(f"**Descrição:** {ktr_model.description or 'Não informado'}")
        
        # Steps
        if ktr_model.steps:
            st.subheader("🔧 Steps Detectados")
            
            for step in ktr_model.steps:
                with st.expander(f"📌 {step.name} ({step.type.value})"):
                    st.write(f"**Tipo:** {step.type.value}")
                    st.write(f"**Categoria:** {'Input' if step.is_input else 'Output' if step.is_output else 'Transform'}")
                    
                    if hasattr(step, 'connection_name') and step.connection_name:
                        st.write(f"**Conexão:** {step.connection_name}")
                    
                    if hasattr(step, 'sql') and step.sql:
                        st.write("**SQL:**")
                        st.code(step.sql[:300] + "..." if len(step.sql) > 300 else step.sql, language="sql")
        
        # Padrões
        if analysis.patterns:
            st.subheader("🎯 Padrões Detectados")
            for pattern in analysis.patterns:
                st.info(f"**{pattern.name}**: {pattern.description} (Confiança: {pattern.confidence:.1%})")
        
        # Otimizações
        if analysis.optimizations:
            st.subheader("🚀 Otimizações Sugeridas")
            for opt in analysis.optimizations:
                st.warning(f"**{opt.type.replace('_', ' ').title()}**: {opt.description}")
        
        # Guardar no session state
        st.session_state.ktr_model = ktr_model
        st.session_state.analysis = analysis
        
        # Cleanup
        os.unlink(tmp_path)
        
    except Exception as e:
        st.error(f"❌ Erro na análise: {str(e)}")

def convert_ktr(uploaded_file):
    """Converte KTR para Python"""
    
    try:
        # Verificar se já foi analisado ou fazer análise rápida
        if 'ktr_model' not in st.session_state:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.ktr') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            parser = KTRParser()
            ktr_model = parser.parse_file(tmp_path)
            os.unlink(tmp_path)
        else:
            ktr_model = st.session_state.ktr_model
        
        # Gerar código
        with st.spinner("🐍 Gerando código Python..."):
            generator = CodeGenerator()
            
            with tempfile.TemporaryDirectory() as temp_dir:
                project = generator.generate_pipeline(ktr_model, temp_dir)
                
                # Mostrar resultados
                st.success("✅ Conversão concluída!")
                
                # Métricas do projeto
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("📄 Arquivos", len(project.files))
                with col2:
                    st.metric("📦 Dependências", len(project.dependencies))
                with col3:
                    st.metric("🐍 Linhas", sum(len(content.split('\n')) for content in project.files.values()))
                
                # Preview dos arquivos
                st.subheader("👀 Arquivos Gerados")
                
                for file_path, content in project.files.items():
                    with st.expander(f"📄 {file_path}"):
                        # Detectar linguagem
                        if file_path.endswith('.py'):
                            language = "python"
                        elif file_path.endswith('.md'):
                            language = "markdown"
                        else:
                            language = "text"
                        
                        # Mostrar preview
                        preview = content[:1500] + "..." if len(content) > 1500 else content
                        st.code(preview, language=language)
                
                # Criar ZIP para download
                zip_buffer = create_zip(project.files)
                
                if zip_buffer:
                    st.download_button(
                        label="📥 Download Projeto Python",
                        data=zip_buffer,
                        file_name=f"{project.name}_python_pipeline.zip",
                        mime="application/zip",
                        type="primary"
                    )
        
    except Exception as e:
        st.error(f"❌ Erro na conversão: {str(e)}")

def create_zip(files_dict):
    """Cria arquivo ZIP em memória"""
    
    try:
        import io
        
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