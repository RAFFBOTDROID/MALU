import os
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import openai

# =====================
# CONFIGURAÇÃO
# =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.getenv("PORT", 10000))
openai.api_key = OPENAI_API_KEY

# =====================
# FUNÇÃO DE IA
# =====================
async def ask_ai(prompt: str) -> str:
    try:
        response = await asyncio.to_thread(lambda: openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        ))
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Erro na IA: {e}"

# =====================
# HANDLERS DO BOT
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Olá! Malu IA iniciada!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    await update.message.chat.send_action("typing")
    reply = await ask_ai(msg)
    await update.message.reply_text(reply)

# =====================
# FUNÇÃO PRINCIPAL
# =====================
async def main_bot():
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    await app_bot.run_polling(close_loop=False)

# =====================
# SERVIDOR HTTP PARA RENDER
# =====================
async def handle(request):
    return web.Response(text="🤖 Bot IA rodando!")

async def main_server():
    server_app = web.Application()
    server_app.add_routes([web.get("/", handle)])
    runner = web.AppRunner(server_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"HTTP server rodando na porta {PORT}")
    await main_bot()  # roda o bot junto

# =====================
# EXECUÇÃO
# =====================
if __name__ == "__main__":
    asyncio.run(main_server())
