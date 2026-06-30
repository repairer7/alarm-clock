import datetime
import os
import json
import requests
from chinese_calendar import is_workday
from urllib.parse import quote

def check_and_notify():
    today = datetime.date.today()

    if is_workday(today):
        print(f"日期: {today} 是工作日 (含调休)，准备检查闹铃开关...")

        # --- 新增：读取 whetheralarm.json 状态 ---
        alarm_switch = "yes"  # 默认值，如果文件缺失或读取失败，默认允许响铃
        try:
            if os.path.exists("whetheralarm.json"):
                with open("whetheralarm.json", "r", encoding="utf-8") as f:
                    alarm_data = json.load(f)
                    # 转为字符串、去空格、转小写，提高容错率
                    alarm_switch = str(alarm_data.get("whetheralarm", "yes")).strip().lower()
            else:
                print("未找到 whetheralarm.json，将默认执行响铃逻辑。")
        except Exception as e:
            print(f"读取 whetheralarm.json 出错: {e}，将默认执行响铃逻辑。")

        # 如果开关被明确设置为 no，则直接拦截
        if alarm_switch == "no":
            print("检测到 whetheralarm.json 设置为 'no'，已关闭本次闹铃通知。")
            return
        # ----------------------------------------

        print("闹铃开关已开启，准备发送通知...")

        bark_host = os.environ.get("BARK_HOST")  # 建议只填域名，比如 bark.imtsui.com
        bark_key = os.environ.get("BARK_KEY")
        bark_title = "持续响铃"

        if not bark_host or not bark_key:
            print("环境变量 BARK_HOST 或 BARK_KEY 未配置，无法发送通知。")
            return

        # 只保留主机部分，去掉前后的空格和斜杠
        bark_host = bark_host.strip().lstrip("/").rstrip("/")

        # 无论你 Secrets 里写没写 https://，这里都强制加上
        bark_url = f"https://{bark_host}/{bark_key}/{quote(bark_title)}"

        # 打印时把 key 打码，方便你确认 URL 结构
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
