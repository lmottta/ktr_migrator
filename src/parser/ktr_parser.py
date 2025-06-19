"""
Parser principal para arquivos KTR do Pentaho
Converte XML do KTR em modelo interno Python
"""
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from loguru import logger
import re

from src.models.ktr_models import (
    KTRModel, Connection, Step, Hop, Field,
    TableInputStep, TableOutputStep, ExcelInputStep, 
    StringOperationsStep, StepType
)

class KTRParser:
    """Parser principal para arquivos KTR"""
    
    def __init__(self):
        self.step_parsers = {
            "TableInput": self._parse_table_input,
            "TableOutput": self._parse_table_output,
            "ExcelInput": self._parse_excel_input,
            "StringOperations": self._parse_string_operations,
        }
    
    def parse_file(self, ktr_file_path: str) -> KTRModel:
        """
        Parse completo do arquivo KTR
        """
        logger.info(f"🔍 Analisando arquivo KTR: {ktr_file_path}")
        
        try:
            tree = ET.parse(ktr_file_path)
            root = tree.getroot()
            
            # Extrair informações básicas
            info = root.find('info')
            name = info.find('name').text if info.find('name') is not None else "unnamed_pipeline"
            description = info.find('description').text if info.find('description') is not None else ""
            
            # Parse de cada seção
            connections = self._parse_connections(root)
            steps = self._parse_steps(root)
            hops = self._parse_hops(root)
            
            model = KTRModel(
                name=name,
                description=description,
                connections=connections,
                steps=steps,
                hops=hops
            )
            
            logger.info(f"✅ KTR analisado: {len(connections)} conexões, {len(steps)} steps, {len(hops)} hops")
            return model
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar KTR: {e}")
            raise
    
    def _parse_connections(self, root: ET.Element) -> List[Connection]:
        """Parse das conexões de banco de dados"""
        connections = []
        
        for conn_elem in root.findall('connection'):
            try:
                name = conn_elem.find('name').text
                server = conn_elem.find('server').text or ""
                db_type = conn_elem.find('type').text
                database = conn_elem.find('database').text or ""
                port = int(conn_elem.find('port').text) if conn_elem.find('port') is not None else 5432
                username = conn_elem.find('username').text or ""
                password = conn_elem.find('password').text or ""
                
                # Parse de atributos adicionais
                attributes = {}
                attrs_elem = conn_elem.find('attributes')
                if attrs_elem is not None:
                    for attr in attrs_elem.findall('attribute'):
                        code = attr.find('code').text
                        value = attr.find('attribute').text
                        attributes[code] = value
                
                connection = Connection(
                    name=name,
                    type=db_type,
                    server=server,
                    database=database,
                    port=port,
                    username=username,
                    password=password,
                    attributes=attributes
                )
                
                connections.append(connection)
                logger.debug(f"📡 Conexão encontrada: {name} ({db_type})")
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao parse de conexão: {e}")
                continue
        
        return connections
    
    def _parse_steps(self, root: ET.Element) -> List[Step]:
        """Parse dos steps do pipeline"""
        steps = []
        
        for step_elem in root.findall('step'):
            try:
                name = step_elem.find('name').text
                step_type = step_elem.find('type').text
                description = step_elem.find('description').text or ""
                
                # Use parser específico se disponível
                if step_type in self.step_parsers:
                    step = self.step_parsers[step_type](step_elem, name, description)
                else:
                    # Step genérico
                    step = Step(
                        name=name,
                        type=StepType(step_type) if step_type in [e.value for e in StepType] else StepType.TABLE_INPUT,
                        description=description
                    )
                
                steps.append(step)
                logger.debug(f"🔧 Step encontrado: {name} ({step_type})")
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao parse de step: {e}")
                continue
        
        return steps
    
    def _parse_hops(self, root: ET.Element) -> List[Hop]:
        """Parse das conexões entre steps (hops)"""
        hops = []
        
        order_elem = root.find('order')
        if order_elem is not None:
            for hop_elem in order_elem.findall('hop'):
                try:
                    from_step = hop_elem.find('from').text
                    to_step = hop_elem.find('to').text
                    enabled = hop_elem.find('enabled').text == 'Y'
                    
                    hop = Hop(
                        from_step=from_step,
                        to_step=to_step,
                        enabled=enabled
                    )
                    
                    hops.append(hop)
                    logger.debug(f"🔗 Hop encontrado: {from_step} → {to_step}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao parse de hop: {e}")
                    continue
        
        return hops
    
    def _parse_table_input(self, step_elem: ET.Element, name: str, description: str) -> TableInputStep:
        """Parse específico para TableInput"""
        connection_name = step_elem.find('connection').text if step_elem.find('connection') is not None else ""
        sql = step_elem.find('sql').text if step_elem.find('sql') is not None else ""
        limit = int(step_elem.find('limit').text) if step_elem.find('limit') is not None else 0
        
        # Limpa SQL (remove caracteres especiais do Pentaho)
        if sql:
            sql = self._clean_sql(sql)
        
        return TableInputStep(
            name=name,
            description=description,
            connection_name=connection_name,
            sql=sql,
            limit=limit
        )
    
    def _parse_table_output(self, step_elem: ET.Element, name: str, description: str) -> TableOutputStep:
        """Parse específico para TableOutput"""
        connection_name = step_elem.find('connection').text if step_elem.find('connection') is not None else ""
        schema = step_elem.find('schema').text if step_elem.find('schema') is not None else ""
        table = step_elem.find('table').text if step_elem.find('table') is not None else ""
        truncate = step_elem.find('truncate').text == 'Y' if step_elem.find('truncate') is not None else False
        commit_size = int(step_elem.find('commit').text) if step_elem.find('commit') is not None else 1000
        
        # Parse field mapping
        field_mapping = {}
        fields_elem = step_elem.find('fields')
        if fields_elem is not None:
            for field_elem in fields_elem.findall('field'):
                column_name = field_elem.find('column_name').text
                stream_name = field_elem.find('stream_name').text
                field_mapping[stream_name] = column_name
        
        return TableOutputStep(
            name=name,
            description=description,
            connection_name=connection_name,
            schema=schema,
            table=table,
            truncate=truncate,
            commit_size=commit_size,
            field_mapping=field_mapping
        )
    
    def _parse_excel_input(self, step_elem: ET.Element, name: str, description: str) -> ExcelInputStep:
        """Parse específico para ExcelInput"""
        file_elem = step_elem.find('file')
        file_path = ""
        if file_elem is not None:
            name_elem = file_elem.find('name')
            if name_elem is not None:
                file_path = name_elem.text
        
        header = step_elem.find('header').text == 'Y' if step_elem.find('header') is not None else True
        
        # Parse fields
        fields = []
        fields_elem = step_elem.find('fields')
        if fields_elem is not None:
            for field_elem in fields_elem.findall('field'):
                field_name = field_elem.find('name').text
                field_type = field_elem.find('type').text
                field_length = int(field_elem.find('length').text) if field_elem.find('length') is not None else -1
                field_precision = int(field_elem.find('precision').text) if field_elem.find('precision') is not None else -1
                field_format = field_elem.find('format').text if field_elem.find('format') is not None else None
                
                field = Field(
                    name=field_name,
                    type=field_type,
                    length=field_length,
                    precision=field_precision,
                    format=field_format
                )
                fields.append(field)
        
        # Parse sheet info
        sheet_name = ""
        sheets_elem = step_elem.find('sheets')
        if sheets_elem is not None:
            sheet_elem = sheets_elem.find('sheet')
            if sheet_elem is not None:
                sheet_name = sheet_elem.find('name').text
        
        return ExcelInputStep(
            name=name,
            description=description,
            file_path=file_path,
            sheet_name=sheet_name,
            header=header,
            fields=fields
        )
    
    def _parse_string_operations(self, step_elem: ET.Element, name: str, description: str) -> StringOperationsStep:
        """Parse específico para StringOperations"""
        operations = []
        
        fields_elem = step_elem.find('fields')
        if fields_elem is not None:
            for field_elem in fields_elem.findall('field'):
                operation = {
                    'field_name': field_elem.find('in_stream_name').text,
                    'trim_type': field_elem.find('trim_type').text if field_elem.find('trim_type') is not None else 'none',
                    'lower_upper': field_elem.find('lower_upper').text if field_elem.find('lower_upper') is not None else 'none',
                    'padding_type': field_elem.find('padding_type').text if field_elem.find('padding_type') is not None else 'none'
                }
                operations.append(operation)
        
        return StringOperationsStep(
            name=name,
            description=description,
            operations=operations
        )
    
    def _clean_sql(self, sql: str) -> str:
        """
        Limpa SQL do Pentaho removendo caracteres especiais
        """
        # Remove caracteres de escape do XML
        sql = sql.replace('&#xd;&#xa;', '\n')
        sql = sql.replace('&#x28;', '(')
        sql = sql.replace('&#x29;', ')')
        sql = sql.replace('&#x3d;', '=')
        sql = sql.replace('&#x3a;', ':')
        sql = sql.replace('&#x2f;', '/')
        
        # Remove espaços extras
        sql = re.sub(r'\s+', ' ', sql)
        sql = sql.strip()
        
        return sql 