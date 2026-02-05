import os
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import openai

# ---------------- CONFIG ----------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")
APP_URL = os.getenv("APP_URL")  # ex: https://malu-1.onrender.com
PORT = int(os.getenv("PORT", 10000))

if not BOT_TOKEN or not OPENAI_KEY or not APP_URL:
    raise RuntimeError("⚠️ Defina BOT_TOKEN, OPENAI_KEY e APP_URL nas variáveis de ambiente!")

openai.api_key = OPENAI_KEY

# ---------------- FUNÇÃO GPT-4 ----------------
async def gpt_responder(pergunta: str) -> str:
    try:
        resposta = await asyncio.to_thread(
            lambda: openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é uma IA que responde sempre em português do Brasil, de forma natural, humana e amigável."},
                    {"role": "user", "content": pergunta}
                ],
                temperature=0.7,
                max_tokens=500
            )
        )
        return resposta.choices[0].message.content.strip()
    except Exception as e:
        return f"Ops, algo deu errado: {e}"

# ---------------- HANDLERS ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Oi! Eu sou a Malu 🤖\nManda uma mensagem que vou responder como humano!")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    resposta = await gpt_responder(texto)
    await update.message.reply_text(resposta)

# ---------------- BOT ----------------
app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
app_bot.add_handler(CommandHandler("start", start))
app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

# ---------------- HTTP SERVER ----------------
async def handle_webhook(request):
    data = await request.json()
    await app_bot.update_queue.put(data)
    return web.Response(text="ok")

async def main():
    # Remove webhook antigo
    await app_bot.bot.delete_webhook()
    # Define webhook do Telegram para Render
    await app_bot.bot.set_webhook(f"{APP_URL}/webhook")
    print(f"Webhook definido em {APP_URL}/webhook")

    # Inicializa bot sem run_polling()
    await app_bot.initialize()
    await app_bot.start()
    print("🤖 Malu iniciada com GPT-4!")

    # Inicializa servidor HTTP
    server = web.Application()
    server.add_routes([web.post("/webhook", handle_webhook)])
    runner = web.AppRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"HTTP server rodando na porta {PORT}")

    while True:
        await asyncio.sleep(3600)  # mantém o loop vivo

# ---------------- START ----------------
if __name__ == "__main__":
    asyncio.run(main())
