import os
from dotenv import load_dotenv  # نستورد هذه المكتبة

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # سيقرأ القيمة من ملف .env
    ADMIN_IDS = [1819080408, 6547641571]  # أصبحت الآن قائمة (list) بدلًا من tuple