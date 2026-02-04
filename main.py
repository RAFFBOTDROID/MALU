import os
import asyncio
import logging
import time
import httpx
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ================= CONFIG =================
TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
PORT = int(os.getenv("PORT", 10000))

if not TOKEN:
    raise RuntimeError("❌ BOT_TOKEN não definido")

# ================= LOG =================
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("BOT")

# ================= ANTI-SPAM =================
GROUP_COOLDOWNS = {}
GROUP_COOLDOWN_TIME = 5  # segundos entre respostas automáticas

def can_use_group(chat_id):
    now = time.time()
    last = GROUP_COOLDOWNS.get(chat_id, 0)
    if now - last < GROUP_COOLDOWN_TIME:
        return False
    GROUP_COOLDOWNS[chat_id] = now
    return True

# ================= IA OPENROUTER =================
async def call_ai(prompt, persona="Malu, uma assistente simpática e engraçada do grupo"):
    if not OPENROUTER_KEY:
        return "⚠️ IA indisponível (API não configurada)"

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [{"role": "user", "content": f"{persona}: {prompt}"}],
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
        "🤖 Olá! Eu sou a Malu, IA do grupo!\n"
        "💬 Eu respondo automaticamente mensagens não citadas.\n"
        "⚠️ Não respondo mensagens citadas/respostas de outros membros."
    )

# ================= INTERAÇÃO AUTOMÁTICA =================
async def group_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.is_bot:
        return  # ignora outros bots

    if update.message.reply_to_message:
        return  # não responde mensagens citadas

    msg_text = update.message.text
    chat_id = update.effective_chat.id

    if not can_use_group(chat_id):
        return

    thinking_msg = await update.message.reply_text("🧠 Malu está pensando...")
    reply = await call_ai(msg_text)
    await thinking_msg.edit_text(reply)

# ================= RODAR O BOT =================
async def run_bot():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, group_chat))
    log.info("🤖 Bot Telegram iniciado com polling...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    while True:
        await asyncio.sleep(5)

# ================= SERVIÇO WEB =================
from aiohttp import web

async def web_root(request):
    return web.Response(text="Bot Malu Online ✅", content_type="text/html")

async def run_web():
    app = web.Application()
    app.router.add_get("/", web_root)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    log.info(f"🌐 Porta aberta em {PORT}")

# ================= EXECUÇÃO =================
loop = asyncio.get_event_loop()
loop.create_task(run_bot())
loop.create_task(run_web())
loop.run_forever()
