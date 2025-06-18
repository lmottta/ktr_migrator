# 🚀 KTR Platform Pro - Central de Jobs e Automação

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29%2B-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

Sistema completo para **migração**, **execução** e **agendamento** de pipelines Pentaho KTR para Python, com interface web moderna e sistema de agendamentos avançado.

## 🌟 **Características Principais**

### 🔄 **Migração Automatizada**
- ✅ **Parser KTR** - Análise e conversão de arquivos Pentaho
- ✅ **Geração de Código Python** - Templates otimizados
- ✅ **Estrutura de Projeto** - Organização profissional
- ✅ **Validação** - Análise de compatibilidade

### ⚡ **Execução e Monitoramento**
- ✅ **Executor Assíncrono** - Execução não-bloqueante
- ✅ **Logs em Tempo Real** - Monitoramento detalhado
- ✅ **Status Tracking** - Acompanhamento de execuções
- ✅ **Métricas de Performance** - Estatísticas detalhadas

### ⏰ **Sistema de Agendamentos Avançado**
- ✅ **7 Tipos de Agendamento** - Máxima flexibilidade
- ✅ **Horários Customizáveis** - Configuração granular
- ✅ **Scheduler Robusto** - Execução automática confiável
- ✅ **Interface Intuitiva** - Gerenciamento visual

### 🎯 **Interface Web Moderna**
- ✅ **Dashboard Interativo** - Visão geral completa
- ✅ **Design Responsivo** - Funciona em qualquer dispositivo
- ✅ **Streamlit Nativo** - Performance otimizada
- ✅ **UX Profissional** - Experiência do usuário excepcional

---

## 🚀 **Instalação Rápida**

### **Pré-requisitos**
- Python 3.8+
- pip (gerenciador de pacotes Python)
- Git (opcional, para clonagem)

### **1. Clone o Repositório**
```bash
git clone https://github.com/seu-usuario/ktr-platform-pro.git
cd ktr-platform-pro
```

### **2. Instale as Dependências**
```bash
# Instalar dependências principais
pip install -r requirements.txt

# Instalar dependências da interface
pip install -r requirements_interface.txt

# Instalar dependências da plataforma
pip install -r requirements_platform.txt
```

### **3. Execute a Aplicação**
```bash
# Iniciar interface completa
streamlit run ktr_platform/app.py

# Ou usar script de inicialização
python start_interface.py
```

### **4. Acesse no Navegador**
```
🌐 Interface Web: http://localhost:8501
📊 Dashboard: http://localhost:8501
```

---

## 📚 **Guia de Uso**

### **🔄 Migração de KTR**

1. **Upload do Arquivo KTR**
   - Acesse "➕ Importar Fluxo"
   - Faça upload do arquivo `.ktr`
   - Aguarde análise automática

2. **Análise e Validação**
   - Revise componentes detectados
   - Verifique compatibilidade
   - Customize configurações

3. **Geração do Código**
   - Clique em "Gerar Pipeline Python"
   - Aguarde criação da estrutura
   - Baixe projeto gerado

### **⚡ Execução de Fluxos**

1. **Dashboard Principal**
   - Visualize todos os fluxos
   - Monitore status em tempo real
   - Acesse logs de execução

2. **Execução Manual**
   - Selecione fluxo desejado
   - Clique "▶️ Executar"
   - Acompanhe progresso

3. **Monitoramento**
   - Logs em tempo real
   - Métricas de performance
   - Histórico de execuções

### **⏰ Agendamentos**

1. **Criar Agendamento**
   - Acesse "⏰ Agendamentos"
   - Escolha tipo de agendamento
   - Configure horários e periodicidade

