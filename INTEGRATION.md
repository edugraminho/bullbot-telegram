# 🔗 Integração BullBot Signals ↔ BullBot Telegram

Este documento explica como os dois projetos se comunicam e como configurar a integração baseada no **sistema avançado de confluência de indicadores**.

## 🏗️ Arquitetura da Integração

```
┌─────────────────────────────────────────────────┐    ┌─────────────────────────────────┐
│  BullBot Signals                               │    │  BullBot Telegram               │
│                                                 │    │                                 │
│  🧮 Sistema de Confluência                     │    │  🤖 Bot Telegram                │
│  • RSI + EMA + MACD + Volume                   │◄───┤  • Configurações Personalizadas │
│  • Score 0-8 pontos                            │    │  • Filtros Anti-Spam            │
│  • Múltiplas Exchanges                         │    │  • Envio Inteligente            │
│  • Análise 24/7 via Celery                     │    │  • Gestão de Assinantes         │
│  • API REST FastAPI                            │    │  • Processamento Assíncrono     │
│  • Banco PostgreSQL + Redis                    │    │  • Redis + Celery               │
└─────────────────────────────────────────────────┘    └─────────────────────────────────┘
```

## 📊 Sistema de Confluência de Indicadores

### 🎯 O que é Confluência?

**Confluência** é quando múltiplos indicadores técnicos concordam e apontam na mesma direção, aumentando drasticamente a probabilidade de sucesso do sinal.

**Analogia**: Em vez de confiar apenas em uma pessoa te dizendo "pode atravessar a rua", você espera que 4-5 pessoas concordem. **Maior consenso = Maior confiança!**

### 📊 Sistema de Pontuação (0-8 pontos)

| Indicador | Peso | O que Confirma |
|-----------|------|----------------|
| **RSI** | 2 pontos | Zona de sobrecompra/sobrevenda |
| **EMA** | 3 pontos | Tendência + posição do preço |
| **MACD** | 1 ponto | Momentum bullish/bearish |
| **Volume** | 2 pontos | Volume alto + OBV trending |

**Resultado**: Sinais mais confiáveis, menos falsos positivos, melhor timing de entrada.

### ⚙️ Thresholds por Timeframe

- **15 minutos**: Score mínimo **4 pontos** para gerar sinal
- **1 hora**: Score mínimo **4 pontos** para gerar sinal  
- **4 horas**: Score mínimo **5 pontos** para gerar sinal
- **1 dia**: Score mínimo **5 pontos** para gerar sinal

## 📊 Compartilhamento de Dados

### Banco de Dados Compartilhado

O **BullBot Telegram** se conecta ao mesmo banco PostgreSQL do **BullBot Signals** para:

1. **Ler sinais**: Consome sinais da tabela `signal_history` com scores de confluência
2. **Gestão de assinantes**: Gerencia assinaturas na tabela `user_monitoring_configs`
3. **Configurações**: Acessa configurações personalizadas por usuário

### Tabelas Utilizadas

```sql
-- Sinais gerados pelo BullBot Signals (Sistema de Confluência)
signal_history (
  id, symbol, signal_type, strength, price, timeframe, source,
  indicator_type, indicator_data, indicator_config,
  confidence_score, combined_score, processed, processed_at, processed_by,
  volume_24h, price_change_24h, processing_time_ms, created_at
)

-- Configurações e Assinantes (gerenciado pelo BullBot Telegram)
user_monitoring_configs (
  id, user_id, chat_id, chat_type, username, first_name, last_name,
  config_type, priority, config_name, description, active,
  symbols, timeframes, indicators_config, filter_config,
  last_activity, signals_received, last_signal_at, created_at, updated_at
)
```

## 🔄 Fluxo de Dados Avançado

### 1. Geração de Sinais (BullBot Signals)

```python
# BullBot Signals gera sinais com sistema de confluência
signal = SignalHistory(
    symbol="BTC",
    signal_type="SELL",
    strength="WEAK",
    price=0.15895542,
    timeframe="15m",
    source="binance",
    indicator_type=["RSI", "EMA", "MACD", "Volume"],
    indicator_data={
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
                    "trending_up": True,
                    "reason": "EMA favoravel ao sinal",
                    "values": {
                        "ema_9": 0.15404416,
                        "ema_21": 0.1482638,
                        "ema_50": 0.14411452,
                        "price_above_ema_50": True
                    }
                },
                "MACD": {
                    "score": 0,
                    "is_bullish": True,
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
                    "is_high_volume": True,
                    "obv_trending_up": True,
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
    combined_score=4,  # Score total de confluência
    confidence_score=50.0,  # Porcentagem de confiança
    processed=False,  # Flag para controle
    message="Sinal de venda com score 4/8 - Confluência WEAK"
)
```

