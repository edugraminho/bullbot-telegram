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

    # Configurações de Conexão
    telegram_connection_pool_size: int = 20  # Pool de conexões HTTP
    telegram_pool_timeout: int = 60  # Timeout do pool em segundos
    telegram_batch_size: int = 5  # Máximo de envios simultâneos

    # ===============================================
    # Database Settings
    # ===============================================

    # Conexão com banco do BullBot Signals
    database_url: str

    # ===============================================
    # Redis Settings
    # ===============================================

    # Conexão Redis
    redis_url: str = "redis://redis:6379/0"

    # ===============================================
    # Celery Settings
    # ===============================================

    # Configurações de Concorrência
    celery_worker_count: int = 2  # Número de workers
    celery_tasks_per_worker: int = 1  # Tasks por worker
    celery_task_acknowledge_late: bool = True

    # Configurações de Timeout (segundos)
    celery_task_warning_timeout: int = 300  # 5 min - aviso de timeout
    celery_task_force_kill_timeout: int = 600  # 10 min - força encerramento

    # ===============================================
    # Logging Settings
    # ===============================================

    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Global instance of settings
settings = Settings()
