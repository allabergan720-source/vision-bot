import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import anthropic

# ---- SOZLAMALAR ----
# Bu qiymatlarni Railway'ning "Variables" bo'limiga kiritasiz, kodga yozmaysiz!
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

user_histories = {}

SYSTEM_PROMPT = (
    "Sening isming Vision. Sen Tony Starkning Jarvis'iga o'xshash aqlli, "
    "foydali va biroz hazilkash shaxsiy yordamchisan. Foydalanuvchi bilan "
    "asosan o'zbek tilida gaplashasan (agar u boshqa tilda yozmasa). "
    "Javoblaring qisqa va aniq bo'lsin, Telegram xabari kabi."
)

MAX_HISTORY = 10

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []
    await update.message.reply_text(
        "Salom! Men Vision — sizning shaxsiy AI-yordamchingizman. "
        "Menga istalgan savolni yozing, javob beraman.\n\n"
        "/reset — suhbatni tozalash uchun"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []
    await update.message.reply_text("S