### 2. Consumo de Sinais (BullBot Telegram)

```python
# BullBot Telegram consome sinais não processados com scores
signals = db.query(SignalHistory).filter(
    SignalHistory.processed == False,
    SignalHistory.combined_score >= 4  # Score mínimo
).all()

# Envia para assinantes baseado em configurações personalizadas
for signal in signals:
    eligible_users = get_eligible_users(signal)
    for user in eligible_users:
        if should_send_signal(user, signal):
            await send_personalized_signal(user, signal)
    
    # Marca como processado
    signal.processed = True
    signal.processed_at = datetime.utcnow()
    signal.processed_by = "telegram_bot"
```

## ⚙️ Configuração da Integração

### 1. Configurar BullBot Signals

No arquivo `.env` do **BullBot Signals**:

```bash
# Database
DATABASE_URL=postgresql://bullbot_user:bullbot_password_2025@db:5432/bullbot_signals

# Logging
LOG_LEVEL=INFO

# Redis (compartilhado)
REDIS_URL=redis://redis:6379/0
```

### 2. Configurar BullBot Telegram

No arquivo `.env` do **BullBot Telegram**:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Database (mesmo banco do BullBot Signals)
DATABASE_URL=postgresql://bullbot_user:bullbot_password_2025@db:5432/bullbot_signals

# Redis (compartilhado)
REDIS_URL=redis://redis:6379/0

# Logging
LOG_LEVEL=INFO
```

### 3. Rede Docker Compartilhada

Ambos os projetos devem usar a mesma rede Docker:

```yaml
# Em ambos os docker-compose.yml
networks:
  bullbot_network:
    external: true
    name: bullbot-shared-network
```

### 4. Ordem de Inicialização

1. **Primeiro**: Criar rede compartilhada
   ```bash
   docker network create bullbot-shared-network
   ```

2. **Segundo**: Iniciar BullBot Signals
   ```bash
   cd bullbot-signals
   docker-compose up -d
   ```

3. **Terceiro**: Iniciar BullBot Telegram
   ```bash
   cd bullbot-telegram
   docker-compose up -d
   ```

## 🎯 Sistema de Elegibilidade Avançado

### **🎯 Filtros por Score de Confluência**
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

### **⚙️ Configuração Personalizada por Usuário**
```json
{
  "indicators_config": {
    "RSI": {
      "enabled": true,
      "period": 14,
      "oversold": 20,
      "overbought": 80
    },
    "EMA": {
      "enabled": true,
      "short_period": 9,
      "medium_period": 21,
      "long_period": 50
    },
    "MACD": {
      "enabled": true,
      "fast_period": 12,
      "slow_period": 26,
      "signal_period": 9
    },
    "Volume": {
      "enabled": true,
      "sma_period": 20,
      "threshold_multiplier": 1.2
    },
    "Confluence": {
      "enabled": true,
      "min_score_15m": 4,
      "min_score_1h": 4,
      "min_score_4h": 5,
      "min_score_1d": 5
    }
  }
}
```

## 🚀 Deploy

### Opção 1: Containers Separados (Recomendado)

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
    ports:
      - "8088:8000"
    depends_on:
      - db
      - redis
    networks:
      - bullbot_network

  signals_worker:
    build: ./bullbot-signals
    command: celery -A src.tasks.celery_app worker --loglevel=info
    depends_on:
      - redis
      - db
    networks:
      - bullbot_network

  signals_beat:
    build: ./bullbot-signals
    command: celery -A src.tasks.celery_app beat --loglevel=warning
    depends_on:
      - redis
      - db
    networks:
      - bullbot_network

  # BullBot Telegram
  telegram_bot:
    build: ./bullbot-telegram
    depends_on:
      - db
      - redis
    networks:
      - bullbot_network

  telegram_worker:
    build: ./bullbot-telegram
    command: celery -A src.tasks.celery_app worker --loglevel=info
    depends_on:
      - redis
      - db
    networks:
      - bullbot_network

  # Infraestrutura compartilhada
  db:
    image: postgres:17.1-alpine
    environment:
      POSTGRES_DB: bullbot_signals
      POSTGRES_USER: bullbot_user
      POSTGRES_PASSWORD: bullbot_password_2025
    ports:
      - "5438:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - bullbot_network

  redis:
    image: redis:8.0-alpine
    ports:
      - "6379:6379"
    networks:
      - bullbot_network

volumes:
  pgdata:

networks:
  bullbot_network:
    driver: bridge
```

