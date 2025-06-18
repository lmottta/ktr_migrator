#!/usr/bin/env python3
"""
KTR Migrator - CLI Interface
Ferramenta para migração de pipelines Pentaho KTR para Python

Usage:
    ktr-migrator convert <ktr_file> --output <output_dir>
    ktr-migrator analyze <ktr_file> [--report <report_file>]
    ktr-migrator batch-convert <input_dir> --output <output_dir>
    ktr-migrator validate <ktr_file>
"""

import click
import os
import sys
from pathlib import Path
from typing import List
from loguru import logger
import json

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.parser.ktr_parser import KTRParser
from src.generator.code_generator import CodeGenerator
from src.analyzer.pipeline_analyzer import PipelineAnalyzer

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """🔄 KTR Migrator - Migração de pipelines Pentaho para Python"""
    setup_logging()

def setup_logging():
    """Configura logging global"""
    logger.remove()  # Remove handler padrão
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level="INFO"
    )
    logger.add(
        "logs/ktr_migrator.log",
        rotation="1 MB",
        retention="7 days",
        format="{time} | {level} | {message}",
        level="DEBUG"
    )

@cli.command()
@click.argument('ktr_file', type=click.Path(exists=True))
@click.option('--output', '-o', required=True, help='Diretório de saída')
@click.option('--optimize', is_flag=True, help='Aplicar otimizações avançadas')
@click.option('--format-code', is_flag=True, default=True, help='Formatar código gerado')
@click.option('--generate-tests', is_flag=True, default=True, help='Gerar testes automatizados')
def convert(ktr_file: str, output: str, optimize: bool, format_code: bool, generate_tests: bool):
    """
    🔄 Converte um arquivo KTR para pipeline Python
    
    \b
    Exemplo:
        ktr-migrator convert exemplo.ktr --output ./pipeline_python/
    """
    logger.info(f"🚀 Iniciando conversão: {ktr_file}")
    
    try:
        # Parse do KTR
        parser = KTRParser()
        ktr_model = parser.parse_file(ktr_file)
        
        # Análise (se otimização habilitada)
        if optimize:
            analyzer = PipelineAnalyzer()
            analysis = analyzer.analyze_pipeline(ktr_model)
            logger.info(f"📊 Análise completa: {analysis.complexity_score} pontos")
        
        # Geração do código
        generator = CodeGenerator()
        project = generator.generate_pipeline(ktr_model, output)
        
        # Pós-processamento
        if format_code:
            _format_generated_code(project)
        
        # Relatório de sucesso
        _print_conversion_report(ktr_file, project)
        
        logger.info(f"✅ Conversão concluída com sucesso!")
        logger.info(f"📁 Projeto gerado em: {output}")
        
    except Exception as e:
        logger.error(f"❌ Erro na conversão: {e}")
        sys.exit(1)

@cli.command()
@click.argument('ktr_file', type=click.Path(exists=True))
@click.option('--report', '-r', help='Arquivo de relatório (HTML/JSON)')
@click.option('--format', 'report_format', type=click.Choice(['json', 'html', 'text']), default='text')
def analyze(ktr_file: str, report: str, report_format: str):
    """
    🔍 Analisa um arquivo KTR sem gerar código
    
    \b
    Exemplo:
        ktr-migrator analyze exemplo.ktr --report relatorio.html --format html
    """
    logger.info(f"🔍 Analisando arquivo: {ktr_file}")
    
    try:
        # Parse do KTR
        parser = KTRParser()
        ktr_model = parser.parse_file(ktr_file)
        
        # Análise detalhada
        analyzer = PipelineAnalyzer()
        analysis = analyzer.analyze_pipeline(ktr_model)
        
        # Gerar relatório
        if report:
            _generate_analysis_report(analysis, report, report_format)
        else:
            _print_analysis_summary(analysis)
        
        logger.info("✅ Análise concluída!")
        
    except Exception as e:
        logger.error(f"❌ Erro na análise: {e}")
        sys.exit(1)

