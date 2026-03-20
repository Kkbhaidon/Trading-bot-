import requests
import time

TOKEN = "8276519624:AAHCboXuosrJCLcqQi6ZP4f0MT1xY7voPuk"
CHAT_ID = "741726963"

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

while True:
    send("✅ Bot Working - Test Message")
    time.sleep(60)
