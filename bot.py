import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone='Europe/Warsaw')

CHAT_ID = None  # глобальна змінна для зберігання chat_id

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт, Mors! 🌊 Вітаю у групі Моржів!")

# Вітання нових учасників
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        name = f"Mors {member.first_name}"
        await update.message.reply_text(
            f"Привіт, {name}! 🌊 Ласкаво просимо до нашої групи Моржів! Готуйся загартовуватися!"
        )

# Функція автоматичного опитування
async def weekly_poll():
    global CHAT_ID, app
    if CHAT_ID is not None:
        await app.bot.send_poll(
            chat_id=CHAT_ID,
            question="Хто завтра готовий поморозити свої хвостики? 🌊❄️",
            options=["Я готовий!", "Поки пропущу."],
            is_anonymous=False,
        )

# Активація опитування
async def setup_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id

    # Видалити старі задачі
    scheduler.remove_all_jobs()

    # Додати нове завдання (щосуботи о 16:00)
    scheduler.add_job(
        weekly_poll,
        trigger='cron',
        day_of_week='sat',
        hour=16,
        minute=00
    )

    await update.message.reply_text("✅ Щотижневе автоматичне опитування налаштовано щосуботи о 16:00 за польським часом!")

def main():
    global app
    TOKEN = "8152763219:AAHPHyTJjho-zUnimJ1iJXPiOnQWLQf9Sew"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(CommandHandler("setup", setup_jobs))

    scheduler.start()
    app.run_polling()

if __name__ == '__main__':
    main()
