"""
Configuração principal do Celery - BullBot Telegram
"""

import logging
from celery import Celery
from src.utils.config import settings

# Configurar Celery
celery_app = Celery(
    "bullbot_telegram",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "src.tasks.telegram_tasks",
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
    worker_prefetch_multiplier=settings.celery_tasks_per_worker,
    task_soft_time_limit=settings.celery_task_warning_timeout,
    task_time_limit=settings.celery_task_force_kill_timeout,
)

# Configuração de logging
celery_app.conf.worker_log_format = (
    "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"
)
celery_app.conf.worker_task_log_format = "[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s"

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
