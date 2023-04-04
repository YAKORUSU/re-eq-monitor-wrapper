import requests
import datetime
import time
from fastapi import FastAPI
from starlette.websockets import WebSocket
import syslog

app = FastAPI()
#取得したJsonを格納
body = {}
# websocketで接続中のクライアントを識別するためのIDを格納
clients = {}


def getjson():
    while True:
        # 現在時刻を取得
        now = datetime.datetime.now()

        # Timestampの作成
        timestamp = now.strftime("%Y%m%d%H%M%S")
        
        #Jsonの取得
        url = "http://www.kmoni.bosai.go.jp/webservice/hypo/eew/{}.json".format(timestamp)
        response = requests.get(url)

        # 発報判定
        if response.status_code == 200:
            body = response.json()
            if body["type"] == "eew" and body["report"] == "1" and int(body["intensity"]) >= 3:
                for client in clients.values():
                    await client.send_text("{}".format(body))
                syslog.syslog(syslog.LOG_INFO, 'SentAlert:{}'.format(body))

            # 緊急地震速報のキャンセル情報は送信してクライアント側で処理
            elif body["type"] == "pga_alert_cancel":
                for client in clients.values():
                    await client.send_text("{}".format(body))
                syslog.syslog(syslog.LOG_DEBUG, 'SentCancelAlert:{}'.format(body))
            else:
                syslog.syslog(syslog.LOG_DEBUG, 'NotSentAlert:{}'.format(body))
        else:
            print("HTTP GET Request Failed: ", response.status_code)

        # 1秒待つ
        time.sleep(1)

@app.get("/")
def read():
    return {"Result": "ok"}

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    # クライアントを識別するためのIDを取得
    key = ws.headers.get('sec-websocket-key')
    clients[key] = ws

    # TODO debuglog
    syslog.syslog(syslog.LOG_DEBUG, 'ConnectedClientList:{}'.format(clients))

    try:
        while True:
            data = await ws.receive_text()
    except Exception as e:
        syslog.syslog(syslog.LOG_DEBUG, '{}:{}'.format(type(e),e))
        # TODO close状態で下記のコネクションクローズするとさらにRuntimeError出るのでコメントアウト中
        #await ws.close()
        del clients[key]
