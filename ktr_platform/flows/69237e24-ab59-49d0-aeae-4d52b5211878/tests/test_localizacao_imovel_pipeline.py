"""
Testes para pipeline localizacao_imovel
"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch

from src.pipelines.localizacao_imovel_pipeline import LocalizacaoImovelPipeline

class TestLocalizacaoImovelPipeline:
    """Testes do pipeline localizacao_imovel"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.config = {
            "log_level": "DEBUG",
            "environment": "test"
        }
        self.pipeline = LocalizacaoImovelPipeline(self.config)
    
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
        df_valid = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        assert self.pipeline.validate_data(df_valid)
    
    @patch('pandas.read_sql')
    def test_extract_data(self, mock_read_sql):
        """Testa extração de dados"""
        # Mock da resposta
        mock_df = pd.DataFrame({"test_col": [1, 2, 3]})
        mock_read_sql.return_value = mock_df
        
        # Executar teste
        result = self.pipeline.extract_data()
        
        # Verificações
        assert len(result) == 3
        assert "test_col" in result.columns
    
    def test_run_pipeline_success(self):
        """Testa execução completa do pipeline"""
        with patch.object(self.pipeline, 'extract_data') as mock_extract, \
             patch.object(self.pipeline, 'transform_data') as mock_transform, \
             patch.object(self.pipeline, 'load_data') as mock_load:
            
            # Setup mocks
            test_df = pd.DataFrame({"col1": [1, 2, 3]})
            mock_extract.return_value = test_df
            mock_transform.return_value = test_df
            mock_load.return_value = None
            
            # Executar pipeline
            result = self.pipeline.run_pipeline()
            
            # Verificações
            assert result["status"] == "success"
            assert result["records_processed"] == 3
            assert "total_execution_time" in result
