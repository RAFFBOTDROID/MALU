import os
import logging
import asyncio
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN não encontrado")

if not OPENROUTER_KEY:
    raise RuntimeError("❌ OPENROUTER_API_KEY não encontrada")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================
# IA GRATUITA
# =========================
def call_ai(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "google/gemma-7b-it:free",
        "messages": [
            {"role": "system", "content": "Você é uma IA amigável que responde em português do Brasil."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }

    r = requests.post(url, json=payload, headers=headers, timeout=25)
    data = r.json()

    return data["choices"][0]["message"]["content"]

# =========================
# ANTI-SPAM
# =========================
user_cooldown = {}

def is_spam(uid):
    now = asyncio.get_event_loop().time()
    last = user_cooldown.get(uid, 0)
    if now - last < 3:
        return True
    user_cooldown[uid] = now
    return False

# =========================
# HANDLERS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot online!\n\nEnvie uma mensagem para falar com a IA."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if is_spam(uid):
        return

    text = update.message.text

    await update.message.chat.send_action("typing")

    try:
        reply = await asyncio.to_thread(call_ai, text)
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("⚠️ Erro ao responder. Tente novamente.")

# =========================
# AUTO RECONNECT
# =========================
async def main():
    while True:
        try:
            app = ApplicationBuilder().token(BOT_TOKEN).build()

            app.add_handler(CommandHandler("start", start))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

            print("✅ Bot rodando...")
            await app.run_polling()

        except Exception as e:
            print("❌ Erro crítico, reiniciando em 5s:", e)
            await asyncio.sleep(5)

# =========================
# START
# =========================
if __name__ == "__main__":
    asyncio.run(main())
