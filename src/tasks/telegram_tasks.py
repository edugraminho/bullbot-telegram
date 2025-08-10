"""
Tasks Celery para Telegram - BullBot Telegram
Simplificado para leitura e envio de sinais
"""

import os
from celery import current_app
from src.tasks.celery_app import celery_app
from src.integrations.telegram_bot import telegram_client
from src.services.signal_reader import signal_reader
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
    Task principal para processar sinais não processados
    Agora mais inteligente com cache e detecção de mudanças
    """
    try:
        logger.info("🚀 Iniciando processamento de sinais não processados")

        # 1. Verificar se houve mudanças usando cache (otimização)
        cache_key = "last_signal_count"
        current_count = signal_reader.get_unprocessed_signals_count()

        logger.info(f"📊 Sinais não processados encontrados: {current_count}")

        # Buscar último count do cache
        last_count = redis_client.get(cache_key)
        last_count = int(last_count) if last_count else 0

        # Se não há mudanças, não processar (economia de recursos)
        if current_count == last_count:
            logger.info("ℹ️ Nenhum sinal novo detectado - pulando processamento")
            return {"status": "no_changes", "message": "Nenhum sinal novo detectado"}

        # Atualizar cache
        redis_client.setex(cache_key, 300, current_count)  # Expira em 5 min

        # 2. Se há mudanças, processar sinais
        logger.info(
            f"🆕 Detectados {current_count - last_count} sinais novos! Iniciando processamento..."
        )

        # Buscar sinais não processados
        signals = signal_reader.get_unprocessed_signals(limit=50)

        if not signals:
            logger.info("ℹ️ Nenhum sinal não processado encontrado")
            return {"status": "no_signals", "processed_count": 0, "errors": []}

        logger.info(f"📋 Encontrados {len(signals)} sinais para processar")

        # Por enquanto, apenas marcar como processados sem enviar para Telegram
        # para identificar se o problema está na conexão com o banco ou Telegram
        processed_count = 0
        errors = []

        for signal in signals:
            try:
                # Marcar como processado diretamente
                success = signal_reader.mark_signal_processed(signal["id"])

                if success:
                    processed_count += 1
                    logger.info(
                        f"✅ Sinal {signal['id']} ({signal['symbol']}) marcado como processado"
                    )
                else:
                    errors.append(
                        f"Falha ao marcar sinal {signal['id']} como processado"
                    )
                    logger.error(
                        f"❌ Falha ao marcar sinal {signal['id']} como processado"
                    )

            except Exception as e:
                error_msg = f"Erro no sinal {signal['id']}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"❌ {error_msg}")

        logger.info(f"🎯 Processamento concluído: {processed_count} sinais processados")

        return {
            "status": "completed",
            "processed_count": processed_count,
            "total_signals": len(signals),
            "new_signals_detected": current_count - last_count,
            "errors": errors,
        }

    except Exception as e:
        logger.error(f"❌ Erro na task process_unprocessed_signals: {e}")
        # Retry automático em caso de erro
        raise self.retry(countdown=60, exc=e)


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
