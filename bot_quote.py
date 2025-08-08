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
«Будь самой лучшей версией себя.» — Одри Хепбёрн
«Сильная женщина улыбается сквозь слёзы.» — Мэрилин Монро
«Никто не может заставить тебя чувствовать себя хуже без твоего согласия.» — Элеонор Рузвельт
«Секрет привлекательности женщины — в уверенности.» — София Лорен
«Любовь — это когда счастье другого важнее собственного.» — Далай-лама XIV
«Не ищи принца, будь королевой.» — Коко Шанель
«Ты сильнее, чем думаешь.» — Серена Уильямс
«Главное в женщине — её глаза, они дверь в сердце.» — Одри Хепбёрн
«Мир ломает всех, но после многие становятся сильнее.» — Эрнест Хемингуэй
«Любить себя — это начало романа на всю жизнь.» — Оскар Уайльд
«Счастье женщины в её руках.» — Мадонна
«Красота начинается в тот момент, когда ты решаешь быть собой.» — Коко Шанель
«Никогда не поздно быть тем, кем ты мог бы стать.» — Джордж Элиот
«Любовь — это выбор каждый день.» — Барбара Де Анджелис
«Ни одна женщина не обязана быть идеальной, чтобы быть любимой.» — Мэрилин Монро
«Твоя энергия притягивает то, что ты излучаешь.» — Опра Уинфри
«Самое важное в жизни — научиться отдавать любовь и принимать её.» — Морри Шварц
«Женщина — это сила, замаскированная под нежность.» — Жаклин Кеннеди
«Люби жизнь, и жизнь полюбит тебя.» — Артур Рубинштейн
«Счастливая женщина украшает весь мир.» — София Лорен
«Мы принимаем любовь, которую думаем, что заслуживаем.» — Стивен Чбоски
«Верь в чудеса — и они придут.» — Луиза Хей
«Любовь — это не находить идеального, а видеть идеальное в человеке.» — Сэм Кин
«Сильная женщина поднимает других.» — Мишель Обама
«Ты достойна лучшего.» — Дженнифер Лопес
«Всё возможно для того, кто верит.» — Марк 9:23
«Настоящая любовь не требует доказательств.» — Антуан де Сент-Экзюпери
«Женщина — это музыка, которую надо уметь слушать.» — Виктор Гюго
«Не бойся менять жизнь.» — Элизабет Гилберт
«Всё, что ты можешь себе представить, реально.» — Пабло Пикассо
«Любовь — это искусство находить себя в другом.» — Фридрих Ницше
«Улыбка — лучший макияж девушки.» — Мэрилин Монро
«Женщина сияет, когда любима.» — Лев Толстой
«Только любовь делает нас по-настоящему живыми.» — Лео Бускалья
«Не сравнивай себя с другими.» — Бейонсе
«Самое прекрасное в женщине — её душа.» — Платон
«Если хочешь, чтобы тебя любили, люби сама.» — Сенека
«Будь той, кем ты гордишься.» — Меган Маркл
«Любовь — это когда не хочешь засыпать, потому что реальность лучше сна.» — Доктор Сьюз
«Кто не рискует, тот не любит.» — Эрих Мария Ремарк
«Счастье внутри тебя.» — Луиза Хей
«Женщина — как чайный пакетик: её сила видна, когда она в горячей воде.» — Элеонор Рузвельт
«Без любви жизнь — пустая скорлупа.» — Халиль Джебран
«Сильная женщина улыбается, даже когда сердце плачет.» — Неизвестный автор
«Ты заслуживаешь того, кто будет бояться потерять тебя.» — Неизвестный автор
«Верь в себя, и весь мир поверит в тебя.» — Вирджиния Вулф
«Красота — это свет в сердце.» — Халиль Джебран
«Любовь — это ключ к счастью.» — Будда
«Женщина становится непобедимой, когда верит в себя.» — Опрa Уинфри
«Счастливая женщина — это сила.» — Мишель Обама
]

# ====== Кнопки ======
def start_keyboard():
    return ReplyKeyboardMarkup(
        [["🚀 Старт", "💌 Цитата дня"]],
        resize_keyboard=True
    )

def quote_action_keyboard():
    return ReplyKeyboardMarkup(
        [["📢 Отправить в канал", "🔄 Другая цитата"]],
        resize_keyboard=True
    )

# ====== Хендлеры ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(quotes)
    context.user_data["current_quote"] = quote
    await update.message.reply_text(quote, reply_markup=quote_action_keyboard())

async def quote_of_the_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(quotes)
    context.user_data["current_quote"] = quote
    await update.message.reply_text(quote, reply_markup=quote_action_keyboard())

async def send_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = context.user_data.get("current_quote")
    if not quote:
        await update.message.reply_text("Сначала выбери 🚀 Старт или 💌 Цитата дня!")
        return
    await context.bot.send_message(chat_id=CHANNEL_ID, text=quote)
    await update.message.reply_text("✅ Цитата отправлена в канал!")

async def change_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(quotes)
    context.user_data["current_quote"] = quote
    await update.message.reply_text(quote, reply_markup=quote_action_keyboard())

async def ignore_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Игнор любых сообщений не по кнопкам"""
    await update.message.reply_text("Используй кнопки ниже ⬇️", reply_markup=start_keyboard())

# ====== Запуск приложения ======
def build_app():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^🚀 Старт$"), start))
    app.add_handler(MessageHandler(filters.Regex("^💌 Цитата дня$"), quote_of_the_day))
    app.add_handler(MessageHandler(filters.Regex("^📢 Отправить в канал$"), send_to_channel))
    app.add_handler(MessageHandler(filters.Regex("^🔄 Другая цитата$"), change_quote))
    app.add_handler(MessageHandler(filters.ALL, ignore_text))  # Блокируем любой текст

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