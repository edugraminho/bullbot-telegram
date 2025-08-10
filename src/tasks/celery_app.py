"""
Configuração principal do Celery - BullBot Telegram
"""

import os
import logging
from celery import Celery
from src.utils.config import settings

# Configurar Celery
celery_app = Celery(
    "bullbot_telegram",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0"),
    include=[
        "src.tasks.telegram_tasks",
        "src.tasks.monitor_tasks",
    ],
)

# Configurações do Celery
celery_app.conf.update(
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Concorrência e Performance
    worker_concurrency=settings.celery_worker_count,
    task_acks_late=settings.celery_task_acknowledge_late,
    worker_prefetch_multiplier=settings.celery_worker_prefetch_multiplier,
    # Timeouts
    task_soft_time_limit=settings.celery_task_soft_time_limit,
    task_time_limit=settings.celery_task_time_limit,
    # Configurações de Performance
    worker_max_tasks_per_child=100,  # Reiniciar worker após 100 tasks
    worker_max_memory_per_child=200000,  # 200MB por worker
    task_compression="gzip",  # Comprimir tasks para economizar memória
    # Configurações de Retry
    task_default_retry_delay=60,  # 1 minuto entre retries
    task_max_retries=3,  # Máximo 3 tentativas
    # Configurações de Result
    result_expires=3600,  # Resultados expiram em 1 hora
    result_backend_transport_options={
        "master_name": "mymaster",
        "visibility_timeout": 3600,
    },
)

# Configuração de logging
celery_app.conf.worker_log_format = (
    "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"
)
celery_app.conf.worker_task_log_format = (
    "[%(asctime)s: %(levelname)s][%(task_name)s(%(task_id)s)] %(message)s"
)

# Configurações para reduzir logs verbosos
celery_app.conf.worker_redirect_stdouts = False
celery_app.conf.worker_redirect_stdouts_level = "WARNING"

# Configurar logging para evitar logs duplicados
logging.getLogger("celery.worker").setLevel(logging.WARNING)
logging.getLogger("celery.task").setLevel(logging.WARNING)
logging.getLogger("celery.worker.control").setLevel(logging.WARNING)

# Silenciar logs HTTP do httpx
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# Importar e configurar beat schedule
from src.tasks.beat_schedule import (
    beat_schedule,
    beat_schedule_filename,
    beat_sync_every,
    beat_max_loop_interval,
)

celery_app.conf.beat_schedule = beat_schedule
celery_app.conf.beat_schedule_filename = beat_schedule_filename
celery_app.conf.beat_sync_every = beat_sync_every
celery_app.conf.beat_max_loop_interval = beat_max_loop_interval

# Importar tasks após configuração para evitar problemas de import circular
celery_app.autodiscover_tasks(['src.tasks'])