2. **Tipos Disponíveis**
   - 📅 **Diário** - Todo dia no mesmo horário
   - 📆 **Semanal** - Dias específicos da semana
   - 🗓️ **Datas Específicas** - Datas escolhidas manualmente
   - ⚙️ **Personalizado** - Períodos customizados
   - 🕐 **Múltiplos Horários** - Vários horários por dia
   - 📋 **Horários por Dia** - Configuração por dia da semana
   - ⏱️ **Por Intervalo** - Execução a cada X minutos

3. **Gerenciamento**
   - Editar configurações
   - Pausar/ativar agendamentos
   - Monitorar próximas execuções

---

## 🏗️ **Arquitetura do Sistema**

### **Estrutura de Diretórios**
```
ktr_migrator/
├── 🚀 ktr_platform/          # Plataforma principal
│   ├── app.py                # Interface Streamlit
│   ├── flow_manager.py       # Gerenciamento de fluxos
│   ├── executor.py           # Executor de fluxos
│   ├── scheduler.py          # Sistema de agendamentos
│   ├── settings.py           # Configurações
│   ├── data/                 # Dados persistentes
│   │   ├── flows.json        # Metadados dos fluxos
│   │   └── schedules.json    # Agendamentos
│   └── flows/                # Fluxos migrados
├── 🔧 src/                   # Código fonte da migração
│   ├── parser/               # Parser KTR
│   ├── generator/            # Gerador de código
│   ├── analyzer/             # Analisador de pipelines
│   ├── models/               # Modelos de dados
│   └── templates/            # Templates de código
├── 📋 examples/              # Exemplos e demos
├── 🧪 tests/                 # Testes automatizados
├── 📚 docs/                  # Documentação
└── 📦 requirements*.txt      # Dependências
```

### **Componentes Principais**

#### **FlowManager**
- Gerenciamento CRUD de fluxos
- Persistência de metadados
- Controle de status

#### **FlowExecutor**
- Execução assíncrona
- Captura de logs
- Monitoramento de performance

#### **FlowScheduler**
- Sistema de agendamentos
- 7 tipos de configuração
- Persistência automática
- Cálculos inteligentes

#### **Interface Web**
- Dashboard interativo
- Formulários dinâmicos
- Visualizações em tempo real
- UX responsiva

---

## ⏰ **Sistema de Agendamentos Detalhado**

### **Tipos de Agendamento**

#### **1. 📅 Diário**
```python
# Executa todos os dias no mesmo horário
Configuração: Horário único (ex: 14:30)
Uso: Relatórios diários, backups rotineiros
```

#### **2. 📆 Semanal**
```python
# Executa em dias específicos da semana
Configuração: Dias + horário (ex: Seg, Qua, Sex às 09:00)
Uso: Processamentos semanais, sincronizações
```

#### **3. 🗓️ Datas Específicas**
```python
# Executa em datas escolhidas manualmente
Configuração: Lista de datas + horário
Uso: Processamentos pontuais, campanhas
```

#### **4. ⚙️ Personalizado**
```python
# Período com dias específicos
Configuração: Data início/fim + dias da semana + horário
Uso: Projetos temporários, períodos sazonais
```

#### **5. 🕐 Múltiplos Horários**
```python
# Vários horários no mesmo padrão
Configuração: Lista de horários + padrão (diário/semanal)
Exemplo: 08:00, 12:00, 18:00 todos os dias
Uso: Monitoramento frequente, sincronizações múltiplas
```

#### **6. 📋 Horários por Dia**
```python
# Horários diferentes para cada dia da semana
Configuração: {dia: [horários]}
Exemplo: Segunda [08:00, 14:00], Terça [10:00]
Uso: Rotinas específicas por dia, workflows complexos
```

#### **7. ⏱️ Por Intervalo**
```python
# Execução a intervalos regulares
Configuração: Intervalo + janela de tempo + dias
Exemplo: A cada 30 min das 08:00-18:00, Seg-Sex
Uso: Monitoramento contínuo, coleta de dados frequente
```

### **Funcionalidades Avançadas**

