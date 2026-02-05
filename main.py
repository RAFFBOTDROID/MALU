import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from aiohttp import web

# ================= CONFIGURAÇÃO =================
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("⚠️ BOT_TOKEN não encontrado nos secrets!")

# ================= FUNÇÕES DO BOT =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Oi! Eu sou a Malu 🤖\n"
        "Falo português natural, como uma pessoa de verdade.\n"
        "Manda uma mensagem pra eu responder!"
    )

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    resposta = gerar_resposta(texto)
    await update.message.reply_text(resposta)

def gerar_resposta(texto: str) -> str:
    texto = texto.lower()
    if "oi" in texto or "olá" in texto:
        return "Oi! Que bom te ver por aqui 😊"
    elif "tudo bem" in texto:
        return "Tudo ótimo, e você?"
    elif "nome" in texto:
        return "Eu me chamo Malu 🤖, prazer!"
    else:
        return "Entendi 😄 Pode me contar mais?"

# ================= HTTP SERVER =================
async def handle_http(request):
    return web.Response(text="Bot rodando! ✅")

# ================= FUNÇÃO PRINCIPAL =================
async def main():
    # HTTP server
    port = int(os.getenv("PORT", 10000))
    app_server = web.Application()
    app_server.add_routes([web.get("/", handle_http)])
    runner = web.AppRunner(app_server)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"HTTP server rodando na porta {port}")

    # Telegram bot
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    print("🤖 Malu iniciado com português natural!")

    # Start polling sem criar outro loop
    asyncio.create_task(app_bot.run_polling())

# ================= START =================
# No Render Free, não usamos asyncio.run()
# apenas pegamos o loop atual e agendamos main()
loop = asyncio.get_event_loop()
loop.create_task(main())

# Mantém o loop rodando
loop.run_forever()
