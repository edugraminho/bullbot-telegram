"""
Aplicação principal do BullBot Telegram
Simplificado para focar apenas no processamento de sinais
"""

import asyncio
import logging
from src.utils.logger import get_logger
from src.services.signal_reader import signal_reader
from src.integrations.telegram_bot import telegram_client

logger = get_logger(__name__)


async def test_initial_connections():
    """Testar conexões iniciais com banco e Telegram"""
    logger.info("🔍 Testando conexões iniciais...")

    # Testar conexão com banco (agora síncrono)
    signals_ok = signal_reader.test_connection()
    if not signals_ok:
        logger.error("❌ Falha na conexão com banco de dados")
        return False

    # Testar conexão com Telegram
    telegram_ok = await telegram_client.test_connection()
    if not telegram_ok:
        logger.error("❌ Falha na conexão com Telegram")
        return False

    logger.info("✅ Todas as conexões estão funcionando")
    return True


async def main():
    """Função principal simplificada"""
    logger.info("🚀 Iniciando BullBot Telegram - Processador de Sinais")

    try:
        # Testar conexões iniciais
        connections_ok = await test_initial_connections()
        if not connections_ok:
            logger.error("❌ Falha nas conexões iniciais - encerrando")
            return

        # Obter status inicial do sistema (agora síncrono)
        status = signal_reader.get_system_status()
        if status:
            logger.info(
                f"📊 Status do sistema: {status.get('unprocessed_signals', 0)} sinais pendentes"
            )

        logger.info("✅ BullBot Telegram iniciado com sucesso")
        logger.info("📝 Use o Celery para processar sinais automaticamente")
        logger.info("🔧 Comandos úteis:")
        logger.info(
            "   - Worker: celery -A src.tasks.celery_app worker --loglevel=info"
        )
        logger.info("   - Beat: celery -A src.tasks.celery_app beat --loglevel=info")
        logger.info(
            "   - Teste: celery -A src.tasks.celery_app call src.tasks.telegram_tasks.test_connections"
        )

    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")
        raise


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Executar aplicação
    asyncio.run(main())
