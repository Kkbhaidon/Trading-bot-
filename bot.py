import requests
import time

TOKEN = "8276519624:AAHCboXuosrJCLcqQi6ZP4f0MT1xY7voPuk"
CHAT_ID = "741726963"
API_KEY = "4a3eacedc8fa46448e62978e993c0422"

PAIRS = ["EUR/USD","GBP/USD","USD/JPY","AUD/USD","USD/CAD","EUR/JPY"]

history = []
results = []

wins = 0
losses = 0

pair_stats = {p: {"win":0, "loss":0} for p in PAIRS}

pending = None

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_data(pair):
    url = f"https://api.twelvedata.com/time_series?symbol={pair}&interval=1min&outputsize=20&apikey={API_KEY}"
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

def pair_accuracy(pair):
    stat = pair_stats[pair]
    total = stat["win"] + stat["loss"]
    if total == 0:
        return 50
    return (stat["win"] / total) * 100

def check_result():
    global pending, wins, losses

    if not pending:
        return

    d = get_data(pending["pair"])
    if not d:
        return

    latest = d[-1]

    win = (pending["dir"] == "BUY" and latest > pending["entry"]) or \
          (pending["dir"] == "SELL" and latest < pending["entry"])

    if win:
        wins += 1
        pair_stats[pending["pair"]]["win"] += 1
        result = "✅ WIN"
    else:
        losses += 1
        pair_stats[pending["pair"]]["loss"] += 1
        result = "❌ LOSS"

    results.append(f"{pending['pair']} → {result}")

    if len(results) > 5:
        results.pop(0)

    pending = None

while True:

    sec = int(time.strftime("%S"))

    if sec == 59:
        check_result()

    if sec == 0:

        best = None

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
                score += 2

            if abs(last - prev) > 0.0002:
                score += 1

            # 🔥 AI BOOST
            acc = pair_accuracy(pair)

            if acc > 70:
                score += 2
            elif acc > 60:
                score += 1

            if not best or score > best["score"]:
                best = {
                    "pair": pair,
                    "dir": direction,
                    "score": score,
                    "entry": last,
                    "acc": acc
                }

        if best:

            probability = int((best["score"] * 10) + best["acc"] / 2)

            history.append(f"{best['pair']} {best['dir']}")
            if len(history) > 5:
                history.pop(0)

            total = wins + losses
            overall_acc = round((wins/total)*100,2) if total>0 else 0

            send(f"""🤖 AI SIGNAL
{best['pair']} {best['dir']}

📊 Pair Accuracy: {round(best['acc'],1)}%
🎯 AI Win%: {probability}%

📈 Overall Accuracy: {overall_acc}%

⏱ Entry: Now""")

            pending = best

    time.sleep(1)
