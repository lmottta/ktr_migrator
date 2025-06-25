# 🔐 Banco BISPU - Credenciais Atualizadas

## ✅ **Alteração Realizada em**: 2025-01-23

### 🔑 **Novas Credenciais de Acesso**

```
Host: localhost
Porta: 5433
Banco: bispu
Usuário: bispu_user
Senha: Nuncaperco19*
```

### 🔗 **String de Conexão Atualizada**
```
postgresql://bispu_user:Nuncaperco19*@localhost:5433/bispu
```

### 📋 **Configuração para DBeaver**

```
┌────────────────────────────────────┐
│ 📊 CONFIGURAÇÃO BISPU              │
├────────────────────────────────────┤
│ Host: localhost                    │
│ Port: 5433                         │  
│ Database: bispu                    │
│ Username: bispu_user               │
│ Password: Nuncaperco19*            │
│                                    │
│ ☑️ Show all databases              │
│ ☐ Use SSL                          │
└────────────────────────────────────┘
```

### 🔧 **Configurações SSL (Importante)**
- **SSL Mode**: disable
- **SSL Factory**: (vazio)

### 🧪 **Teste de Conexão**
```sql
-- Verificar conexão
SELECT current_user, current_database();

-- Ver dados de teste
SELECT * FROM mgc.documento;
```

### ✅ **Status**
- ✅ Senha alterada no banco de dados
- ✅ Arquivo .env.bispu atualizado
- ✅ Arquivo .env.bispu.example atualizado
- ✅ Documentação atualizada
- ✅ Teste de conexão bem-sucedido

---

**Desenvolvido por**: Engenheiro de Dados Senior  
**Data**: 2025-01-23 