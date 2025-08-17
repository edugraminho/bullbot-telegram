"""
Tasks Celery para Telegram - BullBot Telegram
Sistema completo de processamento e envio de sinais para assinantes
"""

import os
from celery import current_app
from src.tasks.celery_app import celery_app
from src.integrations.telegram_bot import telegram_client
from src.services.signal_reader import signal_reader
from src.services.signal_dispatch_service import signal_dispatch_service
from src.services.user_config_service import user_config_service
from src.utils.logger import get_logger
import asyncio
import redis

logger = get_logger(__name__)

# Cliente Redis para cache de estado - usando getenv diretamente
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_client = redis.from_url(redis_url)


@celery_app.task(bind=True, max_retries=3)
def process_unprocessed_signals(self):
    """
    Task principal para processar sinais e enviar para usuários elegíveis
    Integrado com sistema completo de assinantes e configurações personalizadas
    """
    try:
        logger.info("Iniciando processamento de sinais não processados")

        # 1. Verificar se houve mudanças usando cache (otimização)
        cache_key = "last_signal_count"
        current_count = signal_reader.get_unprocessed_signals_count()

        logger.info(f"Sinais não processados encontrados: {current_count}")

        # Buscar último count do cache
        last_count = redis_client.get(cache_key)
        last_count = int(last_count) if last_count else 0

        # Se não há mudanças, não processar (economia de recursos)
        if current_count == last_count:
            logger.info("Nenhum sinal novo detectado")
            return {"status": "no_changes", "message": "Nenhum sinal novo detectado"}

        # Atualizar cache
        redis_client.setex(cache_key, 300, current_count)  # Expira em 5 min

        # 2. Se há mudanças, processar sinais
        logger.info(
            f"Detectados {current_count - last_count} sinais novos! Iniciando processamento..."
        )

        # Buscar sinais não processados
        signals = signal_reader.get_unprocessed_signals(limit=50)

        if not signals:
            logger.info("Nenhum sinal não processado encontrado")
            return {"status": "no_signals", "processed_count": 0, "errors": []}

        logger.info(f"Encontrados {len(signals)} sinais para processar")

        # Processar cada sinal
        processed_count = 0
        sent_count = 0
        errors = []

        for signal in signals:
            try:
                signal_id = signal["id"]
                symbol = signal.get("symbol", "")

                logger.info(
                    f"Processando sinal {signal_id}: {symbol} {signal.get('timeframe', '')} {signal.get('signal_type', '')}"
                )

                # 3. Determinar usuários elegíveis para este sinal
                eligible_users = signal_dispatch_service.get_eligible_users_for_signal(
                    signal
                )

                if not eligible_users:
                    logger.info(f"Sinal {signal_id} sem usuários elegíveis")
                else:
                    logger.info(
                        f"Sinal {signal_id} será enviado para {len(eligible_users)} usuários"
                    )

                    # 4. Enviar sinal para usuários elegíveis
                    signal_sent_count = await_sync(
                        send_signal_to_users(signal, eligible_users)
                    )
                    sent_count += signal_sent_count

                # 5. Marcar sinal como processado
                success = signal_reader.mark_signal_processed(signal_id)

                if success:
                    processed_count += 1
                    logger.info(f"Sinal {signal_id} processado com sucesso")
                else:
                    errors.append(f"Falha ao marcar sinal {signal_id} como processado")
                    logger.error(
                        f"❌ Falha ao marcar sinal {signal_id} como processado"
                    )

            except Exception as e:
                error_msg = f"Erro no sinal {signal['id']}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"❌ {error_msg}")

        logger.info(
            f"Processamento concluído: {processed_count} sinais processados, {sent_count} envios realizados"
        )

        return {
            "status": "completed",
            "processed_count": processed_count,
            "total_signals": len(signals),
            "sent_count": sent_count,
            "new_signals_detected": current_count - last_count,
            "errors": errors,
        }

    except Exception as e:
        logger.error(f"❌ Erro na task process_unprocessed_signals: {e}")
        # Retry automático em caso de erro
        raise self.retry(countdown=60, exc=e)


