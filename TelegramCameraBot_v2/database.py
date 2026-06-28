import os
import json

USERS_FILE = "users.json"

def load_users():
    """JSON faylından istifadəçi məlumatlarını yükləyir."""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_users(users):
    """Məlumatları JSON faylına yazır."""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def update_user_photo_count(user_id):
    """İstifadəçinin şəkil sayğacını artırır."""
    users = load_users()
    uid = str(user_id)
    if uid in users:
        users[uid]['photos_received'] = users[uid].get('photos_received', 0) + 1
        save_users(users)

def register_user(user_id, name):
    """Yeni istifadəçini qeydiyyata alır."""
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        from datetime import datetime
        users[uid] = {
            'name': name,
            'joined': datetime.now().isoformat(),
            'photos_received': 0
        }
        save_users(users)
