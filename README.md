# BullBot Telegram 🤖

Sistema completo de bot Telegram para envio personalizado de sinais de trading de criptomoedas baseado no **sistema avançado de confluência de indicadores** do BullBot Signals.

## 📋 Sobre o Projeto

O BullBot Telegram é um serviço independente que consome sinais do banco de dados do **BullBot Signals** e os envia para assinantes via Telegram com **configurações personalizadas por usuário**. O sistema trabalha com o **sistema de confluência avançado** que combina RSI, EMAs, MACD e Volume para gerar sinais de alta precisão.

## 🏗️ Arquitetura

```
┌─── BullBot Signals ────────────────────────────┐    ┌─── BullBot Telegram ─────────────┐
│   🧮 Sistema de Confluência                   │    │   🤖 Bot Telegram                 │
│   • RSI + EMA + MACD + Volume                 │◄───┤   • Configurações Personalizadas  │
│   • Score 0-8 pontos                          │    │   • Filtros Anti-Spam Avançados   │
│   • Múltiplas Exchanges                       │    │   • Envio Inteligente             │
│   • Análise 24/7 via Celery                   │    │   • Gestão de Assinantes          │
│   • API REST FastAPI                          │    │   • Processamento Assíncrono      │
│   • Banco PostgreSQL + Redis                  │    │   • Redis + Celery                │
└───────────────────────────────────────────────┘    └──────────────────────────────────┘
```

## ✨ Funcionalidades

### **🎯 Sistema de Configuração Personalizada**
- **⚙️ Configurações por usuário**: Símbolos, timeframes, indicadores customizáveis
- **🛡️ Filtros anti-spam avançados**: Cooldowns, limites diários, diferença mínima de RSI
- **📊 Múltiplas configurações**: Usuários podem ter várias configurações com prioridades
- **🔧 Defaults inteligentes**: Sistema funciona mesmo sem configuração manual
- **🎚️ Thresholds por timeframe**: Score mínimo personalizado (15m: 4+, 4h: 5+)

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
- **🧮 Filtros por confluência**: Apenas sinais com score mínimo são enviados

### **🔗 Integração Avançada com BullBot Signals**
- **📊 Sistema de confluência**: Consome sinais com scores 0-8 pontos
- **🎯 Múltiplos indicadores**: RSI, EMA, MACD, Volume com pesos configuráveis
- **⚙️ Configuração dinâmica**: Usuários podem habilitar/desabilitar indicadores
- **🔄 Múltiplas exchanges**: Suporte a Binance, Gate.io e MEXC
- **📈 Thresholds inteligentes**: Score mínimo por timeframe configurável

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
DATABASE_URL=postgresql://bullbot_user:bullbot_password_2025@db:5432/bullbot_signals

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
# com base no sistema de confluência do BullBot Signals
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
3. **Filtra por score** de confluência (mínimo 4 pontos para 15m/1h, 5 para 4h+)
4. **Determina usuários elegíveis** baseado em configurações personalizadas
5. **Aplica filtros anti-spam** por usuário
6. **Envia sinais personalizados** via Telegram
7. **Atualiza estatísticas** individuais

### **🎯 Sistema de Elegibilidade Avançado**
```python
# Para cada sinal, o sistema verifica:
✅ Score mínimo por timeframe (15m: 4+, 4h: 5+)
✅ Símbolo está na lista do usuário?
✅ Timeframe está na lista do usuário?
✅ Indicadores habilitados na configuração?
✅ Não está em cooldown?
✅ Não atingiu limite diário?
✅ Score atende threshold personalizado?
```

