import os
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai  # vamos usar OpenAI (ou outro endpoint) para respostas humanas

# ================= CONFIG =================
TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")  # ID do grupo para mensagens automáticas
BOT_NAME = "Malu"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # chave da OpenAI

# Configurar OpenAI
openai.api_key = OPENAI_API_KEY

# Mensagens automáticas baseadas em personalidade
AUTO_MESSAGES = [
    "Oi gente! Como estão todos hoje? 😎",
    "Haha, me contem algo engraçado!",
    "Hmm, interessante... me fale mais!",
    "Sério? Quero saber mais!",
    "😂 Isso me fez rir!"
]

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🤖 {BOT_NAME} iniciado com IA humanizada!")

# Ignorar mensagens citadas
def is_not_reply(update: Update):
    return update.message and update.message.reply_to_message is None

# Função para gerar respostas humanas via IA
async def generate_response(text, user_name=""):
    prompt = (
        f"Você é {BOT_NAME}, uma assistente virtual com personalidade humana e amigável.\n"
        f"Responda de forma natural, casual e divertida para {user_name}.\n"
        f"Mensagem recebida: {text}\n"
        "Resposta:"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # pode trocar por outro modelo
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            temperature=0.9
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Erro IA:", e)
        # fallback caso IA falhe
        return random.choice(AUTO_MESSAGES)

# Handler de mensagens no grupo
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_not_reply(update):
        return  # ignora mensagens citadas
    user_name = update.effective_user.first_name
    reply = await generate_response(update.message.text, user_name)
    await update.message.reply_text(reply)

# Mensagens automáticas
async def auto_messages_job(context: ContextTypes.DEFAULT_TYPE):
    if GROUP_ID:
        message = random.choice(AUTO_MESSAGES)
        await context.bot.send_message(chat_id=int(GROUP_ID), text=message)

# ================= MAIN =================
def main():
    app = Application.builder().token(TOKEN).build()

    # Adicionar handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUP, handle_message))

    # Mensagens automáticas com JobQueue
    if GROUP_ID:
        interval = random.randint(300, 600)  # 5-10 minutos
        app.job_queue.run_repeating(auto_messages_job, interval=interval, first=15)

    print(f"INFO:BOT:🤖 {BOT_NAME} iniciado com IA humanizada!")
    app.run_polling()

if __name__ == "__main__":
    main()
