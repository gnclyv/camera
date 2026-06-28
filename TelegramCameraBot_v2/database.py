import os
import json
from datetime import datetime

USERS_FILE = "users.json"

def load_data():
    """Fayldan bütün datanı oxuyur"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_data(data):
    """Datanı fayla yazır"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def initialize_structure(data):
    """Əgər struktur yoxdursa, ilkin formanı yaradır"""
    if "total_starts" not in data:
        return {
            "total_starts": 0,
            "unique_users": 0,
            "players": {}
        }
    return data

def increment_start(user_id, first_name):
    """Start əmrini və sayğacları idarə edir"""
    data = load_data()
    data = initialize_structure(data)
    
    # Qlobal start sayını artır
    data["total_starts"] += 1
    
    user_id_str = str(user_id)
    
    # Yeni istifadəçidirsə qeydiyyat et, köhnədirsə sayğacını artır
    if user_id_str not in data["players"]:
        data["players"][user_id_str] = {
            'name': first_name,
            'joined': datetime.now().isoformat(),
            'photos_received': 0,
            'personal_starts': 1
        }
        data["unique_users"] = len(data["players"])
    else:
        data["players"][user_id_str]['personal_starts'] = data["players"][user_id_str].get('personal_starts', 0) + 1
        
    save_data(data)
    
    # Geriyə ümumi datanı və bu istifadəçinin şəxsi start sayını qaytarır
    return data, data["players"][user_id_str]['personal_starts']

def increment_photo_count(user_id):
    """İstifadəçinin qəbul etdiyi foto sayğacını artırır"""
    data = load_data()
    user_id_str = str(user_id)
    
    if "players" in data and user_id_str in data["players"]:
        data["players"][user_id_str]['photos_received'] = data["players"][user_id_str].get('photos_received', 0) + 1
        save_data(data)
        return True
    return False

def user_exists(user_id):
    """İstifadəçinin bazada olub-olmadığını yoxlayır"""
    data = load_data()
    return "players" in data and str(user_id) in data["players"]
