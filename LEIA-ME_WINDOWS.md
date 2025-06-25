# 🚀 KTR Migrator Platform Pro - Guia Windows

## 📋 **Execução com 2 Cliques - Sem Git**

### 🎯 **Arquivos .BAT Disponíveis:**

| **Arquivo** | **Função** | **Quando Usar** |
|-------------|------------|-----------------|
| `SETUP_WINDOWS.bat` | **Setup Completo** | Primeira execução ou problemas |
| `START_KTR.bat` | **Execução Rápida** | Uso diário após setup |
| `run_platform.bat` | **Execução Simples** | Alternativa mais básica |
| `DIAGNOSTICO.bat` | **Verificar Problemas** | Quando algo não funciona |

---

## 🚀 **Primeira Execução (Setup Inicial)**

### **Passo 1: Execute o Setup**
1. ✅ **Clique duplo** em `SETUP_WINDOWS.bat`
2. 🔄 O script irá:
   - Verificar se Python está instalado
   - Criar ambiente virtual
   - Instalar todas as dependências
   - Configurar o projeto
   - **Iniciar automaticamente** a plataforma

### **Pré-requisitos:**
- 🐍 **Python 3.8+** instalado
  - Download: https://www.python.org/downloads/
  - ⚠️ **IMPORTANTE**: Marcar "Add Python to PATH" durante instalação

---

## ⚡ **Execução Diária (Após Setup)**

### **Opção 1: Execução Rápida (Recomendada)**
- ✅ **Clique duplo** em `START_KTR.bat`
- 🌐 Navegador abre automaticamente em `http://localhost:8501`

### **Opção 2: Execução Simples**
- ✅ **Clique duplo** em `run_platform.bat`
- 📱 Instala dependências básicas a cada execução

---

## 🔧 **Solução de Problemas**

### **Se algo não funciona:**
1. ✅ **Execute**: `DIAGNOSTICO.bat`
2. 📋 Verifique o relatório de diagnóstico
3. 🔄 Se necessário, execute novamente: `SETUP_WINDOWS.bat`

### **Problemas Comuns:**

#### **❌ Python não encontrado**
```
Solução:
1. Baixe Python: https://www.python.org/downloads/
2. Durante instalação: ✅ "Add Python to PATH"
3. Reinicie o terminal/computador
4. Execute: SETUP_WINDOWS.bat
```

#### **❌ Erro de dependências**
```
Solução:
1. Execute: DIAGNOSTICO.bat
2. Verifique quais pacotes faltam
3. Execute: SETUP_WINDOWS.bat novamente
```

#### **❌ Porta 8501 em uso**
```
Solução:
1. Feche outros processos Streamlit
2. Ou modifique a porta no arquivo .bat:
   --server.port=8502
```

#### **❌ Ambiente virtual corrompido**
```
Solução:
1. Delete a pasta "venv"
2. Execute: SETUP_WINDOWS.bat
```

---

## 📁 **Estrutura do Projeto**

Após o setup, você terá:

```
ktr_migrator/
├── 🔧 SETUP_WINDOWS.bat        # Setup completo
├── ⚡ START_KTR.bat            # Execução rápida  
├── 🚀 run_platform.bat        # Execução simples
├── 🔍 DIAGNOSTICO.bat         # Diagnóstico
├── 📁 venv/                   # Ambiente virtual Python
├── 📁 ktr_platform/           # Aplicação principal
│   ├── 📱 app.py              # Interface Streamlit
│   ├── ⚙️ .env                # Configurações
│   ├── 📊 data/               # Dados persistentes
│   └── 📁 flows/              # Fluxos migrados
└── 📚 docs/                   # Documentação
```

---

## 🎯 **Recursos da Plataforma**

### **📱 Interface Web:**
- 🔄 **Migração de KTR**: Converte arquivos Pentaho para Python
- 📊 **Dashboard**: Visualização de fluxos e estatísticas
- ⏰ **Agendamentos**: 7 tipos de agendamento diferentes
- 🏃 **Execução**: Execute fluxos manualmente ou automaticamente
- 📈 **Monitoramento**: Logs em tempo real e métricas

### **🔗 URLs Importantes:**
- 🌐 **Plataforma**: http://localhost:8501
- 📊 **Flows**: http://localhost:8501 (seção "Fluxos Migrados")
- ⏰ **Agendamentos**: http://localhost:8501 (seção "Agendamentos")

---

## 🛠️ **Configurações Avançadas**

### **Arquivo .env (ktr_platform/.env):**
```ini
# Configurações da aplicação
APP_NAME=KTR Platform Pro
APP_VERSION=1.0.0
DEBUG=false

# Servidor
HOST=localhost
PORT=8501

# Banco de dados
DATABASE_TYPE=postgresql
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=ktr_platform
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres

# Execução
MAX_CONCURRENT_JOBS=3
JOB_TIMEOUT=3600
```

### **Personalizar Porta:**
Se a porta 8501 estiver ocupada, edite nos arquivos .bat:
```batch
streamlit run app.py --server.port=8502
```

---

## 📞 **Suporte**

### **Comandos Úteis:**
```batch
# Verificar Python
python --version

# Verificar pip
pip --version

# Listar pacotes instalados
pip list

# Verificar estrutura
dir ktr_platform
```

### **Logs e Debug:**
- 📋 Logs ficam em: `ktr_platform/logs/`
- 🔍 Para debug: Configure `DEBUG=true` no .env

---

## 🎉 **Pronto para Usar!**

1. ✅ **Primeira vez**: Execute `SETUP_WINDOWS.bat`
2. ⚡ **Uso diário**: Execute `START_KTR.bat`
3. 🌐 **Acesso**: http://localhost:8501
4. 🔧 **Problemas**: Execute `DIAGNOSTICO.bat`

**🎯 Com apenas 2 cliques, sua plataforma estará rodando!** 