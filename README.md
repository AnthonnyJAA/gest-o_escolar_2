# 🎓 Sistema de Gestão Escolar v2.0 - Com Transferências

Sistema completo para gestão escolar com **dashboard interativo**, **gráficos em tempo real** e **sistema de transferências de alunos**.

## 🚀 Novidades da v2.0

### ✨ **Funcionalidades Implementadas:**
- 📊 **Dashboard Interativo** com 6 gráficos em tempo real
- 🔄 **Sistema de Transferência de Alunos** completo
- 📈 **Gráficos Matplotlib** integrados ao Tkinter
- 📚 **Histórico de Transferências** com relatórios
- ⚡ **Validações Automáticas** de transferências
- 🎯 **Transferências em Lote** para eficiência
- 📊 **Estatísticas Avançadas** de movimentação de alunos

## 🔄 **Sistema de Transferências - Principais Recursos:**

### **1. 📋 Interface Intuitiva**
- **Seleção de Turmas:** Origem e destino com informações detalhadas
- **Lista de Alunos:** Checkboxes para seleção individual ou em lote
- **Validação Visual:** Verificação antes da transferência
- **Status em Tempo Real:** Feedback imediato das operações

### **2. 🎯 Tipos de Transferência**
- **Individual:** Transferir um aluno específico
- **Em Lote:** Transferir múltiplos alunos simultaneamente  
- **Promoção de Série:** Para próximo ano letivo
- **Mudança de Turno:** Matutino ↔ Vespertino
- **Remanejamento:** Entre turmas da mesma série

### **3. 📊 Estatísticas Completas**
- Total de transferências (geral, mensal, anual)
- Turmas que mais recebem/perdem alunos
- Relatórios por período personalizado
- Histórico detalhado de cada aluno

### **4. 🛡️ Validações e Segurança**
- Verificação de aluno ativo
- Validação de turma de destino
- Prevenção de transferências duplicadas
- Confirmação antes de executar
- Histórico completo (auditoria)

### **5. 📈 Motivos Pré-definidos**
- Promoção para próxima série
- Mudança de turno
- Remanejamento de turma
- Solicitação dos pais
- Adequação pedagógica
- Transferência administrativa
- Outros (personalizado)

## 📦 **Instalação e Configuração**

### **Pré-requisitos:**
```bash
Python 3.6+
Tkinter (geralmente incluído)
```

### **Dependências:**
```bash
# Instalar dependências para gráficos
pip install matplotlib numpy

# OU usar o arquivo requirements.txt
pip install -r requirements.txt
```

### **Executar o Sistema:**
```bash
# Executar diretamente
python main.py

# O sistema irá:
# 1. Verificar dependências automaticamente
# 2. Criar banco de dados se não existir  
# 3. Gerar dados de exemplo para demonstração
# 4. Abrir interface gráfica completa
```

## 🎯 **Como Usar o Sistema de Transferências**

### **Passo 1: Acessar Transferências**
1. Abrir o sistema
2. Clicar no botão **"🔄 Transferências"** na barra superior
3. Aguardar carregamento das estatísticas

### **Passo 2: Selecionar Turma de Origem**
1. No painel **"🎯 Seleção de Turmas"**
2. Escolher turma no dropdown **"Turma de Origem"**
3. Clicar em **"📋 Carregar Alunos da Turma"**

### **Passo 3: Selecionar Alunos**
1. Na lista de alunos carregada
2. Marcar checkboxes dos alunos desejados
3. Usar **"☑️ Selecionar Todos"** ou **"☐ Limpar Seleção"**

### **Passo 4: Configurar Transferência**
1. No painel **"➡️ Executar Transferência"**
2. Escolher **"🎯 Turma de Destino"**
3. Selecionar **"📝 Motivo"** da transferência
4. Adicionar **"💭 Observações"** se necessário

### **Passo 5: Validar e Executar**
1. Clicar em **"🔍 Validar Transferência"** (recomendado)
2. Verificar se não há problemas
3. Clicar em **"🚀 Transferir Selecionados"**
4. Confirmar a operação no diálogo

### **Passo 6: Verificar Resultado**
1. Ver status da operação
2. Verificar histórico atualizado
3. Conferir estatísticas atualizadas

## 📊 **Exemplos de Uso Prático**

