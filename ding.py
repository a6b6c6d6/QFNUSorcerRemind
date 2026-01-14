import time, hmac, hashlib, base64, requests, json, os

TOKEN   = os.getenv("DING_TOKEN")
SECRET  = os.getenv("DING_SECRET", "")   # 如果机器人没开“加签”可留空

def _sign() -> str:
    if not SECRET:
        return ""
    ts = str(round(time.time() * 1000))
    string = f"{ts}\n{SECRET}"
    mac = hmac.new(SECRET.encode(), string.encode(), digestmod=hashlib.sha256).digest()
    return f"&timestamp={ts}&sign={base64.b64encode(mac).decode()}"

def send_md(title: str, text: str):
    url = f"https://oapi.dingtalk.com/robot/send?access_token={TOKEN}{_sign()}"
    data = {"msgtype": "markdown",
            "markdown": {"title": title, "text": text},
            "at": {"isAtAll": False}}
    requests.post(url, json=data, headers={"Content-Type": "application/json"})