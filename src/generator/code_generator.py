"""
Gerador de código Python a partir de modelos KTR
"""
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from typing import Dict, List, Any
from datetime import datetime
from loguru import logger

from src.models.ktr_models import (
    KTRModel, GeneratedProject, TableInputStep, 
    TableOutputStep, ExcelInputStep, StringOperationsStep
)

class CodeGenerator:
    """Gerador principal de código Python"""
    
    def __init__(self, templates_dir: str = None):
        """Inicializa o gerador com diretório de templates"""
        if templates_dir is None:
            current_dir = Path(__file__).parent
            templates_dir = current_dir.parent / "templates"
        
        self.templates_dir = Path(templates_dir)
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Configuração de geração realizada via métodos específicos
    
    def generate_pipeline(self, ktr_model: KTRModel, output_dir: str) -> GeneratedProject:
        """
        Gera projeto Python completo a partir do modelo KTR
        """
        logger.info(f"🏗️ Gerando pipeline Python: {ktr_model.name}")
        
        # Criar estrutura de diretórios
        output_path = Path(output_dir)
        self._create_project_structure(output_path)
        
        # Dados para templates
        template_data = self._prepare_template_data(ktr_model)
        
        # Gerar arquivo principal do pipeline
        pipeline_content = self._generate_main_pipeline(template_data)
        
        # Gerar arquivos auxiliares
        config_content = self._generate_config(template_data)
        requirements_content = self._generate_requirements(template_data)
        readme_content = self._generate_readme(template_data)
        test_content = self._generate_tests(template_data)
        
        # Criar projeto gerado
        project = GeneratedProject(
            name=ktr_model.name,
            base_path=str(output_path),
            files={
                f"src/pipelines/{ktr_model.name.lower()}_pipeline.py": pipeline_content,
                "config/settings.py": config_content,
                "requirements.txt": requirements_content,
                "README.md": readme_content,
                f"tests/test_{ktr_model.name.lower()}_pipeline.py": test_content,
            },
            dependencies=self._extract_dependencies(ktr_model),
            config=template_data
        )
        
        # Escrever arquivos
        self._write_project_files(project)
        
        logger.info(f"✅ Projeto gerado em: {output_path}")
        return project
    
    def _create_project_structure(self, base_path: Path):
        """Cria estrutura de diretórios do projeto"""
        directories = [
            "src/pipelines",
            "src/extractors", 
            "src/transformers",
            "src/loaders",
            "src/utils",
            "config",
            "tests",
            "logs",
            "docs"
        ]
        
        for directory in directories:
            dir_path = base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Criar __init__.py em diretórios Python
            if directory.startswith("src/"):
                (dir_path / "__init__.py").touch()
    
    def _prepare_template_data(self, ktr_model: KTRModel) -> Dict[str, Any]:
        """Prepara dados para os templates"""
        
        # Analisar steps
        extractors = []
        transformers = []
        loaders = []
        
        for step in ktr_model.steps:
            if step.is_input:
                extractors.append(self._create_extractor_config(step))
            elif step.is_output:
                loaders.append(self._create_loader_config(step))
            else:
                transformers.append(self._create_transformer_config(step))
        
        return {
            "pipeline_name": ktr_model.name,
            "pipeline_class_name": self._to_class_name(ktr_model.name),
            "pipeline_description": ktr_model.description or f"Pipeline gerado do KTR {ktr_model.name}",
            "source_ktr": f"{ktr_model.name}.ktr",
            "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "connections": ktr_model.connections,
            "extractors": extractors,
            "transformers": transformers,
            "loaders": loaders,
            "custom_imports": self._get_custom_imports(ktr_model),
            "required_fields": self._extract_required_fields(ktr_model)
        }
    
    def _create_extractor_config(self, step) -> Dict[str, Any]:
        """Cria configuração para extractor"""
        config = {
            "name": step.name,
            "type": step.type.value,
            "description": f"Extração de dados - {step.name}"
        }
        
        if hasattr(step, 'connection_name'):
            config["connection"] = step.connection_name
        if hasattr(step, 'sql'):
            config["sql"] = step.sql
        if hasattr(step, 'file_path'):
            config["file_path"] = step.file_path
            
        config["generate_code"] = self._generate_extractor_code(step)
        return config
    
    def _create_transformer_config(self, step) -> Dict[str, Any]:
        """Cria configuração para transformer"""
        config = {
            "name": step.name,
            "type": step.type.value,
            "description": f"Transformação de dados - {step.name}",
            "generate_code": self._generate_transformer_code(step)
        }
        return config
    
    def _create_loader_config(self, step) -> Dict[str, Any]:
        """Cria configuração para loader"""
        config = {
            "name": step.name,
            "type": step.type.value,
            "description": f"Carga de dados - {step.name}"
        }
        
        if hasattr(step, 'connection_name'):
            config["connection"] = step.connection_name
        if hasattr(step, 'table'):
            config["table"] = step.table
        if hasattr(step, 'schema'):
            config["schema"] = step.schema
            
        config["generate_code"] = self._generate_loader_code(step)
        return config
    
    def _generate_extractor_code(self, step) -> str:
        """Gera código específico para extrator"""
        if isinstance(step, TableInputStep):
            return f'''# Extração via SQL
connection = self.connections["{step.connection_name}"]
df = pd.read_sql("""{step.sql}""", connection)'''
        
        elif isinstance(step, ExcelInputStep):
            return f'''# Extração de Excel
df = pd.read_excel(
    "{step.file_path}",
    sheet_name="{step.sheet_name}",
    header={0 if step.header else None}
)'''
        
        return "# Extração genérica\ndf = pd.DataFrame()"
    
    def _generate_transformer_code(self, step) -> str:
        """Gera código específico para transformador"""
        if isinstance(step, StringOperationsStep):
            code_lines = []
            for op in step.operations:
                field_name = op['field_name']
                
                if op['trim_type'] == 'both':
                    code_lines.append(f"df['{field_name}'] = df['{field_name}'].str.strip()")
                elif op['trim_type'] == 'left':
                    code_lines.append(f"df['{field_name}'] = df['{field_name}'].str.lstrip()")
                elif op['trim_type'] == 'right':
                    code_lines.append(f"df['{field_name}'] = df['{field_name}'].str.rstrip()")
                
                if op['lower_upper'] == 'lower':
                    code_lines.append(f"df['{field_name}'] = df['{field_name}'].str.lower()")
                elif op['lower_upper'] == 'upper':
                    code_lines.append(f"df['{field_name}'] = df['{field_name}'].str.upper()")
            
            return '\n'.join(code_lines) if code_lines else "# Sem transformações"
        
        return "# Transformação genérica"
    
    def _generate_loader_code(self, step) -> str:
        """Gera código específico para loader"""
        if isinstance(step, TableOutputStep):
            schema_table = f"{step.schema}.{step.table}" if step.schema else step.table
            
            code = f'''# Carga para PostgreSQL
connection = self.connections["{step.connection_name}"]

# {'Truncar tabela antes da carga' if step.truncate else 'Inserção incremental'}
'''
            if step.truncate:
                code += f'''with connection.begin() as conn:
    conn.execute(sa.text("TRUNCATE TABLE {schema_table}"))
    logger.info("🗑️ Tabela truncada: {schema_table}")
'''
            
            code += f'''
df.to_sql(
    name="{step.table}",
    schema="{step.schema}" if "{step.schema}" else None,
    con=connection,
    if_exists="{'replace' if step.truncate else 'append'}",
    index=False,
    method="multi",
    chunksize={step.commit_size}
)'''
            
            return code
        
        return "# Carga genérica"
    
    def _generate_main_pipeline(self, template_data: Dict[str, Any]) -> str:
        """Gera arquivo principal do pipeline"""
        template = self.jinja_env.get_template("base_pipeline.py.j2")
        return template.render(**template_data)
    
    def _generate_config(self, template_data: Dict[str, Any]) -> str:
        """Gera arquivo de configuração"""
        return f'''"""
Configurações do pipeline {template_data["pipeline_name"]}
"""
import os
from decouple import config

# Configurações de banco de dados
DATABASE_CONFIGS = {{
{self._generate_database_configs(template_data["connections"])}
}}

# Configurações de logging
LOG_LEVEL = config("LOG_LEVEL", default="INFO")
LOG_FILE = config("LOG_FILE", default="logs/{template_data["pipeline_name"].lower()}.log")

# Configurações do pipeline
PIPELINE_CONFIG = {{
    "name": "{template_data["pipeline_name"]}",
    "description": "{template_data["pipeline_description"]}",
    "batch_size": config("BATCH_SIZE", default=1000, cast=int),
    "timeout": config("TIMEOUT", default=3600, cast=int)
}}
'''
    
    def _generate_database_configs(self, connections: List) -> str:
        """Gera configurações de banco"""
        configs = []
        for conn in connections:
            config_str = f'''    "{conn.name}": {{
        "host": config("{conn.name.upper()}_HOST", default="{conn.server}"),
        "port": config("{conn.name.upper()}_PORT", default={conn.port}, cast=int),
        "database": config("{conn.name.upper()}_DATABASE", default="{conn.database}"),
        "username": config("{conn.name.upper()}_USERNAME", default="{conn.username}"),
        "password": config("{conn.name.upper()}_PASSWORD", default=""),
        "type": "{conn.type}"
    }}'''
            configs.append(config_str)
        
        return ',\n'.join(configs)
    
    def _generate_requirements(self, template_data: Dict[str, Any]) -> str:
        """Gera arquivo requirements.txt"""
        base_requirements = [
            "pandas>=2.0.0",
            "sqlalchemy>=2.0.0", 
            "loguru>=0.7.0",
            "python-decouple>=3.8"
        ]
        
        # Adicionar dependências específicas baseadas nos steps
        for extractor in template_data["extractors"]:
            if extractor["type"] == "ExcelInput":
                base_requirements.append("openpyxl>=3.1.0")
            elif extractor["type"] == "TableInput":
                base_requirements.append("psycopg2-binary>=2.9.0")
        
        return '\n'.join(sorted(set(base_requirements)))
    
    def _generate_readme(self, template_data: Dict[str, Any]) -> str:
        """Gera arquivo README.md"""
        return f'''# Pipeline {template_data["pipeline_name"]}

Pipeline ETL gerado automaticamente do KTR: {template_data["source_ktr"]}

## Descrição
{template_data["pipeline_description"]}

## Estrutura
- **Extractors**: {len(template_data["extractors"])} configurados
- **Transformers**: {len(template_data["transformers"])} configurados  
- **Loaders**: {len(template_data["loaders"])} configurados

## Instalação
```bash
pip install -r requirements.txt
```

## Configuração
Copie o arquivo `.env.example` para `.env` e configure as variáveis:

```bash
cp .env.example .env
```

## Execução
```bash
python src/pipelines/{template_data["pipeline_name"].lower()}_pipeline.py
```

## Monitoramento
Logs são gerados em: `logs/{template_data["pipeline_name"].lower()}_YYYYMMDD.log`

---
*Gerado em: {template_data["generation_date"]}*
'''
    
    def _generate_tests(self, template_data: Dict[str, Any]) -> str:
        """Gera arquivo de testes"""
        return f'''"""
Testes para pipeline {template_data["pipeline_name"]}
"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch

from src.pipelines.{template_data["pipeline_name"].lower()}_pipeline import {template_data["pipeline_class_name"]}

class Test{template_data["pipeline_class_name"]}:
    """Testes do pipeline {template_data["pipeline_name"]}"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.config = {{
            "log_level": "DEBUG",
            "environment": "test"
        }}
        self.pipeline = {template_data["pipeline_class_name"]}(self.config)
    
    def test_pipeline_initialization(self):
        """Testa inicialização do pipeline"""
        assert self.pipeline.config == self.config
        assert "records_processed" in self.pipeline.metrics
    
    def test_data_validation_empty_dataframe(self):
        """Testa validação com DataFrame vazio"""
        df_empty = pd.DataFrame()
        assert not self.pipeline.validate_data(df_empty)
    
    def test_data_validation_valid_dataframe(self):
        """Testa validação com DataFrame válido"""
        df_valid = pd.DataFrame({{"col1": [1, 2, 3], "col2": ["a", "b", "c"]}})
        assert self.pipeline.validate_data(df_valid)
    
    @patch('pandas.read_sql')
    def test_extract_data(self, mock_read_sql):
        """Testa extração de dados"""
        # Mock da resposta
        mock_df = pd.DataFrame({{"test_col": [1, 2, 3]}})
        mock_read_sql.return_value = mock_df
        
        # Executar teste
        result = self.pipeline.extract_data()
        
        # Verificações
        assert len(result) == 3
        assert "test_col" in result.columns
    
    def test_run_pipeline_success(self):
        """Testa execução completa do pipeline"""
        with patch.object(self.pipeline, 'extract_data') as mock_extract, \\
             patch.object(self.pipeline, 'transform_data') as mock_transform, \\
             patch.object(self.pipeline, 'load_data') as mock_load:
            
            # Setup mocks
            test_df = pd.DataFrame({{"col1": [1, 2, 3]}})
            mock_extract.return_value = test_df
            mock_transform.return_value = test_df
            mock_load.return_value = None
            
            # Executar pipeline
            result = self.pipeline.run_pipeline()
            
            # Verificações
            assert result["status"] == "success"
            assert result["records_processed"] == 3
            assert "total_execution_time" in result
'''
    
    def _extract_dependencies(self, ktr_model: KTRModel) -> List[str]:
        """Extrai dependências necessárias do modelo"""
        deps = ["pandas", "sqlalchemy", "loguru"]
        
        for step in ktr_model.steps:
            if step.type.value == "ExcelInput":
                deps.append("openpyxl")
            elif step.type.value in ["TableInput", "TableOutput"]:
                deps.append("psycopg2-binary")
        
        return list(set(deps))
    
    def _get_custom_imports(self, ktr_model: KTRModel) -> List[str]:
        """Gera imports customizados baseados no modelo"""
        imports = []
        
        # Verificar se precisa de imports específicos
        for step in ktr_model.steps:
            if step.type.value in ["TableInput", "TableOutput"]:
                imports.append("from sqlalchemy import text")
        
        return imports
    
    def _extract_required_fields(self, ktr_model: KTRModel) -> List[str]:
        """Extrai campos obrigatórios do modelo"""
        # Implementação básica - pode ser expandida
        return []
    
    def _to_class_name(self, name: str) -> str:
        """Converte nome para formato de classe"""
        # Remove caracteres especiais e converte para PascalCase
        clean_name = ''.join(c for c in name if c.isalnum() or c in '_-')
        parts = clean_name.replace('-', '_').split('_')
        return ''.join(word.capitalize() for word in parts) + 'Pipeline'
    
    def _write_project_files(self, project: GeneratedProject):
        """Escreve arquivos do projeto no disco"""
        base_path = Path(project.base_path)
        
        for file_path, content in project.files.items():
            full_path = base_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.debug(f"📄 Arquivo criado: {file_path}")
        
        # Criar .env.example
        env_example_path = base_path / ".env.example"
        with open(env_example_path, 'w') as f:
            f.write(self._generate_env_example(project.config))
        
        logger.info(f"✅ {len(project.files)} arquivos criados em {project.base_path}")
    
    def _generate_env_example(self, template_data: Dict[str, Any]) -> str:
        """Gera arquivo .env.example"""
        env_vars = ["# Configurações do Pipeline", "LOG_LEVEL=INFO", ""]
        
        for conn in template_data.get("connections", []):
            env_vars.extend([
                f"# Conexão {conn.name}",
                f"{conn.name.upper()}_HOST={conn.server}",
                f"{conn.name.upper()}_PORT={conn.port}",
                f"{conn.name.upper()}_DATABASE={conn.database}",
                f"{conn.name.upper()}_USERNAME={conn.username}",
                f"{conn.name.upper()}_PASSWORD=",
                ""
            ])
        
        return '\n'.join(env_vars) 