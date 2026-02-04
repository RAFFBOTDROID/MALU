import os
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")  # ID do grupo para mensagens automáticas
BOT_NAME = "Malu"

RESPONSES = [
    "Oi! Como você está?",
    "Interessante...",
    "Hmm, me conta mais!",
    "😂 Isso é engraçado!",
    "Entendi!",
    "Sério? Conta mais sobre isso!",
    "😏 Interessante...",
    "Que legal!"
]

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🤖 {BOT_NAME} iniciado com IA humanizada!")

# Ignorar mensagens citadas
def is_not_reply(update: Update):
    return update.message and update.message.reply_to_message is None

# Responder mensagens do grupo
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_not_reply(update):
        return  # ignora mensagens citadas
    response = random.choice(RESPONSES)
    await update.message.reply_text(response)

# Mensagens automáticas
async def auto_messages_job(context: ContextTypes.DEFAULT_TYPE):
    if GROUP_ID:
        response = random.choice(RESPONSES)
        await context.bot.send_message(chat_id=int(GROUP_ID), text=response)

# Função principal
def main():
    # Criar aplicação
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUP, handle_message))

    # JobQueue integrado ao Application
    if GROUP_ID:
        interval = random.randint(300, 600)  # 5-10 minutos
        app.job_queue.run_repeating(auto_messages_job, interval=interval, first=10)

    print(f"INFO:BOT:🤖 {BOT_NAME} iniciado com IA humanizada!")
    
    # Rodar polling sem asyncio.run (evita conflito de loop)
    app.run_polling()

if __name__ == "__main__":
    main()
