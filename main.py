import os
import random
import logging
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, JobQueue

TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("BOT")

PERSONAGEM = "Malu"
AUTO_MESSAGES = [
    "Alguém aí quer conversar comigo? 😏",
    "Tô animada hoje! 😎",
    "Quem tá de bom humor? 😁",
    "Tô só observando 👀",
]

cooldowns = {}
COOLDOWN_TIME = 5  # segundos

def can_use(uid):
    import time
    now = time.time()
    last = cooldowns.get(uid, 0)
    if now - last < COOLDOWN_TIME:
        return False
    cooldowns[uid] = now
    return True

async def call_ai_humana(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(url, headers=headers, json=payload)
            data = r.json()

        if "choices" in data:
            resposta = data["choices"][0]["message"]["content"]
            if random.random() < 0.3:
                resposta += " 😏"
            elif random.random() < 0.3:
                resposta += " hehe 😎"
            return resposta
        return "Hmm, não sei o que dizer 🤔"
    except Exception as e:
        log.error(f"ERRO IA: {e}")
        return "Ops, deu uma travada aqui 😅"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🤖 {PERSONAGEM} online! Vou interagir no grupo de forma natural 😎"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:  # ignora mensagens citadas
        return

    uid = update.effective_user.id
    if not can_use(uid):
        return

    msg_text = update.message.text
    reply = await call_ai_humana(msg_text)
    await update.message.reply_text(reply)

async def save_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if "chats" not in context.bot_data:
        context.bot_data["chats"] = set()
    context.bot_data["chats"].add(chat_id)

async def auto_messages_job(context: ContextTypes.DEFAULT_TYPE):
    chats = context.bot_data.get("chats", set())
    if not chats:
        return
    for chat_id in chats:
        msg = random.choice(AUTO_MESSAGES)
        await context.bot.send_message(chat_id=chat_id, text=msg)

# ================= EXECUÇÃO =================
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.ALL, save_chat))

# agenda mensagens automáticas a cada 5-10 minutos
job_queue: JobQueue = app.job_queue
job_queue.run_repeating(auto_messages_job, interval=random.randint(300, 600), first=10)

log.info(f"🤖 {PERSONAGEM} iniciado com IA humanizada!")
app.run_polling()
