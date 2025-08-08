import os
import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ====== Читаем переменные окружения ======
TOKEN = os.getenv("TOKEN")
WEBHOOK_BASE = os.getenv("WEBHOOK_BASE")
CHANNEL_ID = os.getenv("CHANNEL_ID")
MODE = os.getenv("MODE", "polling")
PORT = int(os.getenv("PORT", 10000))

if not TOKEN:
    raise RuntimeError("ENV TOKEN не задан. Установи TOKEN в Render → Environment.")

# ====== Список цитат ======
quotes = [
    "Любовь — это не что-то, что находится, а что-то, что создаётся каждый день.",
    "Любовь — единственная вещь, которая растёт, если её тратить. — Антуан де Сент-Экзюпери",
    "Сердце, которое любит, вечно молодо. — Греческая пословица",
    "Любить — значит видеть чудо, невидимое для других. — Франсуа Мориак",
    "В любви нет страха, но совершенная любовь изгоняет страх. — 1 Иоанна 4:18"
]

# ====== Кнопки ======
def main_keyboard():
    return ReplyKeyboardMarkup(
        [["Цитата дня"]],
        resize_keyboard=True
    )

def quote_action_keyboard():
    return ReplyKeyboardMarkup(
        [["Отправить в канал", "Поменять цитату"]],
        resize_keyboard=True
    )

# ====== Хендлеры ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"[LOG] /start от {update.effective_user.id}")
    await update.message.reply_text("Нажми «Цитата дня», чтобы получить цитату", reply_markup=main_keyboard())

async def quote_of_the_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(quotes)
    context.user_data["current_quote"] = quote
    print(f"[LOG] Пользователь {update.effective_user.id} получил цитату: {quote}")
    await update.message.reply_text(quote, reply_markup=quote_action_keyboard())

async def send_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = context.user_data.get("current_quote")
    if not quote:
        await update.message.reply_text("Сначала выбери «Цитата дня»!")
        return
    await context.bot.send_message(chat_id=CHANNEL_ID, text=quote)
    print(f"[LOG] Цитата отправлена в канал {CHANNEL_ID}: {quote}")
    await update.message.reply_text("Цитата отправлена в канал!")

async def change_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(quotes)
    context.user_data["current_quote"] = quote
    print(f"[LOG] Пользователь {update.effective_user.id} поменял цитату на: {quote}")
    await update.message.reply_text(quote, reply_markup=quote_action_keyboard())

async def log_all_updates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отладка — логируем всё, что приходит"""
    print("[DEBUG] Получен апдейт:", update)

# ====== Запуск приложения ======
def build_app():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^Цитата дня$"), quote_of_the_day))
    app.add_handler(MessageHandler(filters.Regex("^Отправить в канал$"), send_to_channel))
    app.add_handler(MessageHandler(filters.Regex("^Поменять цитату$"), change_quote))
    app.add_handler(MessageHandler(filters.ALL, log_all_updates))  # Логируем всё

    return app

if __name__ == "__main__":
    app = build_app()

    print(f"=== DEBUG: ENV VARS ===")
    print(f"TOKEN: {TOKEN}")
    print(f"WEBHOOK_BASE: {WEBHOOK_BASE}")
    print(f"CHANNEL_ID: {CHANNEL_ID}")
    print(f"MODE: {MODE}")
    print(f"PORT: {PORT}")
    print("=======================")

    # Отправляем тест в канал при старте
    try:
        app.bot.send_message(chat_id=CHANNEL_ID, text="🤖 Бот запущен и готов присылать цитаты!")
        print("[LOG] Сообщение в канал отправлено при старте")
    except Exception as e:
        print(f"[ERROR] Не удалось отправить тест в канал: {e}")

    if MODE == "webhook":
        print("[LOG] Запуск в режиме WEBHOOK")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"{WEBHOOK_BASE}/{TOKEN}"
        )
    else:
        print("[LOG] Запуск в режиме POLLING")
        app.run_polling()