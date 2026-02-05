import os
import random
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai

# ================= CONFIGURAÇÃO =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise RuntimeError("⚠️ BOT_TOKEN ou OPENAI_API_KEY não encontrado nos secrets!")

openai.api_key = OPENAI_API_KEY

# ================= FUNÇÃO DE IA =================
async def ask_ai(prompt: str) -> str:
    try:
        response = await asyncio.to_thread(lambda: openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=150
        ))
        text = response.choices[0].message.content.strip()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return "\n".join(lines[:3])
    except Exception as e:
        return f"❌ Erro na IA: {e}"

# ================= FUNÇÃO DE RESPOSTA =================
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text

    # Simula digitação humana
    typing_time = min(max(len(msg) * 0.05 + random.uniform(0.5, 1.5), 1), 5)
    await update.message.chat.send_action("typing")
    await asyncio.sleep(typing_time)

    reply = await ask_ai(msg)
    prefix = random.choice(["🤔", "😄", "🧐", "Hmm,", "Ah,", ""])
    await update.message.reply_text(f"{prefix} {reply}")

# ================= MENSAGENS AUTOMÁTICAS =================
async def auto_message(app: Application):
    await asyncio.sleep(10)  # espera 10s antes da primeira mensagem
    while True:
        await asyncio.sleep(3600)  # a cada 1 hora
        chat_id = "SEU_CHAT_ID"  # coloque o ID do grupo
        await app.bot.send_message(chat_id=chat_id, text=random.choice([
            "Oi pessoal! 😄 Como estão hoje?",
            "Hora de conversar! 🧐",
            "Alguém tem uma pergunta interessante? 🤔"
        ]))

# ================= COMANDOS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Eu sou a Malu 🤖💬, pronta para conversar!")

# ================= FUNÇÃO PRINCIPAL =================
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    # Start auto messages em paralelo
    asyncio.create_task(auto_message(app))

    # Rodar bot
    await app.run_polling()

# ================= INICIAR BOT =================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:
        print("⚠️ RuntimeError ignorada: event loop já estava rodando")
