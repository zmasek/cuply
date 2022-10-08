import os
import telegram

TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHANNEL = os.environ.get('TELEGRAM_CHANNEL')

bot = telegram.Bot(token=TOKEN)
