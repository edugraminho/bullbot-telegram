"""
BullBot Telegram - Bot do Telegram para sinais de trading
"""

import asyncio
from src.integrations.telegram_handlers import run_telegram_bot
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def main():
    """Função principal do BullBot Telegram"""
    logger.info("🚀 Iniciando BullBot Telegram...")

    try:
        await run_telegram_bot()
    except KeyboardInterrupt:
        logger.info("Bot interrompido manualmente")
    except Exception as e:
        logger.error(f"❌ Erro no BullBot Telegram: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
