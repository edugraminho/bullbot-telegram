"""
Mensagens de texto para o bot Telegram - BullBot Telegram
Centraliza todas as mensagens para facilitar manutenção e traduções
"""

# Mensagens de boas-vindas e cadastro
WELCOME_NEW_USER = """🎉 <b>Bem-vindo ao BullBot Signals!</b>

✅ <b>Cadastro realizado com sucesso!</b>
🔧 <b>Configuração padrão criada:</b>
• 🪙 Símbolos: BTC, ETH
• ⏰ Timeframes: 15m, 1h
• 📈 RSI: 20-80 (padrão do sistema)

<b>📋 Próximos passos OBRIGATÓRIOS:</b>
1. <b>Configure seus símbolos:</b> /symbols BTC,ETH,SOL
2. <b>Configure timeframes:</b> /timeframes 15m,1h,4h

<b>⚡ Comandos disponíveis:</b>
/symbols - Definir símbolos para monitorar (OBRIGATÓRIO)
/timeframes - Definir timeframes (OBRIGATÓRIO)
/rsi - Configurar RSI (opcional)
/settings - Ver configuração atual
/help - Lista completa de comandos

<b>🔔 Funcionamento:</b>
Você receberá sinais automaticamente quando detectados:
• 🟢 RSI ≤ 20 (oportunidades de COMPRA)
• 🔴 RSI ≥ 80 (oportunidades de VENDA)

<i>⚠️ Configure seus símbolos e timeframes antes de receber sinais!</i>"""

WELCOME_RETURNING_USER = """🎉 <b>Bem-vindo de volta!</b>

✅ <b>Sua configuração atual:</b>
• 🪙 Símbolos: {symbols}
• ⏰ Timeframes: {timeframes}
• 📈 RSI: {rsi_oversold}-{rsi_overbought}

<b>⚡ Comandos disponíveis:</b>
/symbols - Alterar símbolos
/timeframes - Alterar timeframes  
/rsi - Configurar RSI
/settings - Ver configuração completa
/help - Lista de comandos

<i>✅ Você já está configurado e receberá sinais automaticamente!</i>"""

ERROR_CREATE_CONFIG = """❌ Erro ao criar configuração padrão.

Use os comandos para configurar manualmente:
/symbols BTC,ETH - Definir símbolos
/timeframes 15m,1h - Definir timeframes"""

# Mensagens de status
STATUS_MESSAGE = """📊 <b>Status do BullBot Signals</b>

✅ <b>Sistema:</b> Ativo e funcionando
🤖 <b>Bot:</b> Online e monitorando
📡 <b>Monitoramento:</b> Ativo 24/7

🔔 <b>Seu Chat ID:</b> <code>{chat_id}</code>
📱 <b>Tipo:</b> {chat_type}

<i>O bot está funcionando e enviará sinais automaticamente quando detectados.</i>"""

# Mensagens de ajuda
HELP_MESSAGE = """📚 <b>Comandos do BullBot Signals</b>

<b>🚀 Comandos principais:</b>
/start - Criar conta e configuração inicial
/settings - Ver sua configuração atual
/help - Esta mensagem de ajuda

<b>⚙️ Configuração (OBRIGATÓRIOS):</b>
/symbols BTC,ETH,SOL - Definir símbolos para monitorar
/timeframes 15m,1h,4h - Definir timeframes de análise

<b>🔧 Configuração (OPCIONAIS):</b>
/rsi 20,80 - Configurar níveis de RSI (padrão: 20-80)

<b>🔔 Tipos de sinais:</b>
• 🟢 COMPRA: RSI ≤ 20 (sobrevenda)
• 🔴 VENDA: RSI ≥ 80 (sobrecompra)
• 💪 Força: STRONG, MODERATE, WEAK

<b>✅ Suporte:</b>
• Múltiplas exchanges
• Análise em tempo real 24/7
• Filtros anti-spam automáticos

<i>💡 Configure apenas símbolos e timeframes. O resto é automático!</i>"""

