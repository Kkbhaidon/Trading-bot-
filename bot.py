import requests
import time

# ✅ YOUR DETAILS (already added)
TOKEN = "8276519624:AAHCboXuosrJCLcqQi6ZP4f0MT1xY7voPuk"
CHAT_ID = "741726963"
API_KEY = "4a3eacedc8fa46448e62978e993c0422"

PAIRS = ["EUR/USD","GBP/USD","USD/JPY","AUD/USD","USD/CAD","EUR/JPY"]

last_signal_time = 0

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_data(pair):
    url = f"https://api.twelvedata.com/time_series?symbol={pair}&interval=1min&outputsize=50&apikey={API_KEY}"
    data = requests.get(url).json()
    if "values" not in data:
        return None
    return [float(x["close"]) for x in data["values"]][::-1]

def ema(data, p):
    k = 2/(p+1)
    e = data[0]
    for i in range(1,len(data)):
        e = data[i]*k + e*(1-k)
    return e

def strong(data):
    return abs(data[-1] - data[-2]) > 0.0003

while True:
    sec = int(time.strftime("%S"))

    # 🔥 SNIPER WINDOW
    if sec >= 55:

        # ⛔ duplicate avoid
        if time.time() - last_signal_time < 60:
            time.sleep(1)
            continue

        for pair in PAIRS:
            d = get_data(pair)
            if not d:
                continue

            last = d[-1]
            prev = d[-2]

            trend = "BUY" if ema(d,20) > ema(d,50) else "SELL"
            direction = "BUY" if last > prev else "SELL"

            score = 0

            # 🔥 double confirmation
            if trend == direction:
                score += 2

            # ⚡ strong candle
            if strong(d):
                score += 2

            # 🎯 FINAL CONDITION
            if score >= 4:
                send(f"💣 SNIPER SIGNAL\n{pair} {direction}\nEntry: Next Candle")
                last_signal_time = time.time()
                break

    time.sleep(1)
