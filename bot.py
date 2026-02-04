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

MODEL = "meta-llama/llama-3.1-8b-instruct:free"

logging.basicConfig(level=logging.INFO)

# ============== PERSONALIDADE =============
SYSTEM_PROMPT = (
    "Você se chama Malu. "
    "Você é jovem, simpática e zoeira. "
    "Responda em português do Brasil. "
    "Use frases completas, naturais e com contexto. "
    "Fale como alguém de grupo, não fale como IA. "
    "No máximo 2 emojis."
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
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://render.com",
        "X-Title": "MaluBot"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": texto}
        ],
        "temperature": 0.6,
        "max_tokens": 120
    }

    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )

        if r.status_code != 200:
            logging.error(f"OPENROUTER STATUS {r.status_code}: {r.text}")
            raise Exception("Falha OpenRouter")

        data = r.json()
        resposta = data["choices"][0]["message"]["content"].strip()

        if not resposta:
            return random.choice([
                "Buguei rapidão 😂",
                "Fiquei pensativa 🤔",
                "Meu cérebro deu 404 😅"
            ])

        return resposta

    except Exception as e:
        logging.error(f"ERRO IA: {e}")
        return random.choice([
            "Travou aqui rapidinho 😂",
            "Volto já, fui pensar 🤯",
            "Meu Wi-Fi mental caiu 😅"
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
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("🤖 Bot rodando no Render...")
    app.run_polling()

if __name__ == "__main__":
    main()
