# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Docker & Compose
```bash
# Full stack startup
docker-compose up -d

# Development - infrastructure only  
docker-compose up -d redis

# View logs
docker-compose logs -f telegram_bot
docker-compose logs -f celery_worker
docker-compose logs -f celery_beat

# Execute bot manually
docker-compose exec app python -m src.main
```

### Python Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run bot directly (ensure Redis is running)
python -m src.main

# Run specific Telegram handlers
python -c "import asyncio; from src.integrations.telegram_handlers import run_telegram_bot; asyncio.run(run_telegram_bot())"
```

### Celery Commands
```bash
# Start worker
celery -A src.tasks.celery_app worker --loglevel=info --queues=telegram --concurrency=1

# Start beat scheduler
celery -A src.tasks.celery_app beat --loglevel=info

# Manual task execution
celery -A src.tasks.celery_app call src.tasks.telegram_tasks.process_unprocessed_signals
celery -A src.tasks.celery_app call src.tasks.telegram_tasks.test_connections
celery -A src.tasks.celery_app call src.tasks.telegram_tasks.get_subscription_stats
```

### Code Quality
```bash
# Lint with Ruff
ruff check src/
ruff format src/

# Run tests (if pytest is configured)
pytest tests/
```

## Architecture Overview

### High-Level Design
BullBot Telegram is a **signal dispatch service** that:
1. **Reads trading signals** from a shared PostgreSQL database (populated by BullBot Signals)
2. **Applies user-specific filtering** based on personalized configurations
3. **Sends targeted notifications** via Telegram bot to subscribed users
4. **Prevents spam** through intelligent cooldowns and daily limits

### Core Components

#### 1. Signal Processing Pipeline (`src/services/`)
- **signal_reader.py**: Direct database queries to fetch unprocessed signals
- **signal_dispatch_service.py**: Applies user filters and manages dispatch logic
- **user_config_service.py**: Manages user configurations and subscriptions

#### 2. Telegram Integration (`src/integrations/`)
- **telegram_bot.py**: Core bot client for sending messages
- **telegram_handlers.py**: Command handlers (`/start`, `/symbols`, `/timeframes`, `/rsi`, etc.)
- **telegram_messages.py**: Message templates and formatting

#### 3. Asynchronous Processing (`src/tasks/`)
- **celery_app.py**: Celery configuration with Redis broker
- **beat_schedule.py**: Automated scheduling (processes signals every minute)
- **telegram_tasks.py**: Background tasks for signal processing
- **monitor_tasks.py**: System monitoring and health checks

#### 4. Database Layer (`src/database/`)
- **connection.py**: PostgreSQL connection management via SQLAlchemy
- **models.py**: Database models (signals, user configs, subscriptions)

### Key Data Flow
1. **BullBot Signals** writes signals to `signal_history` table
2. **Celery Beat** triggers `process_unprocessed_signals` every minute
3. **SignalReader** fetches unprocessed signals via direct SQL queries
4. **UserConfigService** determines eligible users based on symbols/timeframes/RSI criteria
5. **TelegramBot** sends personalized messages with anti-spam filtering
6. **SignalHistory** records are marked as `processed=true`

### Database Schema
The service connects to an **external database** shared with BullBot Signals:

**Key Tables:**
- `signal_history`: Trading signals with RSI data, processed status
- `user_monitoring_configs`: User configurations (symbols, timeframes, RSI thresholds)

**Important:** This service does NOT manage its own database - it connects to BullBot Signals' PostgreSQL instance.

## Configuration Management

### Environment Variables (.env)
```bash
# Required - Telegram
TELEGRAM_BOT_TOKEN=bot_token_from_botfather

# Required - Database (shared with BullBot Signals)
DATABASE_URL=postgresql://user:password@host:port/database

# Required - Redis 
REDIS_URL=redis://redis:6379/0

# Optional - Logging
LOG_LEVEL=INFO
```

### User Configuration System
Users configure the bot through Telegram commands:
- **Mandatory**: `/symbols BTC,ETH,SOL` and `/timeframes 15m,1h,4h`
- **Optional**: `/rsi 20,80` (default: 20-80 RSI thresholds)

Each user can have multiple configurations with priority levels.

## Anti-Spam and Filtering

### Intelligent Filtering Rules
- **Symbol matching**: User-defined symbol whitelist
- **Timeframe filtering**: User-specified timeframes (15m, 1h, 4h, etc.)
- **RSI thresholds**: Customizable oversold/overbought levels
- **Cooldown periods**: Prevents duplicate signals per timeframe
- **Daily limits**: Maximum 3 signals per symbol per day
- **RSI difference**: Minimum 2-point difference between consecutive signals

### Performance Optimizations
- Direct SQL queries instead of ORM for signal processing
- Celery task queues with memory limits
- Redis caching for user configurations
- Resource-constrained Docker containers (optimized for t2.micro)

## Development Patterns

### Adding New Telegram Commands
1. Add handler method in `TelegramBot` class (`src/integrations/telegram_handlers.py`)
2. Register handler in `setup_handlers()` method
3. Add message templates in `src/integrations/telegram_messages.py`
4. Update help text in `HELP_MESSAGE`

### Adding New Celery Tasks
1. Create task function in `src/tasks/telegram_tasks.py` or `src/tasks/monitor_tasks.py`
2. Add `@celery_app.task` decorator
3. Register in `src/tasks/beat_schedule.py` for scheduled execution
4. Test via manual celery call command

### Database Migrations
Since this service shares the database with BullBot Signals:
1. Database schema changes must be coordinated with BullBot Signals
2. Use BullBot Signals' migration system (Alembic)
3. Test schema changes in both applications

## Testing & Debugging

### Manual Signal Processing
```bash
# Test database connection
docker-compose exec app python -c "from src.services.signal_reader import signal_reader; print(signal_reader.test_connection())"

# Check unprocessed signals count
docker-compose exec app python -c "from src.services.signal_reader import signal_reader; print(signal_reader.get_unprocessed_signals_count())"

# Process signals manually
celery -A src.tasks.celery_app call src.tasks.telegram_tasks.process_unprocessed_signals
```

### Bot Command Testing
Send commands directly to the Telegram bot:
- `/start` - Register user and create default config
- `/symbols BTC,ETH` - Test symbol configuration  
- `/timeframes 15m,1h` - Test timeframe setup
- `/settings` - View current configuration
- `/status` - Check system status

### Common Issues
- **Bot not responding**: Check `TELEGRAM_BOT_TOKEN` and network connectivity
- **No signals processing**: Verify database connection and unprocessed signals count
- **Memory issues**: Monitor Docker container memory limits in `docker-compose.yml`
- **Celery tasks not running**: Ensure Redis is accessible and beat scheduler is running

## Deployment Notes

### Service Dependencies
1. **BullBot Signals** must be running and populating signals
2. **Redis** for Celery broker and caching
3. **PostgreSQL** shared database access
4. **External Docker network** `bullbot-signals_bullbot_network`

### Resource Requirements
Optimized for AWS t2.micro instances:
- telegram_bot: 128M memory limit
- celery_worker: 80M memory limit  
- celery_beat: 64M memory limit
- redis: 48M memory limit

### Health Monitoring
The system includes automated monitoring tasks:
- Connection tests every 5 minutes
- System status every 15 minutes  
- Subscription stats every 30 minutes
- Data cleanup every hour