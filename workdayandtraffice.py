import datetime
import requests
from chinese_calendar import is_workday

# ======= 配置 =======
AK = "C3Rv5rELHCBrbwKtCC8byAHK9KVflP11"

origin_addr = "苏州市相城区绿地都会雅苑"
destination_addr = "苏州市燃气大厦"

# Bark 推送 URL
BARK_URL = "https://bark.imtsui.com/KJrVzNCWPKdfV9ykYWsb2k/%E6%8C%81%E7%BB%AD%E5%93%8D%E9%93%83?call=1&level=critical&group=Alarm&isArchive=0"


# ======= 地址转坐标 =======
def geocode(address):
    url = "https://api.map.baidu.com/geocoding/v3/"
    params = {
        "address": address,
        "output": "json",
        "ak": AK
    }
    r = requests.get(url, params=params)
    data = r.json()
    if data["status"] != 0:
        raise Exception(f"Geocoding failed: {data}")

    loc = data["result"]["location"]

    # DirectionLite 要求 lat,lng
    return f"{loc['lat']},{loc['lng']}"


# ======= 驾车路线规划 =======
def get_drive_time(origin, destination):
    url = "https://api.map.baidu.com/directionlite/v1/driving"
    params = {
        "origin": origin,
        "destination": destination,
        "ak": AK
    }
    r = requests.get(url, params=params)
    data = r.json()

    if data["status"] != 0:
        raise Exception(f"Direction API failed: {data}")

    route = data["result"]["routes"][0]
    duration_sec = route["duration"]
    duration_min = round(duration_sec / 60, 1)

    return duration_sec, duration_min


# ======= Bark 推送 =======
def send_bark(msg):
    try:
        response = requests.get(BARK_URL, params={"body": msg}, timeout=10)
        if response.status_code == 200:
            print("Bark 通知发送成功！")
        else:
            print(f"Bark 通知失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"Bark 请求错误: {e}")


# ======= 主流程 =======
def check_and_notify():
    today = datetime.date.today()

    # 1. 判断是否工作日
    if not is_workday(today):
        print(f"日期: {today} 是休息日，无需检查通勤。")
        return

    print(f"日期: {today} 是工作日，开始检查通勤时间...")

    # 2. 获取坐标
    origin = geocode(origin_addr)
    destination = geocode(destination_addr)

    # 3. 获取驾车时间
    sec, mins = get_drive_time(origin, destination)
    print(f"当前驾车时间：{mins} 分钟")

    # 4. 判断是否超过 40 分钟
    if mins > 40:
        print("通勤时间超过 40 分钟，发送 Bark 通知...")
        send_bark(f"通勤时间过长：{mins} 分钟")
    else:
        print("通勤时间正常，无需通知。")


if __name__ == "__main__":
    check_and_notify()