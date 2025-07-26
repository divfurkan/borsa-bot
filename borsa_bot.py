from flask import Flask
import os
import threading
import time
import requests

# === KENDİ BİLGİLERİNİ BURAYA GİR ===
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

hisseler = [
    {"symbol": "AKBNK.IS", "target": 17.5},
    {"symbol": "THYAO.IS", "target": 295},
    {"symbol": "SISE.IS", "target": 57},
    {"symbol": "ASELS.IS", "target": 67.2},
    {"symbol": "KRDMD.IS", "target": 27.1}
]

def fiyat_getir(symbol):
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        r = requests.get(url)
        data = r.json()
        return data.get('c')
    except Exception as e:
        print(f"⚠️ {symbol} için veri alınamadı: {e}")
        return None

def telegram_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mesaj
    }
    try:
        r = requests.post(url, data=payload)
        if not r.ok:
            print(f"❌ Telegram mesajı gönderilemedi: {r.text}")
    except Exception as e:
        print(f"❌ Telegram gönderim hatası: {e}")

def takip_et():
    print("📡 Takip başlatıldı...")
    while True:
        for hisse in hisseler:
            fiyat = fiyat_getir(hisse["symbol"])
            if fiyat:
                print(f"{hisse['symbol']}: {fiyat} TL")
                if fiyat >= hisse["target"]:
                    mesaj = f"📈 {hisse['symbol']} hedefe ulaştı!\nFiyat: {fiyat} TL, Hedef: {hisse['target']} TL"
                    telegram_gonder(mesaj)
                    hisse["target"] = float('inf')  # Tekrar bildirim göndermesin
            else:
                print(f"⚠️ {hisse['symbol']} için fiyat alınamadı.")
        time.sleep(5)  # 5 saniyede bir kontrol

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot çalışıyor."

if __name__ == "__main__":
    # Bot takibini ayrı thread olarak çalıştır
    thread = threading.Thread(target=takip_et)
    thread.daemon = True
    thread.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
