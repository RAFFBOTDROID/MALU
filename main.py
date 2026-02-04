import os
import logging
import random
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai

# Configuração
TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")
GROUP_ID = os.getenv("GROUP_ID")  # chat_id do grupo para mensagens automáticas

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# IA Humanizada
async def chat_with_ia(user_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_text}],
            api_key=OPENAI_KEY
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Erro na IA: {e}")
        return "Ops, algo deu errado 😅"

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Eu sou a Malu, seu bot humanizado 😎")

# Resposta a mensagens
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ignorar mensagens citadas
    if update.message.reply_to_message:
        return

    user_text = update.message.text
    reply = await chat_with_ia(user_text)
    await update.message.reply_text(reply)

# Mensagens automáticas
async def auto_message_job(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=GROUP_ID, text=random.choice([
        "Oi pessoal! 😎",
        "Como estão todos hoje?",
        "Lembre-se de se divertir 😏"
    ]))

# Main
async def main():
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # JobQueue para mensagens automáticas
    job_queue = app.job_queue
    job_queue.run_repeating(auto_message_job, interval=600, first=10)  # a cada 10 min

    # Rodar bot
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
