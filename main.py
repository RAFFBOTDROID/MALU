import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # Para mensagens automáticas

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise RuntimeError("⚠️ BOT_TOKEN ou OPENAI_API_KEY não encontrado nos secrets!")

# =====================
# COMANDOS
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
            if ADMIN_CHAT_ID:
                await app.bot.send_message(chat_id=int(ADMIN_CHAT_ID), text="⏰ Hora de jogar!")
        except Exception as e:
            print("Erro auto_message:", e)
        await asyncio.sleep(3600)  # 1 hora

# =====================
# FUNÇÃO PRINCIPAL
# =====================
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))

    # Tarefa de mensagem automática
    asyncio.create_task(auto_message(app))

    # Inicia polling
    await app.run_polling(close_loop=False)

# =====================
# EXECUÇÃO SEGURA PARA RENDER
# =====================
if __name__ == "__main__":
    try:
        # Pega loop já existente no Render
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.create_task(main())
    loop.run_forever()
