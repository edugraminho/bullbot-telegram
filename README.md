# BullBot Telegram 🤖

Sistema completo de bot Telegram para envio personalizado de sinais de trading de criptomoedas baseado no indicador RSI.

## 📋 Sobre o Projeto

O BullBot Telegram é um serviço independente que consome sinais do banco de dados do **BullBot Signals** e os envia para assinantes via Telegram com **configurações personalizadas por usuário**.

## 🏗️ Arquitetura

```
┌─── BullBot Signals ────┐    ┌─── BullBot Telegram ───┐
│   • Monitoramento RSI  │    │   • Bot Telegram       │
│   • Cálculo de Sinais  │◄───┤   • Configurações      │
│   • Banco PostgreSQL   │    │     Personalizadas     │
│   • Múltiplos          │    │   • Filtros Anti-Spam  │
│     Indicadores        │    │   • Envio Inteligente  │
└────────────────────────┘    └────────────────────────┘
```

## ✨ Funcionalidades

### **🎯 Sistema de Configuração Personalizada**
- **⚙️ Configurações por usuário**: Símbolos, timeframes, RSI customizáveis
- **🛡️ Filtros anti-spam**: Cooldowns, limites diários, diferença mínima de RSI
- **📊 Múltiplas configurações**: Usuários podem ter várias configurações com prioridades
- **🔧 Defaults inteligentes**: Sistema funciona mesmo sem configuração manual

### **📱 Bot Telegram Completo**
- **🚀 Cadastro automático**: `/start` cria usuário e configuração padrão
- **⚙️ Comandos obrigatórios**: `/symbols`, `/timeframes` para configuração básica
- **🔧 Comandos opcionais**: `/rsi`, `/settings` para personalização avançada
- **💡 Interface intuitiva**: Instruções detalhadas e validações em tempo real

### **🎨 Sistema de Envio Inteligente**
- **🎯 Envio personalizado**: Cada usuário recebe apenas sinais relevantes
- **⚡ Processamento assíncrono**: Celery + Redis para alta performance
- **📊 Estatísticas individuais**: Contador de sinais recebidos por usuário
- **🔄 Sistema robusto**: Retry automático e tratamento de erros

## 🛠️ Tecnologias

- **Python 3.11+**
- **python-telegram-bot**: Cliente Telegram
- **Celery**: Processamento assíncrono
- **Redis**: Broker e cache
- **PostgreSQL**: Conexão com banco do BullBot Signals
- **Docker**: Containerização

## 🚀 Instalação

1. **Clone o repositório**
```bash
git clone <repository-url>
cd bullbot-telegram
```

2. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. **Execute com Docker**
```bash
docker-compose up -d
```

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Database (BullBot Signals)
DATABASE_URL=postgresql://user:password@host:port/database

# Redis
REDIS_URL=redis://redis:6379/0

# Logging
LOG_LEVEL=INFO
```

## 📱 Comandos do Bot

### **🚀 Comandos Principais**
- `/start` - Cadastrar usuário e criar configuração padrão
- `/help` - Lista completa de comandos com exemplos
- `/status` - Ver status do sistema e do usuário

### **⚙️ Configuração (OBRIGATÓRIOS)**
- `/symbols BTC,ETH,SOL` - Definir símbolos para monitorar
- `/timeframes 15m,1h,4h` - Definir timeframes de análise

### **🔧 Configuração (OPCIONAIS)**
- `/rsi 20,80` - Configurar níveis de RSI (padrão: 20-80)
- `/settings` - Ver configuração atual completa

## 🎯 Como Usar

### **Cadastro Rápido (3 passos)**
```bash
1. /start                    # Cadastro automático
2. /symbols BTC,ETH,SOL      # Configurar símbolos
3. /timeframes 15m,1h        # Configurar timeframes
```

### **Configuração Avançada**
```bash
/rsi 25,75                   # RSI personalizado
/settings                    # Verificar configuração
```

### **Exemplo de Uso Completo**
```
Usuário: /start
Bot: 🎉 Bem-vindo! Configuração padrão criada.

Usuário: /symbols BTC,ETH,SOL,ADA,AVAX
Bot: ✅ 5 símbolos configurados!

Usuário: /timeframes 15m,1h,4h
Bot: ✅ Configuração básica completa!

Usuário: /rsi 20,80
Bot: ✅ RSI personalizado configurado!

# Agora o usuário receberá sinais automaticamente
```

## 🔧 Desenvolvimento

### Executar em Desenvolvimento

```bash
# Subir infraestrutura
docker-compose up -d redis

