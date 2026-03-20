import requests
import time

TOKEN = "8276519624:AAHCboXuosrJCLcqQi6ZP4f0MT1xY7voPuk"
CHAT_ID = "741726963"
API_KEY = "4a3eacedc8fa46448e62978e993c0422"

PAIRS = ["EUR/USD","GBP/USD","USD/JPY","AUD/USD","USD/CAD","EUR/JPY"]

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_data(pair):
    url = f"https://api.twelvedata.com/time_series?symbol={pair}&interval=1min&outputsize=20&apikey={API_KEY}"
    data = requests.get(url).json()

    if "values" not in data:
        print("API ERROR:", data)
        return None

    return [float(x["close"]) for x in data["values"]][::-1]

def ema(data, p):
    k = 2/(p+1)
    e = data[0]
    for i in range(1,len(data)):
        e = data[i]*k + e*(1-k)
    return e

while True:

    best_signal = None

    for pair in PAIRS:
        d = get_data(pair)
        if not d:
            continue

        last = d[-1]
        prev = d[-2]

        trend = "BUY" if ema(d,10) > ema(d,20) else "SELL"
        direction = "BUY" if last > prev else "SELL"

        score = 0

        if trend == direction:
            score += 1

        if abs(last - prev) > 0.0002:
            score += 1

        if score >= 1:
            best_signal = (pair, direction, score)
            break

    if best_signal:
        pair, direction, score = best_signal

        probability = 60 + score * 15

        send(f"💣 LIVE SIGNAL\n{pair} {direction}\nWin%: {probability}%\n⏱ Entry: Next Candle")

    else:
        send("⚠️ No clear signal")

    time.sleep(60)
