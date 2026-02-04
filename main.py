import os
import random
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import openai

# ================= CONFIG =================
TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_KEY

BOT_NAME = "Malu"  # nome do bot/personagem

# ================= FUNÇÕES =================

async def gerar_resposta(texto: str) -> str:
    """
    Gera resposta humanizada usando OpenAI
    """
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"Você é {BOT_NAME}, uma pessoa amigável e natural no Telegram."},
                {"role": "user", "content": texto}
            ],
            temperature=0.8,
            max_tokens=150
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print("Erro OpenAI:", e)
        return "Ops, algo deu errado 😅"

async def responder_mensagens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde mensagens normais, ignorando mensagens citadas
    """
    # Ignora mensagens que são citações
    if update.message.reply_to_message:
        return

    texto = update.message.text
    resposta = await gerar_resposta(texto)
    await update.message.reply_text(resposta)

async def auto_mensagem(context: ContextTypes.DEFAULT_TYPE):
    """
    Envia mensagens automáticas de vez em quando
    """
    chat_id = os.getenv("GROUP_ID")  # coloque o ID do grupo
    mensagens = [
        "Oi pessoal! 😎",
        "Como vocês estão hoje?",
        "Alguém viu algo interessante?",
        "Malu passando para dizer oi 👋"
    ]
    await context.bot.send_message(chat_id=chat_id, text=random.choice(mensagens))

# ================= MAIN =================

async def main():
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_mensagens))

    # Job Queue: mensagens automáticas
    app.job_queue.run_repeating(auto_mensagem, interval=random.randint(300, 600), first=15)

    print(f"INFO:BOT:🤖 {BOT_NAME} iniciado com IA humanizada!")
    await app.run_polling()

# ================= EXEC =================
if __name__ == "__main__":
    asyncio.run(main())
