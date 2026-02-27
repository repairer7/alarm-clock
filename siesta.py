import datetime
import requests
import json
from chinese_calendar import is_workday

def check_and_notify():
    # 1. 获取今天的日期
    today = datetime.date.today()
    #today = datetime.date.today() + datetime.timedelta(days=1)

    # 2. 判断是否是工作日
    if is_workday(today):
        print(f"日期: {today} 是工作日 (含调休)，继续检查距离...")

        # 3. 读取 /opt/workday/distance.json
        try:
            with open("/opt/workday/distance.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                distance = data.get("distance", None)
        except Exception as e:
            print(f"读取 distance.json 出错: {e}")
            return

        # 4. 判断距离是否小于 1
        if distance is not None and distance < 1:
            print(f"距离: {distance} < 1，准备发送通知...")

            # 5. 执行 Bark 通知
            bark_url = "https://bark.imtsui.com/KJrVzNCWPKdfV9ykYWsb2k/%E6%8C%81%E7%BB%AD%E5%93%8D%E9%93%83?call=1&level=critical&group=Alarm&isArchive=0"
            params = {
                "call": "1",
                "level": "critical"
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