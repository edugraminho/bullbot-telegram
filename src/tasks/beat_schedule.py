"""
Configuração do Celery Beat - BullBot Telegram
Agendamento de tasks para processamento automático de sinais
"""

# Configuração do Beat Schedule
beat_schedule = {
    # Processar sinais não processados a cada 1 minuto (otimizado para recursos)
    "process-signals-every-1min": {
        "task": "src.tasks.telegram_tasks.process_unprocessed_signals",
        "schedule": 60.0,  # 1 minuto - balanceia responsividade e eficiência
        "options": {"queue": "telegram"},
    },
    # Testar conexões a cada 5 minutos
    "test-connections-every-5min": {
        "task": "src.tasks.telegram_tasks.test_connections",
        "schedule": 300.0,  # 5 minutos
        "options": {"queue": "telegram"},
    },
    # Obter status do sistema a cada 15 minutos
    "get-system-status-every-15min": {
        "task": "src.tasks.telegram_tasks.get_system_status",
        "schedule": 900.0,  # 15 minutos
        "options": {"queue": "telegram"},
    },
    # Obter estatísticas de assinantes a cada 30 minutos
    "subscription-stats-every-30min": {
        "task": "src.tasks.telegram_tasks.get_subscription_stats",
        "schedule": 1800.0,  # 30 minutos
        "options": {"queue": "telegram"},
    },
    # Limpeza de cache e otimizações a cada hora
    "cleanup-every-hour": {
        "task": "src.tasks.telegram_tasks.cleanup_old_data",
        "schedule": 3600.0,  # 1 hora
        "options": {"queue": "telegram"},
    },
}

# Configurações adicionais do Beat
beat_schedule_filename = "/tmp/celerybeat-schedule"
beat_sync_every = 1  # Sincronizar a cada task
beat_max_loop_interval = 15  # Máximo 15 segundos entre verificações
