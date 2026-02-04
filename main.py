import os
import asyncio
import logging
import random
import time
from collections import deque
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from aiohttp import web

# ================= CONFIG =================
TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))

if not TOKEN:
    raise RuntimeError("❌ BOT_TOKEN não definido")

# ================= LOG =================
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("BOT")

# ================= MEMÓRIA DO GRUPO =================
MAX_MEMORY = 20  # mensagens recentes que o bot lembra
group_memory = {}  # chat_id -> deque

# ================= ANTI-SPAM =================
GROUP_COOLDOWNS = {}
GROUP_COOLDOWN_TIME = 5  # segundos entre respostas

def can_use_group(chat_id):
    now = time.time()
    last = GROUP_COOLDOWNS.get(chat_id, 0)
    if now - last < GROUP_COOLDOWN_TIME:
        return False
    GROUP_COOLDOWNS[chat_id] = now
    return True

# ================= PERSONALIDADE =================
PERSONALITY = {
    "name": "Malu",
    "style": "engraçada, curiosa e um pouco sarcástica",
    "responses": [
        "Haha, adorei! 😂",
        "Interessante... 👀",
        "Não sei se concordo 😅",
        "Boa! Continue assim 😎",
        "Hmm, isso é curioso 🤔",
        "Isso me lembra algo engraçado… 😏",
        "Hmm… preciso pensar melhor nisso 😆",
    ],
    "spontaneous": [
        "Alguém mais viu isso? 😜",
        "Hoje tá movimentado aqui hein 😏",
        "Alguém quer contar uma fofoca? 🤭",
    ],
}

async def get_personality_reply(chat_id, msg_text=None, spontaneous=False):
    # lembra das mensagens recentes
    memory = group_memory.setdefault(chat_id, deque(maxlen=MAX_MEMORY))
    if msg_text:
        memory.append(msg_text)

    if spontaneous:
        return random.choice(PERSONALITY["spontaneous"])
    else:
        return random.choice(PERSONALITY["responses"])

# ================= COMANDOS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🤖 Olá! Eu sou {PERSONALITY['name']}!\n"
        f"💬 Minha personalidade é: {PERSONALITY['style']}\n"
        "Eu interajo naturalmente com o grupo, mas não respondo mensagens citadas."
    )

# ================= INTERAÇÃO NO GRUPO =================
async def group_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.is_bot:
        return  # ignora outros bots

    if update.message.reply_to_message:
        return  # não responde mensagens citadas

    chat_id = update.effective_chat.id
    if not can_use_group(chat_id):
        return

    msg_text = update.message.text
    reply = await get_personality_reply(chat_id, msg_text)
    await update.message.reply_text(reply)

# ================= MENSAGENS ESPONTÂNEAS =================
async def spontaneous_messages():
    while True:
        await asyncio.sleep(random.randint(60, 180))  # envia a cada 1-3 minutos
        for chat_id in group_memory.keys():
            if can_use_group(chat_id):
                reply = await get_personality_reply(chat_id, spontaneous=True)
                try:
                    await app.bot.send_message(chat_id=chat_id, text=reply)
                except Exception as e:
                    log.error(f"Erro ao enviar mensagem espontânea: {e}")

# ================= SERVIÇO WEB =================
async def web_root(request):
    return web.Response(text=f"{PERSONALITY['name']} Online ✅", content_type="text/html")

async def run_web():
    web_app = web.Application()
    web_app.router.add_get("/", web_root)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    log.info(f"🌐 Porta aberta em {PORT}")

# ================= RODAR O BOT =================
async def run_bot():
    global app
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, group_chat))
    log.info(f"🤖 {PERSONALITY['name']} iniciado com polling...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await spontaneous_messages()  # inicia mensagens espontâneas

# ================= EXECUÇÃO =================
loop = asyncio.get_event_loop()
loop.create_task(run_bot())
loop.create_task(run_web())
loop.run_forever()
