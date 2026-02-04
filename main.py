import os
import random
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import openai

# ===================== CONFIGURAÇÃO =====================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GROUP_CHAT_ID = os.environ.get("GROUP_CHAT_ID")  # opcional, para mensagens automáticas

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise RuntimeError("⚠️ BOT_TOKEN ou OPENAI_API_KEY não encontrado nos secrets!")

openai.api_key = OPENAI_API_KEY

# Mensagens automáticas que o bot enviará periodicamente
AUTO_MESSAGES = [
    "Oi, tudo bem? 🤖",
    "Quer bater um papo comigo? 😎",
    "Estou aqui para conversar e ajudar! 🫱🫲",
]

# ===================== FUNÇÕES =====================
async def chat_with_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde qualquer mensagem do usuário com IA humanizada"""
    user_message = update.message.text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}],
            temperature=0.7,
            max_tokens=250
        )
        ai_reply = response.choices[0].message.content
    except Exception as e:
        print(f"Erro OpenAI: {e}")
        ai_reply = "Desculpe, tive um problema ao processar sua mensagem 😓"

    await update.message.reply_text(ai_reply)

async def auto_messages(app: Application, interval: int = 600):
    """Envia mensagens automáticas periodicamente"""
    while True:
        try:
            if GROUP_CHAT_ID:
                msg = random.choice(AUTO_MESSAGES)
                await app.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
        except Exception as e:
            print(f"Erro ao enviar mensagem automática: {e}")
        await asyncio.sleep(interval)

# ===================== MAIN =====================
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Captura **qualquer mensagem de texto** para responder com IA
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_with_ai))

    # Inicia o envio automático de mensagens
    asyncio.create_task(auto_messages(app, interval=600))  # envia a cada 10 min

    # Rodar o bot no Render sem dar erro de loop
    await app.run_polling(close_loop=False)

# ===================== EXECUÇÃO =====================
if __name__ == "__main__":
    asyncio.run(main())