### **📋 Estrutura de Sinais com Confluência**
```json
{
  "symbol": "BTC",
  "signal_type": "SELL",
  "strength": "WEAK",
  "price": 0.15895542,
  "timeframe": "15m",
  "source": "binance",
  "indicator_type": ["RSI", "EMA", "MACD", "Volume"],
  "indicator_data": {
    "confluence_score": {
      "total_score": 4,
      "max_possible_score": 8,
      "details": {
        "RSI": {
          "score": 2,
          "value": 82.51,
          "reason": "RSI 82.51 em zona de sobrecompra",
          "levels": {
            "oversold": 20,
            "overbought": 80,
            "current_zone": "overbought"
          }
        },
        "EMA": {
          "score": 1,
          "trending_up": true,
          "reason": "EMA favoravel ao sinal",
          "values": {
            "ema_9": 0.15404416,
            "ema_21": 0.1482638,
            "ema_50": 0.14411452,
            "price_above_ema_50": true
          }
        },
        "MACD": {
          "score": 0,
          "is_bullish": true,
          "reason": "MACD nao confirma o sinal",
          "values": {
            "macd_line": 0.00497119,
            "signal_line": 0.00282583,
            "histogram": 0.00214536,
            "crossover": "bullish"
          }
        },
        "Volume": {
          "score": 1,
          "is_high_volume": true,
          "obv_trending_up": true,
          "reason": "Volume suporta o sinal",
          "values": {
            "volume_ratio": 1.721,
            "obv": 20192145.0,
            "vwap": 0.15895542,
            "price_vs_vwap": "above",
            "volume_threshold": "172%"
          }
        }
      }
    },
    "rsi_value": 82.51,
    "recommendation": "Sinal de VENDA FRACO - Score: 4/8",
    "risk_level": "ALTO"
  },
  "combined_score": 4,
  "confidence_score": 50.0,
  "message": "Sinal de venda com score 4/8 - Confluência WEAK",
  "timestamp": "2025-01-31T11:30:00Z"
}
```

### **🛡️ Filtros Anti-Spam Avançados (por usuário)**
- **Cooldown por timeframe**: 15m (15min), 1h (60min), 4h (120min)
- **Limite diário**: Máximo 3 sinais por símbolo por dia
- **Diferença mínima de RSI**: 2.0 pontos entre sinais consecutivos
- **Configuração por força**: STRONG, MODERATE, WEAK têm cooldowns diferentes
- **Score mínimo configurável**: Usuários podem definir threshold personalizado

## 🗄️ Estrutura do Banco de Dados

### **📋 Tabelas Compartilhadas com BullBot Signals**

#### **signal_history** (Sinais com Sistema de Confluência)
```sql
CREATE TABLE signal_history (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(20) NOT NULL,  -- BUY, SELL, HOLD
    strength VARCHAR(20) NOT NULL,     -- WEAK, MODERATE, STRONG
    price FLOAT NOT NULL,
    timeframe VARCHAR(10) NOT NULL,    -- 15m, 1h, 4h, etc
    source VARCHAR(20) NOT NULL,       -- binance, gate, mexc
    message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Sistema de Confluência
    indicator_type JSON NOT NULL,      -- ["RSI", "EMA", "MACD", "Volume"]
    indicator_data JSON NOT NULL,      -- Dados detalhados de cada indicador
    indicator_config JSON,             -- Configurações dos indicadores
    
    -- Scores de Qualidade
    confidence_score FLOAT,            -- Score de confiança (0-100)
    combined_score FLOAT,              -- Score total de confluência (0-8)
    
    -- Controle de Processamento
    processed BOOLEAN DEFAULT FALSE,   -- Se foi processado pelo Telegram
    processed_at TIMESTAMPTZ,          -- Quando foi processado
    processed_by VARCHAR(50),          -- Qual serviço processou
    
    -- Contexto Adicional
    volume_24h FLOAT,                 -- Volume 24h no momento do sinal
    price_change_24h FLOAT,           -- Variação % 24h
    processing_time_ms INTEGER         -- Tempo de processamento
);
```

#### **user_monitoring_configs** (Configurações e Assinantes Unificados)
```sql
CREATE TABLE user_monitoring_configs (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
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
- **As tabelas são criadas e gerenciadas pelo BullBot Signals**
- **Use o sistema de migrations do BullBot Signals para atualizar a estrutura**
- **Ambos os projetos compartilham o mesmo banco com estrutura avançada**
- **O sistema de confluência é totalmente gerenciado pelo BullBot Signals**

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
1. **Criar rede Docker compartilhada**
   ```bash
   docker network create bullbot-shared-network
   ```

2. **BullBot Signals** (com tabelas de confluência)
   ```bash
   cd bullbot-signals
   docker-compose up -d
   ```

3. **BullBot Telegram** 
   ```bash
   cd bullbot-telegram
   docker-compose up -d
   ```

### **Verificações Importantes**
- ✅ Rede Docker `bullbot-shared-network` criada
- ✅ Tabelas criadas no banco do BullBot Signals
- ✅ Mesma `DATABASE_URL` em ambos os projetos
- ✅ `TELEGRAM_BOT_TOKEN` configurado
- ✅ Redis funcionando e compartilhado
- ✅ Sistema de confluência gerando sinais com scores

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. 