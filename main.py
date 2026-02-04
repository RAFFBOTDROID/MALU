import os
import random
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ================= CONFIGURAÇÃO =================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ BOT_TOKEN não encontrado!")

# Lista de respostas automáticas humanizadas
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

# Personagem do bot
BOT_NAME = "Malu"

# =================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🤖 {BOT_NAME} iniciado com IA humanizada!")

# Função para mensagens automáticas no grupo
async def auto_messages_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    response = random.choice(RESPONSES)
    await context.bot.send_message(chat_id=chat_id, text=response)

# Ignorar mensagens citadas
def is_not_reply(update: Update):
    return update.message and update.message.reply_to_message is None

# Handler de mensagens gerais
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_not_reply(update):
        return  # Ignora mensagens citadas

    # Resposta aleatória humanizada
    response = random.choice(RESPONSES)
    await update.message.reply_text(response)

# =================================================
def main():
    # Criando a aplicação
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUP, handle_message))

    # ================== JobQueue ==================
    # Mensagens automáticas a cada 5-10 minutos
    chat_id = os.getenv("GROUP_ID")  # Coloque o ID do grupo
    if chat_id:
        interval = random.randint(300, 600)
        app.job_queue.run_repeating(auto_messages_job, interval=interval, first=10, chat_id=int(chat_id))

    # Rodar polling (sem asyncio.run para evitar conflito de loop)
    print(f"INFO:BOT:🤖 {BOT_NAME} iniciado com IA humanizada!")
    app.run_polling()

# =================================================
if __name__ == "__main__":
    main()
