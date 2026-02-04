import os
import asyncio
import logging
import time
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN não definido")

# ================= LOG LIMPO =================
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("BOT")

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

# ================= IA OPENROUTER =================
async def call_ai(prompt):
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

# ================= COMANDOS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot online no Render FREE!\n\nDigite qualquer coisa para falar com a IA."
    )

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if not can_use(uid):
        await update.message.reply_text("⏳ Aguarde alguns segundos...")
        return

    msg = update.message.text
    await update.message.reply_text("🧠 Pensando...")

    reply = await call_ai(msg)
    await update.message.reply_text(reply)

# ================= ANTI-CONFLITO TELEGRAM =================
async def safe_start(app):
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
    except:
        pass

    while True:
        try:
            log.info("🤖 Bot iniciado")
            await app.run_polling()
        except Exception as e:
            log.error(f"RECONEXÃO: {e}")
            await asyncio.sleep(5)

# ================= MAIN =================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))

    asyncio.run(safe_start(app))

if __name__ == "__main__":
    main()


