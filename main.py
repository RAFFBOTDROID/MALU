import os
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise RuntimeError("⚠️ BOT_TOKEN ou OPENAI_API_KEY não encontrado nos secrets!")

openai.api_key = OPENAI_API_KEY

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Olá! Eu sou a Malu!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start - iniciar bot\n/help - ajuda")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_msg}]
    )
    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

async def auto_message(context: ContextTypes.DEFAULT_TYPE):
    if CHAT_ID:
        await context.bot.send_message(chat_id=CHAT_ID, text="💬 Olá pessoal! Vamos conversar?")

# ==========================
# CONFIGURAÇÃO DO BOT
# ==========================
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.job_queue.run_repeating(auto_message, interval=random.randint(300, 600), first=15)

print("🤖 Malu iniciado com IA humanizada!")

# ==========================
# EXECUÇÃO DO BOT
# ==========================
# Render já roda um loop, então NÃO use asyncio.run()
app.run_polling(close_loop=False)
