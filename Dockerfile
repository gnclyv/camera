FROM python:3.11-slim

# İşçi qovluğunu təyin et
WORKDIR /app

# Əvvəlcə requirements.txt faylını köçür və quraşdır (bu, deploy-u sürətləndirir)
COPY TelegramCameraBot_v2/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# İndi bütün digər kodları köçür
COPY . .

# Botu işə sal (faylın yolu: qovluq_adı/fayl_adı)
CMD ["python", "TelegramCameraBot_v2/telegram_bot_v2.py"]
