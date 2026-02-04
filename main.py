import os
import logging
import random
import time
import asyncio
from collections import deque
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from aiohttp import web
import httpx

# ================= CONFIG =================
TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
PORT = int(os.getenv("PORT", 10000))

if not TOKEN:
    raise RuntimeError("BOT_TOKEN não definido")

# ================= LOG =================
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("BOT")

# ================= MEMÓRIA & PERSONALIDADE =================
MEMORY_LIMIT = 100
user_history = {}  # {user_id: deque([...])}
BOT_MEMORY = deque(maxlen=MEMORY_LIMIT)

PERSONALITY = [
    "😏 Interessante...",
    "😂 Haha, isso me fez rir",
    "🤔 Hmmm, deixa eu pensar...",
    "😎 Sempre com estilo!",
    "😜 Haha, gostei!",
    "😉 E aí, como vai?",
    "🥱 Ai que sono...",
    "🙃 Sério isso?",
    "😅 Meio confuso..."
]

TYPOS = ["", ".", "..", "...", "?!", "!"]

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

# ================= CHAMADA IA =================
async def call_ai(prompt):
    if not OPENROUTER_KEY:
        return random.choice(PERSONALITY)

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
            return data["choices"][0]["message"]["content"]
        return random.choice(PERSONALITY)
    except Exception as e:
        log.error(f"ERRO IA: {e}")
        return random.choice(PERSONALITY)

# ================= COMANDOS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot online! Agora com personalidade própria e interações realistas!"
    )

# ================= INTERAÇÃO =================
async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = message.from_user.id
    text = message.text

    # Ignora mensagens citadas (respostas a outros membros)
    if message.reply_to_message:
        return

    if not can_use(user_id):
        return

    # Histórico do usuário
    history = user_history.setdefault(user_id, deque(maxlen=MEMORY_LIMIT))
    history.append(text)

    # Escolhe tipo de resposta
    if random.random() < 0.6:
        # Resposta estilo humano
        reply = random.choice(PERSONALITY)
        if history:
            reply += f" {random.choice(TYPOS)}"
    else:
        # Resposta IA
        reply = await call_ai(text)

    # Adiciona “erros de digitação” ocasionais
    if random.random() < 0.2:
        reply = "".join(c if random.random() > 0.1 else random.choice("abcdefghijklmnopqrstuvwxyz") for c in reply)

    BOT_MEMORY.append(reply)

    # Pausa natural
    await asyncio.sleep(random.uniform(0.5, 2.5))
    await message.reply_text(reply)

# ================= INTERAÇÃO AUTOMÁTICA =================
async def auto_converse(context: ContextTypes.DEFAULT_TYPE):
    app = context.application
    chat_ids = list(user_history.keys())
    if not chat_ids:
        return
    chat_id = random.choice(chat_ids)
    reply = random.choice(PERSONALITY)
    BOT_MEMORY.append(reply)
    try:
        # Pausa antes de enviar
        await asyncio.sleep(random.uniform(1,3))
        await app.bot.send_message(chat_id=chat_id, text=reply)
    except Exception as e:
        log.error(f"Erro enviando mensagem automática: {e}")

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
async def run_bot():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))

    # Loop para conversas automáticas
    async def auto_loop():
        while True:
            await asyncio.sleep(random.randint(60, 180))  # 1 a 3 min
            await auto_converse(app)

    asyncio.create_task(auto_loop())

    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
    except:
        pass

    log.info("🤖 Bot Telegram iniciado com polling...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

# ================= ENTRYPOINT =================
loop = asyncio.get_event_loop()
loop.create_task(run_web())
loop.create_task(run_bot())
loop.run_forever()
