import logging
import nest_asyncio
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from config import TOKEN
from fetcher import fetch_homeworks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("📜 Призвать ДЗ", callback_data='get_hw')]]
    await update.message.reply_text(
        "Явился по первому твоему клику, Темнейший...\nНажми кнопку ниже, и я принесу тебе ДЗ с алтаря знаний:",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == 'get_hw':
        try:
            text = fetch_homeworks()
            await q.edit_message_text(text, parse_mode='MarkdownV2')
        except Exception as e:
            logger.error("🚨 Ошибка отправки сообщения в Telegram: %s", e)
            await q.edit_message_text("⚠️ Ошибка при отправке ДЗ. Проверь логи.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧾 /start — пробуждение\n📖 /help — инструкция")

async def main():
    logger.info("🧿 Призываю демона Telegram...")
    if not load_token():
        logger.info("🔐 Токен не найден. Призываю Selenium для входа...")
        get_token_with_browser()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    await app.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    if asyncio.get_event_loop().is_running():
        asyncio.get_event_loop().stop()
    asyncio.run(main())