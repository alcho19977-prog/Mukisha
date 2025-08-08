import os
import random
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import time

# ===== ЛОГИ =====
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ===== ЦИТАТЫ =====
QUOTES = [
    "Будь самой лучшей версией себя. — Одри Хепбёрн",
    "Сильная женщина улыбается сквозь слёзы. — Мэрилин Монро",
    "Никто не может заставить тебя чувствовать себя хуже без твоего согласия. — Элеонор Рузвельт",
    "Секрет привлекательности женщины — в уверенности. — София Лорен",
    "Любовь — это когда счастье другого важнее собственного. — Далай-лама XIV",
    "Не ищи принца, будь королевой. — Коко Шанель",
    "Ты сильнее, чем думаешь. — Серена Уильямс",
    "Главное в женщине — её глаза, они дверь в сердце. — Одри Хепбёрн",
    "Мир ломает всех, но после многие становятся сильнее. — Эрнест Хемингуэй",
    "Любить себя — это начало романа на всю жизнь. — Оскар Уайльд",
    "Счастье женщины в её руках. — Мадонна",
    "Красота начинается в тот момент, когда ты решаешь быть собой. — Коко Шанель",
    "Никогда не поздно быть тем, кем ты мог бы стать. — Джордж Элиот",
    "Любовь — это выбор каждый день. — Барбара Де Анджелис",
    "Ни одна женщина не обязана быть идеальной, чтобы быть любимой. — Мэрилин Монро",
    "Твоя энергия притягивает то, что ты излучаешь. — Опра Уинфри",
    "Самое важное в жизни — научиться отдавать любовь и принимать её. — Морри Шварц",
    "Женщина — это сила, замаскированная под нежность. — Жаклин Кеннеди",
    "Люби жизнь, и жизнь полюбит тебя. — Артур Рубинштейн",
    "Счастливая женщина украшает весь мир. — София Лорен",
    "Мы принимаем любовь, которую думаем, что заслуживаем. — Стивен Чбоски",
    "Верь в чудеса — и они придут. — Луиза Хей",
    "Любовь — это не находить идеального, а видеть идеальное в человеке. — Сэм Кин",
    "Сильная женщина поднимает других. — Мишель Обама",
    "Ты достойна лучшего. — Дженнифер Лопес",
    "Всё возможно для того, кто верит. — Марк 9:23",
    "Настоящая любовь не требует доказательств. — Антуан де Сент-Экзюпери",
    "Женщина — это музыка, которую надо уметь слушать. — Виктор Гюго",
    "Не бойся менять жизнь. — Элизабет Гилберт",
    "Всё, что ты можешь себе представить, реально. — Пабло Пикассо",
    "Любовь — это искусство находить себя в другом. — Фридрих Ницше",
    "Улыбка — лучший макияж девушки. — Мэрилин Монро",
    "Женщина сияет, когда любима. — Лев Толстой",
    "Только любовь делает нас по-настоящему живыми. — Лео Бускалья",
    "Не сравнивай себя с другими. — Бейонсе",
    "Самое прекрасное в женщине — её душа. — Платон",
    "Если хочешь, чтобы тебя любили, люби сама. — Сенека",
    "Будь той, кем ты гордишься. — Меган Маркл",
    "Любовь — это когда не хочешь засыпать, потому что реальность лучше сна. — Доктор Сьюз",
    "Кто не рискует, тот не любит. — Эрих Мария Ремарк",
    "Счастье внутри тебя. — Луиза Хей",
    "Женщина — как чайный пакетик: её сила видна, когда она в горячей воде. — Элеонор Рузвельт",
    "Без любви жизнь — пустая скорлупа. — Халиль Джебран",
    "Верь в себя, и весь мир поверит в тебя. — Вирджиния Вулф",
    "Красота — это свет в сердце. — Халиль Джебран",
    "Любовь — это ключ к счастью. — Будда",
    "Женщина становится непобедимой, когда верит в себя. — Опра Уинфри",
    "Счастливая женщина — это сила. — Мишель Обама"
]

# ===== ПАРАМЕТРЫ =====
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
MODE = os.getenv("MODE", "webhook")
WEBHOOK_BASE = os.getenv("WEBHOOK_BASE")
PORT = int(os.getenv("PORT", 10000))

if not TOKEN:
    raise RuntimeError("ENV TOKEN не задан. Установи TOKEN в Render → Environment.")
if not CHANNEL_ID:
    raise RuntimeError("ENV CHANNEL_ID не задан.")

# ===== ЛОГИ ПЕРЕМЕННЫХ =====
print(f"PORT: {PORT}")
print(f"MODE: {MODE}")
print(f"CHANNEL_ID: {CHANNEL_ID}")
print(f"WEBHOOK_BASE: {WEBHOOK_BASE}")
print(f"TOKEN: {TOKEN}")

# ===== ФУНКЦИИ =====
def get_random_quote():
    return random.choice(QUOTES)

async def send_daily_quote(context: ContextTypes.DEFAULT_TYPE):
    quote = get_random_quote()
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=f"💌 _{quote}_",
        parse_mode="Markdown"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = get_random_quote()
    buttons = [["📤 Отправить в канал", "🔄 Другая цитата"]]
    await update.message.reply_text(
        f"💌 _{quote}_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📤 Отправить в канал":
        quote = update.message.reply_to_message.text if update.message.reply_to_message else get_random_quote()
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"💌 {quote}",
            parse_mode="Markdown"
        )
        await update.message.reply_text("✅ Цитата отправлена в канал.")
    elif text == "🔄 Другая цитата":
        await start(update, context)

# ===== СБОРКА =====
app = ApplicationBuilder().token(TOKEN).build()

# Автопостинг в 10:00
scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
scheduler.add_job(send_daily_quote, trigger="cron", hour=10, minute=0, args=[app.bot])
scheduler.start()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

# ===== ЗАПУСК =====
if MODE == "webhook":
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{WEBHOOK_BASE}/{TOKEN}"
    )
else:
    app.run_polling()