"""
Models do banco de dados - BullBot Telegram
Simplificado para focar apenas em leitura e envio de sinais
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SignalHistory(Base):
    """Histórico de sinais - Estrutura simplificada para leitura"""

    __tablename__ = "signal_history"

    # Campos básicos
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    signal_type = Column(String(20), nullable=False)  # BUY, SELL, HOLD
    strength = Column(String(20), nullable=False)  # WEAK, MODERATE, STRONG
    price = Column(Float, nullable=False)
    timeframe = Column(String(10), nullable=False)  # 15m, 1h, 4h, etc
    source = Column(String(20), nullable=False)  # binance, gate, mexc
    message = Column(Text)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )

    # Campos para múltiplos indicadores
    indicator_type = Column(JSON, nullable=False)  # ["RSI", "MACD", "MA_CROSSOVER"]
    indicator_data = Column(JSON, nullable=False)  # Dados de todos os indicadores
    indicator_config = Column(JSON, nullable=True)  # Configurações dos indicadores

    # Campos de contexto básico
    volume_24h = Column(Float, nullable=True)  # Volume 24h no momento do sinal
    price_change_24h = Column(Float, nullable=True)  # Variação % 24h

    # Campos de qualidade
    confidence_score = Column(Float, nullable=True)  # Score de confiança (0-100)
    combined_score = Column(
        Float, nullable=True
    )  # Score combinado de todos indicadores

    # Controle de processamento (para bot do Telegram)
    processed = Column(Boolean, default=False)  # Se foi processado por algum serviço
    processed_at = Column(DateTime, nullable=True)  # Quando foi processado
    processed_by = Column(String(50), nullable=True)  # Qual serviço processou

    # Auditoria mínima
    processing_time_ms = Column(Integer, nullable=True)  # Tempo de processamento


class MonitoringConfig(Base):
    """Configurações de monitoramento de sinais"""

    __tablename__ = "monitoring_config"

    id = Column(Integer, primary_key=True)

    # Identificação
    name = Column(
        String(50), nullable=False, unique=True
    )  # "default", "aggressive", etc
    description = Column(Text, nullable=True)  # Descrição da configuração
    active = Column(Boolean, default=True)

    # Configuração de ativos
    symbols = Column(JSON, nullable=False)  # Lista de símbolos
    timeframes = Column(JSON, default=["15m", "1h", "4h"])

    # Configuração de indicadores (estrutura flexível JSON)
    indicators_config = Column(JSON, nullable=False)
    # Exemplo: {
    #     "RSI": {
    #         "enabled": true,
    #         "period": 14,
    #         "oversold": 20,
    #         "overbought": 80
    #     }
    # }

    # Metadados
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
