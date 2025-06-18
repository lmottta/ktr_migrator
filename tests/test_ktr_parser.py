"""
Testes para o parser de arquivos KTR
"""
import pytest
import xml.etree.ElementTree as ET
from pathlib import Path
import tempfile

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.parser.ktr_parser import KTRParser
from src.models.ktr_models import KTRModel, TableInputStep, TableOutputStep, Connection

class TestKTRParser:
    """Testes do parser KTR"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.parser = KTRParser()
    
    def test_parse_simple_ktr(self):
        """Testa parsing de KTR simples"""
        ktr_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <transformation>
          <info>
            <name>test_pipeline</name>
            <description>Pipeline de teste</description>
          </info>
          <connection>
            <name>test_db</name>
            <server>localhost</server>
            <type>POSTGRESQL</type>
            <database>test</database>
            <port>5432</port>
            <username>user</username>
            <password>pass</password>
          </connection>
          <step>
            <name>input_step</name>
            <type>TableInput</type>
            <connection>test_db</connection>
            <sql>SELECT * FROM test_table</sql>
          </step>
          <step>
            <name>output_step</name>
            <type>TableOutput</type>
            <connection>test_db</connection>
            <table>output_table</table>
            <truncate>Y</truncate>
          </step>
          <order>
            <hop>
              <from>input_step</from>
              <to>output_step</to>
              <enabled>Y</enabled>
            </hop>
          </order>
        </transformation>'''
        
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ktr', delete=False) as f:
            f.write(ktr_content)
            temp_file = f.name
        
        try:
            # Parse do arquivo
            model = self.parser.parse_file(temp_file)
            
            # Verificações
            assert model.name == "test_pipeline"
            assert model.description == "Pipeline de teste"
            assert len(model.connections) == 1
            assert len(model.steps) == 2
            assert len(model.hops) == 1
            
            # Verificar conexão
            conn = model.connections[0]
            assert conn.name == "test_db"
            assert conn.type == "POSTGRESQL"
            assert conn.server == "localhost"
            
            # Verificar steps
            input_step = model.get_step("input_step")
            assert isinstance(input_step, TableInputStep)
            assert input_step.sql == "SELECT * FROM test_table"
            
            output_step = model.get_step("output_step")
            assert isinstance(output_step, TableOutputStep)
            assert output_step.table == "output_table"
            assert output_step.truncate == True
            
        finally:
            # Cleanup
            Path(temp_file).unlink()
    
    def test_parse_excel_input_step(self):
        """Testa parsing de step ExcelInput"""
        ktr_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <transformation>
          <info>
            <name>excel_pipeline</name>
          </info>
          <step>
            <name>excel_input</name>
            <type>ExcelInput</type>
            <header>Y</header>
            <file>
              <name>C:\\data\\input.xlsx</name>
            </file>
            <sheets>
              <sheet>
                <name>Sheet1</name>
              </sheet>
            </sheets>
            <fields>
              <field>
                <name>column1</name>
                <type>String</type>
                <length>50</length>
              </field>
              <field>
                <name>column2</name>
                <type>Integer</type>
              </field>
            </fields>
          </step>
        </transformation>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ktr', delete=False) as f:
            f.write(ktr_content)
            temp_file = f.name
        
        try:
            model = self.parser.parse_file(temp_file)
            
            step = model.get_step("excel_input")
            assert step.file_path == "C:\\data\\input.xlsx"
            assert step.sheet_name == "Sheet1"
            assert step.header == True
            assert len(step.fields) == 2
            
            field1 = step.fields[0]
            assert field1.name == "column1"
            assert field1.type == "String"
            assert field1.length == 50
            
        finally:
            Path(temp_file).unlink()
    
    def test_parse_string_operations_step(self):
        """Testa parsing de step StringOperations"""
        ktr_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <transformation>
          <info>
            <name>string_ops_pipeline</name>
          </info>
          <step>
            <name>string_ops</name>
            <type>StringOperations</type>
            <fields>
              <field>
                <in_stream_name>field1</in_stream_name>
                <trim_type>both</trim_type>
                <lower_upper>upper</lower_upper>
              </field>
              <field>
                <in_stream_name>field2</in_stream_name>
                <trim_type>left</trim_type>
                <lower_upper>lower</lower_upper>
              </field>
            </fields>
          </step>
        </transformation>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ktr', delete=False) as f:
            f.write(ktr_content)
            temp_file = f.name
        
        try:
            model = self.parser.parse_file(temp_file)
            
            step = model.get_step("string_ops")
            assert len(step.operations) == 2
            
            op1 = step.operations[0]
            assert op1['field_name'] == "field1"
            assert op1['trim_type'] == "both"
            assert op1['lower_upper'] == "upper"
            
            op2 = step.operations[1]
            assert op2['field_name'] == "field2"
            assert op2['trim_type'] == "left"
            assert op2['lower_upper'] == "lower"
            
        finally:
            Path(temp_file).unlink()
    
    def test_clean_sql_method(self):
        """Testa limpeza de SQL com caracteres especiais"""
        dirty_sql = "SELECT&#xd;&#xa;    campo&#x28;test&#x29;&#xd;&#xa;FROM&#x2f;table"
        cleaned = self.parser._clean_sql(dirty_sql)
        
        expected = "SELECT campo(test) FROM/table"
        assert cleaned == expected
    
    def test_parse_invalid_file(self):
        """Testa parsing de arquivo inválido"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ktr', delete=False) as f:
            f.write("invalid xml content")
            temp_file = f.name
        
        try:
            with pytest.raises(Exception):
                self.parser.parse_file(temp_file)
        finally:
            Path(temp_file).unlink()
    
    def test_parse_empty_ktr(self):
        """Testa parsing de KTR vazio"""
        ktr_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <transformation>
          <info>
            <name>empty_pipeline</name>
          </info>
        </transformation>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ktr', delete=False) as f:
            f.write(ktr_content)
            temp_file = f.name
        
        try:
            model = self.parser.parse_file(temp_file)
            
            assert model.name == "empty_pipeline"
            assert len(model.connections) == 0
            assert len(model.steps) == 0
            assert len(model.hops) == 0
            
        finally:
            Path(temp_file).unlink()
    
    def test_connection_sqlalchemy_url(self):
        """Testa geração de URL SQLAlchemy"""
        conn = Connection(
            name="test",
            type="POSTGRESQL",
            server="localhost",
            database="testdb",
            port=5432,
            username="user",
            password="pass",
            attributes={}
        )
        
        url = conn.to_sqlalchemy_url()
        expected = "postgresql://user:pass@localhost:5432/testdb"
        assert url == expected
    
    def test_model_helper_methods(self):
        """Testa métodos auxiliares do modelo"""
        # Criar modelo com dados de teste
        conn = Connection("test_conn", "POSTGRESQL", "localhost", "db", 5432, "user", "pass")
        input_step = TableInputStep("input", "", "test_conn", "SELECT 1", 0)
        output_step = TableOutputStep("output", "", "test_conn", "public", "table", True, 1000)
        
        model = KTRModel(
            name="test",
            connections=[conn],
            steps=[input_step, output_step]
        )
        
        # Testar métodos
        assert model.get_connection("test_conn") == conn
        assert model.get_connection("nonexistent") is None
        
        assert model.get_step("input") == input_step
        assert model.get_step("nonexistent") is None
        
        assert len(model.get_input_steps()) == 1
        assert len(model.get_output_steps()) == 1
        assert len(model.get_transform_steps()) == 0
        
        assert input_step.is_input == True
        assert input_step.is_output == False
        assert input_step.is_transform == False
        
        assert output_step.is_input == False
        assert output_step.is_output == True
        assert output_step.is_transform == False

if __name__ == "__main__":
    pytest.main([__file__]) 