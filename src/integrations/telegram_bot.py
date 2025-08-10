"""
Cliente Telegram para envio de sinais - BullBot Telegram
Simplificado para envio direto para grupo fixo
"""

from typing import Dict, Any
from telegram import Bot
from telegram.error import TelegramError
from telegram.request import HTTPXRequest
from src.utils.logger import get_logger
from src.utils.price_formatter import format_crypto_price
from src.utils.config import settings

logger = get_logger(__name__)


class TelegramClient:
    """Cliente para envio de mensagens via Telegram - Simplificado para grupo fixo"""

    def __init__(self, bot_token: str):
        # Configurar request personalizado com pool de conexões otimizado
        self.request = HTTPXRequest(
            connection_pool_size=settings.telegram_connection_pool_size,
            read_timeout=30.0,  # Timeout de leitura
            write_timeout=30.0,  # Timeout de escrita
            connect_timeout=10.0,  # Timeout de conexão
            pool_timeout=settings.telegram_pool_timeout,  # Configurável
        )

        self.bot = Bot(token=bot_token, request=self.request)
        self.bot_token = bot_token

        # Chat ID do grupo fixo (configurável via env)
        self.group_chat_id = settings.telegram_group_chat_id

        logger.info(
            f"Cliente Telegram configurado com pool de {settings.telegram_connection_pool_size} conexões"
        )
        logger.info(f"Grupo de destino: {self.group_chat_id}")

    async def send_signal(self, signal_data: Dict[str, Any]) -> bool:
        """
        Envia sinal para o grupo fixo do Telegram
        """
        try:
            message = self._format_signal_message(signal_data)

            await self.bot.send_message(
                chat_id=self.group_chat_id,
                text=message,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )

            logger.info(f"Sinal enviado para grupo {self.group_chat_id}")
            return True

        except TelegramError as e:
            logger.error(f"❌ Erro ao enviar para grupo {self.group_chat_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro inesperado ao enviar sinal: {e}")
            return False

    def _format_signal_message(self, signal_data: Dict[str, Any]) -> str:
        """Formatar mensagem do sinal"""
        symbol = signal_data.get("symbol", "UNKNOWN")
        signal_type = signal_data.get("signal_type", "UNKNOWN")
        rsi_value = signal_data.get("indicator_data", {}).get("RSI", {}).get("value", 0)
        current_price = signal_data.get("price", 0)
        strength = signal_data.get("strength", "UNKNOWN")
        timeframe = signal_data.get("timeframe", "UNKNOWN")
        message = signal_data.get("message", "")
        source = signal_data.get("source", "UNKNOWN")

        # Emojis por tipo de sinal
        emoji_map = {
            "BUY": "🚀🟢",
            "SELL": "📉🔴",
            "HOLD": "⏸️🟡",
        }

        # Emoji de força
        strength_emoji = {
            "STRONG": "💪",
            "MODERATE": "👍",
            "WEAK": "👌",
        }

        # Emoji do tipo de sinal
        signal_emoji = emoji_map.get(signal_type, "📊")
        strength_icon = strength_emoji.get(strength, "📊")

        # Formatar preço
        formatted_price = format_crypto_price(current_price)

        # Template da mensagem
        template = f"""
{signal_emoji} <b>SINAL DE TRADING</b> {signal_emoji}

{strength_icon} <b>{symbol}</b> - {strength}
💰 Preço: {formatted_price}
📊 RSI: {rsi_value:.1f}
⏰ Timeframe: {timeframe}
🔗 Fonte: {source}

{message}

🔔 <i>BullBot Signals</i>
        """.strip()

        return template

    async def test_connection(self) -> bool:
        """Testar conexão com a API do Telegram"""
        try:
            me = await self.bot.get_me()
            logger.info(f"✅ Conexão Telegram OK - Bot: @{me.username}")
            return True

        except Exception as e:
            logger.error(f"❌ Erro na conexão Telegram: {e}")
            return False


# Instância global do cliente
telegram_client = TelegramClient(settings.telegram_bot_token)
