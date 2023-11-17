import requests
import os

TOKEN = os.getenv('TOKEN')
CHATID = os.getenv('CHATID')

def send_telegram(text: str):
    url = "https://api.telegram.org/bot"
    url += TOKEN
    method = url + "/sendMessage"

    r = requests.post(method, data={
        "chat_id": CHATID,
        "text": text
    })

    if r.status_code != 200:
        raise Exception("post_text error")
