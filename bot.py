import logging
from telegram import Update, ChatMember
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ChatMemberHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Обробка команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт, Mors! 🌊 Вітаю у групі Моржів!")

# Обробка привітання нових учасників
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        name = f"Mors {member.first_name}"
        await update.message.reply_text(
            f"Привіт, {name}! 🌊 Ласкаво просимо до нашої групи Моржів! Готуйся загартовуватися!"
        )

def main():
    TOKEN = "8152763219:AAHPHyTJjho-zUnimJ1iJXPiOnQWLQf9Sew"
    app = ApplicationBuilder().token(TOKEN).build()

    # Обробники команд та подій
    app.add_handler(CommandHandler("start", start))
    app.add_handler(ChatMemberHandler(welcome, ChatMemberHandler.CHAT_MEMBER))

    app.run_polling()

if __name__ == '__main__':
    main()
