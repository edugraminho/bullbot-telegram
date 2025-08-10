"""
Tasks Celery para Monitoramento de Sinais - BullBot Telegram
Sistema de monitoramento em lote para processamento de símbolos
"""

import os
import time
from celery import current_app
from src.tasks.celery_app import celery_app
from src.utils.logger import get_logger
import redis

logger = get_logger(__name__)

# Cliente Redis para cache de estado
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_client = redis.from_url(redis_url)


@celery_app.task(bind=True, max_retries=3)
def process_symbol_batch(self, exchange, symbols, **kwargs):
    """
    Processa um lote de símbolos de uma exchange específica

    Args:
        exchange (str): Nome da exchange (ex: 'mexc', 'binance', 'okx')
        symbols (list): Lista de símbolos para processar
        **kwargs: Argumentos adicionais

    Returns:
        dict: Resultado do processamento do lote
    """
    try:
        logger.info(
            f"Processando lote de {len(symbols)} símbolos da exchange {exchange}"
        )

        # Simular processamento dos símbolos
        processed_symbols = []
        errors = []

        for symbol in symbols:
            try:
                # Aqui você implementaria a lógica real de processamento
                # Por exemplo: buscar dados de preço, analisar indicadores, etc.

                # Simulação de processamento
                time.sleep(0.1)  # Simular trabalho

                processed_symbols.append(
                    {
                        "exchange": exchange,
                        "symbol": symbol,
                        "status": "processed",
                        "timestamp": time.time(),
                    }
                )

            except Exception as e:
                error_msg = f"Erro ao processar {symbol}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"❌ {error_msg}")

        result = {
            "exchange": exchange,
            "total_symbols": len(symbols),
            "processed_count": len(processed_symbols),
            "error_count": len(errors),
            "processed_symbols": processed_symbols,
            "errors": errors,
            "batch_id": self.request.id,
            "timestamp": time.time(),
        }

        logger.info(
            f"Lote processado: {len(processed_symbols)}/{len(symbols)} símbolos com sucesso"
        )
        return result

    except Exception as e:
        logger.error(f"❌ Erro fatal no processamento do lote: {e}")
        # Retry automático em caso de erro
        raise self.retry(countdown=60, exc=e)


@celery_app.task(bind=True)
def finalize_monitoring_cycle(
    self, cycle_start_time, total_symbols, total_exchanges, **kwargs
):
    """
    Finaliza um ciclo de monitoramento e gera relatório

    Args:
        cycle_start_time (float): Timestamp de início do ciclo
        total_symbols (int): Total de símbolos processados
        total_exchanges (int): Total de exchanges processadas
        **kwargs: Argumentos adicionais

    Returns:
        dict: Relatório final do ciclo
    """
    try:
        cycle_duration = time.time() - cycle_start_time

        # Gerar relatório do ciclo
        report = {
            "cycle_id": self.request.id,
            "cycle_start_time": cycle_start_time,
            "cycle_end_time": time.time(),
            "cycle_duration_seconds": cycle_duration,
            "total_symbols": total_symbols,
            "total_exchanges": total_exchanges,
            "status": "completed",
            "timestamp": time.time(),
        }

        # Salvar relatório no Redis para histórico
        cache_key = f"monitoring_cycle_{int(cycle_start_time)}"
        redis_client.setex(cache_key, 86400, str(report))  # Expira em 24h

        logger.info(
            f"Ciclo de monitoramento finalizado: {total_symbols} símbolos em {total_exchanges} exchanges em {cycle_duration:.2f}s"
        )

        return report

    except Exception as e:
        logger.error(f"❌ Erro ao finalizar ciclo de monitoramento: {e}")
        return {"status": "error", "error": str(e), "cycle_id": self.request.id}


@celery_app.task
def schedule_next_monitoring(**kwargs):
    """
    Agenda o próximo ciclo de monitoramento

    Returns:
        dict: Status do agendamento
    """
    try:
        # Aqui você implementaria a lógica para agendar o próximo ciclo
        # Por exemplo: criar tasks para o próximo batch de símbolos

        logger.info("Próximo ciclo de monitoramento agendado")

        return {
            "status": "scheduled",
            "next_cycle_time": time.time() + 300,  # 5 minutos
            "message": "Próximo ciclo agendado com sucesso",
        }

    except Exception as e:
        logger.error(f"❌ Erro ao agendar próximo ciclo: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task
def start_monitoring_cycle(exchanges_symbols, **kwargs):
    """
    Inicia um novo ciclo de monitoramento

    Args:
        exchanges_symbols (dict): Dicionário com exchanges e seus símbolos
        **kwargs: Argumentos adicionais

    Returns:
        dict: Status do início do ciclo
    """
    try:
        cycle_start_time = time.time()
        total_symbols = sum(len(symbols) for symbols in exchanges_symbols.values())
        total_exchanges = len(exchanges_symbols)

        logger.info(
            f"🚀 Iniciando ciclo de monitoramento: {total_symbols} símbolos em {total_exchanges} exchanges"
        )

        # Criar tasks para cada exchange
        batch_tasks = []

        for exchange, symbols in exchanges_symbols.items():
            # Dividir símbolos em lotes menores se necessário
            batch_size = 50  # Máximo de símbolos por lote
            symbol_batches = [
                symbols[i : i + batch_size] for i in range(0, len(symbols), batch_size)
            ]

            for batch in symbol_batches:
                task = process_symbol_batch.delay(exchange, batch)
                batch_tasks.append(task)

        # Agendar task de finalização
        finalize_task = finalize_monitoring_cycle.delay(
            cycle_start_time=cycle_start_time,
            total_symbols=total_symbols,
            total_exchanges=total_exchanges,
        )

        # Configurar callback para agendar próximo ciclo
        finalize_task.link(schedule_next_monitoring.s())

        result = {
            "cycle_id": finalize_task.id,
            "cycle_start_time": cycle_start_time,
            "total_symbols": total_symbols,
            "total_exchanges": total_exchanges,
            "batch_tasks_created": len(batch_tasks),
            "status": "started",
        }

        logger.info(f"Ciclo iniciado com {len(batch_tasks)} tasks de lote")
        return result

    except Exception as e:
        logger.error(f"❌ Erro ao iniciar ciclo de monitoramento: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task
def get_monitoring_status(**kwargs):
    """
    Obtém o status atual do sistema de monitoramento

    Returns:
        dict: Status do sistema de monitoramento
    """
    try:
        # Buscar informações do Redis
        active_cycles = []
        cycle_keys = redis_client.keys("monitoring_cycle_*")

        for key in cycle_keys[:10]:  # Últimos 10 ciclos
            try:
                cycle_data = redis_client.get(key)
                if cycle_data:
                    active_cycles.append(eval(cycle_data))
            except:
                continue

        # Estatísticas básicas
        stats = {
            "active_cycles_count": len(active_cycles),
            "redis_keys_count": len(cycle_keys),
            "last_cycle": active_cycles[-1] if active_cycles else None,
            "system_time": time.time(),
        }

        return {
            "status": "ok",
            "monitoring_stats": stats,
            "recent_cycles": active_cycles,
        }

    except Exception as e:
        logger.error(f"❌ Erro ao obter status do monitoramento: {e}")
        return {"status": "error", "error": str(e)}
