import os
import random
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================= CONFIGURAÇÃO =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHAT_ID = os.getenv("CHAT_ID")  # Grupo ou chat para mensagens automáticas

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise RuntimeError("⚠️ BOT_TOKEN ou OPENAI_API_KEY não encontrado nos secrets!")

# ================= FUNÇÕES =================
async def get_ai_response(message: str) -> str:
    respostas = [
        "Oi! Como posso ajudar você hoje?",
        "Interessante, me conte mais!",
        "Estou pensando sobre isso...",
        "Hmmm, não tinha pensado assim antes!"
    ]
    await asyncio.sleep(1)
    return random.choice(respostas)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Olá! Eu sou a Malu, seu bot com IA humanizada!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use qualquer mensagem para conversar comigo!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response = await get_ai_response(user_message)
    await update.message.reply_text(response)

# ================= MENSAGENS AUTOMÁTICAS =================
async def auto_message(app: Application):
    while True:
        await asyncio.sleep(random.randint(300, 600))  # 5 a 10 minutos
        if CHAT_ID:
            await app.bot.send_message(CHAT_ID, "💬 Olá pessoal! Vamos conversar?")

# ================= EXECUÇÃO DO BOT =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Mensagens automáticas
    asyncio.create_task(auto_message(app))

    # Rodar o bot (polling gerencia o loop internamente)
    app.run_polling()

# ================= START =================
if __name__ == "__main__":
    main()
