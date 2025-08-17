"""
Serviço para determinar quais usuários devem receber sinais - BullBot Telegram
Aplica filtros personalizados e lógica de eligibilidade por usuário
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from src.database.connection import get_db
from src.database.models import (
    UserMonitoringConfig,
    SignalHistory,
)
from src.utils.logger import get_logger
from datetime import datetime, timezone, timedelta

logger = get_logger(__name__)


class SignalDispatchService:
    """Serviço para determinar usuários elegíveis para receber sinais"""

    def __init__(self):
        self.logger = logger

    def get_eligible_users_for_signal(
        self, signal_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Determinar quais usuários devem receber um sinal específico

        Args:
            signal_data: Dados do sinal (symbol, timeframe, signal_type, indicator_data, etc.)

        Returns:
            Lista de usuários elegíveis com suas configurações
        """
        try:
            symbol = signal_data.get("symbol", "").upper()
            timeframe = signal_data.get("timeframe", "")
            signal_type = signal_data.get("signal_type", "").upper()

            # Obter dados do RSI
            rsi_data = signal_data.get("indicator_data", {})
            rsi_value = rsi_data.get("rsi_value", 0)

            if not symbol or not timeframe or not signal_type:
                self.logger.warning(
                    "Dados insuficientes no sinal para determinar usuários elegíveis"
                )
                return []

            self.logger.info(
                f"Buscando usuários elegíveis para {symbol} {timeframe} {signal_type} RSI:{rsi_value}"
            )

            db = next(get_db())

            # Buscar usuários ativos diretamente da tabela unificada
            active_configs = (
                db.query(UserMonitoringConfig)
                .filter(UserMonitoringConfig.active == True)
                .order_by(desc(UserMonitoringConfig.priority))
                .all()
            )

            if not active_configs:
                self.logger.info("Nenhuma configuração ativa encontrada")
                return []

            eligible_users = []

            # Agrupar configurações por chat_id para processar por prioridade
            configs_by_user = {}
            for config in active_configs:
                if config.chat_id not in configs_by_user:
                    configs_by_user[config.chat_id] = []
                configs_by_user[config.chat_id].append(config)

            # Processar cada usuário
            for chat_id, user_configs in configs_by_user.items():
                # Ordenar por prioridade (mais alta primeiro)
                user_configs.sort(key=lambda x: x.priority, reverse=True)

                # Processar cada configuração do usuário (prioridade decrescente)
                for config in user_configs:
                    if self._is_user_eligible_for_signal(config, signal_data):
                        # Verificar filtros anti-spam
                        if self._check_anti_spam_filters(config, signal_data):
                            eligible_users.append(
                                {
                                    "chat_id": config.chat_id,
                                    "chat_type": config.chat_type,
                                    "config_name": config.config_name,
                                    "config_priority": config.priority,
                                    "user_config": config,
                                }
                            )
                            break  # Usuário já elegível com esta config, não precisa testar outras

            self.logger.info(
                f"Encontrados {len(eligible_users)} usuários elegíveis para o sinal"
            )
            return eligible_users

        except Exception as e:
            self.logger.error(f"❌ Erro ao determinar usuários elegíveis: {e}")
            return []

    def _is_user_eligible_for_signal(
        self,
        config: UserMonitoringConfig,
        signal_data: Dict[str, Any],
    ) -> bool:
        """Verificar se usuário é elegível baseado em sua configuração"""
        try:
            symbol = signal_data.get("symbol", "").upper()
            timeframe = signal_data.get("timeframe", "")
            signal_type = signal_data.get("signal_type", "").upper()

            # Obter dados do RSI
            rsi_data = signal_data.get("indicator_data", {})
            rsi_value = rsi_data.get("rsi_value", 0)

            # 1. Verificar se símbolo está na lista do usuário
            if symbol not in config.symbols:
                self.logger.info(
                    f"❌ Símbolo {symbol} não está na lista do usuário {config.chat_id}"
                )
                return False

            # 2. Verificar se timeframe está na lista do usuário
            if timeframe not in config.timeframes:
                self.logger.info(
                    f"❌ Timeframe {timeframe} não está na lista do usuário {config.chat_id}"
                )
                return False

            # 3. Verificar configuração de RSI do usuário
            rsi_config = config.indicators_config.get("RSI", {})

            if rsi_config.get("enabled", True):  # RSI habilitado por padrão
                oversold = rsi_config.get("oversold", 20)
                overbought = rsi_config.get("overbought", 80)

                # Verificar se sinal RSI está dentro dos critérios do usuário
                if signal_type in ["BUY", "STRONG_BUY"]:
                    if rsi_value > oversold:
                        self.logger.info(
                            f"❌ RSI {rsi_value} > {oversold} (sobrevenda) - não elegível para COMPRA"
                        )
                        return False
                elif signal_type in ["SELL", "STRONG_SELL"]:
                    if rsi_value < overbought:
                        self.logger.info(
                            f"❌ RSI {rsi_value} < {overbought} (sobrecompra) - não elegível para VENDA"
                        )
                        return False

            # Log de sucesso
            self.logger.info(
                f"Usuário {config.chat_id} elegível para {symbol} {timeframe} {signal_type} RSI:{rsi_value}"
            )
            return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar elegibilidade do usuário: {e}")
            return False

    def _check_anti_spam_filters(
        self, config: UserMonitoringConfig, signal_data: Dict[str, Any]
    ) -> bool:
        """Verificar filtros anti-spam para evitar sinais excessivos"""
        try:
            symbol = signal_data.get("symbol", "").upper()
            timeframe = signal_data.get("timeframe", "")
            strength = signal_data.get("strength", "").upper()

            rsi_data = signal_data.get("indicator_data", {})
            rsi_value = rsi_data.get("rsi_value", 0)

            filter_config = config.filter_config or {}

            # 1. Verificar limite diário de sinais
            max_signals_per_day = filter_config.get("max_signals_per_day", 3)
            if not self._check_daily_limit(config.user_id, symbol, max_signals_per_day):
                self.logger.info(
                    f"Usuário {config.user_id} atingiu limite diário para {symbol}"
                )
                return False

            # 2. Verificar cooldown por timeframe e força
            cooldown_config = filter_config.get("cooldown_minutes", {})
            if not self._check_cooldown(
                config.user_id, symbol, timeframe, strength, cooldown_config
            ):
                self.logger.info(
                    f"Usuário {config.user_id} em cooldown para {symbol} {timeframe} {strength}"
                )
                return False

            # 3. Verificar diferença mínima de RSI
            min_rsi_diff = filter_config.get("min_rsi_difference", 2.0)
            if not self._check_rsi_difference(
                config.user_id, symbol, rsi_value, min_rsi_diff
            ):
                self.logger.info(
                    f"Usuário {config.user_id} RSI muito próximo do último sinal para {symbol}"
                )
                return False

            return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar filtros anti-spam: {e}")
            return True  # Em caso de erro, permitir o sinal

    def _check_daily_limit(self, user_id: int, symbol: str, max_signals: int) -> bool:
        """Verificar se usuário não ultrapassou limite diário de sinais"""
        try:
            db = next(get_db())

            # Contar sinais enviados hoje para este usuário e símbolo
            today = datetime.now(timezone.utc).date()

            # Como não temos tabela de envios, vamos usar uma heurística baseada em sinais processados
            # Esta é uma simplificação - idealmente teríamos uma tabela de signal_sends
            signals_today = (
                db.query(SignalHistory)
                .filter(
                    and_(
                        SignalHistory.symbol == symbol,
                        SignalHistory.created_at >= today,
                        SignalHistory.processed == True,  # noqa: E712
                    )
                )
                .count()
            )

            # Estimativa conservadora: assumir que todos os sinais processados foram enviados
            estimated_signals_sent = min(signals_today, max_signals + 1)

            return estimated_signals_sent < max_signals

        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar limite diário: {e}")
            return True

    def _check_cooldown(
        self,
        user_id: int,
        symbol: str,
        timeframe: str,
        strength: str,
        cooldown_config: Dict[str, Any],
    ) -> bool:
        """Verificar se cooldown foi respeitado"""
        try:
            # Obter configuração de cooldown para este timeframe e força
            tf_config = cooldown_config.get(timeframe, {})
            cooldown_minutes = tf_config.get(strength.lower(), 0)

            if cooldown_minutes <= 0:
                return True  # Sem cooldown configurado

            db = next(get_db())

            # Buscar último sinal processado para este símbolo
            cutoff_time = datetime.now(timezone.utc) - timedelta(
                minutes=cooldown_minutes
            )

            recent_signal = (
                db.query(SignalHistory)
                .filter(
                    and_(
                        SignalHistory.symbol == symbol,
                        SignalHistory.processed == True,  # noqa: E712
                        SignalHistory.processed_at >= cutoff_time,
                    )
                )
                .first()
            )

            return recent_signal is None

        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar cooldown: {e}")
            return True

    def _check_rsi_difference(
        self, user_id: int, symbol: str, current_rsi: float, min_difference: float
    ) -> bool:
        """Verificar se RSI atual tem diferença mínima do último sinal"""
        try:
            if min_difference <= 0:
                return True  # Sem diferença mínima configurada

            db = next(get_db())

            # Buscar último sinal processado para este símbolo
            last_signal = (
                db.query(SignalHistory)
                .filter(
                    and_(
                        SignalHistory.symbol == symbol,
                        SignalHistory.processed == True,  # noqa: E712
                    )
                )
                .order_by(desc(SignalHistory.processed_at))
                .first()
            )

            if not last_signal:
                return True  # Nenhum sinal anterior

            # Obter RSI do último sinal
            last_rsi_data = (
                last_signal.indicator_data.get("RSI", {})
                if last_signal.indicator_data
                else {}
            )
            last_rsi = last_rsi_data.get("value", 0)

            if last_rsi == 0:
                return True  # RSI anterior não disponível

            # Verificar diferença
            rsi_difference = abs(current_rsi - last_rsi)
            return rsi_difference >= min_difference

        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar diferença de RSI: {e}")
            return True

    def get_user_signal_stats(self, user_id: int) -> Dict[str, Any]:
        """Obter estatísticas de sinais para um usuário"""
        try:
            db = next(get_db())

            # Obter configurações do usuário
            configs = (
                db.query(UserMonitoringConfig)
                .filter(
                    and_(
                        UserMonitoringConfig.user_id == user_id,
                        UserMonitoringConfig.active == True,  # noqa: E712
                    )
                )
                .all()
            )

            if not configs:
                return {"error": "Usuário sem configurações ativas"}

            # Estatísticas básicas
            today = datetime.now(timezone.utc).date()

            # Contar sinais processados hoje (aproximação)
            signals_today = (
                db.query(SignalHistory)
                .filter(
                    and_(
                        SignalHistory.created_at >= today,
                        SignalHistory.processed == True,  # noqa: E712
                    )
                )
                .count()
            )

            # Obter estatísticas da configuração principal
            main_config = configs[0] if configs else None

            return {
                "user_id": user_id,
                "active_configs": len(configs),
                "signals_received_total": main_config.signals_received
                if main_config
                else 0,
                "estimated_signals_today": signals_today,
                "subscription_active": main_config.active if main_config else False,
                "last_activity": main_config.last_activity if main_config else None,
            }

        except Exception as e:
            self.logger.error(
                f"❌ Erro ao obter estatísticas do usuário {user_id}: {e}"
            )
            return {"error": str(e)}


# Instância global do serviço
signal_dispatch_service = SignalDispatchService()
