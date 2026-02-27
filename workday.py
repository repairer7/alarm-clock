import datetime
import os
import requests
from chinese_calendar import is_workday
from urllib.parse import quote

def check_and_notify():
    today = datetime.date.today()

    if is_workday(today):
        print(f"日期: {today} 是工作日 (含调休)，准备发送通知...")

        bark_host = os.environ.get("BARK_HOST")
        bark_key = os.environ.get("BARK_KEY")
        bark_title = "持续响铃"

        if not bark_host or not bark_key:
            print("环境变量 BARK_HOST 或 BARK_KEY 未配置，无法发送通知。")
            return

        bark_url = f"{bark_host}/{bark_key}/{quote(bark_title)}"

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
