# re-eq-monitor-wrapper

## Motivation

2022年夏以来NeosVRにて稼働していたEEWシステムにおいてGoogleChromeの拡張機能の「[強震モニタ](https://chrome.google.com/webstore/detail/%E5%BC%B7%E9%9C%87%E3%83%A2%E3%83%8B%E3%82%BF-extension/ghkclpkmplddbagagffmmcmdbgjecbbj?hl=ja)」というもを利用していたが誰か常にPCを立ち上げていなければいけないという難点があった。  
よくよく調べてみると、強震モニターにはJsonを直接取得する術があり、取得したJsonの比較を用いて速報の発報を行えると考えた。
元々中継サーバとして使用していたサーバーに、Jsonの取得を追加し利用者負担の軽減を図ることにした。

## Overview

緊急地震速報をWebsocketにて接続しているクライアントに通知するためのWrapperである。
このWebアプリでは下記の機能を提供予定。

- 強震モニタからJSONをGETするクライアント
- 緊急地震速報をNeosVR内から受け取るためのWebsocketのエンドポイント

強震モニタは地震情報をJson形式で公開している。

## Json詳細

### リクエスト形式
```shell
GET http://www.kmoni.bosai.go.jp/webservice/hypo/eew/${timestamp}.json
```

`${timestamp}`部分は、`YYYYMMDDhhmmss`フォーマット

### 応答内容


| 要素名 | 型	| 説明･備考 |	例 |
| :--- | :--- | :--- | :--- |
| `result.message` |	string |	地震発生時は空文字列になり、それ以外のときは"データがありません"となる。 |	`""` |
| `report_time` |	string |	情報更新時刻(YYYY/MM/DD hh:mm:dd形式) |	`"2019/07/15 01:30:59"` |
| `report_id` |	string |	地震ID |	`"20190715013049"` |
| `origin_time` |	string |	地震発生時刻 |	`"20190715013043"` |
| `report_num` |	string |	第n報 |	`"2"` |
| `region_name` |	string |	震源地 |	`"千葉県北東部"` |
| `latitude` |	string |	緯度(北緯) | `"35.7"` |
| `longitude` |	string |	経度(東経) | `"140.7"` |
| `depth` |	string | 震源の深さ | `"20km"` |
| `calcintensity` |	string |	最大震度 |	`"5弱"` |
| `magunitude` | string |	マグニチュード |	`"3.8"` |
| `is_final` | boolean |	最終報か否か |	`false` |
| `is_cancel` |	boolean |	キャンセル報か否か(未利用?) |	`false` |
| 'is_training` |	boolean |	訓練報か否か | `false` |


## Infrastructure

<--!　### 論理構成図
// TODO

### WebAPIエンドポイント
// TODO

### サーバ情報

- ConoHaVPS (vCPU:1,Mem:512MB)

"変更なし"

#### webサーバ

- nginx
  - 443にてListen
  - 証明書はLet's Encrypt
  
"変更なし"

#### ASGIサーバ

- gunicorn
- uvicorn

"変更なし"

##### プロセス管理

- systemdにてgunicornをデーモン化
- gunicornではuvicornをマルチプロセス化して起動

"変更なし"

### Pythonのバージョン管理

- pyenvを利用
- systemdにて起動

"変更なし"

#### ファイアウォール

- ufwにて制御

"変更なし"

## Application

### 技術仕様

- 言語：Pytnon3系
- フレームワーク：FastAPI

### 緊急地震速報通知フロー

- 1.緊急地震速報クライアントからWebsocketのエンドポイントに接続
- ~~2.緊急地震速報が発報されモニタプラグインからWebAPIのエンドポイントにPOSTされる~~
- 2.Jsonを取得し内容を判別する
- 3.1でコネクションを張っている緊急地震速報クライアントに対してPOSTのタイミングでWebsocketのSendで送信(複数コネクションがあれば全てに対してSend)
- 4.緊急地震速報クライアントで通知されたJsonを解析し該当の音声データにてワールド内にいるユーザに対して通知

### コネクション数制限
// TODO 調整中

## About
// TODO
