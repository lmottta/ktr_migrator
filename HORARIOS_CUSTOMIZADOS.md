# 🕐 Horários Customizados - KTR Platform

## 📋 Visão Geral

O sistema de agendamentos do KTR Platform foi expandido para oferecer **máxima flexibilidade** na configuração de horários, permitindo:

- 🕐 **Múltiplos horários** para o mesmo fluxo
- 📅 **Horários específicos por dia** da semana
- ⏱️ **Execução por intervalos** configuráveis
- 🎯 **Combinações avançadas** de todos os tipos

---

## 🚀 Novos Tipos de Agendamento

### 1. 🕐 Múltiplos Horários

Permite configurar **vários horários** para o mesmo tipo de agendamento.

**Configurações:**
- **Todos os dias**: Executa em múltiplos horários diariamente
- **Dias específicos**: Executa em múltiplos horários apenas nos dias selecionados

**Exemplo:**
```
Tipo: Múltiplos Horários - Todos os dias
Horários: 08:00, 12:00, 18:00
Resultado: Executa 3x por dia (8h, 12h, 18h)
```

**Exemplo Avançado:**
```
Tipo: Múltiplos Horários - Dias específicos
Dias: Segunda, Quarta, Sexta
Horários: 09:00, 15:00, 21:00
Resultado: 9 execuções por semana (3 dias × 3 horários)
```

### 2. 📋 Horários por Dia da Semana

Configure **horários diferentes** para cada dia da semana.

**Características:**
- Horários únicos por dia
- Flexibilidade total por dia da semana
- Ideal para rotinas específicas

**Exemplo:**
```
Segunda-feira: 08:00, 14:00
Terça-feira: 10:00
Quarta-feira: 08:00, 12:00, 16:00
Quinta-feira: 09:00, 18:00
Sexta-feira: 08:00, 20:00
Sábado: 10:00
Domingo: Não configurado

Total: 11 execuções por semana
```

### 3. ⏱️ Execução por Intervalo

Execute fluxos a **intervalos regulares** dentro de períodos específicos.

**Configurações:**
- **Intervalo**: De 1 minuto até 24 horas (1440 minutos)
- **Período**: Todo o dia, horário específico ou dias específicos
- **Controle de janela**: Horário de início e fim

**Exemplos:**

**Monitoramento Contínuo:**
```
Intervalo: 15 minutos
Período: Todo o dia (00:00 - 23:59)
Dias: Todos
Resultado: 96 execuções por dia
```

**Horário Comercial:**
```
Intervalo: 30 minutos
Período: 08:00 - 18:00
Dias: Segunda a Sexta
Resultado: 20 execuções por dia × 5 dias = 100 execuções/semana
```

**Fim de Semana:**
```
Intervalo: 2 horas
Período: 10:00 - 22:00
Dias: Sábado, Domingo
Resultado: 6 execuções por dia × 2 dias = 12 execuções/fim de semana
```

---

## 🎯 Casos de Uso Práticos

### 📊 **Relatórios de Vendas**
```
Tipo: Horários por Dia
Segunda: 09:00 (Relatório semanal)
Terça-Sexta: 17:30 (Relatório diário)
Sábado: 12:00 (Relatório fim de semana)
```

### 🔄 **Sincronização de Dados**
```
Tipo: Múltiplos Horários - Todos os dias
Horários: 06:00, 12:00, 18:00, 00:00
Descrição: Sincronização a cada 6 horas
```

### 📡 **Monitoramento de Sistema**
```
Tipo: Por Intervalo
Intervalo: 5 minutos
Período: 24/7
Descrição: Verificação contínua de saúde do sistema
```

### 💼 **Processamento Noturno**
```
Tipo: Por Intervalo
Intervalo: 30 minutos
Período: 22:00 - 06:00
Dias: Segunda a Sexta
Descrição: Processamento pesado fora do horário comercial
```

---

## 🛠️ Interface Atualizada

### **Criação de Agendamentos**

A interface agora oferece **7 tipos** de agendamento:

1. 📅 **Diário** - Horário único diário
2. 📆 **Semanal** - Horário único em dias específicos
3. 🗓️ **Datas Específicas** - Datas escolhidas manualmente
4. ⚙️ **Personalizado** - Período com dias específicos
5. 🕐 **Múltiplos Horários** - Vários horários por execução
6. 📋 **Horários por Dia** - Horários únicos por dia da semana
7. ⏱️ **Por Intervalo** - Execução a intervalos regulares

