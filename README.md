# BullBot Telegram 🤖

Bot do Telegram para envio de sinais de trading de criptomoedas baseado no indicador RSI.

## 📋 Sobre o Projeto

O BullBot Telegram é um serviço independente que consome sinais do banco de dados do **BullBot Signals** e os envia para assinantes via Telegram.

## 🏗️ Arquitetura

```
┌─── BullBot Signals ────┐    ┌─── BullBot Telegram ───┐
│   • Monitoramento RSI  │    │   • Bot Telegram       │
│   • Cálculo de Sinais  │◄───┤   • Envio de Mensagens │
│   • Banco PostgreSQL   │    │   • Gestão Assinantes  │
└────────────────────────┘    └────────────────────────┘
```

## ✨ Funcionalidades

- **📱 Bot Telegram**: Interface para usuários
- **📊 Sinais Formatados**: Mensagens ricas com emojis e análise
- **👥 Gestão de Assinantes**: Cadastro, ativação, desativação
- **🔄 Envio Paralelo**: Múltiplos assinantes simultaneamente
- **🛡️ Anti-Spam**: Controle de rate limits e retry inteligente
- **📈 Templates Dinâmicos**: Mensagens personalizadas por força do sinal

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

- `/start` - Cadastrar e ativar assinatura
- `/stop` - Desativar assinatura
- `/status` - Ver status da assinatura
- `/help` - Lista de comandos disponíveis

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

## 📊 Monitoramento

O bot consome sinais automaticamente do banco do BullBot Signals e envia para todos os assinantes ativos.

### Estrutura de Sinais

```json
{
  "symbol": "BTC",
  "signal_type": "BUY",
  "rsi_value": 25.0,
  "current_price": 67530.25,
  "strength": "STRONG",
  "timeframe": "15m",
  "message": "Sinal de compra detectado",
  "source": "binance",
  "timestamp": "2025-01-31T11:30:00Z"
}
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. 