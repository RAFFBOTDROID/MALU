import os
import asyncio
import logging
import random
import time
from collections import deque
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ================= CONFIG =================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN não definido")

# ================= LOG =================
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("BOT")

# ================= MEMÓRIA DO GRUPO =================
# Mantém últimas 50 mensagens por usuário
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
COOLDOWN_TIME = 5  # segundos

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

        # Pequeno toque de contexto usando a última mensagem
        if history:
            last_msg = history[-1]
            reply_text += f" 😏 Você disse: '{last_msg}'"

        await message.reply_text(reply_text)

# ================= FUNÇÃO PRINCIPAL =================
async def run_bot():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))

    # Anti-conflito de polling (render)
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
    except:
        pass

    log.info("🤖 Bot Telegram iniciado com polling...")
    await app.run_polling()

# ================= SERVIÇO WEB PARA MANTER ONLINE =================
from aiohttp import web

async def handle_root(request):
    return web.Response(text="🤖 Bot ativo!", content_type="text/plain")

async def run_web():
    app = web.Application()
    app.add_routes([web.get("/", handle_root)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 10000)))
    await site.start()
    log.info(f"🌐 Porta aberta em {os.getenv('PORT', 10000)}")

# ================= MAIN =================
async def main():
    await asyncio.gather(run_bot(), run_web())

if __name__ == "__main__":
    asyncio.run(main())