def await_sync(coro):
    """Helper para executar código assíncrono em contexto síncrono"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def send_signal_to_users(signal_data, eligible_users):
    """
    Enviar sinal para lista de usuários elegíveis

    Args:
        signal_data: Dados do sinal
        eligible_users: Lista de usuários elegíveis

    Returns:
        Número de envios bem-sucedidos
    """
    sent_count = 0

    for user_info in eligible_users:
        try:
            chat_id = user_info["chat_id"]

            # Enviar sinal personalizado para cada usuário
            success = await send_signal_to_user(signal_data, chat_id)

            if success:
                # Atualizar estatísticas do usuário
                user_config_service.increment_signals_received(chat_id)
                sent_count += 1
                logger.info(f"Sinal enviado com sucesso para {chat_id}")
            else:
                logger.error(f"❌ Falha ao enviar sinal para {chat_id}")

        except Exception as e:
            logger.error(
                f"❌ Erro ao enviar sinal para {user_info.get('chat_id', 'unknown')}: {e}"
            )

    return sent_count


async def send_signal_to_user(signal_data, chat_id):
    """
    Enviar sinal para um usuário específico via Telegram Bot API

    Args:
        signal_data: Dados do sinal
        chat_id: ID do chat do usuário

    Returns:
        bool: True se enviado com sucesso
    """
    try:
        from telegram import Bot
        from telegram.constants import ParseMode
        from src.utils.config import settings

        bot = Bot(token=settings.telegram_bot_token)

        # Formatar mensagem do sinal
        message = _format_signal_message_for_user(signal_data)

        # Enviar mensagem
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

        return True

    except Exception as e:
        logger.error(f"❌ Erro ao enviar sinal para usuário {chat_id}: {e}")
        return False


def _format_signal_message_for_user(signal_data):
    """Formatar mensagem do sinal personalizada para usuário"""
    try:
        from src.utils.price_formatter import format_crypto_price

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
        signal_emoji = emoji_map.get(signal_type.upper(), "📊")
        strength_icon = strength_emoji.get(strength.upper(), "📊")

        # Formatar preço
        formatted_price = format_crypto_price(current_price)

        # Template da mensagem personalizada
        template = f"""{signal_emoji} <b>SINAL DE TRADING</b> {signal_emoji}

{strength_icon} <b>{symbol}</b> - {strength}
💰 Preço: {formatted_price}
📊 RSI: {rsi_value:.1f}
⏰ Timeframe: {timeframe}
🔗 Fonte: {source}

{message}

<i>🤖 BullBot Signals</i>"""

        return template.strip()

    except Exception as e:
        logger.error(f"❌ Erro ao formatar mensagem: {e}")
        return f"Sinal: {signal_data.get('symbol', 'N/A')} {signal_data.get('signal_type', 'N/A')}"


@celery_app.task
def get_subscription_stats():
    """Task para obter estatísticas de assinantes"""
    try:
        stats = user_config_service.get_subscription_stats()
        logger.info(f"Estatísticas de assinantes: {stats}")
        return stats
    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas de assinantes: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task
def test_connections():
    """Task para testar conexões com banco e Telegram"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Testar conexão com banco (agora síncrono)
            signals_ok = signal_reader.test_connection()

            # Testar conexão com Telegram
            telegram_ok = loop.run_until_complete(telegram_client.test_connection())

            status = {
                "database": "ok" if signals_ok else "error",
                "telegram": "ok" if telegram_ok else "error",
                "overall": "ok" if (signals_ok and telegram_ok) else "error",
            }

            logger.info(f"Status das conexões: {status}")
            return status

        finally:
            loop.close()

    except Exception as e:
        logger.error(f"❌ Erro no teste de conexões: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task
def get_system_status():
    """Task para obter status do sistema via banco direto"""
    try:
        # Agora é síncrono - não precisa de loop
        status = signal_reader.get_system_status()
        return status
    except Exception as e:
        logger.error(f"❌ Erro ao obter status: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task
def cleanup_old_data():
    """Task para limpeza e otimizações periódicas"""
    try:
        # Limpar cache Redis antigo
        cache_keys = ["last_signal_count", "signal_cache_*"]
        for pattern in cache_keys:
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
                logger.info(f"Limpos {len(keys)} keys do cache Redis")

        # Verificar e otimizar conexões
        status = signal_reader.get_system_status()

        return {
            "status": "cleanup_completed",
            "cache_cleaned": True,
            "system_status": status,
        }

    except Exception as e:
        logger.error(f"❌ Erro na limpeza: {e}")
        return {"status": "error", "error": str(e)}
