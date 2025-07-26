import yfinance as yf
import requests
import time

# === TELEGRAM AYARLARI ===
TELEGRAM_BOT_TOKEN = "8213753796:AAGhNJjmJy6yGx9gA1wqCJk-hgLhVn52ouI"
TELEGRAM_CHAT_ID = "CHAT_ID_BURAYA_YAZ"  # Lütfen buraya kendi chat ID’ni yapıştır

# === TAKİP EDECEĞİN BIST HİSSELERİ ===
hisseler = [
    {"symbol": "AKBNK.IS", "target": 17.5},
    {"symbol": "THYAO.IS", "target": 295},
    {"symbol": "SISE.IS", "target": 57},
    {"symbol": "ASELS.IS", "target": 67.2},
    {"symbol": "KRDMD.IS", "target": 27.1}
]

def fiyat_getir(symbol):
    try:
        hisse = yf.Ticker(symbol)
        data = hisse.history(period="1d")
        return round(data['Close'].iloc[-1], 2)
    except Exception as e:
        print(f"⚠️ {symbol} için fiyat alınamadı: {e}")
        return None

def telegram_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mesaj}
    response = requests.post(url, data=payload)
    if not response.ok:
        print(f"❌ Telegram mesajı gönderilemedi: {response.text}")

def takip_et():
    print("🔍 Takip başladı...")
    while True:
        for hisse in hisseler:
            fiyat = fiyat_getir(hisse["symbol"])
            if fiyat is not None:
                print(f"{hisse['symbol']}: {fiyat} TL")
                if fiyat >= hisse["target"]:
                    mesaj = f"📈 {hisse['symbol']} hedefe ulaştı!\nFiyat: {fiyat} TL, Hedef: {hisse['target']} TL"
                    telegram_gonder(mesaj)
                    hisse["target"] = float('inf')  # tekrar bildirmesin
        time.sleep(5)  # 5 saniyede bir kontrol

if __name__ == "__main__":
    takip_et()
