import logging
import os
from telegram import (
    Bot,
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler,
    Filters,
)
TOKEN = os.environ.get("TOKEN")

# Majburiy obuna kanallar
CHANNELS = [
    "https://t.me/top_mods_1",
    "https://t.me/soft_na_grand",
    "https://t.me/GMP_Rynok"
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LANG_SELECT, TOPIC_COUNT, TOPIC_NAMES, GROUP_ID = range(4)
user_data = {}

def start(update: Update, context: CallbackContext):
    buttons = [[InlineKeyboardButton("✅ Tekshirish", callback_data="check_subs")]]
    text = "🔔 Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:\n\n"
    for ch in CHANNELS:
        text += f"➡️ {ch}\n"
    update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

def check_subs(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user.id
    bot = context.bot
    not_joined = []

    for link in CHANNELS:
        try:
            chat = bot.get_chat(link)
            member = chat.get_member(user_id)
            if member.status not in ("member", "administrator", "creator"):
                not_joined.append(link)
        except:
            not_joined.append(link)

    if not_joined:
        update.callback_query.message.reply_text("❗ Siz quyidagi kanallarga obuna bo‘lishingiz kerak:\n" + "\n".join(not_joined))
    else:
        buttons = [
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz")]
        ]
        update.callback_query.message.reply_text("🌐 Выберите язык / Tilni tanlang:", reply_markup=InlineKeyboardMarkup(buttons))

def language_selected(update: Update, context: CallbackContext):
    lang = update.callback_query.data.split("_")[1]
    context.user_data["lang"] = lang
    buttons = [
        [InlineKeyboardButton("📝 Создать топики", callback_data="create_topics")],
        [InlineKeyboardButton("👤 Связаться с админом", url="https://t.me/rude_lxz")]
    ]
    update.callback_query.message.reply_text("📋 Главное меню:", reply_markup=InlineKeyboardMarkup(buttons))

def ask_topic_count(update: Update, context: CallbackContext):
    update.callback_query.message.reply_text("📥 Отправьте количество топиков (максимум 50):")
    return TOPIC_COUNT

def get_topic_count(update: Update, context: CallbackContext):
    try:
        count = int(update.message.text)
        if not 1 <= count <= 50:
            raise ValueError
        context.user_data["topic_count"] = count
        update.message.reply_text("📌 Введите названия топиков (каждое с новой строки):")
        return TOPIC_NAMES
    except:
        update.message.reply_text("❗ Пожалуйста, отправьте число от 1 до 50.")
        return TOPIC_COUNT

def get_topic_names(update: Update, context: CallbackContext):
    names = update.message.text.strip().split("\n")
    if len(names) != context.user_data["topic_count"]:
        update.message.reply_text("❗ Количество названий не совпадает с указанным числом.")
        return TOPIC_NAMES
    context.user_data["topics"] = names
    update.message.reply_text("📎 Введите ID или @юзернейм группы (где бот админ):")
    return GROUP_ID

def get_group_id(update: Update, context: CallbackContext):
    group = update.message.text.strip()
    bot = context.bot
    topics = context.user_data["topics"]
    try:
        for name in topics:
            bot.create_forum_topic(chat_id=group, name=name[:128])
        update.message.reply_text("✅ Все топики успешно созданы!")
    except Exception as e:
        update.message.reply_text(f"❌ Ошибка: {e}")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("❌ Отменено.")
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(check_subs, pattern="check_subs"))
    dp.add_handler(CallbackQueryHandler(language_selected, pattern="lang_"))
    dp.add_handler(CallbackQueryHandler(ask_topic_count, pattern="create_topics"))

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(ask_topic_count, pattern="create_topics")],
        states={
            TOPIC_COUNT: [MessageHandler(Filters.text & ~Filters.command, get_topic_count)],
            TOPIC_NAMES: [MessageHandler(Filters.text & ~Filters.command, get_topic_names)],
            GROUP_ID: [MessageHandler(Filters.text & ~Filters.command, get_group_id)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()