import os

class Config:
    # Telegram Bot Token
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # Render Configuration
    RENDER_URL = os.getenv("RENDER_URL", "your-render-service-name.onrender.com")
    PORT = int(os.getenv("PORT", 10000))
    
    # Deployment Environment
    DEPLOY_ENV = os.getenv("DEPLOY_ENV", "development")
    
    # Admin IDs
    ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "123456789").split(",")]