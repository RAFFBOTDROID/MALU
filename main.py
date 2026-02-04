import os
import logging
import time
import asyncio
import httpx
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ================= CONFIG =================
TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
PORT = int(os.environ.get("PORT", 10000))
HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
URL = f"https://{HOSTNAME}/{TOKEN}" if HOSTNAME else None

if not TOKEN:
    raise RuntimeError("BOT_TOKEN não definido")

# ================= LOG =================
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("BOT")

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

# ================= IA =================
async def call_ai(prompt: str):
    if not OPENROUTER_KEY:
        return "⚠️ IA indisponível (API não configurada)"

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
        return "⚠️ IA retornou resposta vazia"
    except Exception as e:
        log.error(f"ERRO IA: {e}")
        return "⚠️ Falha temporária na IA"

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot online no Render Free!\n\nDigite qualquer coisa para conversar com a IA."
    )

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not can_use(uid):
        await update.message.reply_text("⏳ Aguarde alguns segundos antes de enviar outra mensagem...")
        return

    msg = update.message.text
    await update.message.reply_text("🧠 Pensando...")
    reply = await call_ai(msg)
    await update.message.reply_text(reply)

# ================= WEB PING =================
async def handle_ping(request):
    return web.Response(text="Bot ativo ✅")

async def run_web():
    app_web = web.Application()
    app_web.router.add_get("/", handle_ping)
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    log.info(f"🌐 Porta aberta em {PORT} para ping HTTP")
    while True:
        await asyncio.sleep(3600)

# ================= BOT =================
async def run_bot():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))

    # Remove webhook antigo
    await app.bot.delete_webhook(drop_pending_updates=True)

    # Define webhook no Render
    if URL:
        await app.bot.set_webhook(URL)
        log.info(f"🤖 Bot Telegram iniciado com webhook: {URL}")
    else:
        log.info("⚠️ URL do webhook não definida, use polling")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

# ================= MAIN =================
async def main():
    await asyncio.gather(run_web(), run_bot())

if __name__ == "__main__":
    asyncio.run(main())
