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
        
        # Inicializar dicionário de arquivos
        files = {
            f"src/pipelines/{ktr_model.name.lower()}_pipeline.py": pipeline_content,
            "config/settings.py": config_content,
            "requirements.txt": requirements_content,
            "README.md": readme_content,
            f"tests/test_{ktr_model.name.lower()}_pipeline.py": test_content,
        }
        
        # Gerar arquivos específicos de ETL
        extractor_files = self._generate_extractor_files(template_data)
        transformer_files = self._generate_transformer_files(template_data)
        loader_files = self._generate_loader_files(template_data)
        utility_files = self._generate_utility_files(template_data)
        
        # Adicionar arquivos ETL ao projeto
        files.update(extractor_files)
        files.update(transformer_files)
        files.update(loader_files)
        files.update(utility_files)
        
        # Gerar __init__.py files com imports
        init_files = self._generate_init_files(template_data)
        files.update(init_files)
        
        # Criar projeto gerado
        project = GeneratedProject(
            name=ktr_model.name,
            base_path=str(output_path),
            files=files,
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
    
    def _generate_extractor_files(self, template_data: Dict[str, Any]) -> Dict[str, str]:
        """Gera arquivos específicos para extractors"""
        files = {}
        
        for extractor in template_data.get("extractors", []):
            file_name = f"src/extractors/{extractor['name'].lower().replace(' ', '_')}_extractor.py"
            content = self._generate_extractor_file_content(extractor, template_data)
            files[file_name] = content
            logger.debug(f"📄 Gerado extractor: {file_name}")
        
        return files
    
    def _generate_transformer_files(self, template_data: Dict[str, Any]) -> Dict[str, str]:
        """Gera arquivos específicos para transformers"""
        files = {}
        
        for transformer in template_data.get("transformers", []):
            file_name = f"src/transformers/{transformer['name'].lower().replace(' ', '_')}_transformer.py"
            content = self._generate_transformer_file_content(transformer, template_data)
            files[file_name] = content
            logger.debug(f"📄 Gerado transformer: {file_name}")
        
        return files
    
    def _generate_loader_files(self, template_data: Dict[str, Any]) -> Dict[str, str]:
        """Gera arquivos específicos para loaders"""
        files = {}
        
        for loader in template_data.get("loaders", []):
            file_name = f"src/loaders/{loader['name'].lower().replace(' ', '_')}_loader.py"
            content = self._generate_loader_file_content(loader, template_data)
            files[file_name] = content
            logger.debug(f"📄 Gerado loader: {file_name}")
        
        return files
    
    def _generate_utility_files(self, template_data: Dict[str, Any]) -> Dict[str, str]:
        """Gera arquivos de utilities comuns"""
        files = {}
        
        # Database utilities
        files["src/utils/database_utils.py"] = self._generate_database_utils()
        
        # Data validation utilities
        files["src/utils/validation_utils.py"] = self._generate_validation_utils()
        
        # Logging utilities
        files["src/utils/logging_utils.py"] = self._generate_logging_utils()
        
        # Configuration utilities
        files["src/utils/config_utils.py"] = self._generate_config_utils()
        
        logger.debug("📄 Gerados 4 arquivos de utilities")
        return files
    
    def _generate_init_files(self, template_data: Dict[str, Any]) -> Dict[str, str]:
        """Gera arquivos __init__.py com imports corretos"""
        files = {}
        
        # Extractors __init__.py
        extractor_imports = []
        for extractor in template_data.get("extractors", []):
            module_name = extractor['name'].lower().replace(' ', '_')
            class_name = self._to_class_name(extractor['name']) + 'Extractor'
            extractor_imports.append(f"from .{module_name}_extractor import {class_name}")
        
        files["src/extractors/__init__.py"] = '\n'.join(extractor_imports) + '\n'
        
        # Transformers __init__.py
        transformer_imports = []
        for transformer in template_data.get("transformers", []):
            module_name = transformer['name'].lower().replace(' ', '_')
            class_name = self._to_class_name(transformer['name']) + 'Transformer'
            transformer_imports.append(f"from .{module_name}_transformer import {class_name}")
        
        files["src/transformers/__init__.py"] = '\n'.join(transformer_imports) + '\n'
        
        # Loaders __init__.py
        loader_imports = []
        for loader in template_data.get("loaders", []):
            module_name = loader['name'].lower().replace(' ', '_')
            class_name = self._to_class_name(loader['name']) + 'Loader'
            loader_imports.append(f"from .{module_name}_loader import {class_name}")
        
        files["src/loaders/__init__.py"] = '\n'.join(loader_imports) + '\n'
        
        # Utils __init__.py
        utils_imports = [
            "from .database_utils import DatabaseUtils",
            "from .validation_utils import ValidationUtils",
            "from .logging_utils import LoggingUtils",
            "from .config_utils import ConfigUtils"
        ]
        files["src/utils/__init__.py"] = '\n'.join(utils_imports) + '\n'
        
        return files
    
    def _generate_extractor_file_content(self, extractor: Dict[str, Any], template_data: Dict[str, Any]) -> str:
        """Gera conteúdo do arquivo extractor"""
        class_name = self._to_class_name(extractor['name']) + 'Extractor'
        
        return f'''"""
{extractor['description']}
Gerado automaticamente do KTR: {template_data['source_ktr']}
"""
import pandas as pd
from sqlalchemy import create_engine, text
from loguru import logger
from typing import Dict, Any, Optional
from ..utils.database_utils import DatabaseUtils
from ..utils.validation_utils import ValidationUtils

class {class_name}:
    """
    Extractor para: {extractor['name']}
    Tipo: {extractor['type']}
    """
    
    def __init__(self, connections: Dict[str, Any]):
        self.connections = connections
        self.validator = ValidationUtils()
        
    def extract(self) -> pd.DataFrame:
        """
        Executa a extração de dados
        """
        logger.info(f"🔄 Iniciando extração: {extractor['name']}")
        
        try:
                         {extractor.get('generate_code', '# Extração genérica' + chr(10) + 'df = pd.DataFrame()').replace(chr(10), chr(10) + '            ')}
            
            # Validação dos dados extraídos
            if self.validator.validate_dataframe(df):
                logger.info(f"✅ Extração concluída: {{len(df)}} registros")
                return df
            else:
                logger.warning("⚠️ Dados extraídos não passaram na validação")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"❌ Erro na extração {extractor['name']}: {{e}}")
            raise
    
    def get_schema(self) -> Dict[str, str]:
        """
        Retorna o schema esperado dos dados
        """
        return {{
            # Definir schema baseado no tipo de extração
            "extracted_at": "datetime",
            "source": "string"
        }}
'''
    
    def _generate_transformer_file_content(self, transformer: Dict[str, Any], template_data: Dict[str, Any]) -> str:
        """Gera conteúdo do arquivo transformer"""
        class_name = self._to_class_name(transformer['name']) + 'Transformer'
        
        return f'''"""
{transformer['description']}
Gerado automaticamente do KTR: {template_data['source_ktr']}
"""
import pandas as pd
import numpy as np
from loguru import logger
from typing import Dict, Any, Optional, List
from ..utils.validation_utils import ValidationUtils

class {class_name}:
    """
    Transformer para: {transformer['name']}
    Tipo: {transformer['type']}
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {{}}
        self.validator = ValidationUtils()
        
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executa as transformações nos dados
        """
        logger.info(f"🔄 Iniciando transformação: {transformer['name']}")
        
        try:
            if df.empty:
                logger.warning("⚠️ DataFrame vazio recebido para transformação")
                return df
            
            original_count = len(df)
            
            {transformer.get('generate_code', '# Transformação genérica').replace(chr(10), chr(10) + '            ')}
            
            # Adicionar metadata de transformação
            df['transformed_at'] = pd.Timestamp.now()
            df['transformation_applied'] = '{transformer['name']}'
            
            final_count = len(df)
            logger.info(f"✅ Transformação concluída: {{original_count}} → {{final_count}} registros")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Erro na transformação {transformer['name']}: {{e}}")
            raise
    
    def validate_input(self, df: pd.DataFrame) -> bool:
        """
        Valida se os dados de entrada estão corretos
        """
        return self.validator.validate_dataframe(df)
    
    def get_required_columns(self) -> List[str]:
        """
        Retorna as colunas obrigatórias para esta transformação
        """
        return []  # Definir baseado no tipo de transformação
'''
    
    def _generate_loader_file_content(self, loader: Dict[str, Any], template_data: Dict[str, Any]) -> str:
        """Gera conteúdo do arquivo loader"""
        class_name = self._to_class_name(loader['name']) + 'Loader'
        
        return f'''"""
{loader['description']}
Gerado automaticamente do KTR: {template_data['source_ktr']}
"""
import pandas as pd
from sqlalchemy import create_engine, text
from loguru import logger
from typing import Dict, Any, Optional
from ..utils.database_utils import DatabaseUtils
from ..utils.validation_utils import ValidationUtils

class {class_name}:
    """
    Loader para: {loader['name']}
    Tipo: {loader['type']}
    """
    
    def __init__(self, connections: Dict[str, Any]):
        self.connections = connections
        self.db_utils = DatabaseUtils()
        self.validator = ValidationUtils()
        
    def load(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Executa a carga dos dados
        """
        logger.info(f"🔄 Iniciando carga: {loader['name']}")
        
        try:
            if df.empty:
                logger.warning("⚠️ DataFrame vazio recebido para carga")
                return {{"status": "warning", "records": 0}}
            
            # Validação pré-carga
            if not self.validator.validate_dataframe(df):
                raise ValueError("Dados não passaram na validação pré-carga")
            
            records_count = len(df)
            
                         {loader.get('generate_code', '# Carga genérica' + chr(10) + 'logger.info("Carga simulada")').replace(chr(10), chr(10) + '            ')}
            
            logger.info(f"✅ Carga concluída: {{records_count}} registros")
            
            return {{
                "status": "success",
                "records": records_count,
                "target": "{loader['name']}"
            }}
            
        except Exception as e:
            logger.error(f"❌ Erro na carga {loader['name']}: {{e}}")
            raise
    
    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara os dados para carga (formatação final)
        """
        # Adicionar timestamp de carga
        df['loaded_at'] = pd.Timestamp.now()
        
        return df
    
    def get_target_schema(self) -> Dict[str, str]:
        """
        Retorna o schema da tabela/destino de carga
        """
        return {{
            # Definir schema baseado no destino
            "loaded_at": "datetime"
        }}
'''
    
    def _generate_database_utils(self) -> str:
        """Gera arquivo database_utils.py"""
        return '''"""
Utilities para manipulação de banco de dados
"""
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from loguru import logger
from typing import Dict, Any, List, Optional

class DatabaseUtils:
    """Utilidades para operações de banco de dados"""
    
    @staticmethod
    def test_connection(connection_string: str) -> bool:
        """Testa conexão com banco de dados"""
        try:
            engine = create_engine(connection_string)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✅ Conexão testada com sucesso")
            return True
        except Exception as e:
            logger.error(f"❌ Falha na conexão: {e}")
            return False
    
    @staticmethod
    def get_table_info(engine, table_name: str, schema: str = None) -> Dict[str, Any]:
        """Obtém informações da tabela"""
        try:
            inspector = inspect(engine)
            full_table = f"{schema}.{table_name}" if schema else table_name
            
            columns = inspector.get_columns(table_name, schema=schema)
            pk = inspector.get_pk_constraint(table_name, schema=schema)
            
            return {
                "table": full_table,
                "columns": columns,
                "primary_key": pk,
                "exists": True
            }
        except Exception as e:
            logger.warning(f"⚠️ Tabela {table_name} não encontrada: {e}")
            return {"exists": False}
    
    @staticmethod
    def execute_query(engine, query: str, params: Dict = None) -> pd.DataFrame:
        """Executa query e retorna DataFrame"""
        try:
            return pd.read_sql(query, engine, params=params)
        except Exception as e:
            logger.error(f"❌ Erro na execução da query: {e}")
            raise
'''
    
    def _generate_validation_utils(self) -> str:
        """Gera arquivo validation_utils.py"""
        return '''"""
Utilities para validação de dados
"""
import pandas as pd
import numpy as np
from loguru import logger
from typing import Dict, Any, List, Optional

class ValidationUtils:
    """Utilidades para validação de dados"""
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> bool:
        """Validação básica de DataFrame"""
        if df is None:
            logger.error("❌ DataFrame é None")
            return False
        
        if df.empty:
            logger.warning("⚠️ DataFrame está vazio")
            return True  # Vazio é válido em alguns casos
        
        logger.info(f"✅ DataFrame válido: {len(df)} registros, {len(df.columns)} colunas")
        return True
    
    @staticmethod
    def check_required_columns(df: pd.DataFrame, required_cols: List[str]) -> bool:
        """Verifica se as colunas obrigatórias estão presentes"""
        missing_cols = set(required_cols) - set(df.columns)
        
        if missing_cols:
            logger.error(f"❌ Colunas obrigatórias ausentes: {missing_cols}")
            return False
        
        logger.info("✅ Todas as colunas obrigatórias estão presentes")
        return True
    
    @staticmethod
    def check_data_types(df: pd.DataFrame, expected_types: Dict[str, str]) -> bool:
        """Verifica tipos de dados das colunas"""
        errors = []
        
        for col, expected_type in expected_types.items():
            if col not in df.columns:
                continue
                
            actual_type = str(df[col].dtype)
            if expected_type not in actual_type:
                errors.append(f"{col}: esperado {expected_type}, encontrado {actual_type}")
        
        if errors:
            logger.error(f"❌ Tipos incorretos: {errors}")
            return False
        
        logger.info("✅ Tipos de dados corretos")
        return True
    
    @staticmethod
    def check_null_values(df: pd.DataFrame, null_threshold: float = 0.1) -> Dict[str, Any]:
        """Verifica valores nulos"""
        null_info = {}
        
        for col in df.columns:
            null_count = df[col].isnull().sum()
            null_percentage = null_count / len(df)
            
            null_info[col] = {
                "null_count": null_count,
                "null_percentage": null_percentage,
                "exceeds_threshold": null_percentage > null_threshold
            }
        
        return null_info
'''
    
    def _generate_logging_utils(self) -> str:
        """Gera arquivo logging_utils.py"""
        return '''"""
Utilities para configuração de logging
"""
import sys
from pathlib import Path
from loguru import logger
from typing import Optional

class LoggingUtils:
    """Utilidades para configuração de logging"""
    
    @staticmethod
    def setup_pipeline_logging(
        pipeline_name: str,
        log_level: str = "INFO",
        log_dir: str = "logs",
        console_output: bool = True
    ) -> None:
        """Configura logging para pipeline"""
        
        # Remover handlers existentes
        logger.remove()
        
        # Console output
        if console_output:
            logger.add(
                sys.stdout,
                level=log_level,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
            )
        
        # File output
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        log_filename = f"{pipeline_name}_" + "{time:YYYY-MM-DD}.log"
        logger.add(
            log_path / log_filename,
            rotation="1 day",
            retention="30 days",
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
        )
        
        logger.info(f"🚀 Logging configurado para pipeline: {pipeline_name}")
    
    @staticmethod
    def log_pipeline_metrics(metrics: dict) -> None:
        """Log das métricas do pipeline"""
        logger.info("📊 Métricas do Pipeline:")
        for key, value in metrics.items():
            logger.info(f"   {key}: {value}")
    
    @staticmethod
    def log_dataframe_info(df, name: str = "DataFrame") -> None:
        """Log das informações do DataFrame"""
        logger.info(f"📊 {name} - Shape: {df.shape}")
        logger.info(f"📊 {name} - Colunas: {list(df.columns)}")
        logger.info(f"📊 {name} - Tipos: {df.dtypes.to_dict()}")
'''
    
    def _generate_config_utils(self) -> str:
        """Gera arquivo config_utils.py"""
        return '''"""
Utilities para configuração
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
from decouple import config
from loguru import logger

class ConfigUtils:
    """Utilidades para gerenciamento de configuração"""
    
    @staticmethod
    def load_database_config(connection_name: str) -> Dict[str, Any]:
        """Carrega configuração de banco de dados"""
        try:
            db_config = {
                "host": config(f"{connection_name.upper()}_HOST"),
                "port": config(f"{connection_name.upper()}_PORT", cast=int),
                "database": config(f"{connection_name.upper()}_DATABASE"),
                "username": config(f"{connection_name.upper()}_USERNAME"),
                "password": config(f"{connection_name.upper()}_PASSWORD"),
            }
            
            logger.info(f"✅ Configuração carregada para: {connection_name}")
            return db_config
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar config de {connection_name}: {e}")
            raise
    
    @staticmethod
    def get_pipeline_config() -> Dict[str, Any]:
        """Carrega configuração geral do pipeline"""
        return {
            "log_level": config("LOG_LEVEL", default="INFO"),
            "environment": config("ENVIRONMENT", default="development"),
            "batch_size": config("BATCH_SIZE", default=1000, cast=int),
            "max_retries": config("MAX_RETRIES", default=3, cast=int),
            "timeout": config("TIMEOUT", default=300, cast=int),
        }
    
    @staticmethod
    def validate_required_env_vars(required_vars: list) -> bool:
        """Valida se todas as variáveis obrigatórias estão definidas"""
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Variáveis de ambiente obrigatórias não definidas: {missing_vars}")
            return False
        
        logger.info("✅ Todas as variáveis obrigatórias estão definidas")
        return True
    
    @staticmethod
    def create_sqlalchemy_url(db_config: Dict[str, Any], db_type: str = "postgresql") -> str:
        """Cria URL do SQLAlchemy"""
        if db_type == "postgresql":
            driver = "psycopg2"
        elif db_type == "mysql":
            driver = "pymysql"
        else:
            driver = ""
        
        driver_suffix = f"+{driver}" if driver else ""
        
        url = f"{db_type}{driver_suffix}://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        
        return url
''' 