# Mensagens de ajuda para comandos específicos
SYMBOLS_HELP = """<b>💡 Como usar o comando /symbols</b>

<b>Formato:</b> /symbols BTC,ETH,SOL,ADA

<b>📋 Instruções:</b>
• Liste os símbolos separados por vírgula
• Use apenas o nome da moeda (ex: BTC, não BTCUSDT)
• Máximo 20 caracteres por símbolo
• Este campo é OBRIGATÓRIO para receber sinais

<b>✅ Exemplo correto:</b>
/symbols BTC,ETH,SOL,ADA,AVAX

<b>❌ Exemplo incorreto:</b>
/symbols BTCUSDT,ETHUSDT (não use pares)

<i>💡 Dica: Comece com poucos símbolos para testar</i>"""

TIMEFRAMES_HELP = """<b>💡 Como usar o comando /timeframes</b>

<b>Formato:</b> /timeframes 15m,1h,4h

<b>📋 Timeframes válidos:</b>
• <b>15m</b> - 15 minutos (scalping)
• <b>1h</b> - 1 hora (intraday)
• <b>4h</b> - 4 horas (swing)
• <b>1d</b> - 1 dia (posição)

<b>✅ Exemplo correto:</b>
/timeframes 15m,1h,4h

<b>❌ Exemplo incorreto:</b>
/timeframes 5m,30m (timeframes não suportados)

<i>💡 Dica: Combine timeframes para análise multi-temporal</i>"""

RSI_HELP = """<b>💡 Como usar o comando /rsi</b>

<b>Formato:</b> /rsi 20,80

<b>📋 Parâmetros:</b>
• <b>Primeiro número:</b> Nível de sobrevenda (recomendado: 15-30)
• <b>Segundo número:</b> Nível de sobrecompra (recomendado: 70-85)

<b>✅ Exemplos:</b>
/rsi 20,80 - Configuração padrão (balanceada)
/rsi 15,85 - Configuração conservadora (menos sinais)
/rsi 25,75 - Configuração agressiva (mais sinais)

<b>📊 Como funciona:</b>
• 🟢 <b>Sinal de COMPRA:</b> quando RSI ≤ sobrevenda
• 🔴 <b>Sinal de VENDA:</b> quando RSI ≥ sobrecompra

<b>💡 Valores padrão do sistema:</b>
• Sobrevenda: 20
• Sobrecompra: 80

<i>🔧 Este comando é OPCIONAL. Se não usar, valores padrão serão aplicados.</i>"""

# Mensagens de resposta para comandos
SYMBOLS_SUCCESS = """✅ <b>Símbolos atualizados com sucesso!</b>

🪙 <b>Seus símbolos:</b> {symbols}
📊 <b>Total:</b> {count} símbolos

<b>🔔 Próximo passo:</b>
Configure seus timeframes: /timeframes 15m,1h,4h

<i>✅ Agora você receberá sinais destes símbolos!</i>"""

SYMBOLS_ERROR = """❌ <b>Erro ao atualizar símbolos</b>

Possíveis causas:
• Você não tem configuração criada (use /start primeiro)
• Símbolos inválidos fornecidos
• Erro interno do sistema

💡 <b>Solução:</b> Use /start primeiro, depois tente novamente"""

TIMEFRAMES_SUCCESS = """✅ <b>Timeframes atualizados com sucesso!</b>

⏰ <b>Seus timeframes:</b> {timeframes}
📊 <b>Total:</b> {count} timeframes

<b>✅ Configuração básica completa!</b>
Agora você receberá sinais dos símbolos e timeframes configurados.

<b>🔧 Comandos opcionais:</b>
/rsi 20,80 - Ajustar níveis de RSI
/settings - Ver configuração completa"""

TIMEFRAMES_ERROR = """❌ <b>Erro ao atualizar timeframes</b>

Possíveis causas:
• Timeframes inválidos (use: 15m, 1h, 4h, 1d)
• Você não tem configuração criada (use /start primeiro)
• Erro interno do sistema

💡 <b>Solução:</b> Verifique os timeframes e tente novamente"""

