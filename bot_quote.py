import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)

# === Переменные окружения (Render -> Environment) ===
TOKEN = os.getenv("TOKEN")
WEBHOOK_BASE = os.getenv("WEBHOOK_BASE")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # строкой тоже ок
MODE = os.getenv("MODE", "webhook").lower()
PORT = int(os.getenv("PORT", 8443))

# Базовые проверки (чтобы падало явно, если чего-то нет)
if not TOKEN:
    raise RuntimeError("ENV TOKEN не задан. Установи TOKEN=твой_токен_бота в Render → Environment.")
if not WEBHOOK_BASE:
    raise RuntimeError("ENV WEBHOOK_BASE не задан. Пример: https://mukisha.onrender.com")
if not CHANNEL_ID:
    raise RuntimeError("ENV CHANNEL_ID не задан. Пример: -1002701059389")

# === Простой набор цитат (можешь расширить) ===
QUOTES = [
    "Любовь — это когда счастье другого человека важнее твоего собственного. — Х. Джексон Браун",
    "Мы принимаем любовь, которую думаем, что заслуживаем. — Стивен Чбоски",
    "Там, где есть любовь, есть жизнь. — Махатма Ганди",
    "Любить — значит видеть чудо, невидимое для других. — Франсуа Мориак",
    "Только в любви мы можем найти себя по-настоящему. — Томас Мертон",
]

# Запоминаем «текущую» цитату для каждого чата
current_quotes = {}


# === Хендлеры ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("📩 /start получен")
    quote = random.choice(QUOTES)
    current_quotes[update.effective_chat.id] = quote
    keyboard = [
        [InlineKeyboardButton("📣 Отправить в канал", callback_data="send")],
        [InlineKeyboardButton("🔁 Поменять цитату", callback_data="change")],
    ]
    await update.message.reply_text(
        f"📜 Цитата дня:\n\n{quote}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = update.effective_chat.id
    await query.answer()
    print(f"🖱 Кнопка нажата: {query.data}, chat={chat_id}")

    if query.data == "send":
        quote = current_quotes.get(chat_id)
        if quote:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=quote)
            await query.edit_message_text(f"✅ Цитата отправлена в канал:\n\n{quote}")
        else:
            await query.edit_message_text("Нет цитаты в памяти. Нажми /start.")

    elif query.data == "change":
        quote = random.choice(QUOTES)
        current_quotes[chat_id] = quote
        keyboard = [
            [InlineKeyboardButton("📣 Отправить в канал", callback_data="send")],
            [InlineKeyboardButton("🔁 Поменять цитату", callback_data="change")],
        ]
        await query.edit_message_text(
            f"📜 Новая цитата:\n\n{quote}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


# === Приложение ===
def build_app():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    return app


# === Запуск (Render) ===
if __name__ == "__main__":
    app = build_app()

    if MODE == "webhook":
        webhook_url = f"{WEBHOOK_BASE}/webhook/{TOKEN}"
        print(f"🚀 WEBHOOK режим. URL: {webhook_url} | PORT: {PORT}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,           # путь у вашего сервера
            webhook_url=webhook_url,  # полный публичный URL для Telegram
            allowed_updates=Update.ALL_TYPES
        )
    else:
        print("🚀 POLLING режим")
        app.run_polling(allowed_updates=Update.ALL_TYPES)