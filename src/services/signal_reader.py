"""
Serviço para leitura de sinais do banco - BullBot Telegram
Focado em buscar sinais não processados diretamente do banco compartilhado
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from src.database.connection import get_db
from src.database.models import SignalHistory
from src.utils.logger import get_logger
from src.utils.config import settings
from datetime import datetime, timezone

logger = get_logger(__name__)


class SignalReader:
    """Serviço para leitura direta de sinais do banco compartilhado"""

    def __init__(self):
        self.bot_id = "bullbot-telegram"
        self.logger = logger

    def get_unprocessed_signals_count(self) -> int:
        """
        Obter contagem rápida de sinais não processados
        Usado para detectar mudanças sem carregar dados completos
        """
        try:
            db = next(get_db())

            # Query otimizada apenas para contar
            count = (
                db.query(SignalHistory)
                .filter(
                    and_(
                        SignalHistory.processed == False,  # noqa: E712
                        SignalHistory.signal_type.in_(["BUY", "SELL", "buy", "sell"]),
                    )
                )
                .count()
            )

            return count

        except Exception as e:
            self.logger.error(f"❌ Erro ao contar sinais não processados: {e}")
            return 0

    def get_unprocessed_signals(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Buscar sinais não processados diretamente do banco
        """
        try:
            db = next(get_db())

            # Query direta ao banco - muito mais performático
            signals = (
                db.query(SignalHistory)
                .filter(
                    and_(
                        SignalHistory.processed == False,  # noqa: E712
                        SignalHistory.signal_type.in_(
                            ["BUY", "SELL", "buy", "sell"]
                        ),  # Apenas sinais de trading
                    )
                )
                .order_by(desc(SignalHistory.created_at))
                .limit(limit)
                .all()
            )

            # Converter para dicionários
            signals_data = []
            for signal in signals:
                signal_dict = {
                    "id": signal.id,
                    "symbol": signal.symbol,
                    "signal_type": signal.signal_type,
                    "strength": signal.strength,
                    "price": signal.price,
                    "timeframe": signal.timeframe,
                    "source": signal.source,
                    "message": signal.message,
                    "created_at": signal.created_at.isoformat()
                    if signal.created_at
                    else None,
                    "indicator_type": signal.indicator_type,
                    "indicator_data": signal.indicator_data,
                    "indicator_config": signal.indicator_config,
                    "volume_24h": signal.volume_24h,
                    "price_change_24h": signal.price_change_24h,
                    "confidence_score": signal.confidence_score,
                    "combined_score": signal.combined_score,
                }
                signals_data.append(signal_dict)

            self.logger.info(
                f"Encontrados {len(signals_data)} sinais não processados via query direta"
            )
            return signals_data

        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar sinais diretamente do banco: {e}")
            return []

    def mark_signal_processed(self, signal_id: int) -> bool:
        """
        Marcar sinal como processado diretamente no banco
        """
        try:
            db = next(get_db())

            # Atualizar diretamente no banco
            signal = (
                db.query(SignalHistory).filter(SignalHistory.id == signal_id).first()
            )

            if signal:
                signal.processed = True
                signal.processed_at = datetime.now(timezone.utc)
                signal.processed_by = self.bot_id

                db.commit()

                self.logger.info(
                    f"Sinal {signal_id} marcado como processado via query direta"
                )
                return True
            else:
                self.logger.warning(f"⚠️ Sinal {signal_id} não encontrado no banco")
                return False

        except Exception as e:
            self.logger.error(
                f"❌ Erro ao marcar sinal {signal_id} como processado: {e}"
            )
            return False

    def get_system_status(self) -> Optional[Dict[str, Any]]:
        """
        Obter status do sistema via queries diretas ao banco
        """
        try:
            db = next(get_db())

            # Contar sinais não processados
            unprocessed_count = (
                db.query(SignalHistory).filter(SignalHistory.processed == False).count()  # noqa: E712
            )

            # Contar total de sinais
            total_signals = db.query(SignalHistory).count()

            # Último sinal criado
            last_signal = (
                db.query(SignalHistory).order_by(desc(SignalHistory.created_at)).first()
            )

            status = {
                "unprocessed_signals": unprocessed_count,
                "total_signals": total_signals,
                "last_signal_at": last_signal.created_at.isoformat()
                if last_signal
                else None,
                "database_connection": "OK",
                "source": "direct_database_query",
            }

            return status

        except Exception as e:
            self.logger.error(f"❌ Erro ao obter status do sistema: {e}")
            return None

    def test_connection(self) -> bool:
        """
        Testar conexão direta com o banco
        """
        try:
            status = self.get_system_status()
            if status:
                self.logger.info(
                    f"Conexão direta com banco OK - {status.get('unprocessed_signals', 0)} sinais pendentes"
                )
                return True
            return False
        except Exception as e:
            self.logger.error(f"❌ Falha no teste de conexão direta: {e}")
            return False


# Instância global do serviço
signal_reader = SignalReader()
