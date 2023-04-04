import requests
import datetime
import time


while True:
    # 現在時刻を取得
    now = datetime.datetime.now()

    # Timestampの作成
    timestamp = now.strftime("%Y%m%d%H%M%S")
    
    #Jsonの取得
    url = "http://www.kmoni.bosai.go.jp/webservice/hypo/eew/{}.json".format(timestamp)
    response = requests.get(url)

    if response.status_code == 200:
        json_data = response.json()
        print(json_data)
    else:
        print("HTTP GET Request Failed: ", response.status_code)

    # 1秒待つ
    time.sleep(1)
