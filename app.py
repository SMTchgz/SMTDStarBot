import os
import json
import telebot
from flask import Flask, request
from googletrans import Translator
from config import Config

# Initialize Flask app
app = Flask(__name__)

# Initialize bot
bot = telebot.TeleBot(Config.BOT_TOKEN)
translator = Translator()

# Data file setup
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "data.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Load or initialize data
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {
        "points": {},
        "wallets": {},
        "langs": {},
        "pending": {}
    }

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Health check endpoint (required for Render)
@app.route('/')
def health_check():
    return "Bot is running!", 200

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_data = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
        return "OK", 200
    return "Invalid request", 403

# Command handlers (same as before but with improved error handling)
@bot.message_handler(commands=['start'])
def welcome(message):
    try:
        lang = get_lang(message.from_user.id)
        msg = {
            "en": "Welcome to SMTD StarRank Bot!",
            "ar": "مرحبًا بك في بوت SMTD StarRank!",
            "zh": "欢迎使用SMTD StarRank机器人!"
        }
        bot.reply_to(message, msg.get(lang, msg["en"]))
    except Exception as e:
        print(f"Error in welcome: {e}")

# ... [Keep all your other existing handler functions unchanged] ...

# Initialize webhook
def set_webhook():
    try:
        webhook_url = f"https://{Config.RENDER_URL}/webhook"
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        print(f"Webhook set to: {webhook_url}")
    except Exception as e:
        print(f"Error setting webhook: {e}")

if __name__ == '__main__':
    print("Starting bot...")
    if Config.DEPLOY_ENV == "production":
        set_webhook()
        app.run(host='0.0.0.0', port=Config.PORT)
    else:
        print("Running in polling mode...")
        bot.polling(none_stop=True)