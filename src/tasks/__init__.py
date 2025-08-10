# Tasks Celery para processamento assíncrono

# Importar tasks principais
from . import telegram_tasks
from . import monitor_tasks

# Exportar tasks para facilitar importação
__all__ = [
    "telegram_tasks",
    "monitor_tasks",
]
