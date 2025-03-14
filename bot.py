import logging, json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import pytz

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone='Europe/Warsaw')
CHAT_ID = None
BIRTHDAYS_FILE = 'birthdays.json'

# Завантаження дат народження
def load_birthdays():
    try:
        with open(BIRTHDAYS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

# Збереження дат народження
def save_birthdays(data):
    with open(BIRTHDAYS_FILE, 'w') as f:
        json.dump(data, f)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт, Mors! 🌊 Вітаю у групі Моржів!")

# Вітання нових учасників
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        name = f"Mors {member.first_name}"
        await update.message.reply_text(
            f"Привіт, {name}! 🌊 Ласкаво просимо до нашої групи Моржів! Готуйся загартовуватися!"
        )

# Додавання дати народження
async def set_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    birthdays = load_birthdays()

    try:
        date_str = context.args[0]  # формату DD.MM
        datetime.strptime(date_str, "%d.%m")
        birthdays[str(user.id)] = {
            "name": user.first_name,
            "birthday": date_str
        }
        save_birthdays(birthdays)
        await update.message.reply_text("✅ Дата народження успішно збережена!")
    except:
        await update.message.reply_text("❌ Використовуйте формат: /birthday DD.MM (наприклад: /birthday 25.12)")

# Автоматичне привітання з днем народження
async def birthday_greetings():
    global CHAT_ID, app
    birthdays = load_birthdays()
    today = datetime.now(pytz.timezone('Europe/Warsaw')).strftime("%d.%m")

    for user_id, data in birthdays.items():
        if data["birthday"] == today:
            await app.bot.send_message(
                chat_id=CHAT_ID,
                text=f"🎉🎈 Вітаємо з днем народження, Mors {data['name']}! Бажаємо міцного здоров'я та свіжих занурень! 🌊❄️"
            )

# Налаштування завдань
async def setup_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    scheduler.remove_all_jobs()

    # Щотижневе опитування (п'ятниця, 16:00)
    scheduler.add_job(weekly_poll, trigger='cron', day_of_week='fri', hour=16, minute=0)

    # Перевірка дня народження щоденно о 9:00
    scheduler.add_job(birthday_greetings, trigger='cron', hour=9, minute=0)

    await update.message.reply_text("✅ Завдання налаштовані (опитування + дні народження)!")

# Щотижневе опитування
async def weekly_poll():
    global CHAT_ID, app
    await app.bot.send_poll(
        chat_id=CHAT_ID,
        question="Хто завтра готовий поморозити свої хвостики? 🌊❄️",
        options=["Я готовий!", "Поки пропущу."],
        is_anonymous=False,
    )

def main():
    global app
    TOKEN = "8152763219:AAHPHyTJjho-zUnimJ1iJXPiOnQWLQf9Sew"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(CommandHandler("setup", setup_jobs))
    app.add_handler(CommandHandler("birthday", set_birthday))

    scheduler.start()
    app.run_polling()

if __name__ == '__main__':
    main()
