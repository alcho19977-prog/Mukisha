import os
import random
from typing import Dict, List, Optional

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)

# ===== НАСТРОЙКИ =====
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1002701059389"))  # ID канала
QUOTES_FILE = os.getenv("QUOTES_FILE", "quotes.txt")          # файл с цитатами (по строке)
TOKEN = os.getenv("TOKEN")                                    # токен из ENV

# Память «без повторов» на чат
chat_state: Dict[int, Dict[str, object]] = {}
QUOTES: List[str] = []


# ===== ЗАГРУЗКА ЦИТАТ =====
def load_quotes() -> List[str]:
    if not os.path.exists(QUOTES_FILE):
        return [
            "Любовь — это жизнь, и всё, что я понимаю в жизни, я понимаю только потому, что люблю. — Лев Толстой",
            "Любить — значит видеть человека таким, каким его задумал Бог. — Ф. М. Достоевский",
            "Величайшее счастье в жизни — уверенность, что тебя любят. — Виктор Гюго",
            "Быть любимым даёт силу, а любить даёт мужество. — Лао-цзы",
            "Мы любим не потому, что нашли совершенного человека, а потому, что научились видеть совершенство в несовершенном. — Сэм Кин",
        ]
    with open(QUOTES_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


# ===== ЛОГИКА ПОЛУЧЕНИЯ ЦИТАТ =====
def next_quote_for(chat_id: int) -> str:
    state = chat_state.get(chat_id)
    if not state or not state.get("order"):
        order = list(range(len(QUOTES)))
        random.shuffle(order)
        chat_state[chat_id] = {"order": order, "idx": 0}
        state = chat_state[chat_id]

    order: List[int] = state["order"]  # type: ignore
    idx: int = state["idx"]            # type: ignore

    q = QUOTES[order[idx]]
    idx += 1
    if idx >= len(order):
        random.shuffle(order)
        idx = 0
    state["idx"] = idx
    return q


# ===== КНОПКИ =====
def kb_start() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🗓️ Цитата дня", callback_data="get")]])


def kb_after_quote() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("📣 Отправить в канал", callback_data="send"),
        InlineKeyboardButton("🔁 Поменять цитату", callback_data="change"),
        InlineKeyboardButton("🔄 Обновить цитаты", callback_data="reload")
    ]])


# ===== ОТОБРАЖЕНИЕ ЦИТАТЫ =====
async def send_quote_flow(chat_id: int, context: ContextTypes.DEFAULT_TYPE, new_quote: Optional[str] = None):
    if new_quote is None:
        new_quote = next_quote_for(chat_id)
    context.chat_data["current_quote"] = new_quote
    await context.bot.send_message(chat_id=chat_id, text=new_quote, reply_markup=kb_after_quote())


# ===== ОБРАБОТЧИКИ =====
async def start_like(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "Нажми «Цитата дня» — пришлю цитату и предложу отправить её в канал.",
        reply_markup=kb_start()
    )


async def on_get(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await send_quote_flow(query.message.chat_id, context)


async def on_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    q = context.chat_data.get("current_quote")
    if not q:
        q = next_quote_for(query.message.chat_id)
        context.chat_data["current_quote"] = q
    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=q)
        await query.message.reply_text("✅ Отправил в канал.", reply_markup=kb_after_quote())
    except Exception as e:
        await query.message.reply_text(f"❌ Не удалось отправить в канал: {e}", reply_markup=kb_after_quote())


async def on_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    new_q = next_quote_for(query.message.chat_id)
    await send_quote_flow(query.message.chat_id, context, new_quote=new_q)


async def on_reload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    global QUOTES
    QUOTES = load_quotes()
    chat_state.clear()
    await query.message.reply_text(f"♻ Цитаты обновлены. Всего теперь {len(QUOTES)} шт.", reply_markup=kb_start())


async def reload_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global QUOTES
    QUOTES = load_quotes()
    chat_state.clear()
    await update.effective_message.reply_text(f"♻ Цитаты обновлены. Всего теперь {len(QUOTES)} шт.")


async def push_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = next_quote_for(update.effective_chat.id)
    await context.bot.send_message(chat_id=CHANNEL_ID, text=q)
    await update.effective_message.reply_text("✅ Цитата опубликована в канал.")


# ===== СБОРКА ПРИЛОЖЕНИЯ =====
def build_app() -> Application:
    if not TOKEN:
        raise RuntimeError("ENV TOKEN не задан. Установи TOKEN=твой_токен_бота")
    app = Application.builder().token(TOKEN).build()

    # Пробуждение
    app.add_handler(CommandHandler("start", start_like))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start_like))

    # Кнопки
    app.add_handler(CallbackQueryHandler(on_get, pattern="^get$"))
    app.add_handler(CallbackQueryHandler(on_send, pattern="^send$"))
    app.add_handler(CallbackQueryHandler(on_change, pattern="^change$"))
    app.add_handler(CallbackQueryHandler(on_reload, pattern="^reload$"))

    # Команды
    app.add_handler(CommandHandler("reload", reload_cmd))
    app.add_handler(CommandHandler("push", push_cmd))

    return app


async def setup_webhook(app: Application):
    base = os.getenv("WEBHOOK_BASE")  # например, https://your-service.onrender.com
    if not base:
        raise RuntimeError("ENV WEBHOOK_BASE не задан")
    port = int(os.getenv("PORT", "8080"))
    path = f"/webhook/{TOKEN}"
    url = f"{base}{path}"
    await app.bot.set_webhook(url=url, drop_pending_updates=True)
    await app.run_webhook(listen="0.0.0.0", port=port, webhook_path=path, stop_signals=None)


if __name__ == "__main__":
    QUOTES = load_quotes()
    app = build_app()
    mode = os.getenv("MODE", "polling").lower()
    if mode == "webhook":
        app.create_task(setup_webhook(app))
        app.run_async()
    else:
        app.run_polling(allowed_updates=Update.ALL_TYPES)