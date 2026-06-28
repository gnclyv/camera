# 🎯 Telegram Kamera Bot v2.0 - Global Paylaşma Sistemi

## Nə Dəyişdi?

**v1.0 (Eski):**
- Bot hər dəfə link göndərir
- Sadəcə təkrar istifadə edilmir

**v2.0 (YENİ) ✨:**
- Hər istifadəçi **ÖZƏL GLOBAL LINK** alır
- Link **sonsuz sayda** istifadə edilə bilər
- **Başqa kimsə** şəkil çəkən zaman, **link sahibinə** gedir
- Şəkilləri **faylda** saxlayır

---

## 🎯 Sistem Necə İşləyir

```
ALİ (Bot'u başlatan)
  ↓
  /start yazır
  ↓
Bot: "Özəl linkini kopyala"
https://site.com/share?user_id=ali_id
  ↓
  ALİ bu linki VƏLİ-yə göndərir
  ↓
VƏLİ linki açır
  ↓
  Kamera icazəsi verir
  ↓
  Şəkil çəkir
  ↓
  GÖNDƏR düyməsi
  ↓
ALİ-NİN TELEGRAMINA ŞƏKİL GƏLƏR! ✅
  (Vəli-yə DEYİL, ALİ-YƏ!)
```

---

## 📥 Quraşdırma

### 1. Yeni Bot Kodunu Aç

**Köhnə faylı əvəz et:**
```bash
# Köhnə
# telegram_bot.py

# YENİ
telegram_bot_v2.py
```

### 2. Tokeni və URL-i Düzəlt

`telegram_bot_v2.py` açıb:

```python
BOT_TOKEN = "8069501498:AAExx7_1QkbFWLAkBcWZF7JNMKrpIo0uWCg"
WEBHOOK_URL = "https://gender-epiphany-serpent.ngrok-free.dev"
```

Dəyişdir:

```python
BOT_TOKEN = "SENIN_TOKENIN"
WEBHOOK_URL = "https://senin-ngrok-urlin"
```

### 3. Bot'u Çalışdır

```bash
python telegram_bot_v2.py
```

Terminal mesajı:
```
Bot started successfully!
Share links format: https://gender-epiphany-serpent.ngrok-free.dev/share?user_id=USER_ID
```

---

## 🚀 İstifadə

### ALİ (Başlatan):

1. Telegram-da bot axtarıb `/start` yazır
2. Bot özəl link göndərir:
   ```
   https://gender-epiphany-serpent.ngrok-free.dev/share?user_id=123456789
   ```
3. **Linki kopyala** düyməsinə kliklə
4. Linki Vəli-yə/başqasına göndər

### VƏLİ (Şəkil Çəkən):

1. Linki açır (`https://site.com/share?user_id=xxx`)
2. **🎥 Kameraı Başlat** düyməsi kliklə
3. Kamera icazəsi verir
4. **📸 Şəkil Çək** düyməsi kliklə
5. Şəkili bax
6. **✓ Göndər** düyməsi kliklə

### ALİ-NIN TELEGRAMINDA:

```
📸 Yeni Şəkil Alındı!
⏰ 2026-06-28 01:32:15
[ŞƏKIL]
```

**Hazır!** ✅

---

## 📁 Saxlama Sistemi

### `users.json`:
```json
{
  "123456789": {
    "name": "Ali",
    "telegram_id": 123456789,
    "joined": "2026-06-28T01:30:00",
    "photos_received": 5
  }
}
```

### `photos.json`:
```json
{
  "abc12345": {
    "user_id": "123456789",
    "timestamp": "2026-06-28T01:32:00",
    "photo": "data:image/jpeg;base64,..."
  }
}
```

**Bu fayllar bot kalosunun **yanında** yaranacaq!**

---

## ✨ Xüsusiyyətlər

✅ **Qlobal Link** - Hər istifadəçi özəl link alır  
✅ **Sonsuz Istifadə** - Link istənilən sayda istifadə edilə bilər  
✅ **Hər Kəs Açıb Şəkil Çəkə Bilər** - Qeydiyyat tələb etmir  
✅ **Otomatik Göndərmə** - Şəkil link sahibinə gedir  
✅ **Faylda Saxlama** - Database tələb etmir  
✅ **Saymaç** - Neçə şəkil aldığını bilir  

---

## 🔒 Təhlükəsizlik

- **Linki açıq tutma** - Sadəcə güvənən adamlara göndər
- **Şəkilləri Sil** - `photos.json` faylını sil (istəsən)
- **İstifadəçiləri Sil** - `users.json` faylını düzəlt

---

## 🐛 Problemlərin Həlli

### "Link işləmir"
- ngrok çalışır mı? (`.\ngrok http 5000`)
- Bot çalışır mı? (`python telegram_bot_v2.py`)
- URL düzgün mü?

### "Şəkil gəlmir"
- Bot tokeni doğru mu?
- Telegram hesabı doğru mu?
- Internet bağlantısı var mı?

### "Kamera icazəsi rədd edildi"
- Chrome/Firefox istifadə et
- Brauzer kamera icazəsini yoxla
- Mobil telefondan cəhd et

---

## 📊 Faylları Yedəklə

**Şəkilləri saxlamaq üçün:**
```bash
# Şəkillərin sayını yoxla
type photos.json

# Yedək yarat
copy photos.json photos_backup.json
```

---

## 🎉 Hər şey Hazır!

1. ✅ Bot çalışır
2. ✅ Link sabitdir
3. ✅ Hər kəs istifadə edə bilər
4. ✅ Şəkilləri faylda saxlanır

**Başla! 🚀**

---

## 📝 Yeniliklərin Qısa Xülasəsi

| Xüsusiyyət | v1.0 | v2.0 |
|-----------|------|------|
| Qlobal Link | ❌ | ✅ |
| Təkrarlanan İstifadə | ❌ | ✅ |
| Şəkil Sayısı | Məhdud | ♾️ |
| Hər Kəs Açıb Çəkə Bilər | ❌ | ✅ |
| Faylda Saxlama | ❌ | ✅ |
| Database Tələbi | ✅ | ❌ |

---

**Istifadə! 🎉**