@cli.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.option('--output', '-o', required=True, help='Diretório base de saída')
@click.option('--pattern', default='*.ktr', help='Padrão de arquivos (ex: *.ktr)')
@click.option('--optimize', is_flag=True, help='Aplicar otimizações')
def batch_convert(input_dir: str, output: str, pattern: str, optimize: bool):
    """
    📦 Converte múltiplos arquivos KTR em lote
    
    \b
    Exemplo:
        ktr-migrator batch-convert ./ktr_files/ --output ./python_pipelines/
    """
    logger.info(f"📦 Conversão em lote: {input_dir}")
    
    input_path = Path(input_dir)
    ktr_files = list(input_path.glob(pattern))
    
    if not ktr_files:
        logger.warning(f"⚠️ Nenhum arquivo encontrado com padrão: {pattern}")
        return
    
    logger.info(f"📁 {len(ktr_files)} arquivos encontrados")
    
    success_count = 0
    error_count = 0
    
    for ktr_file in ktr_files:
        try:
            logger.info(f"🔄 Processando: {ktr_file.name}")
            
            # Parse e geração
            parser = KTRParser()
            ktr_model = parser.parse_file(str(ktr_file))
            
            # Diretório específico para este pipeline
            pipeline_output = Path(output) / ktr_model.name
            
            generator = CodeGenerator()
            project = generator.generate_pipeline(ktr_model, str(pipeline_output))
            
            success_count += 1
            logger.info(f"✅ {ktr_file.name} convertido")
            
        except Exception as e:
            error_count += 1
            logger.error(f"❌ Erro em {ktr_file.name}: {e}")
            continue
    
    # Relatório final
    logger.info(f"📊 Conversão em lote concluída:")
    logger.info(f"   ✅ Sucessos: {success_count}")
    logger.info(f"   ❌ Erros: {error_count}")
    logger.info(f"   📁 Saída: {output}")

@cli.command()
@click.argument('ktr_file', type=click.Path(exists=True))
def validate(ktr_file: str):
    """
    ✅ Valida a estrutura de um arquivo KTR
    
    \b
    Exemplo:
        ktr-migrator validate exemplo.ktr
    """
    logger.info(f"✅ Validando arquivo: {ktr_file}")
    
    try:
        parser = KTRParser()
        ktr_model = parser.parse_file(ktr_file)
        
        # Validações básicas
        issues = []
        
        if not ktr_model.connections:
            issues.append("⚠️ Nenhuma conexão definida")
        
        if not ktr_model.steps:
            issues.append("❌ Nenhum step encontrado")
        
        if not ktr_model.hops:
            issues.append("⚠️ Nenhum hop (conexão entre steps) encontrado")
        
        # Validar integridade dos hops
        step_names = {step.name for step in ktr_model.steps}
        for hop in ktr_model.hops:
            if hop.from_step not in step_names:
                issues.append(f"❌ Hop inválido: step '{hop.from_step}' não existe")
            if hop.to_step not in step_names:
                issues.append(f"❌ Hop inválido: step '{hop.to_step}' não existe")
        
        # Relatório de validação
        if issues:
            logger.warning("⚠️ Issues encontrados:")
            for issue in issues:
                click.echo(f"  {issue}")
        else:
            logger.info("✅ KTR válido!")
            
        # Estatísticas
        click.echo(f"\n📊 Estatísticas:")
        click.echo(f"  📡 Conexões: {len(ktr_model.connections)}")
        click.echo(f"  🔧 Steps: {len(ktr_model.steps)}")
        click.echo(f"  🔗 Hops: {len(ktr_model.hops)}")
        
        # Breakdown por tipo de step
        input_steps = len([s for s in ktr_model.steps if s.is_input])
        transform_steps = len([s for s in ktr_model.steps if s.is_transform])
        output_steps = len([s for s in ktr_model.steps if s.is_output])
        
        click.echo(f"     📥 Input: {input_steps}")
        click.echo(f"     ⚙️ Transform: {transform_steps}")
        click.echo(f"     📤 Output: {output_steps}")
        
    except Exception as e:
        logger.error(f"❌ Erro na validação: {e}")
        sys.exit(1)

