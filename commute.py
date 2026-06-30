import datetime
import os
import json
import requests
from chinese_calendar import is_workday
from urllib.parse import quote

AK = os.environ.get("BAIDU_AK")
BARK_HOST = os.environ.get("BARK_HOST")
BARK_KEY = os.environ.get("BARK_KEY")

origin_addr = os.environ.get("ORIGIN_ADDR")
destination_addr = os.environ.get("DESTINATION_ADDR")

def geocode(address):
    url = "https://api.map.baidu.com/geocoding/v3/"
    params = {
        "address": address,
        "output": "json",
        "ak": AK
    }
    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    if data["status"] != 0:
        raise Exception(f"Geocoding failed: {data}")

    loc = data["result"]["location"]
    return f"{loc['lat']},{loc['lng']}"

def get_drive_time(origin, destination):
    url = "https://api.map.baidu.com/directionlite/v1/driving"
    params = {
        "origin": origin,
        "destination": destination,
        "ak": AK
    }
    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    if data["status"] != 0:
        raise Exception(f"Direction API failed: {data}")

    route = data["result"]["routes"][0]
    duration_sec = route["duration"]
    duration_min = round(duration_sec / 60, 1)

    return duration_sec, duration_min

def send_bark(msg):
    if not BARK_HOST or not BARK_KEY:
        print("BARK_HOST 或 BARK_KEY 未配置，无法发送 Bark 通知。")
        return

    host = BARK_HOST.strip().lstrip("/").rstrip("/")
    bark_url = f"https://{host}/{BARK_KEY}/{quote('通勤提醒')}"

    print("即将请求的 Bark URL:", bark_url.replace(BARK_KEY, "***"))

    params = {
        "body": msg,
        "call": "1",
        "level": "critical",
        "group": "Alarm",
        "isArchive": "0",
    }

    try:
        response = requests.get(bark_url, params=params, timeout=10)
        if response.status_code == 200:
            print("Bark 通知发送成功！")
        else:
            print(f"Bark 通知失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"Bark 请求错误: {e}")

def check_and_notify():
    today = datetime.date.today()

    if not is_workday(today):
        print(f"日期: {today} 是休息日，无需检查通勤。")
        return

    print(f"日期: {today} 是工作日，准备检查闹铃总开关...")

    # --- 新增：读取 whetheralarm.json 状态 ---
    alarm_switch = "yes"  # 默认值，文件不存在或读取失败时默认开启
    try:
        if os.path.exists("whetheralarm.json"):
            with open("whetheralarm.json", "r", encoding="utf-8") as f:
                alarm_data = json.load(f)
                # 转换为字符串、去空格、转小写，防止大小写或空格导致匹配失败
                alarm_switch = str(alarm_data.get("whetheralarm", "yes")).strip().lower()
        else:
            print("未找到 whetheralarm.json，将默认执行通勤检查逻辑。")
    except Exception as e:
        print(f"读取 whetheralarm.json 出错: {e}，将默认执行通勤检查逻辑。")

    # 如果开关被明确设置为 no，则直接拦截并退出
    if alarm_switch == "no":
        print("检测到 whetheralarm.json 设置为 'no'，已关闭本次闹铃与通勤检查。")
        return
    # ----------------------------------------

    print("闹铃开关已开启，开始调用地图 API 检查通勤时间...")

    origin = geocode(origin_addr)
    destination = geocode(destination_addr)

    sec, mins = get_drive_time(origin, destination)
    print(f"当前驾车时间：{mins} 分钟")

    if mins > 40:
        print("通勤时间超过 40 分钟，发送 Bark 通知...")
        send_bark(f"当前通勤时间：{mins} 分钟，已超过阈值 35 分钟")
    else:
        print("通勤时间正常，无需通知。")

if __name__ == "__main__":
    check_and_notify()
