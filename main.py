import os
import time
import logging
import asyncio
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ================= CONFIGURAÇÃO =================
TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN não definido!")

# ================= LOG LIMPO =================
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("BOT")

# ================= ANTI-SPAM =================
cooldowns = {}
COOLDOWN_TIME = 5  # segundos de cooldown

def can_use(uid):
    now = time.time()
    last = cooldowns.get(uid, 0)
    if now - last < COOLDOWN_TIME:
        return False
    cooldowns[uid] = now
    return True

# ================= FUNÇÃO IA =================
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

        if "choices" in data and len(data["choices"]) > 0:
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
    thinking_msg = await update.message.reply_text("🧠 Pensando...")

    reply = await call_ai(msg)
    await thinking_msg.edit_text(reply)

# ================= FUNÇÃO PRINCIPAL =================
async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))

    # Polling puro (ideal para Render Free)
    log.info("🤖 Bot Telegram iniciado com polling...")
    await app.run_polling()

# ================= EXECUÇÃO =================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        # Para casos de event loop já rodando
        log.error(f"Erro de loop: {e}")
