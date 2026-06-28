# Configuration Example
# Copy this file to config.py and update with your values

# Get from @BotFather on Telegram
BOT_TOKEN = "8069501498:AAExx7_1QkbFWLAkBcWZF7JNMKrpIo0uWCg"

# Get from ngrok or your VPS
# Example: https://xxxx-xxxx-xxxx-xxxx.ngrok.io
# Do NOT include trailing slash
WEBHOOK_URL = "YOUR_WEBHOOK_URL_HERE"

# Flask port (usually 5000, change if occupied)
FLASK_PORT = 5000

# Optional: Database
USE_DATABASE = False
DATABASE_URL = ""

# Optional: Logging
LOG_LEVEL = "INFO"
LOG_FILE = "bot.log"

# Optional: Rate limiting
MAX_PHOTOS_PER_HOUR = 100
MAX_SESSIONS_PER_USER = 5
