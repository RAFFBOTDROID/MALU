import os
import random
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
import openai

# =======================
# CONFIGURAÇÕES
# =======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHAT_ID = os.getenv("CHAT_ID")  # Id do chat ou grupo para mensagens automáticas

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise RuntimeError("⚠️ BOT_TOKEN ou OPENAI_API_KEY não encontrado nos secrets!")

openai.api_key = OPENAI_API_KEY

# =======================
# HANDLERS
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Olá! Eu sou a Malu, sua IA humanizada!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 Comandos:\n/start - iniciar bot\n/help - ajuda")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text

    # Aqui chamamos a OpenAI para gerar resposta
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_msg}]
    )
    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

# =======================
# MENSAGENS AUTOMÁTICAS
# =======================
async def auto_message(context: ContextTypes.DEFAULT_TYPE):
    if CHAT_ID:
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text="💬 Olá pessoal! Vamos conversar?"
        )

# =======================
# MAIN
# =======================
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Adiciona handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Mensagens automáticas com JobQueue
    app.job_queue.run_repeating(auto_message, interval=random.randint(300, 600), first=15)

    # Inicia o bot
    print("🤖 Malu iniciado com IA humanizada!")
    await app.run_polling()

# =======================
# EXECUÇÃO
# =======================
if __name__ == "__main__":
    asyncio.run(main())
