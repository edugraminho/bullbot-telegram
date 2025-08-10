"""
Configurações do projeto BullBot Telegram
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações principais do projeto BullBot Telegram"""

    # ===============================================
    # Telegram Settings
    # ===============================================

    # Token do bot Telegram
    telegram_bot_token: str

    # Chat ID do grupo para envio de sinais
    telegram_group_chat_id: str

    # Configurações de Conexão
    telegram_connection_pool_size: int = (
        10  # Pool de conexões HTTP (reduzido para t2.micro)
    )
    telegram_pool_timeout: int = 30  # Timeout do pool em segundos
    telegram_batch_size: int = (
        3  # Máximo de envios simultâneos (reduzido para t2.micro)
    )

    # ===============================================
    # Celery Settings
    # ===============================================

    # Configurações de Concorrência
    celery_worker_count: int = 1  # Apenas 1 worker para t2.micro
    celery_tasks_per_worker: int = 1  # 1 task por worker
    celery_task_acknowledge_late: bool = True

    # Configurações de Timeout (segundos)
    celery_task_warning_timeout: int = 180  # 3 min - aviso de timeout
    celery_task_force_kill_timeout: int = 300  # 5 min - força encerramento

    # Configurações de Performance
    celery_worker_prefetch_multiplier: int = 1  # Prefetch mínimo
    celery_task_soft_time_limit: int = 180  # Soft limit 3 min
    celery_task_time_limit: int = 300  # Hard limit 5 min

    # ===============================================
    # Logging Settings
    # ===============================================

    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Instância global das configurações
settings = Settings()
