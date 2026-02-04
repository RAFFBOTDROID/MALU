import os
import requests
import random
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters
)

# ================= CONFIG =================
TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# MODELOS GRATUITOS COM FALLBACK
MODELS = [
    "meta-llama/llama-3.1-8b-instruct:free",
    "qwen/qwen-2.5-7b-instruct:free",
    "microsoft/phi-3-mini-4k-instruct:free"
]

logging.basicConfig(level=logging.INFO)

# ============== PERSONALIDADE =============
SYSTEM_PROMPT = (
    "Você se chama Malu. "
    "Você é jovem, simpática, zoeira e fala como gente normal. "
    "Responda em português do Brasil. "
    "Não fale como IA. "
    "No máximo 2 emojis. "
    "Seja divertida e natural."
)

# ============== RESPOSTAS RÁPIDAS =========
RESPOSTAS_RAPIDAS = {
    "oi": ["E aí! 😄", "Oi! Cheguei 😎"],
    "bom dia": ["Bom diaaa ☀️", "Bom dia! Bora acordar 😅"],
    "boa noite": ["Boa noite 😴", "Até amanhã 👋"],
    "kkkk": ["Rindo junto 😂", "Essa foi boa 😅"],
}

# ============== IA =========================
def perguntar_ia(texto):
    if not OPENROUTER_API_KEY:
        return "Tô sem cérebro agora 😅 (API KEY não configurada)"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://render.com",
        "X-Title": "MaluBot"
    }

    # tenta vários modelos
    for model in MODELS:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": texto}
            ],
            "temperature": 0.7,
            "max_tokens": 120,
            "top_p": 0.9
        }

        try:
            r = requests.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
                timeout=40
            )

            if r.status_code != 200:
                logging.warning(f"Modelo falhou {model}: {r.text}")
                continue

            data = r.json()
            resposta = data["choices"][0]["message"]["content"].strip()

            if resposta:
                return resposta

        except Exception as e:
            logging.warning(f"Erro modelo {model}: {e}")
            continue

    # fallback final
    return random.choice([
        "Buguei forte agora 😂",
        "Meu cérebro caiu 😅",
        "Fui pensar e me perdi 🤯",
        "Travou aqui rapidinho 😂"
    ])

# ============== COMANDO ===================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Malu online! Bora conversar 😎")

# ============== MENSAGENS =================
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return

    texto_original = msg.text.strip()
    texto = texto_original.lower()

    bot_username = context.bot.username.lower()

    # 🚫 NÃO responder reply a humano
    if msg.reply_to_message:
        autor = msg.reply_to_message.from_user
        if autor and not autor.is_bot:
            return

    # 🚫 NÃO responder menções que não sejam o bot
    if msg.entities:
        for ent in msg.entities:
            if ent.type == "mention":
                mencionado = texto_original[ent.offset: ent.offset + ent.length].lower()
                if mencionado != f"@{bot_username}":
                    return

    # ========= RESPOSTAS RÁPIDAS =========
    if texto in RESPOSTAS_RAPIDAS:
        await msg.reply_text(random.choice(RESPOSTAS_RAPIDAS[texto]))
        return

    # ========= IA =========
    resposta = perguntar_ia(texto_original)
    await msg.reply_text(resposta)

# ============== MAIN ======================
def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN não definido")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("🤖 Malu rodando no Render...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

