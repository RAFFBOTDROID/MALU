import os
import time
import logging
import asyncio
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ================= CONFIG =================
TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN não definido!")

# ================= LOG =================
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("BOT")

# ================= ANTI-SPAM =================
cooldowns_user = {}
cooldowns_group = {}
USER_COOLDOWN = 5
GROUP_COOLDOWN = 15

def can_use_user(uid):
    now = time.time()
    last = cooldowns_user.get(uid, 0)
    if now - last < USER_COOLDOWN:
        return False
    cooldowns_user[uid] = now
    return True

def can_use_group(chat_id):
    now = time.time()
    last = cooldowns_group.get(chat_id, 0)
    if now - last < GROUP_COOLDOWN:
        return False
    cooldowns_group[chat_id] = now
    return True

# ================= FUNÇÃO IA COM PERSONALIDADE =================
async def call_ai(prompt: str):
    if not OPENROUTER_KEY:
        return "⚠️ IA indisponível (API não configurada)"

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }

    # Define a personalidade do bot
    personality_prompt = (
        "Você é um bot chamado 'Malu', jovem, divertido, sarcástico e carinhoso. "
        "Você responde mensagens de forma leve e engraçada, gosta de interagir com os membros do grupo e tem bom humor. "
        "Não se apresente como um bot, apenas fale como se fosse uma pessoa real."
    )

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": personality_prompt},
            {"role": "user", "content": prompt}
        ],
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
        "🤖 Olá! Eu sou a Malu, o bot divertido do grupo! 🌟"
    )

# ================= INTERAÇÃO AUTOMÁTICA =================
async def group_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_text = update.message.text
    chat_id = update.effective_chat.id
    uid = update.effective_user.id

    # Evita flood de respostas automáticas
    if not can_use_group(chat_id):
        return

    # Ignora mensagens do próprio bot
    if update.effective_user.is_bot:
        return

    # Gera resposta usando IA
    thinking_msg = await update.message.reply_text("🧠 Malu está pensando...")
    reply = await call_ai(msg_text)
    await thinking_msg.edit_text(reply)

# ================= EXECUÇÃO =================
async def run_bot():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, group_chat))

    while True:
        try:
            # Remove webhook para evitar conflito
            try:
                await app.bot.delete_webhook(drop_pending_updates=True)
            except:
                pass

            log.info("🤖 Bot Malu iniciado com polling...")
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            await app.updater.idle()
            await app.stop()
            await app.shutdown()
        except Exception as e:
            log.error(f"⚡ Erro no bot, reconectando em 5s: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    loop.run_forever()
