import datetime
import os
import json
import requests
from chinese_calendar import is_workday
from urllib.parse import quote

def check_and_notify():
    today = datetime.date.today()

    if is_workday(today):
        print(f"日期: {today} 是工作日 (含调休)，继续检查距离...")

        # 读取仓库内的 distance.json
        try:
            with open("distance.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                distance = data.get("distance", None)
        except Exception as e:
            print(f"读取 distance.json 出错: {e}")
            return

        if distance is not None and distance < 1:
            print(f"距离: {distance} < 1，准备发送通知...")

            # 从 Secrets 读取 Bark 配置
            bark_host = os.environ.get("BARK_HOST")
            bark_key = os.environ.get("BARK_KEY")
            bark_title = "持续响铃"

            if not bark_host or not bark_key:
                print("BARK_HOST 或 BARK_KEY 未配置，无法发送通知。")
                return

            # 清洗 host
            bark_host = bark_host.strip().lstrip("/").rstrip("/")

            # 强制加 https://
            bark_url = f"https://{bark_host}/{bark_key}/{quote(bark_title)}"

            print("即将请求的 Bark URL:", bark_url.replace(bark_key, "***"))

            params = {
                "call": "1",
                "level": "critical",
                "group": "Alarm",
                "isArchive": "0",
            }

            try:
                response = requests.get(bark_url, params=params, timeout=10)
                if response.status_code == 200:
                    print("通知发送成功！")
                else:
                    print(f"通知发送失败，状态码: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"请求发生错误: {e}")
        else:
            print(f"距离: {distance} >= 1，不触发通知。")
    else:
        print(f"日期: {today} 是休息日或法定节假日，无需工作。")

if __name__ == "__main__":
    check_and_notify()
