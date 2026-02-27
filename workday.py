import datetime
import os
import requests
from chinese_calendar import is_workday
from urllib.parse import quote

def check_and_notify():
    today = datetime.date.today()

    if is_workday(today):
        print(f"日期: {today} 是工作日 (含调休)，准备发送通知...")

        bark_host = os.environ.get("BARK_HOST")  # 建议只填 bark.imtsui.com
        bark_key = os.environ.get("BARK_KEY")
        bark_title = "持续响铃"

        if not bark_host or not bark_key:
            print("环境变量 BARK_HOST 或 BARK_KEY 未配置，无法发送通知。")
            return

        # 去掉空格和斜杠
        bark_host = bark_host.strip().lstrip("/").rstrip("/")

        # 🔥 强制加上 https:// —— 无论你 Secrets 里写没写
        bark_url = f"https://{bark_host}/{bark_key}/{quote(bark_title)}"

        # 打印时隐藏 key
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
                print(f"通知发送失败，状态码: {response.status_code}，响应内容: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"请求发生错误: {e}")

    else:
        print(f"日期: {today} 是休息日或法定节假日，无需工作。")

if __name__ == "__main__":
    check_and_notify()
