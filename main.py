import os
import asyncio
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import openai
from aiohttp import web

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise RuntimeError("⚠️ BOT_TOKEN ou OPENAI_API_KEY não encontrado nos secrets!")

openai.api_key = OPENAI_API_KEY

# ================= MEMÓRIA DE USUÁRIO =================
user_memory = {}  # {user_id: [{"role": "user"/"assistant", "content": "..."}]}
MAX_MEMORY = 20  # Quantidade máxima de mensagens por usuário

def remember_message(user_id, role, content):
    if user_id not in user_memory:
        user_memory[user_id] = []
    user_memory[user_id].append({"role": role, "content": content})
    if len(user_memory[user_id]) > MAX_MEMORY:
        user_memory[user_id].pop(0)

# ================= FUNÇÃO GPT =================
async def ask_gpt(user_id, message):
    remember_message(user_id, "user", message)
    try:
        # Força português e jeito humano
        prompt = user_memory[user_id] + [{"role": "system", "content": "Responda em português do Brasil, de forma natural, descontraída e sem parecer uma IA. Use gírias leves e emojis se fizer sentido."}]
        response = await asyncio.to_thread(
            lambda: openai.ChatCompletion.create(
                model="gpt-4",
                messages=prompt,
                temperature=0.8
            )
        )
        reply = response.choices[0].message.content.strip()
        remember_message(user_id, "assistant", reply)
        return reply
    except Exception as e:
        print("Erro GPT:", e)
        return "Ops... deu algum problema aqui 😅"

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "E aí! Sou a Malu 😎, bora trocar uma ideia? Pode me mandar qualquer coisa!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_msg = update.message.text

    # Delay humano aleatório
    await asyncio.sleep(random.uniform(0.8, 2.0))
    reply = await ask_gpt(user_id, user_msg)
    await update.message.reply_text(reply)

# ================= MAIN BOT =================
async def main_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    await app.run_polling(close_loop=False)

# ================= HTTP SERVER =================
async def handle_http(request):
    return web.Response(text="🤖 Malu GPT ativo! Conversa em português 🇧🇷")

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
        print("⚠️ RuntimeError ignorada: event loop já estava rodando")
