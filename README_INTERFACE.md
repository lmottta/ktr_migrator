# 🎨 **INTERFACE WEB - KTR MIGRATOR**

Interface gráfica moderna para migração de pipelines Pentaho KTR para Python.

![Interface Preview](https://img.shields.io/badge/Interface-Streamlit-FF6B6B)
![Status](https://img.shields.io/badge/Status-Funcional-00D26A)

## 🚀 **Como Iniciar**

### **Método 1: Script Automático**
```bash
python start_interface.py
```

### **Método 2: Streamlit Direto**
```bash
streamlit run interface.py
```

### **Método 3: Comando Personalizado**
```bash
streamlit run interface.py --server.port 8501 --browser.gatherUsageStats false
```

## 📱 **Funcionalidades da Interface**

### 🔍 **1. Upload e Análise**
- **📁 Upload de arquivos KTR** via drag & drop
- **🔍 Análise automática** de estrutura e padrões
- **📊 Métricas visuais** de complexidade

### 🎯 **2. Visualização do Pipeline**
- **🔄 Fluxo visual** dos steps e conexões
- **📋 Detalhes dos steps** com informações técnicas
- **🎨 Gráficos interativos** com Plotly

### ⚙️ **3. Configuração de Conversão**
- **🚀 Opções de otimização** selecionáveis
- **🎨 Formatação automática** de código
- **🧪 Geração de testes** unitários

### 📥 **4. Download do Projeto**
- **📦 Projeto Python completo** em ZIP
- **📄 Múltiplos arquivos** estruturados
- **⚡ Download instantâneo**

## 🎮 **Como Usar**

### **Passo 1: Carregar KTR**
1. Abra a interface em http://localhost:8501
2. Na barra lateral, clique em "📁 Selecione seu arquivo KTR"
3. Faça upload do arquivo .ktr

### **Passo 2: Analisar**
1. Clique em "🔍 Analisar KTR"
2. Visualize as métricas e fluxo do pipeline
3. Revise os padrões detectados

### **Passo 3: Configurar**
1. Marque as opções desejadas:
   - ✅ 🚀 Aplicar otimizações
   - ✅ 🎨 Formatar código  
   - ✅ 🧪 Gerar testes

### **Passo 4: Converter**
1. Clique em "🔄 Converter para Python"
2. Aguarde a geração do código
3. Faça preview dos arquivos gerados

### **Passo 5: Download**
1. Clique em "📥 Download Projeto Python"
2. Extraia o arquivo ZIP
3. Siga as instruções do README gerado

## 📊 **Recursos Visuais**

### **Dashboard Principal**
- **📈 Métricas em tempo real**
- **🎯 Score de complexidade**
- **⚡ Performance estimada**
- **🔧 Contadores de steps**

### **Visualização de Fluxo**
- **🔄 Grafo interativo** do pipeline
- **🎨 Cores por tipo** de step
- **📝 Tooltips informativos**
- **🔍 Zoom e navegação**

### **Análise Detalhada**
- **📋 Cards de padrões** detectados
- **🚀 Sugestões de otimização** com exemplos
- **📊 Gráficos de distribuição** de steps

## 🛠️ **Tecnologias Utilizadas**

| Componente | Tecnologia | Versão |
|------------|------------|--------|
| **Interface** | Streamlit | 1.28+ |
| **Visualização** | Plotly | 5.17+ |
| **Backend** | KTR Migrator | 1.0.0 |
| **Processamento** | Pandas | 2.0+ |

## 🎯 **Exemplos de Uso**

### **1. Pipeline Simples ETL**
```
📥 Input: usuarios.ktr
🔄 Análise: 3 steps, complexidade 44
📊 Padrões: Simple ETL (90% confiança)
📥 Output: projeto Python com 5 arquivos
```

### **2. Pipeline Complexo com Joins**
```
📥 Input: vendas_complexo.ktr  
🔄 Análise: 12 steps, complexidade 78
📊 Padrões: Lookup/Join (85% confiança)
📥 Output: projeto Python otimizado
```

## 🔧 **Personalização**

### **Configurar Porta**
```bash
streamlit run interface.py --server.port 8080
```

### **Modo Desenvolvimento**
```bash
streamlit run interface.py --server.runOnSave true
```

### **Desabilitar Analytics**
```bash
streamlit run interface.py --browser.gatherUsageStats false
```

## 📱 **Interface Mobile**

A interface é **responsiva** e funciona em:
- **💻 Desktop** (recomendado)
- **📱 Tablet** (funcional)
- **📱 Smartphone** (limitado)

## 🆘 **Solução de Problemas**

### **Interface não abre**
```bash
# Verificar se Streamlit está instalado
pip install streamlit

# Verificar conflitos de porta
netstat -an | grep 8501
```

### **Erro de import**
```bash
# Verificar se está no diretório correto
cd /caminho/para/ktr_migrator

# Verificar dependências
pip install -r requirements_interface.txt
```

### **Upload falha**
- Verificar se o arquivo é .ktr válido
- Tamanho máximo: 200MB
- Formatos aceitos: .ktr, .XML

## 📈 **Performance**

| Operação | Tempo Médio | Recursos |
|----------|-------------|----------|
| **Upload** | < 1s | Baixo |
| **Análise** | 2-5s | Médio |
| **Conversão** | 3-10s | Alto |
| **Download** | < 1s | Baixo |

## 🎉 **Próximas Funcionalidades**

- [ ] **📊 Dashboard de múltiplos KTRs**
- [ ] **🔄 Conversão em lote via interface**
- [ ] **📝 Editor de código online**
- [ ] **🧪 Execução de testes na interface**
- [ ] **📊 Comparação antes/depois**

---

**🎯 A interface está pronta para uso! Experimente agora mesmo!** 🚀 