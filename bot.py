import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Логування для отримання інформації про роботу бота
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт, Mors! 🌊 Вітаю у групі Моржів!")

# Основна функція для запуску бота
def main():
    TOKEN = "8152763219:AAHPHyTJjho-zUnimJ1iJXPiOnQWLQf9Sew"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.run_polling()

if __name__ == '__main__':
    main()
