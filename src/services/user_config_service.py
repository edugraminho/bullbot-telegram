"""
Serviço unificado para gestão de usuários e configurações - BullBot Telegram
Lida com CRUD de configurações personalizadas, assinaturas e estatísticas
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from src.database.connection import get_db
from src.database.models import UserMonitoringConfig
from src.utils.logger import get_logger
from datetime import datetime, timezone

logger = get_logger(__name__)


class UserConfigService:
    """Serviço unificado para gestão de configurações e assinaturas de usuário"""

    def __init__(self):
        self.logger = logger

    def _get_default_indicators_config(self) -> Dict[str, Any]:
        """Configuração padrão de indicadores"""
        return {
            "RSI": {"enabled": True, "period": 14, "oversold": 20, "overbought": 80}
        }

    def _get_default_filter_config(self) -> Dict[str, Any]:
        """Configuração padrão de filtros anti-spam"""
        return {
            "cooldown_minutes": {
                "15m": {"strong": 15, "moderate": 30, "weak": 60},
                "1h": {"strong": 60, "moderate": 120, "weak": 240},
                "4h": {"strong": 120, "moderate": 240, "weak": 360},
                "1d": {"strong": 360, "moderate": 720, "weak": 1440},
            },
            "max_signals_per_day": 3,
            "min_rsi_difference": 2.0,
        }

    def _validate_symbols(self, symbols: List[str]) -> bool:
        """Validar formato dos símbolos"""
        if not symbols or len(symbols) == 0:
            return False

        for symbol in symbols:
            if not symbol or len(symbol.strip()) == 0:
                return False
            if len(symbol) > 20:  # Limite de tamanho
                return False

        return True

    def _validate_timeframes(self, timeframes: List[str]) -> bool:
        """Validar timeframes suportados"""
        if not timeframes or len(timeframes) == 0:
            return False

        valid_timeframes = ["15m", "1h", "4h", "1d"]
        for tf in timeframes:
            if tf not in valid_timeframes:
                return False

        return True

    def create_user_config(
        self,
        user_id: int,
        symbols: List[str],
        timeframes: List[str],
        user_username: str = None,
        config_name: str = "default",
        description: str = None,
        indicators_config: Dict[str, Any] = None,
        filter_config: Dict[str, Any] = None,
        priority: int = 1,
    ) -> Optional[UserMonitoringConfig]:
        """
        Criar nova configuração para usuário

        Campos obrigatórios:
        - user_id: ID do usuário do Telegram
        - symbols: Lista de símbolos (formato: ["BTC", "ETH"])
        - timeframes: Lista de timeframes (formato: ["15m", "1h"])

        Campos opcionais (usam defaults do sistema):
        - indicators_config: Configuração de indicadores
        - filter_config: Filtros anti-spam
        """
        try:
            # Validações obrigatórias
            if not self._validate_symbols(symbols):
                self.logger.error("Símbolos inválidos fornecidos")
                return None

            if not self._validate_timeframes(timeframes):
                self.logger.error("Timeframes inválidos fornecidos")
                return None

            # Normalizar símbolos (uppercase, trim)
            symbols = [s.strip().upper() for s in symbols]

            # Usar defaults se não fornecidos
            if indicators_config is None:
                indicators_config = self._get_default_indicators_config()

            if filter_config is None:
                filter_config = self._get_default_filter_config()

            db = next(get_db())

            # Verificar se já existe config com mesmo nome
            existing = (
                db.query(UserMonitoringConfig)
                .filter(
                    and_(
                        UserMonitoringConfig.user_id == user_id,
                        UserMonitoringConfig.config_name == config_name,
                    )
                )
                .first()
            )

            if existing:
                self.logger.warning(
                    f"Configuração '{config_name}' já existe para usuário {user_id}"
                )
                return None

            # Criar nova configuração
            config = UserMonitoringConfig(
                user_id=user_id,
                user_username=user_username,
                config_name=config_name,
                description=description,
                symbols=symbols,
                timeframes=timeframes,
                indicators_config=indicators_config,
                filter_config=filter_config,
                priority=priority,
                active=True,
            )

            db.add(config)
            db.commit()
            db.refresh(config)

            self.logger.info(
                f"Configuração criada para usuário {user_id}: {len(symbols)} símbolos, {len(timeframes)} timeframes"
            )
            return config

        except Exception as e:
            self.logger.error(f"Erro ao criar configuração para usuário {user_id}: {e}")
            return None

    def get_user_configs(
        self, user_id: int, active_only: bool = True
    ) -> List[UserMonitoringConfig]:
        """Obter todas as configurações de um usuário"""
        try:
            db = next(get_db())

            query = db.query(UserMonitoringConfig).filter(
                UserMonitoringConfig.user_id == user_id
            )

            if active_only:
                query = query.filter(UserMonitoringConfig.active == True)

            configs = query.order_by(desc(UserMonitoringConfig.priority)).all()

            return configs

        except Exception as e:
            self.logger.error(f"Erro ao buscar configurações do usuário {user_id}: {e}")
            return []

    def update_user_symbols(
        self, user_id: int, symbols: List[str], config_name: str = "default"
    ) -> bool:
        """Atualizar símbolos de uma configuração específica"""
        try:
            if not self._validate_symbols(symbols):
                self.logger.error("Símbolos inválidos fornecidos")
                return False

            # Normalizar símbolos
            symbols = [s.strip().upper() for s in symbols]

            db = next(get_db())

            config = (
                db.query(UserMonitoringConfig)
                .filter(
                    and_(
                        UserMonitoringConfig.user_id == user_id,
                        UserMonitoringConfig.config_name == config_name,
                        UserMonitoringConfig.active == True,
                    )
                )
                .first()
            )

            if not config:
                self.logger.warning(
                    f"Configuração '{config_name}' não encontrada para usuário {user_id}"
                )
                return False

            config.symbols = symbols
            config.updated_at = datetime.now(timezone.utc)

            db.commit()

            self.logger.info(f"Símbolos atualizados para usuário {user_id}: {symbols}")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao atualizar símbolos do usuário {user_id}: {e}")
            return False

    def update_user_timeframes(
        self, user_id: int, timeframes: List[str], config_name: str = "default"
    ) -> bool:
        """Atualizar timeframes de uma configuração específica"""
        try:
            if not self._validate_timeframes(timeframes):
                self.logger.error("Timeframes inválidos fornecidos")
                return False

            db = next(get_db())

            config = (
                db.query(UserMonitoringConfig)
                .filter(
                    and_(
                        UserMonitoringConfig.user_id == user_id,
                        UserMonitoringConfig.config_name == config_name,
                        UserMonitoringConfig.active == True,
                    )
                )
                .first()
            )

            if not config:
                self.logger.warning(
                    f"Configuração '{config_name}' não encontrada para usuário {user_id}"
                )
                return False

            config.timeframes = timeframes
            config.updated_at = datetime.now(timezone.utc)

            db.commit()

            self.logger.info(
                f"Timeframes atualizados para usuário {user_id}: {timeframes}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Erro ao atualizar timeframes do usuário {user_id}: {e}")
            return False

    def update_user_rsi_config(
        self,
        user_id: int,
        oversold: int = 20,
        overbought: int = 80,
        period: int = 14,
        config_name: str = "default",
    ) -> bool:
        """Atualizar configuração de RSI"""
        try:
            # Validações básicas
            if oversold >= overbought:
                self.logger.error("RSI oversold deve ser menor que overbought")
                return False

            if oversold < 0 or overbought > 100:
                self.logger.error("Valores de RSI devem estar entre 0 e 100")
                return False

            db = next(get_db())

            config = (
                db.query(UserMonitoringConfig)
                .filter(
                    and_(
                        UserMonitoringConfig.user_id == user_id,
                        UserMonitoringConfig.config_name == config_name,
                        UserMonitoringConfig.active == True,
                    )
                )
                .first()
            )

            if not config:
                self.logger.warning(
                    f"Configuração '{config_name}' não encontrada para usuário {user_id}"
                )
                return False

            # Log valores antes da atualização
            old_config = (
                config.indicators_config.get("RSI", {})
                if config.indicators_config
                else {}
            )
            self.logger.info(f"RSI ANTES: {old_config}")

            # Atualizar apenas RSI mantendo outras configurações de indicadores
            if not config.indicators_config:
                config.indicators_config = self._get_default_indicators_config()

            # Fazer uma cópia para forçar SQLAlchemy a detectar a mudança
            indicators_config = config.indicators_config.copy()
            indicators_config["RSI"] = {
                "enabled": True,
                "period": period,
                "oversold": oversold,
                "overbought": overbought,
            }

            # Atribuir a nova configuração
            config.indicators_config = indicators_config
            config.updated_at = datetime.now(timezone.utc)

            # Forçar SQLAlchemy a marcar como modificado
            from sqlalchemy.orm.attributes import flag_modified

            flag_modified(config, "indicators_config")

            db.commit()
            db.refresh(config)

            # Log valores após a atualização
            new_config = config.indicators_config.get("RSI", {})
            self.logger.info(f"RSI DEPOIS: {new_config}")

            self.logger.info(
                f"RSI atualizado para usuário {user_id}: {oversold}/{overbought}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Erro ao atualizar RSI do usuário {user_id}: {e}")
            if "db" in locals():
                db.rollback()
            return False

    def update_user_filter_config(
        self, user_id: int, filter_config: Dict[str, Any], config_name: str = "default"
    ) -> bool:
        """Atualizar configuração de filtros anti-spam"""
        try:
            db = next(get_db())

            config = (
                db.query(UserMonitoringConfig)
                .filter(
                    and_(
                        UserMonitoringConfig.user_id == user_id,
                        UserMonitoringConfig.config_name == config_name,
                        UserMonitoringConfig.active == True,
                    )
                )
                .first()
            )

            if not config:
                self.logger.warning(
                    f"Configuração '{config_name}' não encontrada para usuário {user_id}"
                )
                return False

            config.filter_config = filter_config
            config.updated_at = datetime.now(timezone.utc)

            db.commit()

            self.logger.info(f"Filtros atualizados para usuário {user_id}")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao atualizar filtros do usuário {user_id}: {e}")
            return False

    def get_user_config_summary(
        self, user_id: int, config_name: str = "default"
    ) -> Optional[Dict[str, Any]]:
        """Obter resumo da configuração do usuário para exibir no bot"""
        try:
            db = next(get_db())

            config = (
                db.query(UserMonitoringConfig)
                .filter(
                    and_(
                        UserMonitoringConfig.user_id == user_id,
                        UserMonitoringConfig.config_name == config_name,
                        UserMonitoringConfig.active == True,
                    )
                )
                .first()
            )

            if not config:
                return None

            rsi_config = config.indicators_config.get("RSI", {})
            filter_config = config.filter_config or {}

            return {
                "config_name": config.config_name,
                "symbols": config.symbols,
                "timeframes": config.timeframes,
                "rsi_oversold": rsi_config.get("oversold", 20),
                "rsi_overbought": rsi_config.get("overbought", 80),
                "max_signals_per_day": filter_config.get("max_signals_per_day", 3),
                "cooldown_minutes": filter_config.get("cooldown_minutes", {}),
                "active": config.active,
                "updated_at": config.updated_at,
            }

        except Exception as e:
            self.logger.error(
                f"Erro ao obter resumo da configuração do usuário {user_id}: {e}"
            )
            return None

    def delete_user_config(self, user_id: int, config_name: str) -> bool:
        """Deletar configuração específica do usuário"""
        try:
            db = next(get_db())

            config = (
                db.query(UserMonitoringConfig)
                .filter(
                    and_(
                        UserMonitoringConfig.user_id == user_id,
                        UserMonitoringConfig.config_name == config_name,
                    )
                )
                .first()
            )

            if not config:
                self.logger.warning(
                    f"Configuração '{config_name}' não encontrada para usuário {user_id}"
                )
                return False

            db.delete(config)
            db.commit()

            self.logger.info(
                f"Configuração '{config_name}' deletada para usuário {user_id}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Erro ao deletar configuração do usuário {user_id}: {e}")
            return False

    # ================================================================
    # MÉTODOS DE GESTÃO DE ASSINATURA (absorvido do SubscriptionService)
    # ================================================================

    def subscribe_user(
        self,
        chat_id: str,
        chat_type: str,
        username: str = None,
        first_name: str = None,
        last_name: str = None,
        symbols: List[str] = None,
        timeframes: List[str] = None,
        config_name: str = "default",
    ) -> Optional[UserMonitoringConfig]:
        """
        Cadastrar novo usuário ou atualizar existente
        Combina subscription + configuração em uma única operação
        """
        try:
            user_id = int(chat_id)
            db = next(get_db())

            # Verificar se usuário já existe
            existing = (
                db.query(UserMonitoringConfig)
                .filter(UserMonitoringConfig.chat_id == str(chat_id))
                .first()
            )

            if existing:
                # Atualizar informações do usuário existente
                existing.chat_type = chat_type
                existing.username = username
                existing.first_name = first_name
                existing.last_name = last_name
                existing.active = True
                existing.last_activity = datetime.now(timezone.utc)

                db.commit()
                db.refresh(existing)

                self.logger.info(f"Usuário atualizado: {chat_id} ({chat_type})")
                return existing

            # Criar novo usuário com configuração padrão
            symbols = symbols or ["BTC", "ETH"]
            timeframes = timeframes or ["15m", "1h"]

            config = UserMonitoringConfig(
                user_id=user_id,
                chat_id=str(chat_id),
                chat_type=chat_type,
                username=username,
                first_name=first_name,
                last_name=last_name,
                user_username=username,  # Compatibilidade
                config_name=config_name,
                description="Configuração padrão criada automaticamente",
                symbols=symbols,
                timeframes=timeframes,
                indicators_config=self._get_default_indicators_config(),
                filter_config=self._get_default_filter_config(),
                active=True,
            )

            db.add(config)
            db.commit()
            db.refresh(config)

            self.logger.info(f"Novo usuário cadastrado: {chat_id} ({chat_type})")
            return config

        except Exception as e:
            self.logger.error(f"Erro ao cadastrar usuário {chat_id}: {e}")
            return None

    def unsubscribe_user(self, chat_id: str) -> bool:
        """Desativar assinatura de um usuário"""
        try:
            db = next(get_db())

            config = (
                db.query(UserMonitoringConfig)
                .filter(UserMonitoringConfig.chat_id == str(chat_id))
                .first()
            )

            if not config:
                self.logger.warning(f"Usuário {chat_id} não encontrado para desativar")
                return False

            config.active = False
            config.last_activity = datetime.now(timezone.utc)

            db.commit()

            self.logger.info(f"Usuário desativado: {chat_id}")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao desativar usuário {chat_id}: {e}")
            return False

    def get_active_subscribers(
        self, chat_type: str = None
    ) -> List[UserMonitoringConfig]:
        """Obter lista de assinantes ativos"""
        try:
            db = next(get_db())

            query = db.query(UserMonitoringConfig).filter(
                UserMonitoringConfig.active == True
            )

            if chat_type:
                query = query.filter(UserMonitoringConfig.chat_type == chat_type)

            subscribers = query.all()

            return subscribers

        except Exception as e:
            self.logger.error(f"Erro ao buscar assinantes ativos: {e}")
            return []

    def get_subscriber(self, chat_id: str) -> Optional[UserMonitoringConfig]:
        """Obter informações de um assinante específico"""
        try:
            db = next(get_db())

            config = (
                db.query(UserMonitoringConfig)
                .filter(UserMonitoringConfig.chat_id == str(chat_id))
                .first()
            )

            return config

        except Exception as e:
            self.logger.error(f"Erro ao buscar assinante {chat_id}: {e}")
            return None

    def update_last_activity(self, chat_id: str) -> bool:
        """Atualizar última atividade do usuário"""
        try:
            db = next(get_db())

            config = (
                db.query(UserMonitoringConfig)
                .filter(UserMonitoringConfig.chat_id == str(chat_id))
                .first()
            )

            if not config:
                return False

            config.last_activity = datetime.now(timezone.utc)
            db.commit()

            return True

        except Exception as e:
            self.logger.error(f"Erro ao atualizar atividade do usuário {chat_id}: {e}")
            return False

    def increment_signals_received(self, chat_id: str) -> bool:
        """Incrementar contador de sinais recebidos"""
        try:
            db = next(get_db())

            config = (
                db.query(UserMonitoringConfig)
                .filter(UserMonitoringConfig.chat_id == str(chat_id))
                .first()
            )

            if not config:
                return False

            config.signals_received += 1
            config.last_signal_at = datetime.now(timezone.utc)
            db.commit()

            return True

        except Exception as e:
            self.logger.error(
                f"Erro ao incrementar contador de sinais para {chat_id}: {e}"
            )
            return False

    def get_subscription_stats(self) -> Dict[str, Any]:
        """Obter estatísticas gerais de assinantes"""
        try:
            db = next(get_db())

            total_subscribers = db.query(UserMonitoringConfig).count()
            active_subscribers = (
                db.query(UserMonitoringConfig)
                .filter(UserMonitoringConfig.active == True)
                .count()
            )

            # Estatísticas por tipo de chat
            private_chats = (
                db.query(UserMonitoringConfig)
                .filter(
                    and_(
                        UserMonitoringConfig.active == True,
                        UserMonitoringConfig.chat_type == "private",
                    )
                )
                .count()
            )

            groups = (
                db.query(UserMonitoringConfig)
                .filter(
                    and_(
                        UserMonitoringConfig.active == True,
                        UserMonitoringConfig.chat_type.in_(["group", "supergroup"]),
                    )
                )
                .count()
            )

            # Total de sinais enviados
            total_signals_sent = (
                db.query(UserMonitoringConfig)
                .with_entities(func.sum(UserMonitoringConfig.signals_received))
                .scalar()
                or 0
            )

            return {
                "total_subscribers": total_subscribers,
                "active_subscribers": active_subscribers,
                "private_chats": private_chats,
                "groups": groups,
                "total_signals_sent": total_signals_sent,
            }

        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas de assinantes: {e}")
            return {}

    def get_user_subscription_info(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Obter informações de assinatura formatadas para exibir no bot"""
        try:
            config = self.get_subscriber(chat_id)

            if not config:
                return None

            return {
                "chat_id": config.chat_id,
                "chat_type": config.chat_type,
                "username": config.username,
                "first_name": config.first_name,
                "active": config.active,
                "signals_received": config.signals_received,
                "last_signal_at": config.last_signal_at,
                "created_at": config.created_at,
                "last_activity": config.last_activity,
            }

        except Exception as e:
            self.logger.error(
                f"Erro ao obter informações de assinatura para {chat_id}: {e}"
            )
            return None

    def cleanup_inactive_subscribers(self, days_inactive: int = 30) -> int:
        """Limpar assinantes inativos há mais de X dias"""
        try:
            db = next(get_db())

            cutoff_date = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            ) - timezone.timedelta(days=days_inactive)

            inactive_configs = (
                db.query(UserMonitoringConfig)
                .filter(
                    and_(
                        UserMonitoringConfig.active == True,
                        UserMonitoringConfig.last_activity < cutoff_date,
                    )
                )
                .all()
            )

            count = 0
            for config in inactive_configs:
                config.active = False
                count += 1

            db.commit()

            self.logger.info(
                f"Limpeza concluída: {count} assinantes inativos desativados"
            )
            return count

        except Exception as e:
            self.logger.error(f"Erro na limpeza de assinantes inativos: {e}")
            return 0


# Instância global do serviço
user_config_service = UserConfigService()
