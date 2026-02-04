import os
import random
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai

# Configuração
TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")
GROUP_ID = os.getenv("GROUP_ID")  # chat_id do grupo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# IA humanizada
async def chat_with_ia(text: str):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": text}],
            api_key=OPENAI_KEY
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Erro na IA: {e}")
        return "Ops, algo deu errado 😅"

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Eu sou a Malu, seu bot humanizado 😎")

# Responder mensagens
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ignora mensagens citadas
    if update.message.reply_to_message:
        return

    reply = await chat_with_ia(update.message.text)
    await update.message.reply_text(reply)

# Mensagens automáticas
async def auto_message_job(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=GROUP_ID, text=random.choice([
        "Oi pessoal! 😎",
        "Como estão todos hoje?",
        "Lembre-se de se divertir 😏"
    ]))

# Build do bot
app = Application.builder().token(TOKEN).build()

# Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# JobQueue
app.job_queue.run_repeating(auto_message_job, interval=600, first=10)  # a cada 10 min

# Rodar bot (Render já gerencia o loop)
app.run_polling()
