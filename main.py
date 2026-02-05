import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import openai

# ================= CONFIG =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise RuntimeError("❌ Configure TELEGRAM_TOKEN e OPENAI_API_KEY nas variáveis de ambiente.")

openai.api_key = OPENAI_API_KEY

# ================= FUNÇÃO DA IA =================
async def gerar_resposta(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é uma assistente que fala português do Brasil de forma natural, sem parecer IA."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Erro na OpenAI:", e)
        return "Desculpe, aconteceu um erro. Tente novamente."

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Eu sou a Malu 🤖, sua assistente em português natural. Pergunte qualquer coisa!")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    await update.message.chat.send_action(action="typing")
    resposta = await gerar_resposta(texto)
    await update.message.reply_text(resposta)

# ================= MAIN =================
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("🤖 Malu iniciada com português natural!")
    await app.run_polling()

# ================= RUN =================
if __name__ == "__main__":
    asyncio.run(main())
