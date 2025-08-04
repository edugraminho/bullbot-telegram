"""
Tasks Celery para Telegram - BullBot Telegram
"""

from celery import current_app
from src.tasks.celery_app import celery_app
from src.integrations.telegram_bot import telegram_client
from src.database.models import SignalHistory
from src.database.connection import SessionLocal
from src.utils.logger import get_logger
import asyncio
import random
from telegram.error import TimedOut, NetworkError, RetryAfter
from src.database.models import TelegramSubscription

logger = get_logger(__name__)


async def send_message_with_retry(
    bot, chat_id: str, message_text: str, max_retries: int = 3
) -> bool:
    """
    Envia mensagem com retry inteligente e backoff exponencial

    Args:
        bot: Instância do bot Telegram
        chat_id: ID do chat
        message_text: Texto da mensagem
        max_retries: Máximo de tentativas

    Returns:
        True se enviou com sucesso, False caso contrário
    """

    for attempt in range(max_retries + 1):
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=message_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
            return True

        except RetryAfter as e:
            # API rate limit - esperar o tempo indicado
            wait_time = e.retry_after + random.uniform(0.1, 0.5)  # Jitter
            logger.warning(
                f"⏳ Rate limit para chat {chat_id}: aguardando {wait_time:.1f}s"
            )
            await asyncio.sleep(wait_time)

        except (TimedOut, NetworkError) as e:
            if attempt < max_retries:
                # Backoff exponencial com jitter
                wait_time = (2**attempt) + random.uniform(0.1, 1.0)
                logger.warning(
                    f"🔄 Tentativa {attempt + 1}/{max_retries + 1} para chat {chat_id} - aguardando {wait_time:.1f}s"
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"❌ Falha definitiva para chat {chat_id}: {e}")
                return False

        except Exception as e:
            logger.error(f"❌ Erro inesperado para chat {chat_id}: {e}")
            return False

    return False


class TelegramTaskConfig:
    """Configuração para tasks do Telegram"""

    def __init__(self):
        self.max_retries = 3
        self.retry_countdown = 60
        self.cleanup_days = 30


# Instância global de configuração
telegram_config = TelegramTaskConfig()


@celery_app.task(bind=True, max_retries=3)
def send_telegram_signal(self, signal_data):
    """
    Task para enviar sinal via Telegram

    Args:
        signal_data: Dicionário com dados do sinal
    """
    try:
        # Verificar se o cliente Telegram está disponível
        if telegram_client is None:
            logger.error(
                "❌ Cliente Telegram não está disponível - verificar TELEGRAM_BOT_TOKEN"
            )
            return {"status": "failed", "error": "Telegram client not available"}

        symbol = signal_data.get("symbol", "UNKNOWN")
        signal_type = signal_data.get("signal_type", "UNKNOWN")
        rsi_value = signal_data.get("rsi_value", 0)
        current_price = signal_data.get("current_price", 0)
        strength = signal_data.get("strength", "UNKNOWN")
        timeframe = signal_data.get("timeframe", "UNKNOWN")
        message = signal_data.get("message", "")
        source = signal_data.get("source", "UNKNOWN")
        timestamp = signal_data.get("timestamp", "")

        logger.info(
            f"🚀 Iniciando envio de sinal Telegram para {symbol}: {signal_type}"
        )

        # Usar um único loop para toda a operação
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Função assíncrona principal que executa todas as operações
            async def process_telegram_signal():
                # Obter assinantes ativos
                logger.info(f"🔍 Buscando assinantes para {symbol}...")
                chat_ids = await telegram_client.get_active_subscribers(symbol)
                logger.info(f"📋 Encontrados {len(chat_ids)} assinantes para {symbol}")

                if not chat_ids:
                    logger.warning(f"❌ Nenhum assinante ativo para {symbol}")
                    return {"status": "no_subscribers", "symbol": symbol}

                # Enviar sinal para todos os assinantes
                success_count = 0
                failed_count = 0

                for chat_id in chat_ids:
                    try:
                        # Enviar mensagem com retry
                        success = await send_message_with_retry(
                            telegram_client.bot,
                            chat_id,
                            message,
                            telegram_config.max_retries,
                        )

                        if success:
                            success_count += 1
                            logger.info(f"✅ Sinal enviado para chat {chat_id}")
                        else:
                            failed_count += 1
                            logger.error(f"❌ Falha ao enviar para chat {chat_id}")

                    except Exception as e:
                        failed_count += 1
                        logger.error(f"❌ Erro ao enviar para chat {chat_id}: {e}")

                # Marcar como enviado no banco
                await _mark_signal_as_sent(symbol, timestamp)

                return {
                    "status": "completed",
                    "symbol": symbol,
                    "success_count": success_count,
                    "failed_count": failed_count,
                    "total_subscribers": len(chat_ids),
                }

            # Executar função assíncrona
            result = loop.run_until_complete(process_telegram_signal())
            return result

        finally:
            loop.close()

    except Exception as e:
        logger.error(f"❌ Erro na task send_telegram_signal: {e}")
        # Retry automático em caso de erro
        raise self.retry(countdown=telegram_config.retry_countdown, exc=e)


async def _mark_signal_as_sent(symbol: str, timestamp: str):
    """Marcar sinal como enviado no banco de dados"""
    try:
        db = SessionLocal()

        # Buscar sinal mais recente do símbolo
        signal = (
            db.query(SignalHistory)
            .filter(SignalHistory.symbol == symbol)
            .order_by(SignalHistory.created_at.desc())
            .first()
        )

        if signal and not signal.telegram_sent:
            signal.telegram_sent = True
            db.commit()
            logger.info(f"✅ Sinal marcado como enviado para {symbol}")

        db.close()

    except Exception as e:
        logger.error(f"❌ Erro ao marcar sinal como enviado: {e}")


@celery_app.task
def test_telegram_connection():
    """Task para testar conexão com Telegram"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            success = loop.run_until_complete(telegram_client.test_connection())
            return {"status": "success" if success else "failed"}
        finally:
            loop.close()

    except Exception as e:
        logger.error(f"❌ Erro no teste de conexão Telegram: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task
def cleanup_inactive_subscriptions():
    """Task para limpar assinaturas inativas antigas"""
    try:
        from datetime import datetime, timedelta, timezone

        db = SessionLocal()

        # Remover assinaturas inativas com mais de 30 dias
        cutoff_date = datetime.now(timezone.utc) - timedelta(
            days=telegram_config.cleanup_days
        )

        deleted_count = (
            db.query(TelegramSubscription)
            .filter(
                TelegramSubscription.active == False,  # noqa: E712
                TelegramSubscription.created_at < cutoff_date,
            )
            .delete()
        )

        db.commit()
        db.close()

        logger.info(f"🧹 Removidas {deleted_count} assinaturas inativas antigas")
        return {"status": "completed", "deleted_count": deleted_count}

    except Exception as e:
        logger.error(f"❌ Erro na limpeza de assinaturas: {e}")
        return {"status": "error", "error": str(e)}
