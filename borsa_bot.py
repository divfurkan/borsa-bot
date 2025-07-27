from flask import Flask, render_template
import os
import threading
import time
import requests
import logging

# Logger ayarları
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()

# === API Anahtarları ===
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# === Hisse Listesi ===
hisseler = [
    {"symbol": "AKBNK.IS", "target": 1.0},
    {"symbol": "THYAO.IS", "target": 1.0}
]

# === Fiyat Getirme ===
def fiyat_getir(symbol):
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        r = requests.get(url)
        data = r.json()
        logger.debug(f"{symbol} verisi: {data}")
        return data.get('c')
    except Exception as e:
        logger.warning(f"{symbol} için veri alınamadı: {e}")
        return None

# === Telegram Bildirimi ===
def telegram_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mesaj
    }
    try:
        r = requests.post(url, data=payload)
        if not r.ok:
            logger.error(f"Telegram mesajı gönderilemedi: {r.text}")
    except Exception as e:
        logger.error(f"Telegram gönderim hatası: {e}")

# === Hisse Takibi ===
def takip_et():
    logger.info("📡 Takip başlatıldı...")
    while True:
        for hisse in hisseler:
            fiyat = fiyat_getir(hisse["symbol"])
            if fiyat is not None:
                logger.info(f"{hisse['symbol']}: {fiyat} TL")
                if fiyat >= hisse["target"]:
                    mesaj = f"📈 {hisse['symbol']} hedefe ulaştı!\nFiyat: {fiyat} TL, Hedef: {hisse['target']} TL"
                    telegram_gonder(mesaj)
                    hisse["target"] = float('inf')  # Tekrar bildirim göndermesin
            else:
                logger.warning(f"{hisse['symbol']} için fiyat alınamadı.")
        time.sleep(5)  # 5 saniyede bir kontrol

# === Flask Web Uygulaması ===
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")  # templates/index.html dosyasını yükler

# === Uygulama Başlatma ===
if __name__ == "__main__":
    thread = threading.Thread(target=takip_et)
    thread.daemon = True
    thread.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
