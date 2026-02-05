import os
import random
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise RuntimeError("⚠️ BOT_TOKEN ou OPENAI_API_KEY não encontrado nos secrets!")

openai.api_key = OPENAI_API_KEY

# ================= IA =================
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

# ================= CHAT =================
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    typing_time = min(max(len(msg) * 0.05 + random.uniform(0.5, 1.5), 1), 5)
    await update.message.chat.send_action("typing")
    await asyncio.sleep(typing_time)
    reply = await ask_ai(msg)
    prefix = random.choice(["🤔", "😄", "🧐", "Hmm,", "Ah,", ""])
    await update.message.reply_text(f"{prefix} {reply}")

# ================= COMANDOS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Eu sou a Malu 🤖💬, pronta para conversar!")

# ================= MENSAGENS AUTOMÁTICAS =================
async def auto_message(app: Application):
    await asyncio.sleep(10)
    while True:
        await asyncio.sleep(3600)
        chat_id = "SEU_CHAT_ID"
        await app.bot.send_message(chat_id=chat_id, text=random.choice([
            "Oi pessoal! 😄 Como estão hoje?",
            "Hora de conversar! 🧐",
            "Alguém tem uma pergunta interessante? 🤔"
        ]))

# ================= HTTP SERVER =================
async def handle(request):
    return web.Response(text="Bot Malu Online!")

async def start_server():
    app_http = web.Application()
    app_http.router.add_get("/", handle)
    runner = web.AppRunner(app_http)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"HTTP server rodando na porta {port}")

# ================= MAIN =================
async def main():
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    asyncio.create_task(auto_message(app_bot))
    await start_server()
    await app_bot.run_polling(close_loop=False)

# ================= INICIAR =================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:
        print("⚠️ RuntimeError ignorada: event loop já estava rodando")