RSI_SUCCESS = """✅ <b>RSI configurado com sucesso!</b>

📈 <b>Seus níveis de RSI:</b>
• 🟢 Sobrevenda: ≤ {oversold} (sinais de COMPRA)
• 🔴 Sobrecompra: ≥ {overbought} (sinais de VENDA)

<b>📊 Interpretação:</b>
• RSI entre {oversold} e {overbought}: sem sinal
• RSI ≤ {oversold}: oportunidade de compra
• RSI ≥ {overbought}: oportunidade de venda

<b>✅ Configuração completa!</b>
Agora você receberá sinais baseados nos seus parâmetros personalizados.

<i>💡 Use /settings para ver todas as suas configurações</i>"""

RSI_ERROR = """❌ <b>Erro ao configurar RSI</b>

Possíveis causas:
• Você não tem configuração criada (use /start primeiro)
• Valores inválidos fornecidos
• Erro interno do sistema

💡 <b>Solução:</b> Use /start primeiro, depois tente novamente"""

# Mensagens de configuração
SETTINGS_NO_CONFIG = """❌ <b>Nenhuma configuração encontrada</b>

Use /start para criar sua configuração inicial"""

SETTINGS_CONFIG = """⚙️ <b>Sua Configuração Atual</b>

<b>👤 Usuário:</b>
• 📱 Chat ID: <code>{chat_id}</code>
• ✅ Status: {status}
• 📊 Sinais recebidos: {signals_received}

<b>🪙 Símbolos ({symbols_count}):</b>
{symbols}

<b>⏰ Timeframes ({timeframes_count}):</b>
{timeframes}

<b>📈 Indicadores RSI:</b>
• Sobrevenda: ≤ {rsi_oversold}
• Sobrecompra: ≥ {rsi_overbought}

<b>🛡️ Filtros Anti-Spam:</b>
• Max sinais/dia: {max_signals_per_day}
• Cooldown ativo: {cooldown_active}

<b>🔧 Para alterar:</b>
/symbols - Alterar símbolos
/timeframes - Alterar timeframes
/rsi - Configurar RSI

<i>📅 Última atualização: {updated_at}</i>"""

# Mensagens de erro e validação
ERROR_START = "❌ Erro ao cadastrar usuário. Tente novamente."
ERROR_STATUS = "❌ Erro ao obter status. Tente novamente mais tarde."
ERROR_HELP = "❌ Erro ao mostrar ajuda. Tente novamente mais tarde."
ERROR_SYMBOLS = "❌ Erro ao processar símbolos. Tente novamente mais tarde."
ERROR_TIMEFRAMES = "❌ Erro ao processar timeframes. Tente novamente mais tarde."
ERROR_SETTINGS = "❌ Erro ao obter configurações. Tente novamente mais tarde."
ERROR_RSI = "❌ Erro ao processar configuração de RSI. Tente novamente mais tarde."
ERROR_INTERNAL = "❌ Erro interno. Tente novamente mais tarde."

# Mensagens de validação
NO_SYMBOLS_PROVIDED = "❌ Nenhum símbolo válido fornecido. Use: /symbols BTC,ETH"
NO_TIMEFRAMES_PROVIDED = "❌ Nenhum timeframe válido fornecido. Use: /timeframes 15m,1h"
INVALID_RSI_FORMAT = "❌ Formato inválido. Use: /rsi 20,80"
INVALID_RSI_VALUES = "❌ Valores devem ser números inteiros. Use: /rsi 20,80"
INVALID_OVERSOLD_RANGE = "❌ Sobrevenda deve estar entre 0 e 50"
INVALID_OVERBOUGHT_RANGE = "❌ Sobrecompra deve estar entre 50 e 100"
INVALID_RSI_RANGE = "❌ Sobrevenda deve ser menor que sobrecompra"

# Mensagens de comandos desconhecidos
UNKNOWN_COMMAND = """❓ <b>Comando não reconhecido</b>

Use um dos comandos disponíveis:
/start - Iniciar o bot
/status - Ver status
/help - Ver ajuda

<i>O bot funciona automaticamente e enviará sinais quando detectados.</i>"""
