# Pipeline exemplo_simples

Pipeline ETL gerado automaticamente do KTR: exemplo_simples.ktr

## Descrição
Pipeline ETL simples para demonstração do KTR Migrator

## Estrutura
- **Extractors**: 1 configurados
- **Transformers**: 1 configurados  
- **Loaders**: 1 configurados

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
python src/pipelines/exemplo_simples_pipeline.py
```

## Monitoramento
Logs são gerados em: `logs/exemplo_simples_YYYYMMDD.log`

---
*Gerado em: 2025-06-17 22:22:02*
