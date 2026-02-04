import os
import random
import asyncio
from telegram import Update, Message
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Se quiser IA humanizada usando OpenAI, descomente e configure sua API key
# import openai
# openai.api_key = os.getenv("OPENAI_API_KEY")

TOKEN = os.getenv("BOT_TOKEN")

# =====================
# Funções principais
# =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mensagem inicial do bot"""
    await update.message.reply_text(
        "Olá! Eu sou a Malu 😎\nEstou aqui para interagir de forma humanizada."
    )

async def human_response(text: str) -> str:
    """
    Aqui você pode colocar sua IA. 
    Por enquanto, retorna respostas simples para testes.
    """
    # Exemplo simples
    respostas = [
        "Interessante 😏",
        "Ah, entendi!",
        "Pode me contar mais?",
        "Hum… fiquei pensando nisso 🤔",
        "Haha, gostei do que disse 😄",
    ]
    return random.choice(respostas)

    # Exemplo com OpenAI GPT:
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=[{"role": "user", "content": text}],
    #     max_tokens=50,
    # )
    # return response.choices[0].message.content.strip()

async def reply_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde mensagens normais, ignorando mensagens citadas"""
    message: Message = update.message

    # Ignora mensagens sem texto ou mensagens citadas
    if not message.text:
        return
    if message.reply_to_message:
        return

    response = await human_response(message.text)
    await message.reply_text(response)

# =====================
# Mensagens automáticas
# =====================

async def auto_messages_job(context: ContextTypes.DEFAULT_TYPE):
    """Envia mensagens automáticas para o grupo"""
    chat_id = os.getenv("GROUP_CHAT_ID")  # Coloque o ID do grupo aqui
    if not chat_id:
        return
    frases = [
        "Oi pessoal 😎",
        "Como estão todos?",
        "Alguém quer conversar?",
        "Malu está de olho 👀",
        "Vamos animar esse grupo! 🎉",
    ]
    await context.bot.send_message(chat_id=chat_id, text=random.choice(frases))

# =====================
# Main
# =====================

def main():
    app = Application.builder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))

    # Mensagens de membros
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_messages))

    # Mensagens automáticas a cada 5-10 minutos
    app.job_queue.run_repeating(
        auto_messages_job, interval=random.randint(300, 600), first=10
    )

    print("INFO:BOT:🤖 Malu iniciado com IA humanizada!")
    app.run_polling()

# =====================
# Rodando o bot
# =====================
if __name__ == "__main__":
    main()
