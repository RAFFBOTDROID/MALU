import os
import asyncio
import logging
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from aiohttp import web

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
PORT = int(os.getenv("PORT", 10000))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN não encontrado")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("BOT")

# =========================
# IA OPENROUTER
# =========================
async def call_ai(prompt):
    if not OPENROUTER_KEY:
        return "⚠️ IA não configurada"

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "google/gemma-7b-it:free",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 250
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(url, headers=headers, json=payload)
            data = r.json()

        return data["choices"][0]["message"]["content"]
    except:
        return "⚠️ Falha temporária na IA"

# =========================
# ANTI-SPAM
# =========================
cooldowns = {}

def can_use(uid):
    now = asyncio.get_event_loop().time()
    last = cooldowns.get(uid, 0)
    if now - last < 3:
        return False
    cooldowns[uid] = now
    return True

# =========================
# HANDLERS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot online no Render FREE!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if not can_use(uid):
        await update.message.reply_text("⏳ Aguarde alguns segundos...")
        return

    msg = update.message.text
    await update.message.reply_text("🧠 Pensando...")

    reply = await call_ai(msg)
    await update.message.reply_text(reply)

# =========================
# SERVIDOR HTTP FAKE
# =========================
async def handle(request):
    return web.Response(text="Bot Telegram rodando no Render Free")

async def start_web():
    app = web.Application()
    app.router.add_get("/", handle)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    log.info(f"🌐 Porta aberta em {PORT}")

# =========================
# START BOT SEM LOOP CONFLITANTE
# =========================
async def start_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    log.info("🤖 Bot Telegram iniciado")

# =========================
# MAIN
# =========================
async def main():
    await asyncio.gather(
        start_web(),
        start_bot()
    )

if __name__ == "__main__":
    asyncio.run(main())
