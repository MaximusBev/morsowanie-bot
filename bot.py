import logging, json
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import os
import sys

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone='Europe/Warsaw')
CHAT_ID = None
STATS_FILE = 'stats.json'
MEMBERS_FILE = 'members.json'

def load_data(file_name, default_value):
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_value

def save_data(file_name, data):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_stats():
    return load_data(STATS_FILE, {})

def save_stats(stats):
    save_data(STATS_FILE, stats)

def load_members():
    return load_data(MEMBERS_FILE, [])

def save_members(members):
    save_data(MEMBERS_FILE, members)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID
    CHAT_ID = update.message.chat_id
    await update.message.reply_text(
        "Привіт, Mors! 🌊 Використовуйте /help для перегляду команд."
    )

async def birthday_wishes():
    if not CHAT_ID:
        return

    today = datetime.now().strftime('%d.%m')
    members = load_members()
    birthday_members = [m.split(" (")[0] for m in members if today in m]

    messages = [f"🎉 {name}, вітаємо з ДН! 🎂 Нехай твоє занурення буде гарячим, як сауна, та приємним, як ополонка після баньки! І не забувай – мокрі моржі завжди найщасливіші! 🌊😉🍾"]

    for name in birthday_members:
        await app.bot.send_message(chat_id=CHAT_ID, text=messages[0])

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"🌊 Ласкаво просимо, {member.first_name}! 🌊\n"
            f"Щоб стати справжнім моржем, зареєструйся командою:\n"
            f"/register Ім'я Прізвище DD.MM\n\n"
            f"І пам'ятай: якщо не зареєструєшся, ополонка може тебе не впізнати! 🥶😉"
        )

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    admins = await context.bot.get_chat_administrators(update.effective_chat.id)
    return user.id in [admin.user.id for admin in admins]

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = load_stats()
    stats_text = "📊 Статистика:\n" + "\n".join(f"{name}: {count} 🏅" for name, count in stats.items())
    await update.message.reply_text(stats_text)

async def update_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Ви не маєте доступу до цієї команди.")
        return

    stats = load_stats()
    members = load_members()

    input_name = " ".join(context.args)
    matched = [m for m in members if input_name.lower() in m.lower()]

    if not matched:
        await update.message.reply_text("❌ Учасник не знайдений.")
        return

    member_name = matched[0]
    stats[member_name] = stats.get(member_name, 0) + 1
    save_stats(stats)
    await update.message.reply_text(f"✅ {member_name} додано до статистики.")

async def create_poll():
    if not CHAT_ID:
        return
    await app.bot.send_poll(
        chat_id=CHAT_ID,
        question="Хто йде моржувати цієї суботи о 16:00? 🌊",
        options=["Я 🥶", "Ще думаю 🤔", "Пас цього разу 🙅‍♂️"]
    )

async def help_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = "/register, /mors, /stats, /members, /remove_members, /help"
    await update.message.reply_text(f"Доступні команди: {commands}")

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 3:
        await update.message.reply_text("❌ Формат неправильний. Використовуйте: /register Ім'я Прізвище DD.MM")
        return

    full_name = f"{args[0]} {args[1]} ({args[2]})"
    members = load_members()
    if full_name not in members:
        members.append(full_name)
        save_members(members)
        await update.message.reply_text(f"✅ Зареєстровано {full_name}")
    else:
        await update.message.reply_text("⚠️ Ви вже зареєстровані.")

async def member_left(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member_name = update.message.left_chat_member.first_name
    members = [m for m in load_members() if member_name not in m]
    stats = load_stats()
    stats.pop(member_name, None)
    save_members(members)
    save_stats(stats)

async def show_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    members = load_members()
    members_text = "\n".join(members)
    await update.message.reply_text(f"📋 Список учасників:\n{members_text}")

async def remove_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Ви не маєте доступу до цієї команди.")
        return

    input_name = " ".join(context.args)
    members = load_members()
    removed = [m for m in members if input_name.lower() in m.lower()]
    members = [m for m in members if input_name.lower() not in m.lower()]

    if removed:
        save_members(members)
        await update.message.reply_text(f"✅ Видалено учасника: {', '.join(removed)}")
    else:
        await update.message.reply_text("❌ Учасника не знайдено.")

def main():
    global app
    TOKEN = os.getenv("TELEGRAM_TOKEN")

    if not TOKEN:
        logger.error("Токен не знайдено. Перевірте змінну оточення TELEGRAM_TOKEN.")
        sys.exit("Токен не знайдено. Задайте змінну оточення TELEGRAM_TOKEN.")

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_commands))
    app.add_handler(CommandHandler("stats", show_stats))
    app.add_handler(CommandHandler("mors", update_stats))
    app.add_handler(CommandHandler("members", show_members))
    app.add_handler(CommandHandler("remove_members", remove_members))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, member_left))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app = ApplicationBuilder().token(TOKEN).build()

    scheduler.add_job(birthday_wishes, trigger='cron', hour=7)
    scheduler.add_job(create_poll, trigger='cron', day_of_week='sat', hour=16)

    scheduler.start()
    app.run_polling()


if __name__ == '__main__':
    main()