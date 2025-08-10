"""
Handlers para comandos do bot Telegram - BullBot Telegram
Simplificado para focar apenas em envio de sinais
"""

import asyncio
from typing import Optional
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TelegramBot:
    """Bot do Telegram simplificado para envio de sinais"""

    def __init__(self, token: str):
        self.token = token
        self.application = None
        self.bot = Bot(token=token)

    async def start_handler(self, update: Update, context):
        """Handler para comando /start"""
        try:
            chat_id = str(update.effective_chat.id)
            chat_type = update.effective_chat.type

            logger.info(
                f"Comando /start recebido do chat {chat_id} (tipo: {chat_type})"
            )

            # Mensagem de boas-vindas simplificada
            welcome_text = """
                🎉 <b>Bem-vindo ao BullBot Signals!</b>

                🤖 <b>O que eu faço:</b>
                • Monitoro indicadores RSI de criptomoedas
                • Envio sinais de compra/venda automaticamente
                • Analiso múltiplas exchanges (Binance, Gate.io, MEXC)

                ⚡ <b>Comandos disponíveis:</b>
                /status - Ver status do sistema
                /help - Lista completa de comandos

                🔔 <b>Como funciona:</b>
                Você receberá alertas automáticos quando detectarmos:
                • 🟢 Oportunidades de COMPRA (RSI baixo)
                • 🔴 Oportunidades de VENDA (RSI alto)
                • 📊 Análise detalhada com preços e força do sinal

                <i>⚠️ Lembre-se: Sinais são apenas informativos. Sempre faça sua própria análise!</i>"""

            await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML)

        except Exception as e:
            logger.error(f"❌ Erro no comando /start: {e}")
            await update.message.reply_text(
                "❌ Erro interno. Tente novamente mais tarde."
            )

    async def status_handler(self, update: Update, context):
        """Handler para comando /status"""
        try:
            chat_id = str(update.effective_chat.id)
            logger.info(f"Comando /status solicitado pelo chat {chat_id}")

            # Status simplificado do sistema
            status_text = f"""
                📊 <b>Status do BullBot Signals</b>

                ✅ <b>Sistema:</b> Ativo e funcionando
                🤖 <b>Bot:</b> Online e monitorando
                📡 <b>Monitoramento:</b> Ativo 24/7

                🔔 <b>Seu Chat ID:</b> <code>{chat_id}</code>
                📱 <b>Tipo:</b> {update.effective_chat.type}

                <i>O bot está funcionando e enviará sinais automaticamente quando detectados.</i>"""

            await update.message.reply_text(status_text, parse_mode=ParseMode.HTML)

        except Exception as e:
            logger.error(f"❌ Erro no comando /status: {e}")
            await update.message.reply_text(
                "❌ Erro ao obter status. Tente novamente mais tarde."
            )

    async def help_handler(self, update: Update, context):
        """Handler para comando /help"""
        try:
            chat_id = str(update.effective_chat.id)
            logger.info(f"Comando /help solicitado pelo chat {chat_id}")

            help_text = """
                📚 <b>Comandos do BullBot Signals</b>

                🚀 <b>Comandos principais:</b>
                /start - Iniciar o bot e ver informações
                /status - Verificar status do sistema
                /help - Esta mensagem de ajuda

                📊 <b>Funcionalidades:</b>
                • <b>Monitoramento automático</b> de criptomoedas
                • <b>Detecção de sinais</b> RSI em tempo real
                • <b>Alertas automáticos</b> para oportunidades
                • <b>Análise multi-exchange</b> (Binance, Gate.io, MEXC)

                🔔 <b>Alertas automáticos:</b>
                Você receberá mensagens automaticamente quando:
                • 🟢 RSI < 30 (oportunidade de compra)
                • 🔴 RSI > 70 (oportunidade de venda)
                • 📊 Sinais de alta confiança detectados

                <i>💡 Dica: O bot funciona automaticamente. Apenas aguarde os sinais!</i>"""

            await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)

        except Exception as e:
            logger.error(f"❌ Erro no comando /help: {e}")
            await update.message.reply_text(
                "❌ Erro ao mostrar ajuda. Tente novamente mais tarde."
            )

    async def unknown_handler(self, update: Update, context):
        """Handler para comandos desconhecidos"""
        try:
            chat_id = str(update.effective_chat.id)
            logger.info(
                f"Comando desconhecido do chat {chat_id}: {update.message.text}"
            )

            unknown_text = """
                ❓ <b>Comando não reconhecido</b>

                Use um dos comandos disponíveis:
                /start - Iniciar o bot
                /status - Ver status
                /help - Ver ajuda

                <i>O bot funciona automaticamente e enviará sinais quando detectados.</i>"""

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
