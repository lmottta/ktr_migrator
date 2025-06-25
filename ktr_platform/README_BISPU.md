# 🚀 Quick Start - Banco BISPU para Testes KTR

## ⚡ Deploy Rápido

```bash
# 1. Acessar diretório
cd ktr_platform

# 2. Deploy do banco BISPU
./docker-deploy-bispu.sh

# 3. Verificar se está funcionando
docker ps | grep bispu
```

## 📊 Informações de Conexão

```
Host: localhost
Porta: 5433
Banco: bispu
Usuário: bispu_user
Senha: Nuncaperco19*
```

## 🧪 Tabelas de Teste Disponíveis

- `mgc.documento` - 3 registros de exemplo
- `mgc.localizacao_imovel` - 2 registros de exemplo
- `mgc.documento_processado` - Destino dos KTRs

## 🔧 Comandos Essenciais

```bash
# Acessar banco via psql
docker-compose exec bispu-db psql -U bispu_user -d bispu

# Ver dados de exemplo
docker-compose exec bispu-db psql -U bispu_user -d bispu -c "SELECT * FROM mgc.documento;"

# Parar banco
docker-compose --profile bispu down

# Ver logs
docker-compose logs -f bispu-db
```

## 📚 Documentação Completa

👉 Consulte: `docs/desenvolvimento/BANCO_BISPU_TESTES.md`

---

**Desenvolvido por**: Engenheiro de Dados Senior  
**Versão**: 1.0 