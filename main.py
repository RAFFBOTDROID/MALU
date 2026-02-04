import os
import random
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, JobQueue
import openai

# ================= CONFIGURAÇÃO =================
TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TOKEN or not OPENAI_API_KEY:
    raise RuntimeError("⚠️ BOT_TOKEN ou OPENAI_API_KEY não encontrado nos secrets!")

openai.api_key = OPENAI_API_KEY

# ================= FUNÇÕES =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! 🤖 Eu sou a Malu com IA humanizada. Envie algo para conversar!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    response = await ask_openai(user_text)
    await update.message.reply_text(response)

async def ask_openai(prompt: str) -> str:
    """Consulta OpenAI para respostas humanizadas"""
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Ops! Houve um erro na IA: {e}"

async def auto_mensagem(context: ContextTypes.DEFAULT_TYPE):
    """Função de mensagens automáticas periódicas"""
    chats = context.job.chat_id if hasattr(context.job, "chat_id") else None
    if chats:
        await context.bot.send_message(chat_id=chats, text="🤖 Lembrete amigável da Malu!")

# ================= INICIALIZAÇÃO =================
async def main():
    # Criar a aplicação
    app = Application.builder().token(TOKEN).build()

    # Handlers de comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("chat", chat))

    # JobQueue - mensagens automáticas a cada 5-10 minutos
    # Só funciona se você passar um chat_id válido
    job_queue: JobQueue = app.job_queue
    job_queue.run_repeating(auto_mensagem, interval=random.randint(300, 600), first=15)

    # Rodar bot (async polling)
    await app.run_polling()

# ================= RODAR NO RENDER =================
# Render já tem loop do asyncio ativo, então usamos create_task
asyncio.get_event_loop().create_task(main())
print("INFO:BOT:🤖 Malu iniciado com IA humanizada!")
