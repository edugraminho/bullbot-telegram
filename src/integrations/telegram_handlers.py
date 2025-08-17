"""
Handlers para comandos do bot Telegram - BullBot Telegram
Sistema completo de gestão de assinantes e configurações personalizadas
"""

import asyncio
from typing import Optional
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode
from src.utils.config import settings
from src.utils.logger import get_logger
from src.services.user_config_service import user_config_service
from src.integrations.telegram_messages import *

logger = get_logger(__name__)


class TelegramBot:
    """Bot do Telegram simplificado para envio de sinais"""

    def __init__(self, token: str):
        self.token = token
        self.application = None
        self.bot = Bot(token=token)

    async def start_handler(self, update: Update, context):
        """Handler para comando /start - Cadastra usuário e cria configuração padrão"""
        try:
            chat_id = str(update.effective_chat.id)
            chat_type = update.effective_chat.type
            user = update.effective_user

            logger.info(
                f"Comando /start recebido do chat {chat_id} (tipo: {chat_type})"
            )

            # Cadastrar assinante
            subscription = user_config_service.subscribe_user(
                chat_id=chat_id,
                chat_type=chat_type,
                username=user.username if user else None,
                first_name=user.first_name if user else None,
                last_name=user.last_name if user else None,
            )

            if not subscription:
                await update.message.reply_text(ERROR_START)
                return

            # Verificar se já tem configuração
            existing_configs = user_config_service.get_user_configs(int(chat_id))

            if not existing_configs:
                # Criar configuração padrão se não existir
                config = user_config_service.create_user_config(
                    user_id=int(chat_id),
                    symbols=["BTC", "ETH"],  # Símbolos padrão
                    timeframes=["15m", "1h"],  # Timeframes padrão
                    user_username=user.username if user else None,
                    config_name="default",
                    description="Configuração padrão criada automaticamente",
                )

                if config:
                    welcome_text = WELCOME_NEW_USER
                else:
                    welcome_text = ERROR_CREATE_CONFIG
            else:
                # Usuário já existe
                config = existing_configs[0]
                welcome_text = WELCOME_RETURNING_USER.format(
                    symbols=", ".join(config.symbols),
                    timeframes=", ".join(config.timeframes),
                    rsi_oversold=config.indicators_config.get("RSI", {}).get(
                        "oversold", 20
                    ),
                    rsi_overbought=config.indicators_config.get("RSI", {}).get(
                        "overbought", 80
                    ),
                )

            await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML)

        except Exception as e:
            logger.error(f"❌ Erro no comando /start: {e}")
            await update.message.reply_text(ERROR_INTERNAL)

    async def status_handler(self, update: Update, context):
        """Handler para comando /status"""
        try:
            chat_id = str(update.effective_chat.id)
            logger.info(f"Comando /status solicitado pelo chat {chat_id}")

            # Status simplificado do sistema
            status_text = STATUS_MESSAGE.format(
                chat_id=chat_id, chat_type=update.effective_chat.type
            )

            await update.message.reply_text(status_text, parse_mode=ParseMode.HTML)

        except Exception as e:
            logger.error(f"❌ Erro no comando /status: {e}")
            await update.message.reply_text(ERROR_STATUS)

    async def help_handler(self, update: Update, context):
        """Handler para comando /help"""
        try:
            chat_id = str(update.effective_chat.id)
            logger.info(f"Comando /help solicitado pelo chat {chat_id}")

            help_text = HELP_MESSAGE

            await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)

        except Exception as e:
            logger.error(f"❌ Erro no comando /help: {e}")
            await update.message.reply_text(ERROR_HELP)

    async def symbols_handler(self, update: Update, context):
        """Handler para comando /symbols - Configurar símbolos (OBRIGATÓRIO)"""
        try:
            chat_id = str(update.effective_chat.id)
            logger.info(f"Comando /symbols solicitado pelo chat {chat_id}")

            # Atualizar atividade do usuário
            user_config_service.update_last_activity(chat_id)

            if not context.args:
                help_text = SYMBOLS_HELP

                await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)
                return

            # Processar símbolos
            symbols_input = " ".join(context.args)
            symbols = [s.strip().upper() for s in symbols_input.split(",")]

            # Remover strings vazias
            symbols = [s for s in symbols if s]

            if not symbols:
                await update.message.reply_text(NO_SYMBOLS_PROVIDED)
                return

            # Atualizar símbolos
            success = user_config_service.update_user_symbols(
                user_id=int(chat_id), symbols=symbols
            )

            if success:
                symbols_text = ", ".join(symbols)
                response_text = SYMBOLS_SUCCESS.format(
                    symbols=symbols_text, count=len(symbols)
                )
            else:
                response_text = SYMBOLS_ERROR

            await update.message.reply_text(response_text, parse_mode=ParseMode.HTML)

        except Exception as e:
            logger.error(f"❌ Erro no comando /symbols: {e}")
            await update.message.reply_text(ERROR_SYMBOLS)

    async def timeframes_handler(self, update: Update, context):
        """Handler para comando /timeframes - Configurar timeframes (OBRIGATÓRIO)"""
        try:
            chat_id = str(update.effective_chat.id)
            logger.info(f"Comando /timeframes solicitado pelo chat {chat_id}")

            # Atualizar atividade do usuário
            user_config_service.update_last_activity(chat_id)

            if not context.args:
                help_text = TIMEFRAMES_HELP

                await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)
                return

            # Processar timeframes
            timeframes_input = " ".join(context.args)
            timeframes = [tf.strip().lower() for tf in timeframes_input.split(",")]

            # Remover strings vazias
            timeframes = [tf for tf in timeframes if tf]

            if not timeframes:
                await update.message.reply_text(NO_TIMEFRAMES_PROVIDED)
                return

            # Atualizar timeframes
            success = user_config_service.update_user_timeframes(
                user_id=int(chat_id), timeframes=timeframes
            )

            if success:
                timeframes_text = ", ".join(timeframes)
                response_text = TIMEFRAMES_SUCCESS.format(
                    timeframes=timeframes_text, count=len(timeframes)
                )
            else:
                response_text = TIMEFRAMES_ERROR

            await update.message.reply_text(response_text, parse_mode=ParseMode.HTML)

        except Exception as e:
            logger.error(f"❌ Erro no comando /timeframes: {e}")
            await update.message.reply_text(ERROR_TIMEFRAMES)

    async def settings_handler(self, update: Update, context):
        """Handler para comando /settings - Ver configuração atual"""
        try:
            chat_id = str(update.effective_chat.id)
            logger.info(f"Comando /settings solicitado pelo chat {chat_id}")

            # Atualizar atividade do usuário
            user_config_service.update_last_activity(chat_id)

            # Obter configuração do usuário
            config_summary = user_config_service.get_user_config_summary(int(chat_id))

            if not config_summary:
                response_text = SETTINGS_NO_CONFIG
                await update.message.reply_text(
                    response_text, parse_mode=ParseMode.HTML
                )
                return

            # Obter informações da assinatura
            subscription_info = user_config_service.get_user_subscription_info(chat_id)

            # Montar texto da configuração
            symbols_text = ", ".join(config_summary["symbols"])
            timeframes_text = ", ".join(config_summary["timeframes"])

            cooldown_info = config_summary.get("cooldown_minutes", {})

            settings_text = SETTINGS_CONFIG.format(
                chat_id=chat_id,
                status="Ativo"
                if subscription_info and subscription_info["active"]
                else "Inativo",
                signals_received=subscription_info["signals_received"]
                if subscription_info
                else 0,
                symbols_count=len(config_summary["symbols"]),
                symbols=symbols_text,
                timeframes_count=len(config_summary["timeframes"]),
                timeframes=timeframes_text,
                rsi_oversold=config_summary["rsi_oversold"],
                rsi_overbought=config_summary["rsi_overbought"],
                max_signals_per_day=config_summary["max_signals_per_day"],
                cooldown_active="Sim" if cooldown_info else "Padrão do sistema",
                updated_at=config_summary["updated_at"].strftime("%d/%m/%Y %H:%M"),
            )

            await update.message.reply_text(settings_text, parse_mode=ParseMode.HTML)

        except Exception as e:
            logger.error(f"❌ Erro no comando /settings: {e}")
            await update.message.reply_text(ERROR_SETTINGS)

    async def rsi_handler(self, update: Update, context):
        """Handler para comando /rsi - Configurar RSI (OPCIONAL)"""
        try:
            chat_id = str(update.effective_chat.id)
            logger.info(f"Comando /rsi solicitado pelo chat {chat_id}")

            # Atualizar atividade do usuário
            user_config_service.update_last_activity(chat_id)

            if not context.args:
                help_text = RSI_HELP

                await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)
                return

            # Processar parâmetros RSI
            rsi_input = " ".join(context.args)

            try:
                if "," in rsi_input:
                    oversold_str, overbought_str = rsi_input.split(",", 1)
                    oversold = int(oversold_str.strip())
                    overbought = int(overbought_str.strip())
                else:
                    await update.message.reply_text(INVALID_RSI_FORMAT)
                    return

            except ValueError:
                await update.message.reply_text(INVALID_RSI_VALUES)
                return

            # Validações
            if oversold < 0 or oversold > 50:
                await update.message.reply_text(INVALID_OVERSOLD_RANGE)
                return

            if overbought < 50 or overbought > 100:
                await update.message.reply_text(INVALID_OVERBOUGHT_RANGE)
                return

            if oversold >= overbought:
                await update.message.reply_text(INVALID_RSI_RANGE)
                return

            # Atualizar configuração RSI
            success = user_config_service.update_user_rsi_config(
                user_id=int(chat_id), oversold=oversold, overbought=overbought
            )

            if success:
                response_text = RSI_SUCCESS.format(
                    oversold=oversold, overbought=overbought
                )
            else:
                response_text = RSI_ERROR

            await update.message.reply_text(response_text, parse_mode=ParseMode.HTML)

        except Exception as e:
            logger.error(f"❌ Erro no comando /rsi: {e}")
            await update.message.reply_text(ERROR_RSI)

    async def unknown_handler(self, update: Update, context):
        """Handler para comandos desconhecidos"""
        try:
            chat_id = str(update.effective_chat.id)
            logger.info(
                f"Comando desconhecido do chat {chat_id}: {update.message.text}"
            )

            unknown_text = UNKNOWN_COMMAND

            await update.message.reply_text(unknown_text, parse_mode=ParseMode.HTML)

        except Exception as e:
            logger.error(f"❌ Erro no handler de comando desconhecido: {e}")

    def setup_handlers(self):
        """Configurar handlers do bot"""
        try:
            self.application = Application.builder().token(self.token).build()

            # Handlers principais
            self.application.add_handler(CommandHandler("start", self.start_handler))
            self.application.add_handler(CommandHandler("status", self.status_handler))
            self.application.add_handler(CommandHandler("help", self.help_handler))

            # Handlers de configuração (obrigatórios)
            self.application.add_handler(
                CommandHandler("symbols", self.symbols_handler)
            )
            self.application.add_handler(
                CommandHandler("timeframes", self.timeframes_handler)
            )
            self.application.add_handler(
                CommandHandler("settings", self.settings_handler)
            )

            # Handlers de configuração (opcionais)
            self.application.add_handler(CommandHandler("rsi", self.rsi_handler))

            # Handler para mensagens desconhecidas
            self.application.add_handler(
                MessageHandler(filters.COMMAND, self.unknown_handler)
            )

            logger.info("✅ Handlers configurados com sucesso")

        except Exception as e:
            logger.error(f"❌ Erro ao configurar handlers: {e}")

    async def start_polling(self):
        """Iniciar polling do bot"""
        try:
            if not self.application:
                self.setup_handlers()

            logger.info("🚀 Iniciando bot do Telegram...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()

            logger.info("✅ Bot iniciado com sucesso!")

        except Exception as e:
            logger.error(f"❌ Erro ao iniciar bot: {e}")

    async def stop_polling(self):
        """Parar polling do bot"""
        try:
            if self.application:
                await self.application.updater.stop_polling()
                await self.application.stop()
                await self.application.shutdown()
                logger.info("🛑 Bot parado com sucesso")

        except Exception as e:
            logger.error(f"❌ Erro ao parar bot: {e}")


def get_telegram_bot() -> Optional[TelegramBot]:
    """Obter instância do bot Telegram"""
    try:
        token = settings.telegram_bot_token
        if not token:
            logger.error("❌ Token do Telegram não configurado")
            return None

        return TelegramBot(token)

    except Exception as e:
        logger.error(f"❌ Erro ao criar bot: {e}")
        return None


async def run_telegram_bot():
    """Função principal para executar o bot"""
    try:
        bot = get_telegram_bot()
        if not bot:
            logger.error("❌ Não foi possível criar o bot")
            return

        logger.info("🤖 Iniciando BullBot Telegram...")
        await bot.start_polling()

        # Manter o bot rodando
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Interrupção recebida, parando bot...")
            await bot.stop_polling()

    except Exception as e:
        logger.error(f"❌ Erro fatal no bot: {e}")
        raise
