"""
Modelos de dados para representar estruturas do Pentaho KTR
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

class StepType(Enum):
    """Tipos de steps do Pentaho"""
    TABLE_INPUT = "TableInput"
    TABLE_OUTPUT = "TableOutput"
    EXCEL_INPUT = "ExcelInput"
    EXCEL_OUTPUT = "ExcelOutput"
    TEXT_FILE_INPUT = "TextFileInput"
    TEXT_FILE_OUTPUT = "TextFileOutput"
    STRING_OPERATIONS = "StringOperations"
    FILTER_ROWS = "FilterRows"
    VALUE_MAPPER = "ValueMapper"
    CALCULATOR = "Calculator"
    SORT_ROWS = "SortRows"
    GROUP_BY = "GroupBy"
    SELECT_VALUES = "SelectValues"
    JSON_INPUT = "JsonInput"
    JSON_OUTPUT = "JsonOutput"

@dataclass
class Connection:
    """Representa uma conexão de banco de dados"""
    name: str
    type: str
    server: str
    database: str
    port: int
    username: str
    password: str
    attributes: Dict[str, str] = field(default_factory=dict)
    
    def to_sqlalchemy_url(self) -> str:
        """Converte para URL do SQLAlchemy"""
        type_mapping = {
            "POSTGRESQL": "postgresql",
            "MYSQL": "mysql",
            "ORACLE": "oracle",
            "SQLSERVER": "mssql"
        }
        
        db_type = type_mapping.get(self.type, self.type.lower())
        return f"{db_type}://{self.username}:{self.password}@{self.server}:{self.port}/{self.database}"

@dataclass
class Field:
    """Representa um campo de dados"""
    name: str
    type: str
    length: int = -1
    precision: int = -1
    format: Optional[str] = None

@dataclass
class Hop:
    """Representa uma conexão entre steps"""
    from_step: str
    to_step: str
    enabled: bool = True

@dataclass
class Step:
    """Classe base para steps do Pentaho"""
    name: str
    type: StepType
    description: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_input(self) -> bool:
        """Verifica se é um step de entrada"""
        return self.type in [
            StepType.TABLE_INPUT,
            StepType.EXCEL_INPUT,
            StepType.TEXT_FILE_INPUT,
            StepType.JSON_INPUT
        ]
    
    @property
    def is_output(self) -> bool:
        """Verifica se é um step de saída"""
        return self.type in [
            StepType.TABLE_OUTPUT,
            StepType.EXCEL_OUTPUT,
            StepType.TEXT_FILE_OUTPUT,
            StepType.JSON_OUTPUT
        ]
    
    @property
    def is_transform(self) -> bool:
        """Verifica se é um step de transformação"""
        return not (self.is_input or self.is_output)

@dataclass
class TableInputStep(Step):
    """Step específico para TableInput"""
    connection_name: str = ""
    sql: str = ""
    limit: int = 0
    
    def __post_init__(self):
        self.type = StepType.TABLE_INPUT

@dataclass
class TableOutputStep(Step):
    """Step específico para TableOutput"""
    connection_name: str = ""
    schema: str = ""
    table: str = ""
    truncate: bool = False
    commit_size: int = 1000
    field_mapping: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        self.type = StepType.TABLE_OUTPUT

@dataclass
class ExcelInputStep(Step):
    """Step específico para ExcelInput"""
    file_path: str = ""
    sheet_name: str = ""
    header: bool = True
    start_row: int = 0
    start_col: int = 0
    fields: List[Field] = field(default_factory=list)
    
    def __post_init__(self):
        self.type = StepType.EXCEL_INPUT

@dataclass
class StringOperationsStep(Step):
    """Step específico para StringOperations"""
    operations: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        self.type = StepType.STRING_OPERATIONS

@dataclass
class KTRModel:
    """Modelo completo do arquivo KTR"""
    name: str
    description: str = ""
    connections: List[Connection] = field(default_factory=list)
    steps: List[Step] = field(default_factory=list)
    hops: List[Hop] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def get_connection(self, name: str) -> Optional[Connection]:
        """Busca conexão por nome"""
        for conn in self.connections:
            if conn.name == name:
                return conn
        return None
    
    def get_step(self, name: str) -> Optional[Step]:
        """Busca step por nome"""
        for step in self.steps:
            if step.name == name:
                return step
        return None
    
    def get_input_steps(self) -> List[Step]:
        """Retorna todos os steps de entrada"""
        return [step for step in self.steps if step.is_input]
    
    def get_output_steps(self) -> List[Step]:
        """Retorna todos os steps de saída"""
        return [step for step in self.steps if step.is_output]
    
    def get_transform_steps(self) -> List[Step]:
        """Retorna todos os steps de transformação"""
        return [step for step in self.steps if step.is_transform]

@dataclass
class GeneratedProject:
    """Representa o projeto Python gerado"""
    name: str
    base_path: str
    files: Dict[str, str] = field(default_factory=dict)  # path -> content
    dependencies: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict) 