import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Certifique-se de adicionar no Render
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Se usar IA

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise RuntimeError("⚠️ BOT_TOKEN ou OPENAI_API_KEY não encontrado nos secrets!")

# =====================
# COMANDOS BÁSICOS
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Olá! Malu iniciada com IA humanizada!")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong!")

# =====================
# MENSAGEM AUTOMÁTICA
# =====================
async def auto_message(app):
    while True:
        try:
            # Exemplo: envia mensagem a cada 1 hora
            # Substitua chat_id pelo chat real
            chat_id = os.getenv("ADMIN_CHAT_ID")
            if chat_id:
                await app.bot.send_message(chat_id=int(chat_id), text="⏰ Hora de jogar!")
        except Exception as e:
            print("Erro auto_message:", e)
        await asyncio.sleep(3600)  # 1 hora

# =====================
# FUNÇÃO PRINCIPAL
# =====================
async def main():
    # Cria a aplicação do Telegram
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Adiciona handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))

    # Inicia a tarefa de mensagem automática sem conflitos
    asyncio.create_task(auto_message(app))

    # Executa o bot em polling (Render permite apenas 1 instância)
    await app.run_polling(close_loop=False)

# =====================
# EXECUÇÃO SEGURA
# =====================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        print("⚠️ RuntimeError ignorada:", e)
