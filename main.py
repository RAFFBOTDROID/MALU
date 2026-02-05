import os
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import random

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("⚠️ BOT_TOKEN não encontrado nos secrets!")

# Memória simples por usuário
user_memory = {}  # {user_id: [{"msg": "...", "time": datetime}, ...]}

# ================= UTIL =================
def remember(user_id, message):
    """Salva mensagem na memória do usuário (máx 20 mensagens)"""
    if user_id not in user_memory:
        user_memory[user_id] = []
    user_memory[user_id].append({"msg": message, "time": datetime.now()})
    if len(user_memory[user_id]) > 20:
        user_memory[user_id].pop(0)

def generate_reply(user_id, message):
    """Gera resposta baseada na memória e mensagens anteriores"""
    remember(user_id, message)
    # Mensagens padrão de humanização
    greetings = ["Oi! 😄", "E aí? 😎", "Olá! Como vai? 🤖"]
    reactions = ["Interessante…", "Humm… entendi!", "Uau, sério? 😮"]
    # Escolhe resposta baseada em palavras-chave simples
    msg_lower = message.lower()
    if "oi" in msg_lower or "olá" in msg_lower:
        return random.choice(greetings)
    if "como você" in msg_lower or "tudo bem" in msg_lower:
        return random.choice(["Estou ótimo, obrigado! 😁 E você?", "Tudo bem por aqui! 😉"])
    if "?" in msg_lower:
        return random.choice(reactions)
    # Resposta aleatória da memória
    if user_id in user_memory and random.random() < 0.3:
        mem = random.choice(user_memory[user_id])
        return f"Você comentou antes: '{mem['msg']}' 🤔"
    # Resposta genérica
    generic = ["Interessante… me conte mais!", "Humm… continue…", "Isso é legal!"]
    return random.choice(generic)

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Oi! Sou a Malu 🤖 Humanizada. Me mande algo!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_msg = update.message.text
    # Simula delay humano
    await asyncio.sleep(random.uniform(0.5, 1.5))
    reply = generate_reply(user_id, user_msg)
    await update.message.reply_text(reply)

# ================= MAIN BOT =================
async def main_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # Rodar polling do Telegram
    await app.run_polling(close_loop=False)

# ================= HTTP SERVER (Render) =================
from aiohttp import web

async def handle_http(request):
    return web.Response(text="Bot Malu ativo! 🚀")

async def main_server():
    app_server = web.Application()
    app_server.add_routes([web.get("/", handle_http)])
    runner = web.AppRunner(app_server)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 10000)))
    await site.start()
    print(f"HTTP server rodando na porta {os.getenv('PORT', 10000)}")
    await main_bot()  # roda o bot junto

# ================= EXECUTE =================
if __name__ == "__main__":
    try:
        asyncio.run(main_server())
    except RuntimeError:
        # Ignora event loop já rodando
        print("⚠️ RuntimeError ignorada: event loop já estava rodando")