### **Cenário 1: Promoção de Série (Fim do Ano)**
```
Situação: Promover todos os alunos do 2º Ano A para o 3º Ano A

1. Turma Origem: "2º Ano A - 2º Ano (2025) - 25 alunos"
2. Carregar alunos da turma
3. Selecionar todos (☑️)
4. Turma Destino: "3º Ano A - 3º Ano (2026) - 0 alunos"  
5. Motivo: "Promoção para próxima série"
6. Observações: "Promoção automática - ano letivo 2025→2026"
7. Validar → Transferir → Confirmar
```

### **Cenário 2: Mudança de Turno**
```
Situação: Aluno quer mudar do turno matutino para vespertino

1. Turma Origem: "1º Ano A - Matutino (2025)"
2. Carregar e selecionar o aluno específico
3. Turma Destino: "1º Ano B - Vespertino (2025)"
4. Motivo: "Mudança de turno" 
5. Observações: "Solicitação dos pais - horário de trabalho"
6. Validar → Transferir → Confirmar
```

### **Cenário 3: Remanejamento por Capacidade**
```
Situação: Turma muito cheia, redistribuir alguns alunos

1. Turma Origem: "1º Ano A (35 alunos)" - acima da capacidade
2. Selecionar 10 alunos específicos
3. Turma Destino: "1º Ano C (15 alunos)" - com vagas
4. Motivo: "Remanejamento de turma"
5. Observações: "Balanceamento de capacidade das turmas"
6. Transferir em lote
```

## 📈 **Dashboard de Gráficos Interativos**

### **Gráficos Disponíveis:**
1. **📊 Status das Mensalidades** (Pizza)
2. **💰 Receita Mensal** (Barras) - 6 meses
3. **👥 Alunos por Turma** (Barras) - Top 8
4. **📈 Evolução da Inadimplência** (Linha)
5. **🔴 Top 5 Turmas Inadimplentes** (Barras Horizontais)
6. **💼 Resumo Financeiro** (Cards informativos)

### **Funcionalidades dos Gráficos:**
- ✅ **Atualização em Tempo Real**
- ✅ **Dados dos Últimos 6 Meses**
- ✅ **Cores Intuitivas e Profissionais**
- ✅ **Tooltips e Valores Detalhados**
- ✅ **Layout Responsivo com Scroll**

## 📚 **Estrutura do Projeto Atualizada**

```
📁 sistema-gestao-escolar/
├── 📄 main.py                     # Inicializador principal (ATUALIZADO)
├── 📄 requirements.txt            # Dependências (NOVO)
├── 📄 create_sample_data.py       # Gerador de dados exemplo (NOVO)
├── 📄 README.md                   # Este arquivo
│
├── 📁 database/
│   ├── 📄 connection.py           # Conexão com banco
│   └── 📄 init_db.py             # Inicialização do banco
│
├── 📁 services/
│   ├── 📄 dashboard_service.py    # Serviços do dashboard (EXPANDIDO)
│   ├── 📄 transferencia_service.py # Serviços de transferência (NOVO)
│   ├── 📄 aluno_service.py        # Serviços de alunos
│   ├── 📄 turma_service.py        # Serviços de turmas
│   └── 📄 financeiro_service.py   # Serviços financeiros
│
├── 📁 interface/
│   ├── 📄 main_window.py          # Janela principal (ATUALIZADO)
│   ├── 📄 dashboard.py            # Dashboard interativo (RENOVADO)
│   ├── 📄 transferencia.py        # Interface de transferências (NOVO)
│   ├── 📄 alunos.py              # Interface de alunos
│   ├── 📄 turmas.py              # Interface de turmas
│   └── 📄 financeiro.py          # Interface financeiro
│
└── 📁 utils/
    ├── 📄 formatters.py          # Formatadores de dados
    └── 📄 validators.py          # Validadores
```

## 🎯 **Recursos de Auditoria e Relatórios**

### **Histórico Completo:**
- 📅 Data e hora de cada transferência
- 👤 Aluno transferido
- 📤 Turma de origem  
- 📥 Turma de destino
- 📝 Motivo e observações
- 🔍 Rastreabilidade total

