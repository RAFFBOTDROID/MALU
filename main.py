import os
import logging
import random
import time
from collections import deque
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from aiohttp import web

# ================= CONFIG =================
TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))
if not TOKEN:
    raise RuntimeError("BOT_TOKEN não definido")

# ================= LOG =================
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("BOT")

# ================= MEMÓRIA DO GRUPO =================
MEMORY_LIMIT = 50
user_history = {}  # {user_id: deque([...])}

# ================= PERSONALIDADE =================
PERSONALITY = [
    "😏 Ah, você disse isso mesmo?",
    "😂 Isso é interessante...",
    "🤔 Hmmm, deixa eu pensar...",
    "😎 Sempre com estilo!",
    "😜 Haha, gostei!"
]

# ================= ANTI-SPAM =================
cooldowns = {}
COOLDOWN_TIME = 5

def can_use(uid):
    now = time.time()
    last = cooldowns.get(uid, 0)
    if now - last < COOLDOWN_TIME:
        return False
    cooldowns[uid] = now
    return True

# ================= COMANDOS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot online! Tenho personalidade própria e interajo no grupo."
    )

# ================= INTERAÇÃO REALISTA =================
async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = message.from_user.id
    text = message.text

    # Ignora mensagens citadas (respostas a outros membros)
    if message.reply_to_message:
        return

    # Ignora mensagens muito rápidas
    if not can_use(user_id):
        return

    # Armazena mensagem do usuário
    history = user_history.setdefault(user_id, deque(maxlen=MEMORY_LIMIT))
    history.append(text)

    # Gera resposta baseada na personalidade + histórico
    if random.random() < 0.7:  # 70% chance de responder
        reply_text = random.choice(PERSONALITY)

        if history:
            last_msg = history[-1]
            reply_text += f" 😏 Você disse: '{last_msg}'"

        await message.reply_text(reply_text)

# ================= SERVIÇO WEB =================
async def handle_root(request):
    return web.Response(text="🤖 Bot ativo!", content_type="text/plain")

async def run_web():
    app = web.Application()
    app.add_routes([web.get("/", handle_root)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    log.info(f"🌐 Porta aberta em {PORT}")

# ================= BOT =================
async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))

    # Remove webhook para evitar conflitos
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
    except:
        pass

    log.info("🤖 Bot Telegram iniciado com polling...")

    # Rodar bot e web server juntos
    await run_web()
    await app.run_polling()

# ================= ENTRYPOINT =================
# No Render, NÃO usar asyncio.run()
import asyncio
loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
