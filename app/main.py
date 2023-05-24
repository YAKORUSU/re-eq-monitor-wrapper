from fastapi import FastAPI, Body
from starlette.websockets import WebSocket
import syslog
import asyncio

app = FastAPI()

# websocketで接続中のクライアントを識別するためのIDを格納
clients = {}

@app.get("/")
def read():
    return {"Result": "ok"}

@app.post("/")
async def post(body=Body(...)):

    #受けた震度が整数値表現できないため換算
    input_shindo = body["calcintencity"]
    shindo = {"1": 1, "2": 2, "3": 3, "4": 4, "5弱": 5.0, "5強": 5.5, "6弱": 6.0, "6強": 6.5, "7": 7}

    # 緊急地震速報がなりすぎると緊急性が失われるので震度3以上の地震のみ通知をするようにする
    if body["result.message"] == "" and body["report_num"] == "1" and shindo[input_shindo] >= 3:
        for client in clients.values():
            await client.send_text("{}".format(body))
        syslog.syslog(syslog.LOG_INFO, 'SentAlert:{}'.format(body))

    # 緊急地震速報以外はキャンセル扱いのだが送信をしてクライアント側で処理する
    elif body["result.message"] == "データがありません":
        for client in clients.values():
            await client.send_text("{}".format(body))
        syslog.syslog(syslog.LOG_DEBUG, 'SentCancelAlert:{}'.format(body))
    else:
        syslog.syslog(syslog.LOG_DEBUG, 'NotSentAlert:{}'.format(body))

    return {"Result": "ok", "Body": body}

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