### **Relatórios Disponíveis:**
- **📊 Relatório CSV:** Exportação para planilha
- **📈 Estatísticas Visuais:** Gráficos e métricas
- **🔍 Filtros por Período:** Data início/fim personalizável
- **📋 Histórico por Aluno:** Todas as transferências do estudante

## 🛠️ **Tecnologias Utilizadas**

- **🐍 Python 3.6+:** Linguagem principal
- **🖼️ Tkinter:** Interface gráfica nativa
- **📊 Matplotlib:** Gráficos interativos e profissionais
- **🔢 NumPy:** Processamento matemático eficiente  
- **🗄️ SQLite3:** Banco de dados leve e confiável
- **📋 CSV:** Exportação de relatórios
- **🎨 Design Responsivo:** Layout adaptável

## ✅ **Validações Implementadas**

### **Transferências:**
- ✅ Aluno deve estar ativo
- ✅ Turma de destino deve existir e ser diferente da origem
- ✅ Verificação de dados íntegros
- ✅ Confirmação obrigatória para operações críticas
- ✅ Histórico preservado para auditoria

### **Interface:**
- ✅ Botões habilitados apenas quando aplicável
- ✅ Feedback visual em todas as operações
- ✅ Mensagens de erro claras e úteis
- ✅ Contadores dinâmicos de seleção
- ✅ Status em tempo real

## 🔮 **Possíveis Expansões Futuras**

- 📱 **Interface Mobile:** Versão para dispositivos móveis
- ☁️ **Cloud Integration:** Sincronização em nuvem
- 👨‍👩‍👧‍👦 **Portal dos Pais:** Acesso para responsáveis
- 📧 **Notificações Email:** Alertas automáticos
- 🔐 **Sistema de Permissões:** Controle de acesso por usuário
- 📊 **Relatórios Avançados:** BI e analytics
- 🎓 **Módulo Pedagógico:** Notas e frequência
- 📚 **Biblioteca:** Controle de empréstimos

## 🆘 **Solução de Problemas**

### **Erro: Dependências não encontradas**
```bash
# Instalar matplotlib e numpy
pip install matplotlib numpy

# Se ainda houver erro, tentar:
pip install --upgrade matplotlib numpy
```

### **Erro: Banco de dados não inicializado**
```bash
# Deletar arquivo existente (se corrompido)
rm escolar.db

# Executar novamente
python main.py
```

### **Performance lenta nos gráficos**
```bash
# Verificar se matplotlib está usando backend correto
# O sistema força TkAgg automaticamente, mas se ainda lento:

# Opção 1: Reduzir quantidade de dados de exemplo
# Editar create_sample_data.py, linha ~50: range(20) → range(10)

# Opção 2: Usar backend mais rápido (avançado)
# Editar dashboard.py, linha 7: matplotlib.use('TkAgg') → matplotlib.use('Agg')
```

## 📞 **Suporte e Contribuição**

Este sistema foi desenvolvido como demonstração completa de gestão escolar com funcionalidades avançadas.

### **Recursos Implementados:**
- ✅ **Sistema Completo:** CRUD de alunos, turmas, pagamentos
- ✅ **Dashboard Interativo:** 6 gráficos em tempo real
- ✅ **Transferências:** Individual e em lote com histórico
- ✅ **Relatórios:** CSV e estatísticas detalhadas
- ✅ **Validações:** Segurança e integridade dos dados
- ✅ **Interface Profissional:** Design moderno e intuitivo

### **Qualidade do Código:**
- 📝 **Documentação Completa:** Comentários e docstrings
- 🧪 **Tratamento de Erros:** Try/catch em todas as operações  
- 🔧 **Arquitetura MVC:** Separação clara de responsabilidades
- ⚡ **Performance:** Consultas SQL otimizadas
- 🛡️ **Segurança:** Validações e sanitização de dados

---

## 🎉 **Conclusão**

O **Sistema de Gestão Escolar v2.0** agora está completo com:

- 📊 **Dashboard profissional** com gráficos interativos
- 🔄 **Sistema de transferências** robusto e flexível  
- 📈 **Relatórios avançados** e estatísticas detalhadas
- 🎯 **Interface intuitiva** para usuários não-técnicos
- 🛠️ **Código profissional** pronto para produção

**🚀 Pronto para impressionar e atender qualquer necessidade de gestão escolar!**