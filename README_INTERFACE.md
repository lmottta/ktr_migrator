# 🖥️ KTR Platform - Guia da Interface

[![Interface](https://img.shields.io/badge/Interface-Streamlit-brightgreen.svg)](https://streamlit.io)
[![Status](https://img.shields.io/badge/Status-Atualizado-green.svg)]()
[![Deploy](https://img.shields.io/badge/Deploy-Docker%20%2B%20Local-blue.svg)]()

## 🎯 **Visão Geral**

Este guia fornece instruções **atualizadas** para usar a interface web do KTR Platform, incluindo as novas funcionalidades Docker e melhorias de deployment.

### **📊 Dashboard Principal**

A interface principal oferece:

- 🔄 **Migração de KTR** - Upload e conversão de arquivos Pentaho
- ⚡ **Execução de Fluxos** - Execução manual e monitoramento 
- ⏰ **Agendamentos** - Sistema avançado de scheduling
- 📈 **Analytics** - Métricas e performance dos pipelines
- 🐳 **Status Docker** - Monitoramento de containers (quando usando Docker)

---

## 🚀 **Métodos de Acesso**

### **🐳 Via Docker (Recomendado)**

```bash
# 1. Deploy automatizado
cd ktr_platform
./docker-deploy-simple.sh

# 2. Acesse a interface
http://localhost:8501
```

**✅ Vantagens Docker:**
- Ambiente isolado e consistente
- Banco PostgreSQL + Redis incluídos
- Monitoramento integrado
- Backup automático

### **🐍 Via Local (Desenvolvimento)**

```bash
# 1. Preparar ambiente
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Instalar dependências
pip install -r requirements_platform.txt

# 3. Executar aplicação
cd ktr_platform
streamlit run app.py

# 4. Acesse a interface
http://localhost:8501
```

**✅ Vantagens Local:**
- Desenvolvimento rápido
- Debug facilitado
- Flexibilidade total

---

## 📱 **Funcionalidades da Interface**

### **🔄 Seção: Migração de KTR**

#### **Upload de Arquivo**
1. Clique em "➕ **Importar Fluxo**"
2. Faça upload do arquivo `.ktr`
3. Aguarde análise automática

#### **Configuração**
- ⚙️ **Configurações de Banco** - Conectores SQL
- 🔧 **Parâmetros de Pipeline** - Variáveis customizáveis
- 🧪 **Validações** - Regras de qualidade de dados

#### **Geração de Código**
- 📝 **Preview do Código** - Visualização antes da geração
- 📦 **Download do Projeto** - Estrutura completa Python
- 🧪 **Testes Incluídos** - Testes unitários automáticos

### **⚡ Seção: Execução de Fluxos**

#### **Dashboard de Fluxos**
```
📊 Visão Geral dos Fluxos
├── 🔄 Status Atual (Executando/Parado/Erro)
├── ⏱️ Última Execução 
├── 📈 Tempo Médio de Execução
└── 🎯 Taxa de Sucesso
```

#### **Execução Manual**
1. Selecione o fluxo desejado
2. Clique "▶️ **Executar**"
3. Monitore logs em tempo real
4. Analise métricas de performance

#### **Logs em Tempo Real**
- 📋 **Stream de Logs** - Acompanhamento live
- 🔍 **Filtros** - Por nível (ERROR, WARN, INFO)
- 💾 **Download** - Exportar logs para análise

### **⏰ Seção: Agendamentos**

#### **Tipos de Agendamento Disponíveis**

1. **📅 Diário**
   ```
   ⏰ Todo dia no mesmo horário
   Exemplo: Diariamente às 14:30
   ```

2. **📆 Semanal**
   ```
   📅 Dias específicos da semana
   Exemplo: Segunda, Quarta, Sexta às 09:00
   ```

3. **🗓️ Datas Específicas**
   ```
   📋 Lista de datas escolhidas
   Exemplo: 15/01, 15/02, 15/03 às 10:00
   ```

4. **⚙️ Personalizado (Cron)**
   ```
   🔧 Expressões cron avançadas
   Exemplo: 0 */4 * * * (a cada 4 horas)
   ```

5. **🕐 Múltiplos Horários**
   ```
   ⏰ Vários horários por dia
   Exemplo: 08:00, 12:00, 18:00
   ```

6. **📋 Horários por Dia da Semana**
   ```
   📅 Configuração individual por dia
   Exemplo: Seg(09:00), Ter(10:00), Qua(11:00)
   ```

7. **⏱️ Por Intervalo**
   ```
   🔄 Execução periódica
   Exemplo: A cada 30 minutos
   ```

#### **Interface de Agendamentos**

```
🎛️ Configurador de Agendamentos
├── 📝 Nome do Agendamento
├── 🔄 Seleção do Fluxo
├── ⏰ Tipo de Agendamento
├── 🕐 Configuração de Horários
├── 📅 Data de Início/Fim
├── ✅ Ativação do Agendamento
└── 💾 Salvar Configuração
```

### **📈 Seção: Analytics e Monitoramento**

#### **Métricas Principais**
- 📊 **Taxa de Sucesso** - % de execuções bem-sucedidas
- ⏱️ **Tempo Médio** - Performance média dos pipelines
- 🔄 **Execuções/Dia** - Volume de processamento
- 💾 **Uso de Recursos** - CPU, Memória, Disco

#### **Gráficos Interativos**
- 📈 **Timeline de Execuções** - Histórico temporal
- 🥧 **Distribuição de Status** - Success/Error/Running
- 📊 **Performance por Fluxo** - Comparativo de pipelines
- 🔥 **Top Fluxos** - Mais executados

### **🐳 Seção: Status Docker (Novo!)**

**Disponível apenas quando executando via Docker:**

#### **Status dos Containers**
```
🐳 Docker Status
├── 🚀 KTR Platform App (healthy/unhealthy)
├── 🗄️ PostgreSQL DB (healthy/unhealthy)
├── 🚀 Redis Cache (healthy/unhealthy)
├── 🔀 Nginx Proxy (se ativado)
└── 📊 Monitoring Stack (se ativado)
```

#### **Métricas de Containers**
- 💾 **Uso de Memória** - RAM por container
- 🖥️ **CPU Usage** - Processamento em tempo real
- 🌐 **Networking** - Status da comunicação
- 📦 **Volumes** - Espaço em disco usado

---

## 🎨 **Temas e Personalização**

### **Configuração Visual**
A interface suporta personalização através de variáveis de ambiente:

```env
# Tema principal
STREAMLIT_THEME_PRIMARY_COLOR=#FF6B6B
STREAMLIT_THEME_BACKGROUND_COLOR=#FFFFFF
STREAMLIT_THEME_SECONDARY_BACKGROUND_COLOR=#F0F2F6

# Configurações de upload
STREAMLIT_MAX_UPLOAD_SIZE=200
```

### **Modo Escuro/Claro**
- 🌙 **Modo Escuro** - Disponível no menu do Streamlit
- ☀️ **Modo Claro** - Padrão da aplicação
- 🎨 **Auto** - Segue configuração do sistema

---

## 🔧 **Configurações Avançadas**

### **Configurações de Interface**

#### **Via Docker**
```yaml
# docker-compose.yml
environment:
  - STREAMLIT_THEME_PRIMARY_COLOR=#FF6B6B
  - STREAMLIT_MAX_UPLOAD_SIZE=200
  - STREAMLIT_SERVER_HEADLESS=true
  - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

#### **Via Local**
```bash
# Arquivo .streamlit/config.toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"

[server]
headless = true
port = 8501
```

### **Performance da Interface**

#### **Otimizações Aplicadas**
- ✅ **Cache Inteligente** - Streamlit caching otimizado
- ✅ **Lazy Loading** - Carregamento sob demanda
- ✅ **Session State** - Gerenciamento de estado eficiente
- ✅ **Async Operations** - Operações não-bloqueantes

#### **Configurações de Performance**
```python
# Para desenvolvimento local
streamlit run app.py --server.runOnSave=true --server.headless=false

# Para produção
streamlit run app.py --server.headless=true --server.port=8501
```

---

## 📱 **Responsividade e Mobile**

### **Compatibilidade**
- ✅ **Desktop** - Experiência completa
- ✅ **Tablet** - Interface adaptada
- ⚠️ **Mobile** - Funcionalidades básicas (limitações do Streamlit)

### **Recomendações de Uso**
- 💻 **Desenvolvimento** - Desktop/Laptop recomendado
- 📊 **Monitoramento** - Tablet adequado
- 📱 **Consultas Rápidas** - Mobile aceitável

---

## 🆘 **Troubleshooting da Interface**

### **Problemas Comuns**

#### **Interface não carrega**
```bash
# Docker
docker-compose logs ktr-platform | grep streamlit

# Local  
streamlit doctor
```

#### **Upload de arquivo falha**
```bash
# Verificar limite de upload
echo $STREAMLIT_MAX_UPLOAD_SIZE

# Aumentar limite (se necessário)
export STREAMLIT_MAX_UPLOAD_SIZE=500
```

#### **Logs não aparecem em tempo real**
```bash
# Verificar conexão WebSocket
# Abrir DevTools do navegador -> Network -> WS
```

#### **Performance lenta**
```bash
# Limpar cache do Streamlit
streamlit cache clear

# Docker: Verificar recursos
docker stats ktr-platform-app
```

### **Debug da Interface**

#### **Modo Debug**
```bash
# Ativar debug local
export STREAMLIT_DEBUG=true
streamlit run app.py

# Docker debug
docker-compose exec ktr-platform streamlit run app.py --logger.level=debug
```

#### **Profiling de Performance**
```bash
# Instalar profiler
pip install streamlit-profiler

# Usar no código
import streamlit_profiler
streamlit_profiler.start()
```

---

## 📚 **Recursos Úteis**

### **Atalhos de Teclado**
- `R` - Recarregar aplicação
- `Ctrl+Shift+R` - Hard reload
- `F11` - Modo fullscreen
- `Ctrl+/` - Mostrar atalhos

### **URLs Úteis**
- 🏠 **Interface Principal**: http://localhost:8501
- 🔧 **Health Check**: http://localhost:8501/_stcore/health
- 📊 **Metrics** (se habilitado): http://localhost:8501/_stcore/metrics

### **Documentação Adicional**
- 📖 **[README Principal](README.md)** - Guia completo
- 🐳 **[Docker Guide](ktr_platform/README_DOCKER.md)** - Deploy Docker
- ⏰ **[Agendamentos](HORARIOS_CUSTOMIZADOS.md)** - Sistema de jobs
- 🧪 **[Testes](docs/desenvolvimento/)** - Documentação técnica

---

## 🎯 **Próximas Funcionalidades**

### **Roadmap da Interface**
- [ ] **API REST Integration** - Endpoints para automação
- [ ] **User Authentication** - Sistema de login
- [ ] **Multi-tenancy** - Suporte a múltiplos usuários  
- [ ] **Custom Dashboards** - Dashboards personalizáveis
- [ ] **Mobile App** - Aplicativo nativo
- [ ] **Real-time Notifications** - Alertas em tempo real

---

<div align="center">

**🖥️ Interface Moderna e Intuitiva para Engenharia de Dados**

*Desenvolvido com Streamlit para máxima produtividade*

[![Streamlit](https://img.shields.io/badge/Powered%20by-Streamlit-red.svg)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

</div> 