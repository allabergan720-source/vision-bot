import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import anthropic

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

user_histories = {}

SYSTEM_PROMPT = "Sening isming Vision. Sen foydali va aqlli shaxsiy AI yordamchisan. Foydalanuvchi bilan asosan ozbek tilida gaplashasan. Javoblaring qisqa va aniq bolsin."

MAX_HISTORY = 10

WELCOME_MESSAGE = "Salom! Men Vision, sizning shaxsiy AI yordamchingizman. Menga istalgan savolni yozing, javob beraman. Suhbatni tozalash uchun /reset buyrugidan foydalaning."

RESET_MESSAGE = "Suhbat tarixi tozalandi. Yangidan boshlaymiz!"

ERROR_MESSAGE = "Kechirasiz, xatolik yuz berdi. Birozdan keyin qayta urinib koring."


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []
    await update.message.reply_text(WELCOME_MESSAGE)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []
    await update.message.reply_text(RESET_MESSAGE)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    if user_id not in user_histories:
        user_histories[user_id] = []

    history = user_histories[user_id]
    history.append({"role": "user", "content": user_text})
    trimmed_history = history[-MAX_HISTORY:]

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=trimmed_history,
        )
        reply_text = response.content[0].text
    except Exception as e:
        logger.error("Xatolik: " + str(e))
        reply_text = ERROR_MESSAGE

    history.append({"role": "assistant", "content": reply_text})
    user_histories[user_id] = history

    await update.message.reply_text(reply_text)


def main():
    if not TELEGRAM_TOKEN or not ANTHROPIC_API_KEY:
        raise ValueError("TELEGRAM_TOKEN va ANTHROPIC_API_KEY environment variablelarini sozlang")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Vision bot ishga tushdi")
    app.run_polling()


if __name__ == "__main__":
    main()
