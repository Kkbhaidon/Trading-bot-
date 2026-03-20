import requests
import time

TOKEN = "8276519624:AAHCboXuosrJCLcqQi6ZP4f0MT1xY7voPuk"
CHAT_ID = "741726963"
API_KEY = "4a3eacedc8fa46448e62978e993c0422"

PAIRS = ["EUR/USD","GBP/USD","USD/JPY","AUD/USD","USD/CAD","EUR/JPY"]

last_signal_time = 0
pending_signal = None

wins = 0
losses = 0
balance = 10
trade_amount = 1

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_data(pair):
    url = f"https://api.twelvedata.com/time_series?symbol={pair}&interval=1min&outputsize=30&apikey={API_KEY}"
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
    return abs(data[-1] - data[-2]) > 0.0002

def adjust_trade():
    global trade_amount, wins, losses
    total = wins + losses
    if total < 5:
        return
    winrate = (wins / total) * 100
    if winrate > 70:
        trade_amount *= 1.2
    elif winrate < 50:
        trade_amount *= 0.8
    if trade_amount < 1:
        trade_amount = 1

def check_result():
    global pending_signal, wins, losses, balance

    if not pending_signal:
        return

    d = get_data(pending_signal["pair"])
    if not d:
        return

    latest = d[-1]
    entry = pending_signal["entry"]

    win = (pending_signal["dir"] == "BUY" and latest > entry) or \
          (pending_signal["dir"] == "SELL" and latest < entry)

    if win:
        wins += 1
        balance += trade_amount * 0.8
        result = "✅ WIN"
    else:
        losses += 1
        balance -= trade_amount
        result = "❌ LOSS"

    adjust_trade()

    send(f"📊 RESULT\n{result}\nBalance: ${round(balance,2)}\nWin: {wins} | Loss: {losses}")

    pending_signal = None

while True:
    sec = int(time.strftime("%S"))

    # 🔥 PRE SIGNAL
    if sec >= 50 and pending_signal is None:

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

            if trend == direction:
                score += 2
            if strong(d):
                score += 1

            if score >= 2:
                probability = min(90, 50 + score * 15)

                pending_signal = {
                    "pair": pair,
                    "dir": direction,
                    "prob": probability,
                    "entry": last
                }

                send(f"⏳ PRE SIGNAL\n{pair} {direction}\nWin%: {probability}%")
                break

    # 🚀 ENTRY ALERT
    if sec == 0 and pending_signal:
        send(f"🚀 ENTER NOW\n{pending_signal['pair']} {pending_signal['dir']}\nWin%: {pending_signal['prob']}%\nTrade: ${round(trade_amount,2)}")
        last_signal_time = time.time()

    # 📊 RESULT CHECK (after 1 min)
    if sec == 59:
        check_result()

    time.sleep(1)
