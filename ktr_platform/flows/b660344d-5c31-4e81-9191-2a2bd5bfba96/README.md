# Pipeline importatabelas

Pipeline ETL gerado automaticamente do KTR: importatabelas.ktr

## Descrição
Pipeline gerado do KTR importatabelas

## Estrutura
- **Extractors**: 27 configurados
- **Transformers**: 27 configurados  
- **Loaders**: 27 configurados

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
python src/pipelines/importatabelas_pipeline.py
```

## Monitoramento
Logs são gerados em: `logs/importatabelas_YYYYMMDD.log`

---
*Gerado em: 2025-08-26 14:45:03*