# Executar bot
docker-compose exec app python -m src.main
```

### Logs

```bash
# Logs do bot
docker-compose logs -f telegram_bot

# Logs do worker
docker-compose logs -f celery_worker
```

## 📊 Sistema de Processamento

### **🔄 Fluxo Automatizado**
1. **Celery Beat** executa a cada 15 segundos
2. **Busca sinais** não processados no banco do BullBot Signals
3. **Determina usuários elegíveis** baseado em configurações personalizadas
4. **Aplica filtros anti-spam** por usuário
5. **Envia sinais personalizados** via Telegram
6. **Atualiza estatísticas** individuais

### **🎯 Sistema de Elegibilidade**
```python
# Para cada sinal, o sistema verifica:
✅ Símbolo está na lista do usuário?
✅ Timeframe está na lista do usuário?
✅ RSI atende os critérios personalizados?
✅ Não está em cooldown?
✅ Não atingiu limite diário?
✅ RSI tem diferença mínima do último sinal?
```

### **📋 Estrutura de Sinais**
```json
{
  "symbol": "BTC",
  "signal_type": "BUY",
  "strength": "STRONG",
  "price": 67530.25,
  "timeframe": "15m",
  "source": "binance",
  "indicator_data": {
    "RSI": {
      "value": 25.0,
      "period": 14
    }
  },
  "message": "Sinal de compra detectado",
  "timestamp": "2025-01-31T11:30:00Z"
}
```

### **🛡️ Filtros Anti-Spam (por usuário)**
- **Cooldown por timeframe**: 15m (15min), 1h (60min), 4h (120min)
- **Limite diário**: Máximo 3 sinais por símbolo por dia
- **Diferença mínima de RSI**: 2.0 pontos entre sinais consecutivos
- **Configuração por força**: STRONG, MODERATE, WEAK têm cooldowns diferentes

## 🗄️ Estrutura do Banco de Dados

### **📋 Tabela Única (deve ser criada no BullBot Signals)**

#### **user_monitoring_configs** (Configurações e Assinantes Unificados)
```sql
CREATE TABLE user_monitoring_configs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    chat_id VARCHAR(50) UNIQUE NOT NULL,
    chat_type VARCHAR(20) DEFAULT 'private',
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    user_username VARCHAR(100),
    config_type VARCHAR(20) DEFAULT 'personal',
    priority INTEGER DEFAULT 1,
    config_name VARCHAR(50) NOT NULL,
    description TEXT,
    active BOOLEAN DEFAULT TRUE,
    symbols TEXT[] NOT NULL,
    timeframes TEXT[] DEFAULT ARRAY['15m','1h','4h'],
    indicators_config JSONB NOT NULL,
    filter_config JSONB,
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    signals_received INTEGER DEFAULT 0,
    last_signal_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, config_name)
);
```

### **⚠️ Importante**
- **Adicione essa tabela expandida no projeto BullBot Signals**
- **Use o sistema de migrations do BullBot Signals para atualizar a estrutura**
- **Ambos os projetos compartilham o mesmo banco com estrutura simplificada**
- **A tabela `telegram_subscriptions` não é mais necessária - tudo está unificado**

## 🔧 Tasks Celery

### **Tarefas Automáticas**
- `process_unprocessed_signals` - A cada 15 segundos
- `test_connections` - A cada 5 minutos  
- `get_system_status` - A cada 15 minutos
- `get_subscription_stats` - A cada 30 minutos
- `cleanup_old_data` - A cada hora

### **Comandos Manuais**
```bash
# Testar conexões
celery -A src.tasks.celery_app call src.tasks.telegram_tasks.test_connections

# Ver estatísticas
celery -A src.tasks.celery_app call src.tasks.telegram_tasks.get_subscription_stats

# Processar sinais manualmente
celery -A src.tasks.celery_app call src.tasks.telegram_tasks.process_unprocessed_signals
```

## 🚀 Deploy em Produção

### **Ordem de Inicialização**
1. **BullBot Signals** (com tabelas novas)
2. **BullBot Telegram** 

### **Verificações Importantes**
- ✅ Tabelas criadas no banco do BullBot Signals
- ✅ Mesma `DATABASE_URL` em ambos os projetos
- ✅ `TELEGRAM_BOT_TOKEN` configurado
- ✅ Redis funcionando
- ✅ Rede Docker compartilhada

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. 