@cli.command()
@click.argument('ktr_file', type=click.Path(exists=True))
def preview(ktr_file: str):
    """
    👀 Preview do código que seria gerado (sem criar arquivos)
    
    \b
    Exemplo:
        ktr-migrator preview exemplo.ktr
    """
    logger.info(f"👀 Preview de: {ktr_file}")
    
    try:
        # Parse do KTR
        parser = KTRParser()
        ktr_model = parser.parse_file(ktr_file)
        
        # Gerar apenas template principal
        generator = CodeGenerator()
        template_data = generator._prepare_template_data(ktr_model)
        main_pipeline = generator._generate_main_pipeline(template_data)
        
        click.echo("🐍 Código Python que seria gerado:")
        click.echo("=" * 60)
        click.echo(main_pipeline[:2000])  # Primeiras 2000 chars
        
        if len(main_pipeline) > 2000:
            click.echo("\n... (código truncado)")
        
        click.echo("=" * 60)
        click.echo(f"📊 Total: {len(main_pipeline)} caracteres")
        
    except Exception as e:
        logger.error(f"❌ Erro no preview: {e}")
        sys.exit(1)

def _format_generated_code(project):
    """Formata código gerado usando black"""
    try:
        import subprocess
        
        for file_path, content in project.files.items():
            if file_path.endswith('.py'):
                full_path = Path(project.base_path) / file_path
                subprocess.run(['black', str(full_path)], capture_output=True)
        
        logger.info("🎨 Código formatado com black")
    except Exception as e:
        logger.warning(f"⚠️ Não foi possível formatar código: {e}")

def _print_conversion_report(ktr_file: str, project):
    """Imprime relatório de conversão"""
    click.echo("\n" + "=" * 60)
    click.echo("📋 RELATÓRIO DE CONVERSÃO")
    click.echo("=" * 60)
    click.echo(f"📄 Arquivo origem: {ktr_file}")
    click.echo(f"📁 Projeto destino: {project.base_path}")
    click.echo(f"🐍 Pipeline: {project.name}")
    click.echo(f"📦 Dependências: {', '.join(project.dependencies)}")
    click.echo(f"📄 Arquivos gerados: {len(project.files)}")
    
    click.echo("\n📁 Estrutura criada:")
    for file_path in sorted(project.files.keys()):
        click.echo(f"  📄 {file_path}")
    
    click.echo("\n🚀 Próximos passos:")
    click.echo(f"  1. cd {project.base_path}")
    click.echo(f"  2. pip install -r requirements.txt")
    click.echo(f"  3. cp .env.example .env")
    click.echo(f"  4. python src/pipelines/{project.name.lower()}_pipeline.py")

def _generate_analysis_report(analysis, report_file: str, format_type: str):
    """Gera relatório de análise"""
    if format_type == 'json':
        with open(report_file, 'w') as f:
            json.dump(analysis.to_dict(), f, indent=2)
    elif format_type == 'html':
        # Implementar geração HTML
        pass
    else:  # text
        with open(report_file, 'w') as f:
            f.write(f"Relatório de Análise KTR\n")
            f.write(f"=" * 30 + "\n\n")
            f.write(f"Complexidade: {analysis.complexity_score}\n")
            # Adicionar mais detalhes...

def _print_analysis_summary(analysis):
    """Imprime resumo da análise"""
    click.echo("\n📊 ANÁLISE DO PIPELINE")
    click.echo("=" * 30)
    click.echo(f"🎯 Complexidade: {analysis.complexity_score}/100")
    click.echo(f"⚡ Performance estimada: {analysis.estimated_performance_gain}%")
    click.echo(f"🔧 Otimizações sugeridas: {len(analysis.optimizations)}")

if __name__ == '__main__':
    cli() 