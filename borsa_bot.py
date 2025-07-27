from flask import Flask, render_template
import os
import threading
import time
import requests
import logging

# Logger ayarları
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger()

# === API Anahtarları ===
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Kontrol et, yoksa uyar
if not FINNHUB_API_KEY:
    logger.error("FINNHUB_API_KEY çevresel değişkeni ayarlı değil!")
if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN çevresel değişkeni ayarlı değil!")
if not TELEGRAM_CHAT_ID:
    logger.error("TELEGRAM_CHAT_ID çevresel değişkeni ayarlı değil!")

# === Takip Edilecek Hisseler ===
hisseler = [
    {"symbol": "AKBNK.IS", "target": 1.0},
    {"symbol": "THYAO.IS", "target": 1.0}
]

def fiyat_getir(symbol):
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        logger.debug(f"{symbol} verisi: {data}")
        return data.get('c')
    except Exception as e:
        logger.warning(f"{symbol} için veri alınamadı: {e}")
        return None

def telegram_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mesaj
    }
    try:
        r = requests.post(url, data=payload, timeout=5)
        if not r.ok:
            logger.error(f"Telegram mesajı gönderilemedi: {r.text}")
    except Exception as e:
        logger.error(f"Telegram gönderim hatası: {e}")

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
    # templates/index.html dosyasını döner
    return render_template("index.html")

if __name__ == "__main__":
    # Bot takibini ayrı thread'de başlat
    thread = threading.Thread(target=takip_et, daemon=True)
    thread.start()

    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Flask server {port} portunda başlatılıyor...")
    app.run(host="0.0.0.0", port=port)