- ✅ **Cálculos Automáticos** - Previsão de execuções
- ✅ **Validações Inteligentes** - Configurações corretas
- ✅ **Edição Dinâmica** - Modificação sem parar sistema
- ✅ **Execução Manual** - Override de agendamentos
- ✅ **Monitoramento** - Status e próximas execuções

---

## 🔧 **Configuração**

### **Variáveis de Ambiente**
```bash
# .env (opcional)
STREAMLIT_PORT=8501
LOG_LEVEL=INFO
DATA_DIR=./ktr_platform/data
FLOWS_DIR=./ktr_platform/flows
```

### **Configurações do Sistema**
```python
# ktr_platform/settings.py
FLOWS_DIR = Path("ktr_platform/flows")
FLOWS_METADATA_FILE = Path("ktr_platform/data/flows.json")
SCHEDULES_FILE = Path("ktr_platform/data/schedules.json")
```

---

## 🧪 **Testes**

### **Executar Testes**
```bash
# Testes unitários
python -m pytest tests/

# Testes com cobertura
python -m pytest tests/ --cov=src --cov-report=html

# Testes específicos
python -m pytest tests/test_ktr_parser.py -v
```

### **Estrutura de Testes**
```
tests/
├── test_ktr_parser.py        # Parser KTR
├── test_code_generator.py    # Gerador de código
├── test_flow_manager.py      # Gerenciador de fluxos
├── test_scheduler.py         # Sistema de agendamentos
└── fixtures/                 # Dados de teste
```

---

## 📊 **Monitoramento e Logs**

### **Logs do Sistema**
```bash
# Logs principais
tail -f ktr_platform/logs/ktr_platform.log

# Logs específicos de fluxo
tail -f ktr_platform/flows/{flow_id}/logs/
```

### **Métricas Disponíveis**
- ✅ **Execuções por fluxo**
- ✅ **Tempo médio de execução**
- ✅ **Taxa de sucesso/falha**
- ✅ **Agendamentos ativos**
- ✅ **Próximas execuções**

---

## 🤝 **Contribuição**

### **Como Contribuir**
1. **Fork** o repositório
2. **Crie** uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. **Commit** suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/nova-funcionalidade`)
5. **Abra** um Pull Request

### **Padrões de Código**
- Python PEP 8
- Docstrings em português
- Testes para novas funcionalidades
- Commits semânticos

---

## 📄 **Licença**

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🆘 **Suporte**

### **Documentação**
- 📖 [Documentação Completa](docs/)
- 🚀 [Guia de Início Rápido](COMO_USAR_INTERFACE.md)
- ⏰ [Horários Customizados](HORARIOS_CUSTOMIZADOS.md)
- 🧪 [Guia de Testes](TESTE_HORARIOS_CUSTOMIZADOS.md)

### **Contato**
- 🐛 **Issues**: [GitHub Issues](https://github.com/seu-usuario/ktr-platform-pro/issues)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/seu-usuario/ktr-platform-pro/discussions)
- 📧 **Email**: seu-email@exemplo.com

---

## 🎯 **Roadmap**

### **Próximas Funcionalidades**
- [ ] 📊 Dashboard de performance avançado
- [ ] 🔔 Notificações push/email
- [ ] 📱 Interface mobile responsiva
- [ ] 🤖 AI para otimização de horários
- [ ] 🌐 API REST para integração
- [ ] 🐳 Containerização Docker
- [ ] ☁️ Deploy em cloud

### **Melhorias Planejadas**
- [ ] 📈 Métricas avançadas
- [ ] 🔄 Backup/restore automático
- [ ] 👥 Controle de acesso multi-usuário
- [ ] 📡 Webhooks para notificações
- [ ] 🔌 Sistema de plugins

---

**🚀 Desenvolvido com ❤️ para automação de dados empresariais**

*KTR Platform Pro - Transformando pipelines Pentaho em soluções Python modernas e escaláveis.* 