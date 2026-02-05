import os
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# ----------------------------
# CONFIGURAÇÃO
# ----------------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Token do bot
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Chave GPT-4

openai.api_key = OPENAI_API_KEY

# ----------------------------
# FUNÇÃO DE RESPOSTA
# ----------------------------
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    # Chamada GPT-4
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é uma assistente brasileira super natural, responde sempre em português do Brasil e de forma humana."},
            {"role": "user", "content": user_message}
        ],
        max_tokens=500
    )

    answer = response['choices'][0]['message']['content']

    await update.message.reply_text(answer)

# ----------------------------
# COMANDOS INICIAIS
# ----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Oi! Eu sou a Malu, seu bot em português natural. Pode me perguntar qualquer coisa!")

# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))

    # Mensagens de texto
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("🤖 Malu iniciada com GPT-4 em português natural!")
    app.run_polling()
