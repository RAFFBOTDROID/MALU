import os
import asyncio
import random
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ================= CONFIGURAÇÃO =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise RuntimeError("⚠️ BOT_TOKEN ou OPENAI_API_KEY não encontrado nos secrets!")

# Simulando respostas IA (substitua pela sua chamada OpenAI)
async def get_ai_response(message: str) -> str:
    # Aqui você faria:
    # response = openai.ChatCompletion.create(...)
    # return response["choices"][0]["message"]["content"]
    respostas = [
        "Oi! Como posso ajudar você hoje?",
        "Interessante, me conte mais!",
        "Estou pensando sobre isso...",
        "Hmmm, não tinha pensado assim antes!"
    ]
    await asyncio.sleep(1)
    return random.choice(respostas)

# ================= COMANDOS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Olá! Eu sou a Malu, seu bot com IA humanizada!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Use qualquer mensagem para conversar comigo!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response = await get_ai_response(user_message)
    await update.message.reply_text(response)

# ================= MENSAGENS AUTOMÁTICAS =================
async def auto_message(app: Application):
    while True:
        await asyncio.sleep(random.randint(300, 600))  # 5 a 10 minutos
        chat_id = os.getenv("CHAT_ID")  # coloque o ID do grupo ou chat
        if chat_id:
            await app.bot.send_message(chat_id, "💬 Olá pessoal! Vamos conversar?")

# ================= FUNÇÃO PRINCIPAL =================
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Mensagens automáticas
    asyncio.create_task(auto_message(app))

    # Start polling (não fecha o loop)
    await app.run_polling(close_loop=False)

# ================= EXECUÇÃO =================
if __name__ == "__main__":
    # Evita erro de "event loop already running"
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "already running" in str(e):
            loop = asyncio.get_event_loop()
            loop.create_task(main())
            loop.run_forever()
        else:
            raise
