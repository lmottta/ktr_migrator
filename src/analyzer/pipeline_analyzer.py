"""
Analisador de pipelines KTR para detecção de padrões e otimizações
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from loguru import logger
import networkx as nx

from src.models.ktr_models import KTRModel, Step, Hop, StepType

@dataclass
class OptimizationSuggestion:
    """Sugestão de otimização"""
    type: str
    description: str
    impact: str  # "high", "medium", "low"
    code_example: Optional[str] = None

@dataclass
class PipelinePattern:
    """Padrão detectado no pipeline"""
    name: str
    description: str
    steps_involved: List[str]
    confidence: float  # 0.0 - 1.0

@dataclass
class AnalysisResult:
    """Resultado da análise do pipeline"""
    complexity_score: int
    estimated_performance_gain: int
    patterns: List[PipelinePattern] = field(default_factory=list)
    optimizations: List[OptimizationSuggestion] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "complexity_score": self.complexity_score,
            "estimated_performance_gain": self.estimated_performance_gain,
            "patterns": [
                {
                    "name": p.name,
                    "description": p.description,
                    "steps_involved": p.steps_involved,
                    "confidence": p.confidence
                } for p in self.patterns
            ],
            "optimizations": [
                {
                    "type": o.type,
                    "description": o.description,
                    "impact": o.impact,
                    "code_example": o.code_example
                } for o in self.optimizations
            ],
            "metrics": self.metrics
        }

class PipelineAnalyzer:
    """Analisador principal de pipelines KTR"""
    
    def __init__(self):
        self.pattern_detectors = {
            "simple_etl": self._detect_simple_etl,
            "lookup_join": self._detect_lookup_pattern,
            "aggregation": self._detect_aggregation_pattern,
            "file_processing": self._detect_file_processing,
        }
        
        self.optimization_rules = [
            self._suggest_batch_processing,
            self._suggest_parallel_processing,
            self._suggest_data_validation,
            self._suggest_connection_pooling,
            self._suggest_sql_optimization,
        ]
    
    def analyze_pipeline(self, ktr_model: KTRModel) -> AnalysisResult:
        """
        Análise completa do pipeline
        """
        logger.info(f"🔍 Analisando pipeline: {ktr_model.name}")
        
        # Criar grafo do pipeline
        graph = self._create_pipeline_graph(ktr_model)
        
        # Calcular métricas básicas
        metrics = self._calculate_metrics(ktr_model, graph)
        
        # Detectar padrões
        patterns = self._detect_patterns(ktr_model, graph)
        
        # Sugerir otimizações
        optimizations = self._suggest_optimizations(ktr_model, patterns)
        
        # Calcular complexidade
        complexity = self._calculate_complexity(ktr_model, graph)
        
        # Estimar ganho de performance
        performance_gain = self._estimate_performance_gain(optimizations)
        
        result = AnalysisResult(
            complexity_score=complexity,
            estimated_performance_gain=performance_gain,
            patterns=patterns,
            optimizations=optimizations,
            metrics=metrics
        )
        
        logger.info(f"✅ Análise concluída - Complexidade: {complexity}, Otimizações: {len(optimizations)}")
        return result
    
    def _create_pipeline_graph(self, ktr_model: KTRModel) -> nx.DiGraph:
        """Cria grafo direcionado do pipeline"""
        graph = nx.DiGraph()
        
        # Adicionar steps como nós
        for step in ktr_model.steps:
            graph.add_node(step.name, step_type=step.type.value, step_obj=step)
        
        # Adicionar hops como arestas
        for hop in ktr_model.hops:
            if hop.enabled:
                graph.add_edge(hop.from_step, hop.to_step)
        
        return graph
    
    def _calculate_metrics(self, ktr_model: KTRModel, graph: nx.DiGraph) -> Dict[str, Any]:
        """Calcula métricas do pipeline"""
        metrics = {
            "total_steps": len(ktr_model.steps),
            "total_connections": len(ktr_model.connections),
            "total_hops": len(ktr_model.hops),
            "input_steps": len([s for s in ktr_model.steps if s.is_input]),
            "transform_steps": len([s for s in ktr_model.steps if s.is_transform]),
            "output_steps": len([s for s in ktr_model.steps if s.is_output]),
            "graph_depth": 0,
            "graph_width": 0,
            "cycles": len(list(nx.simple_cycles(graph))),
        }
        
        # Calcular profundidade e largura do grafo
        try:
            if graph.nodes():
                metrics["graph_depth"] = nx.dag_longest_path_length(graph) if nx.is_directed_acyclic_graph(graph) else 0
                metrics["graph_width"] = max(len(list(nx.ancestors(graph, node))) + 1 for node in graph.nodes())
        except:
            pass
        
        return metrics
    
    def _detect_patterns(self, ktr_model: KTRModel, graph: nx.DiGraph) -> List[PipelinePattern]:
        """Detecta padrões comuns no pipeline"""
        patterns = []
        
        for pattern_name, detector in self.pattern_detectors.items():
            try:
                pattern = detector(ktr_model, graph)
                if pattern:
                    patterns.append(pattern)
                    logger.debug(f"🎯 Padrão detectado: {pattern_name}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao detectar padrão {pattern_name}: {e}")
        
        return patterns
    
    def _detect_simple_etl(self, ktr_model: KTRModel, graph: nx.DiGraph) -> Optional[PipelinePattern]:
        """Detecta padrão ETL simples: Input → [Transform] → Output"""
        input_steps = [s for s in ktr_model.steps if s.is_input]
        output_steps = [s for s in ktr_model.steps if s.is_output]
        
        if len(input_steps) == 1 and len(output_steps) == 1:
            # Verificar se há caminho direto do input ao output
            input_name = input_steps[0].name
            output_name = output_steps[0].name
            
            if nx.has_path(graph, input_name, output_name):
                path = nx.shortest_path(graph, input_name, output_name)
                
                return PipelinePattern(
                    name="Simple ETL",
                    description="Pipeline ETL simples com uma fonte e um destino",
                    steps_involved=path,
                    confidence=0.9
                )
        
        return None
    
    def _detect_lookup_pattern(self, ktr_model: KTRModel, graph: nx.DiGraph) -> Optional[PipelinePattern]:
        """Detecta padrão de lookup/join"""
        # Buscar nós com múltiplas entradas (possível join)
        join_candidates = [node for node in graph.nodes() if graph.in_degree(node) > 1]
        
        if join_candidates:
            return PipelinePattern(
                name="Lookup/Join",
                description="Pipeline com operações de lookup ou join",
                steps_involved=join_candidates,
                confidence=0.7
            )
        
        return None
    
    def _detect_aggregation_pattern(self, ktr_model: KTRModel, graph: nx.DiGraph) -> Optional[PipelinePattern]:
        """Detecta padrão de agregação"""
        # Buscar steps do tipo GroupBy
        groupby_steps = [s.name for s in ktr_model.steps if s.type == StepType.GROUP_BY]
        
        if groupby_steps:
            return PipelinePattern(
                name="Aggregation",
                description="Pipeline com operações de agregação",
                steps_involved=groupby_steps,
                confidence=0.95
            )
        
        return None
    
    def _detect_file_processing(self, ktr_model: KTRModel, graph: nx.DiGraph) -> Optional[PipelinePattern]:
        """Detecta processamento de arquivos"""
        file_steps = [s.name for s in ktr_model.steps if s.type in [StepType.EXCEL_INPUT, StepType.TEXT_FILE_INPUT]]
        
        if file_steps:
            return PipelinePattern(
                name="File Processing",
                description="Pipeline que processa arquivos (Excel, CSV, etc.)",
                steps_involved=file_steps,
                confidence=0.9
            )
        
        return None
    
    def _suggest_optimizations(self, ktr_model: KTRModel, patterns: List[PipelinePattern]) -> List[OptimizationSuggestion]:
        """Sugere otimizações baseadas na análise"""
        optimizations = []
        
        for rule in self.optimization_rules:
            try:
                suggestion = rule(ktr_model, patterns)
                if suggestion:
                    optimizations.append(suggestion)
            except Exception as e:
                logger.warning(f"⚠️ Erro ao aplicar regra de otimização: {e}")
        
        return optimizations
    
    def _suggest_batch_processing(self, ktr_model: KTRModel, patterns: List[PipelinePattern]) -> Optional[OptimizationSuggestion]:
        """Sugere processamento em lotes"""
        table_outputs = [s for s in ktr_model.steps if s.type == StepType.TABLE_OUTPUT]
        
        if table_outputs:
            return OptimizationSuggestion(
                type="batch_processing",
                description="Implementar processamento em lotes para melhor performance",
                impact="medium",
                code_example='''# Processamento em lotes
df.to_sql(
    name="tabela",
    con=connection,
    if_exists="append",
    index=False,
    method="multi",
    chunksize=10000  # Processar em lotes de 10k
)'''
            )
        
        return None
    
    def _suggest_parallel_processing(self, ktr_model: KTRModel, patterns: List[PipelinePattern]) -> Optional[OptimizationSuggestion]:
        """Sugere processamento paralelo"""
        # Se pipeline tem múltiplas entradas independentes
        input_steps = [s for s in ktr_model.steps if s.is_input]
        
        if len(input_steps) > 1:
            return OptimizationSuggestion(
                type="parallel_processing",
                description="Implementar processamento paralelo para múltiplas fontes",
                impact="high",
                code_example='''# Processamento paralelo
from concurrent.futures import ThreadPoolExecutor

def extract_source(source_config):
    return pd.read_sql(source_config.sql, source_config.connection)

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(extract_source, config) for config in sources]
    dataframes = [future.result() for future in futures]'''
            )
        
        return None
    
    def _suggest_data_validation(self, ktr_model: KTRModel, patterns: List[PipelinePattern]) -> OptimizationSuggestion:
        """Sempre sugere validação de dados"""
        return OptimizationSuggestion(
            type="data_validation",
            description="Adicionar validações de qualidade de dados",
            impact="high",
            code_example='''# Validação com Great Expectations
import great_expectations as gx

def validate_data(df):
    suite = gx.ExpectationSuite("data_quality")
    suite.expect_column_to_exist("required_column")
    suite.expect_column_values_to_not_be_null("required_column")
    
    context = gx.get_context()
    validator = context.get_validator(
        batch_request=gx.BatchRequest(datasource_name="pandas", data_asset_name="df"),
        expectation_suite=suite
    )
    
    result = validator.validate()
    return result.success'''
        )
    
    def _suggest_connection_pooling(self, ktr_model: KTRModel, patterns: List[PipelinePattern]) -> Optional[OptimizationSuggestion]:
        """Sugere pool de conexões"""
        if len(ktr_model.connections) > 0:
            return OptimizationSuggestion(
                type="connection_pooling",
                description="Implementar pool de conexões para melhor gestão de recursos",
                impact="medium",
                code_example='''# Pool de conexões
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    connection_url,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)'''
            )
        
        return None
    
    def _suggest_sql_optimization(self, ktr_model: KTRModel, patterns: List[PipelinePattern]) -> Optional[OptimizationSuggestion]:
        """Sugere otimizações de SQL"""
        table_inputs = [s for s in ktr_model.steps if s.type == StepType.TABLE_INPUT]
        
        if table_inputs:
            return OptimizationSuggestion(
                type="sql_optimization",
                description="Otimizar queries SQL com índices e filtros",
                impact="high",
                code_example='''# SQL otimizado
optimized_query = """
SELECT column1, column2
FROM large_table 
WHERE date_column >= CURRENT_DATE - INTERVAL '7 days'
    AND status = 'active'
