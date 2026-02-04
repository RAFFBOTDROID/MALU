# ================= MAIN (SAFE MODE — LOOP FIX DEFINITIVO) =================
import threading
import time
import shutil
import logging
import os

BACKUP_INTERVAL = 3600
WATCHDOG_INTERVAL = 120

def backup_db():
    while True:
        try:
            if os.path.exists(DB_NAME):
                shutil.copy(DB_NAME, DB_NAME + ".backup")
                logging.info("💾 Backup do banco criado")
        except Exception as e:
            logging.error(f"Erro no backup: {e}")
        time.sleep(BACKUP_INTERVAL)

def watchdog():
    while True:
        logging.info("💓 Bot vivo (Watchdog OK)")
        time.sleep(WATCHDOG_INTERVAL)

def main():
    init_db()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, receber_texto))
    app.add_handler(
        MessageHandler(
            filters.ChatType.CHANNEL
            | filters.ChatType.GROUP
            | filters.ChatType.SUPERGROUP,
            processar
        )
    )

    # Threads seguras (não mexem no event loop)
    threading.Thread(target=backup_db, daemon=True).start()
    threading.Thread(target=watchdog, daemon=True).start()

    logging.info("🚀 Channel Beautify PRO ONLINE — SAFE MODE")

    # RODA NATIVO SEM asyncio.run
    app.run_polling()

if __name__ == "__main__":
    main()