## 🔧 Monitoramento

### Logs do BullBot Signals

```bash
# Logs de monitoramento (sistema de confluência)
docker-compose logs -f signals_worker

# Logs da API FastAPI
docker-compose logs -f signals_app

# Logs do scheduler
docker-compose logs -f signals_beat
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

### Testar Sistema de Confluência

```bash
# No BullBot Signals
docker-compose exec signals_app python -c "
from src.core.services.confluence_analyzer import ConfluenceAnalyzer
analyzer = ConfluenceAnalyzer()
print('✅ Sistema de confluência carregado:', analyzer)
"
```

### Testar Envio de Sinal com Score

```bash
# No BullBot Telegram
docker-compose exec telegram_worker python -c "
from src.tasks.telegram_tasks import send_telegram_signal
signal_data = {
    'symbol': 'TEST',
    'signal_type': 'SELL',
    'strength': 'WEAK',
    'price': 0.15895542,
    'timeframe': '15m',
    'source': 'binance',
    'indicator_type': ['RSI', 'EMA', 'MACD', 'Volume'],
    'indicator_data': {
        'confluence_score': {
            'total_score': 4,
            'max_possible_score': 8,
            'details': {
                'RSI': {
                    'score': 2,
                    'value': 82.51,
                    'reason': 'RSI 82.51 em zona de sobrecompra'
                },
                'EMA': {
                    'score': 1,
                    'trending_up': True,
                    'reason': 'EMA favoravel ao sinal'
                },
                'MACD': {
                    'score': 0,
                    'is_bullish': True,
                    'reason': 'MACD nao confirma o sinal'
                },
                'Volume': {
                    'score': 1,
                    'is_high_volume': True,
                    'reason': 'Volume suporta o sinal'
                }
            }
        },
        'rsi_value': 82.51,
        'recommendation': 'Sinal de VENDA FRACO - Score: 4/8',
        'risk_level': 'ALTO'
    },
    'combined_score': 4,
    'confidence_score': 50.0,
    'message': '🧪 Teste de confluência - Score: 4/8',
    'timestamp': '2025-01-31T00:00:00Z'
}
task = send_telegram_signal.delay(signal_data)
print('🧪 Task de teste agendada:', task.id)
"
```

## 🔒 Segurança

### Isolamento de Redes

- Rede Docker compartilhada `bullbot-shared-network`
- Comunicação via banco de dados PostgreSQL
- Redis compartilhado para Celery

### Controle de Acesso

- BullBot Telegram só tem acesso de leitura às tabelas de sinais
- BullBot Signals não acessa dados do Telegram
- Separação clara de responsabilidades

## 🚨 Troubleshooting

### Problema: BullBot Telegram não encontra sinais

**Solução:**
1. Verificar conexão com banco
2. Confirmar que BullBot Signals está gerando sinais com `processed = False`
3. Verificar se `combined_score >= 4` nos sinais
4. Confirmar que rede Docker está compartilhada

### Problema: Bot não responde

**Solução:**
1. Verificar `TELEGRAM_BOT_TOKEN`
2. Confirmar que o bot está ativo
3. Verificar logs do container `telegram_bot`
4. Confirmar que Redis está funcionando

### Problema: Sinais duplicados

**Solução:**
1. Verificar se `processed` está sendo marcado corretamente
2. Confirmar que não há múltiplas instâncias rodando
3. Verificar configuração de workers
4. Confirmar que filtros anti-spam estão funcionando

### Problema: Sistema de confluência não funciona

**Solução:**
1. Verificar se BullBot Signals está calculando scores
2. Confirmar que `indicator_data` está sendo preenchido
3. Verificar se `combined_score` está sendo calculado
4. Confirmar que thresholds estão configurados corretamente 