ORDER BY date_column
LIMIT 10000
"""

# Usar índices apropriados
# CREATE INDEX idx_date_status ON large_table(date_column, status);'''
            )
        
        return None
    
    def _calculate_complexity(self, ktr_model: KTRModel, graph: nx.DiGraph) -> int:
        """Calcula score de complexidade (0-100)"""
        base_score = 0
        
        # Complexidade baseada em número de steps
        base_score += min(len(ktr_model.steps) * 5, 30)
        
        # Complexidade baseada em conexões
        base_score += min(len(ktr_model.connections) * 10, 20)
        
        # Complexidade baseada em profundidade do grafo
        try:
            if nx.is_directed_acyclic_graph(graph):
                depth = nx.dag_longest_path_length(graph)
                base_score += min(depth * 3, 15)
        except:
            pass
        
        # Complexidade baseada em padrões complexos
        transform_steps = len([s for s in ktr_model.steps if s.is_transform])
        base_score += min(transform_steps * 3, 20)
        
        # Penalidade por ciclos
        try:
            cycles = len(list(nx.simple_cycles(graph)))
            base_score += cycles * 10
        except:
            pass
        
        return min(base_score, 100)
    
    def _estimate_performance_gain(self, optimizations: List[OptimizationSuggestion]) -> int:
        """Estima ganho de performance baseado nas otimizações"""
        impact_weights = {
            "high": 30,
            "medium": 15,
            "low": 5
        }
        
        total_gain = 0
        for opt in optimizations:
            total_gain += impact_weights.get(opt.impact, 0)
        
        # Cap em 80% para ser realista
        return min(total_gain, 80) 