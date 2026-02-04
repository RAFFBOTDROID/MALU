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
        "Content-Type": "application/json",
        "HTTP-Referer": "https://render.com",
        "X-Title": "RenderBot"
    }

   payload = {
    "model": "mistralai/mistral-7b-instruct:free",
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": texto}
    ],
    "temperature": 0.7,
    "max_tokens": 150,
    "top_p": 0.9
}


# ================= COMANDOS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot online no Render FREE!\n\nDigite algo para falar comigo 😎"
    )

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if not can_use(uid):
        await update.message.reply_text("⏳ Calma aí, espera alguns segundos...")
        return

    msg = update.message.text

    await update.message.reply_text("🧠 Pensando...")

    reply = await call_ai(msg)
    await update.message.reply_text(reply)

# ================= MAIN =================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))

    log.info("🤖 Bot iniciado no Render")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()
