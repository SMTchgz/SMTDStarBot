import telebot
import os
import json
from googletrans import Translator
from config import Config

bot = telebot.TeleBot(Config.BOT_TOKEN)
translator = Translator()

DATA_FILE = "data.json"

# تحميل البيانات
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {"points": {}, "wallets": {}, "langs": {}, "pending": {}}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# الترحيب
@bot.message_handler(commands=['start'])
def welcome(message):
    lang = get_lang(message.from_user.id)
    msg = {
        "en": " Welcome to SMTD StarRank Bot!",
        "ar": " مرحبًا بك في بوت SMTD StarRank!",
        "zh": " 欢迎使用SMTD StarRank机器人!"
    }
    bot.reply_to(message, msg.get(lang, msg["en"]))

# تسجيل اللغة
def get_lang(user_id):
    return data["langs"].get(str(user_id), "en")

# التقاط كل رسالة
@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_text(message):
    if message.chat.type != "supergroup" or message.text.startswith('/'):
        return

    uid = str(message.from_user.id)
    mid = str(message.message_id)
    data["pending"][mid] = {
        "user_id": uid,
        "text": message.text,
        "chat_id": message.chat.id
    }
    save_data()

    notify_admins(message)

# إعلام المشرفين برسالة للمراجعة
def notify_admins(message):
    for admin in bot.get_chat_administrators(message.chat.id):
        if admin.user.id in Config.ADMIN_IDS:
            lang = get_lang(admin.user.id)
            text = message.text
            try:
                if lang != 'en':
                    text = translator.translate(message.text, dest=lang).text
            except:
                pass

            bot.send_message(
                admin.user.id,
                f"📨 Review request from {message.from_user.first_name}:\n\n{text}",
                reply_markup=create_buttons(message.message_id)
            )

# الأزرار
def create_buttons(message_id):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("✅ Approve", callback_data=f"approve:{message_id}"),
        telebot.types.InlineKeyboardButton(" Reject", callback_data=f"reject:{message_id}")
    )
    return markup

# عند الضغط على الزر
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    action, mid = call.data.split(":")
    if mid not in data["pending"]:
        bot.answer_callback_query(call.id, " لم يتم العثور على الرسالة.")
        return

    uid = data["pending"][mid]["user_id"]

    if action == "approve":
        data["points"][uid] = data["points"].get(uid, 0) + 1
        bot.answer_callback_query(call.id, "✅ تمت الموافقة وإضافة نقطة.")
    else:
        bot.answer_callback_query(call.id, "🚫 تم الرفض.")

    del data["pending"][mid]
    save_data()

# عرض نقاطي
@bot.message_handler(commands=['mypoints'])
def my_points(message):
    uid = str(message.from_user.id)
    points = data["points"].get(uid, 0)
    bot.reply_to(message, f"⭐ عدد نقاطك: {points}")

# التوب 5
@bot.message_handler(commands=['top5'])
def top5(message):
    sorted_users = sorted(data["points"].items(), key=lambda x: x[1], reverse=True)
    text = " أفضل 5 أعضاء:\n"
    for i, (uid, pts) in enumerate(sorted_users[:5], 1):
        text += f"{i}. {uid}: ⭐ {pts}\n"
    bot.reply_to(message, text if sorted_users else "لا يوجد بيانات بعد.")

# الرسائل المعلقة
@bot.message_handler(commands=['pending'])
def show_pending(message):
    if message.from_user.id not in Config.ADMIN_IDS:
        return
    if not data["pending"]:
        bot.reply_to(message, "لا توجد رسائل معلقة.")
        return
    text = "📌 الرسائل المعلقة:\n"
    for mid, msg in data["pending"].items():
        text += f"- {msg['text']} (User {msg['user_id']})\n"
    bot.reply_to(message, text)

# تسجيل المحفظة
@bot.message_handler(commands=['setwallet'])
def set_wallet(message):
    try:
        parts = message.text.split()
        if len(parts) != 2 or not parts[1].startswith("0x") or len(parts[1]) != 42:
            bot.reply_to(message, " عنوان محفظة غير صالح.")
            return
        data["wallets"][str(message.from_user.id)] = parts[1]
        save_data()
        bot.reply_to(message, "✅ تم حفظ المحفظة.")
    except:
        bot.reply_to(message, " حدث خطأ.")

# عرض المحفظة
@bot.message_handler(commands=['mywallet'])
def my_wallet(message):
    address = data["wallets"].get(str(message.from_user.id))
    bot.reply_to(message, f"محفظتك: {address}" if address else " لم تسجل محفظتك بعد.")

# مشرف يشوف محفظة أي عضو
@bot.message_handler(commands=['wallet'])
def get_wallet(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❗ يجب الرد على رسالة العضو.")
        return
    uid = str(message.reply_to_message.from_user.id)
    wallet = data["wallets"].get(uid)
    bot.reply_to(message, f"محفظة المستخدم: {wallet}" if wallet else " المستخدم لم يسجل محفظته.")

# تشغيل البوت
if __name__ == '__main__':
    print(" SMTD StarRank Bot is running...")
    bot.polling()