### **Visualização Melhorada**

**Lista de Agendamentos:**
- 📊 Estatísticas por tipo
- 🔍 Detalhes específicos por configuração
- ⏰ Tempo até próxima execução
- 📈 Previsão de execuções

**Edição Avançada:**
- ✏️ Edição inline para todos os tipos
- ➕ Adição/remoção de horários
- 🎛️ Configuração dinâmica de intervalos

---

## 📊 Métricas e Monitoramento

### **Previsões Automáticas**

O sistema calcula automaticamente:

- **Execuções por hora** para intervalos
- **Execuções por dia** para configurações complexas
- **Execuções por semana** para agendamentos semanais
- **Total de execuções** para períodos específicos

### **Exemplo de Cálculo:**
```
Configuração: Intervalo de 20 minutos, 08:00-18:00, Seg-Sex

Cálculo:
- Duração: 10 horas por dia
- Execuções/hora: 60/20 = 3
- Execuções/dia: 10 × 3 = 30
- Execuções/semana: 30 × 5 = 150

Resultado exibido: "~3 execuções/hora, ~30 execuções/dia"
```

---

## 🔧 Implementação Técnica

### **Novos Campos no ScheduleConfig:**

```python
@dataclass
class ScheduleConfig:
    times: List[str] = None  # ['08:00', '12:00', '18:00']
    day_times: Dict[str, List[str]] = None  # {'Monday': ['09:00', '15:00']}
    interval_minutes: int = None  # 30
    interval_start_time: str = None  # '08:00'
    interval_end_time: str = None  # '18:00'
```

### **Novos Métodos:**

- `create_multiple_times_schedule()` - Múltiplos horários
- `create_day_specific_times_schedule()` - Horários por dia
- `create_interval_schedule()` - Execução por intervalo
- `_validate_time_format()` - Validação de horários
- `_calculate_next_*_run()` - Cálculo de próximas execuções

---

## 🎊 Benefícios

### **Para Usuários:**
- 🎯 **Flexibilidade máxima** na configuração
- 📈 **Maior controle** sobre execuções
- 🕒 **Otimização** de recursos e tempo
- 👁️ **Visibilidade** completa dos agendamentos

### **Para o Sistema:**
- ⚡ **Performance** otimizada com cálculos inteligentes
- 🔄 **Compatibilidade** com agendamentos existentes
- 🧠 **Escalabilidade** para cenários complexos
- 🛡️ **Robustez** com validações avançadas

---

## 📚 Exemplos de Configuração

### **1. E-commerce - Processamento de Pedidos**
```
🕐 Múltiplos Horários - Todos os dias
Horários: 07:00, 11:00, 15:00, 19:00, 23:00
Descrição: "Processamento de pedidos a cada 4 horas"
```

### **2. Financeiro - Conciliação Bancária**
```
📋 Horários por Dia
Segunda: 08:00 (Abertura semana)
Terça-Quinta: 14:00 (Meio do dia)
Sexta: 16:00, 18:00 (Fechamento duplo)
```

### **3. Logs - Limpeza Automática**
```
⏱️ Por Intervalo
Intervalo: 4 horas (240 minutos)
Período: 02:00 - 06:00
Dias: Todos
Descrição: "Limpeza de logs durante madrugada"
```

### **4. Marketing - Envio de Campanhas**
```
📆 Semanal + 🕐 Múltiplos Horários
Dias: Terça, Quinta
Horários: 10:00, 14:00, 16:00
Descrição: "Campanhas em horários de pico"
```

---

## 🚀 Próximos Passos

Com essa implementação, o KTR Platform oferece agora um dos sistemas de agendamento mais flexíveis e poderosos, permitindo configurações desde simples execuções diárias até complexos padrões de automação empresarial.

**Recursos adicionais planejados:**
- 📊 Dashboard de performance por agendamento
- 🔔 Notificações personalizadas por tipo
- 📱 Interface mobile para monitoramento
- 🤖 AI para sugestões de otimização de horários

---

*Sistema implementado com foco em usabilidade, performance e escalabilidade.* 