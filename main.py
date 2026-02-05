# main.py
import os
import asyncio
from aiohttp import web
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import openai

# ================== CONFIG ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")  # token do bot Telegram
APP_URL = os.getenv("APP_URL")      # URL do Render, ex: https://malu-1.onrender.com
OPENAI_KEY = os.getenv("OPENAI_KEY") # chave OpenAI GPT-4

openai.api_key = OPENAI_KEY

# ================== FUNÇÕES GPT ==================
async def gpt_response(prompt: str) -> str:
    """Chama a API GPT-4 para gerar resposta em português natural."""
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um assistente que responde sempre em português natural, sem parecer IA."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

# ================== HANDLERS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Olá! Eu sou a Malu, sua assistente em português natural.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    reply = await gpt_response(user_msg)
    await update.message.reply_text(reply)

# ================== WEBHOOK ==================
async def handle_webhook(request):
    """Recebe updates do Telegram e coloca na fila do bot"""
    data = await request.json()
    await app_bot.update_queue.put(data)
    return web.Response(text="ok")

# ================== INICIALIZAÇÃO ==================
app_bot = ApplicationBuilder().token(BOT_TOKEN).build()

app_bot.add_handler(CommandHandler("start", start))
app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

async def main():
    # Inicializa bot sem run_polling()
    await app_bot.initialize()
    await app_bot.start()
    # Define webhook para receber mensagens
    await app_bot.bot.set_webhook(f"{APP_URL}/webhook")

    # Cria servidor HTTP para Render
    server = web.Application()
    server.add_routes([web.post("/webhook", handle_webhook)])
    runner = web.AppRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    print(f"HTTP server rodando na porta {os.environ.get('PORT', 10000)}")
    await site.start()

    # Mantém o bot rodando
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot encerrado.")
