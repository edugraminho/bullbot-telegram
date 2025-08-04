# 🔗 Integração BullBot Signals ↔ BullBot Telegram

Este documento explica como os dois projetos se comunicam e como configurar a integração.

## 🏗️ Arquitetura da Integração

```
┌─────────────────┐    ┌─────────────────┐
│  BullBot        │    │  BullBot        │
│  Signals        │    │  Telegram       │
│                 │    │                 │
│  • Monitoramento│    │  • Bot Telegram │
│  • Cálculo RSI  │    │  • Envio de     │
│  • Banco de     │◄───┤    mensagens    │
│    dados        │    │  • Gestão de    │
│  • API REST     │    │    assinantes   │
└─────────────────┘    └─────────────────┘
```

## 📊 Compartilhamento de Dados

### Banco de Dados Compartilhado

O **BullBot Telegram** se conecta ao mesmo banco PostgreSQL do **BullBot Signals** para:

1. **Ler sinais**: Consome sinais da tabela `signal_history`
2. **Gestão de assinantes**: Gerencia assinaturas na tabela `telegram_subscriptions`
3. **Configurações**: Acessa configurações da tabela `monitoring_config`

### Tabelas Utilizadas

```sql
-- Sinais gerados pelo BullBot Signals
signal_history (
  id, symbol, rsi_value, signal_type, strength, 
  price, timeframe, source, telegram_sent, 
  message, created_at
)

-- Assinantes do bot (gerenciado pelo BullBot Telegram)
telegram_subscriptions (
  id, chat_id, chat_type, symbols_filter, 
  active, created_at
)

-- Configurações do sistema (gerenciado pelo BullBot Signals)
monitoring_config (
  id, name, symbols, rsi_oversold, rsi_overbought, 
  timeframes, active, updated_at
)
```

## ⚙️ Configuração da Integração

### 1. Configurar BullBot Signals

No arquivo `.env` do **BullBot Signals**:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/bullbot_signals

# Telegram (opcional - para testes)
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 2. Configurar BullBot Telegram

No arquivo `.env` do **BullBot Telegram**:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Database (mesmo banco do BullBot Signals)
DATABASE_URL=postgresql://user:password@host:5432/bullbot_signals

# Redis
REDIS_URL=redis://redis:6379/0

# Logging
LOG_LEVEL=INFO
```

### 3. Ordem de Inicialização

1. **Primeiro**: Iniciar BullBot Signals
   ```bash
   cd bullbot-signals
   docker-compose up -d
   ```

2. **Depois**: Iniciar BullBot Telegram
   ```bash
   cd bullbot-telegram
   docker-compose up -d
   ```

## 🔄 Fluxo de Dados

### 1. Geração de Sinais (BullBot Signals)

```python
# BullBot Signals gera sinais e salva no banco
signal = SignalHistory(
    symbol="BTC",
    rsi_value=25.0,
    signal_type="BUY",
    strength="STRONG",
    price=67530.25,
    timeframe="15m",
    source="binance",
    telegram_sent=False,  # Flag para controle
    message="Sinal de compra detectado"
)
```

### 2. Consumo de Sinais (BullBot Telegram)

```python
# BullBot Telegram consome sinais não enviados
signals = db.query(SignalHistory).filter(
    SignalHistory.telegram_sent == False
).all()

# Envia para assinantes e marca como enviado
for signal in signals:
    await send_to_subscribers(signal)
    signal.telegram_sent = True
```

## 🚀 Deploy

### Opção 1: Containers Separados

```bash
# Servidor 1: BullBot Signals
cd bullbot-signals
docker-compose up -d

# Servidor 2: BullBot Telegram  
cd bullbot-telegram
docker-compose up -d
```

### Opção 2: Docker Compose Unificado

Criar um `docker-compose.yml` que orquestra ambos:

```yaml
version: '3.8'

services:
  # BullBot Signals
  signals_app:
    build: ./bullbot-signals
    # ... configurações

  signals_worker:
    build: ./bullbot-signals
    # ... configurações

  # BullBot Telegram
  telegram_bot:
    build: ./bullbot-telegram
    # ... configurações

  telegram_worker:
    build: ./bullbot-telegram
    # ... configurações

  # Infraestrutura compartilhada
  db:
    image: postgres:17.1
    # ... configurações

  redis:
    image: redis:8.0
    # ... configurações
```

## 🔧 Monitoramento

### Logs do BullBot Signals

```bash
# Logs de monitoramento
docker-compose logs -f signals_worker

# Logs da API
docker-compose logs -f signals_app
```

### Logs do BullBot Telegram

```bash
# Logs do bot
docker-compose logs -f telegram_bot

# Logs do worker
docker-compose logs -f telegram_worker
```

## 🧪 Testes

### Testar Conexão com Banco

```bash
# No BullBot Telegram
docker-compose exec telegram_bot python -c "
from src.database.connection import SessionLocal
db = SessionLocal()
result = db.execute('SELECT 1').fetchone()
print('✅ Conexão com banco OK:', result)
db.close()
"
```

### Testar Envio de Sinal

```bash
# No BullBot Telegram
docker-compose exec telegram_worker python -c "
from src.tasks.telegram_tasks import send_telegram_signal
signal_data = {
    'symbol': 'TEST',
    'signal_type': 'BUY',
    'rsi_value': 25.0,
    'current_price': 0.001234,
    'strength': 'STRONG',
    'timeframe': '15m',
    'message': '🧪 Teste de integração',
    'source': 'test',
    'timestamp': '2025-01-31T00:00:00Z'
}
task = send_telegram_signal.delay(signal_data)
print('🧪 Task de teste agendada:', task.id)
"
```

## 🔒 Segurança

### Isolamento de Redes

- Cada projeto pode usar redes Docker separadas
- Comunicação apenas via banco de dados
- Redis separado para evitar conflitos

### Controle de Acesso

- BullBot Telegram só tem acesso de leitura às tabelas de sinais
- BullBot Signals não acessa dados do Telegram
- Separação clara de responsabilidades

## 🚨 Troubleshooting

### Problema: BullBot Telegram não encontra sinais

**Solução:**
1. Verificar conexão com banco
2. Confirmar que BullBot Signals está gerando sinais
3. Verificar se `telegram_sent = False` nos sinais

### Problema: Bot não responde

**Solução:**
1. Verificar `TELEGRAM_BOT_TOKEN`
2. Confirmar que o bot está ativo
3. Verificar logs do container `telegram_bot`

### Problema: Sinais duplicados

**Solução:**
1. Verificar se `telegram_sent` está sendo marcado corretamente
2. Confirmar que não há múltiplas instâncias rodando
3. Verificar configuração de workers 