import datetime
import requests
from chinese_calendar import is_workday

def check_and_notify():
    # 1. 获取今天的日期
    today = datetime.date.today()
    #today = datetime.date.today() + datetime.timedelta(days=1)
    # 2. 判断是否是工作日
    # is_workday() 包含了所有逻辑：
    # -如果是周一到周五且不是节假日 -> True
    # -如果是周末但是要"补班" (调休) -> True
    # -如果是法定节假日 -> False
    if is_workday(today):
        print(f"日期: {today} 是工作日 (含调休)，准备发送通知...")
        
        # 3. 执行 Bark 通知
        bark_url = "https://bark.imtsui.com/KJrVzNCWPKdfV9ykYWsb2k/%E6%8C%81%E7%BB%AD%E5%93%8D%E9%93%83?call=1&level=critical&group=Alarm&isArchive=0"
        params = {
            "call": "1",
            "level": "critical"
        }
        
        try:
            # 发送 GET 请求，等同于 curl
            response = requests.get(bark_url, params=params, timeout=10)
            
            if response.status_code == 200:
                print("通知发送成功！")
            else:
                print(f"通知发送失败，状态码: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"请求发生错误: {e}")
            
    else:
        print(f"日期: {today} 是休息日或法定节假日，无需工作。")

if __name__ == "__main__":
    check_and_notify()