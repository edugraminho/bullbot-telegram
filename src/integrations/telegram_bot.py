"""
Cliente Telegram para envio de sinais - BullBot Telegram
"""

from typing import List, Optional, Dict, Any
from telegram import Bot
from telegram.error import TelegramError
from telegram.request import HTTPXRequest
from src.database.models import TelegramSubscription
from src.database.connection import SessionLocal
from src.utils.logger import get_logger
from src.utils.price_formatter import format_crypto_price
from src.utils.config import settings


logger = get_logger(__name__)


class TelegramClient:
    """Cliente para envio de mensagens via Telegram com connection pooling otimizado"""

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
        logger.info(
            f"🔧 Cliente Telegram configurado com pool de {settings.telegram_connection_pool_size} conexões (timeout: {settings.telegram_pool_timeout}s)"
        )

    async def send_signal(
        self, signal_data: Dict[str, Any], chat_ids: List[str]
    ) -> bool:
        """
        Envia sinal para lista de chats

        Args:
            signal_data: Dados do sinal
            chat_ids: Lista de IDs dos chats

        Returns:
            True se enviou com sucesso para pelo menos um chat
        """
        if not chat_ids:
            logger.warning("Nenhum chat_id fornecido para envio")
            return False

        message = self._format_signal_message(signal_data)
        success_count = 0

        for chat_id in chat_ids:
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )
                success_count += 1
                logger.info(f"Sinal enviado para chat {chat_id}")

            except TelegramError as e:
                logger.error(f"❌ Erro ao enviar para chat {chat_id}: {e}")
                # Se chat não existe ou bot foi bloqueado, marcar como inativo
                if (
                    "chat not found" in str(e).lower()
                    or "bot was blocked" in str(e).lower()
                ):
                    await self._deactivate_subscription(chat_id)

        return success_count > 0

    def _format_signal_message(self, signal_data: Dict[str, Any]) -> str:
        """Formatar mensagem do sinal"""
        symbol = signal_data.get("symbol", "UNKNOWN")
        signal_type = signal_data.get("signal_type", "UNKNOWN")
        rsi_value = signal_data.get("rsi_value", 0)
        current_price = signal_data.get("current_price", 0)
        strength = signal_data.get("strength", "UNKNOWN")
        timeframe = signal_data.get("timeframe", "UNKNOWN")
        message = signal_data.get("message", "")

        # Emojis por tipo de sinal
        emoji_map = {
            "STRONG_BUY": "🚀🟢",
            "BUY": "📈🟢",
            "SELL": "📉🔴",
            "STRONG_SELL": "💥🔴",
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

{message}

🔔 <i>BullBot Signals</i>
        """.strip()

        return template

    async def _deactivate_subscription(self, chat_id: str):
        """Desativar assinatura de chat inválido"""
        try:
            db = SessionLocal()
            subscription = (
                db.query(TelegramSubscription)
                .filter(TelegramSubscription.chat_id == chat_id)
                .first()
            )

            if subscription:
                subscription.active = False
                db.commit()
                logger.warning(f"Assinatura desativada para chat {chat_id}")

            db.close()

        except Exception as e:
            logger.error(f"❌ Erro ao desativar assinatura {chat_id}: {e}")

    async def get_active_subscribers(
        self, symbol_filter: Optional[str] = None
    ) -> List[str]:
        """
        Obter lista de assinantes ativos

        Args:
            symbol_filter: Filtrar por símbolo específico

        Returns:
            Lista de chat_ids ativos
        """
        try:
            db = SessionLocal()
            query = db.query(TelegramSubscription).filter(
                TelegramSubscription.active == True
            )

            if symbol_filter:
                # Filtrar por símbolo se configurado
                query = query.filter(
                    (TelegramSubscription.symbols_filter.is_(None))
                    | (symbol_filter.in_(TelegramSubscription.symbols_filter))
                )

            subscriptions = query.all()
            chat_ids = [sub.chat_id for sub in subscriptions]

            db.close()
            logger.info(f"Encontrados {len(chat_ids)} assinantes ativos")

            return chat_ids

        except Exception as e:
            logger.error(f"❌ Erro ao buscar assinantes: {e}")
            return []

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
