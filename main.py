import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from aiohttp import web

# ================== CONFIGURAÇÕES ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # caso queira integrar GPT futuramente

if not BOT_TOKEN:
    raise RuntimeError("⚠️ BOT_TOKEN não encontrado nos secrets!")

# ================== FUNÇÕES DO BOT ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Oi! Eu sou a Malu 🤖\n"
        "Falo português natural, como uma pessoa real.\n"
        "Manda uma mensagem pra eu responder!"
    )

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text

    # Resposta "humana" simples (pode ser expandida com GPT depois)
    resposta = gerar_resposta(texto)
    await update.message.reply_text(resposta)

def gerar_resposta(texto: str) -> str:
    # Aqui você pode colocar regras mais avançadas ou integração GPT
    texto = texto.lower()
    if "oi" in texto or "olá" in texto:
        return "Oi! Que bom te ver por aqui 😊"
    elif "tudo bem" in texto:
        return "Tudo ótimo, e você?"
    elif "nome" in texto:
        return "Eu me chamo Malu 🤖, prazer!"
    else:
        return "Entendi 😄 Pode me contar mais?"

# ================== HTTP SERVER ==================
async def handle_http(request):
    return web.Response(text="Bot rodando! ✅")

# ================== FUNÇÃO PRINCIPAL ==================
async def main_bot():
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("🤖 Malu iniciado com português natural!")
    await app_bot.run_polling(close_loop=False)

async def main_server():
    port = int(os.getenv("PORT", 10000))
    app_server = web.Application()
    app_server.add_routes([web.get("/", handle_http)])

    runner = web.AppRunner(app_server)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"HTTP server rodando na porta {port}")

    # Start Telegram bot junto
    await main_bot()

# ================== START ==================
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main_server())
    except KeyboardInterrupt:
        print("Finalizando bot e servidor...")
