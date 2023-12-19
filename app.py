# -*- coding: utf-8 -*-
#載入LineBot所需要的套件
import re
from flask import Flask, jsonify, request, abort
import paho.mqtt.client as mqtt
import os
import requests
import time
import sqlite3

up, low, f, temp = 0, 0, 0, 0
# 在全局范围内创建 MQTT 客户端连接
broker_address = "broker.MQTTGO.io"
broker_port = 1883

client = mqtt.Client("bot")
client.connect(broker_address, broker_port, 60)


from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('j+6D0WoRXW318S/mcSB91zE6+DY2mtxsc3LxkkNuRFg2hTgSClDzgQvChZQseRwv4xQgIMZT9Zn3bb2n0Iw5mT7y2OZ8Yv+kaMc7J3JZ6B3PtF6F4OuGFJKGCR9v0hvO7GxcfRJegsFNnKXKYeW5kwdB04t89/1O/w1cDnyilFU=')
# 必須放上自己的Channel Secret
handler = WebhookHandler('50a8a71e2572cb912c9e6e22a58da5ec')

line_bot_api.push_message('U3dbca95eb797c6d92d3ecd583da36d52', TextSendMessage(text='服務啟動，很高興為您服務'))


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

 
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def is_integer(s):
    return s.isdigit()

def is_integer_strict(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
 
#訊息傳遞區塊
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global up, low, f

    # 获取 Line Bot 消息文本
    message_text = event.message.text

    # 发布消息到 MQTT
    topic = "temp/test/2023/12/18/2023/12/24/fan"

    if "風扇啟動" in message_text:
        client.publish(topic, "1")
        url = 'https://notify-api.line.me/api/notify'
        token = 'HAEEGV152YwCuL8tknqHwNs0OFhnUfhyUnoLd75S6wp'
        headers = {
            'Authorization': 'Bearer ' + token
        }
        data = {
            'message': "啟動成功"
        }
        requests.post(url, headers=headers, data=data)
        client.publish(topic, 1)
    elif "風扇關閉" in message_text:
        client.publish(topic, "0")
        url = 'https://notify-api.line.me/api/notify'
        token = 'HAEEGV152YwCuL8tknqHwNs0OFhnUfhyUnoLd75S6wp'
        headers = {
            'Authorization': 'Bearer ' + token
        }
        data = {
            'message': "關閉成功"
        }
        requests.post(url, headers=headers, data=data)
        client.publish(topic, 0)
    elif "溫度上限設定" in message_text:
        parts = message_text.split()
        if len(parts) == 2:
            keyword = parts[0]
            up = int(parts[1]) 
            url = 'https://notify-api.line.me/api/notify'
            token = 'HAEEGV152YwCuL8tknqHwNs0OFhnUfhyUnoLd75S6wp'
            headers = {
                'Authorization': 'Bearer ' + token
                    }
            data = {
                'message': "設定成功 => 上限為" + str(up) + "°C"
                    }
            requests.post(url, headers=headers, data=data)
    elif "溫度下限設定" in message_text:

        parts = message_text.split()
        if len(parts) == 2:
            keyword = parts[0]
            low = int(parts[1]) 
            url = 'https://notify-api.line.me/api/notify'
            token = 'HAEEGV152YwCuL8tknqHwNs0OFhnUfhyUnoLd75S6wp'
            headers = {
                'Authorization': 'Bearer ' + token
                    }
            data = {
                'message': "設定成功 => 下限為" + str(low) + "°C"
                    }
            requests.post(url, headers=headers, data=data)

    elif "溫度頻率設定" in message_text:

        parts = message_text.split()
        if len(parts) == 2:
            keyword = parts[0]
            f = int(parts[1])
            if f > 10 : 
                topic = "temp/test/2023/12/18/2023/12/24/f"
                url = 'https://notify-api.line.me/api/notify'
                token = 'HAEEGV152YwCuL8tknqHwNs0OFhnUfhyUnoLd75S6wp'
                headers = {
                    'Authorization': 'Bearer ' + token
                        }
                data = {
                    'message': "設定成功 => 頻率為" + str(f) + "秒"
                        }
                requests.post(url, headers=headers, data=data)

                client.publish(topic, f)
            elif f <= 10:
                url = 'https://notify-api.line.me/api/notify'
                token = 'HAEEGV152YwCuL8tknqHwNs0OFhnUfhyUnoLd75S6wp'
                headers = {
                    'Authorization': 'Bearer ' + token
                    }
                data = {
                    'message': "頻率時間過短，請重新輸入"
                    }
                requests.post(url, headers=headers, data=data)
    elif "檢視設定" in message_text:

        url = 'https://notify-api.line.me/api/notify'
        token = 'HAEEGV152YwCuL8tknqHwNs0OFhnUfhyUnoLd75S6wp'
        headers = {
            'Authorization': 'Bearer ' + token
                    }
        data = {
            'message': "\n上限為 " + str(up) + "°C\n下限為 " + str(low) + "°C\n頻率為 " + str(f) + "秒"
        }
        requests.post(url, headers=headers, data=data)

@app.route('/temp/<string:tempgit>')
def temp(tempgit):
    try:
        temp = tempgit
        if(float(temp) > low and float(temp) < up):
            url = 'https://notify-api.line.me/api/notify'
            token = 'HAEEGV152YwCuL8tknqHwNs0OFhnUfhyUnoLd75S6wp'
            headers = {
                'Authorization': 'Bearer ' + token
                    }
            data = {
                'message': "目前溫度" + str(temp)
                    }
            requests.post(url, headers=headers, data=data)
        elif(float(temp) > up):
            topic = "temp/test/2023/12/18/2023/12/24/fan"
            client.publish(topic, 1)
            url = 'https://notify-api.line.me/api/notify'
            token = 'HAEEGV152YwCuL8tknqHwNs0OFhnUfhyUnoLd75S6wp'
            headers = {
                'Authorization': 'Bearer ' + token
                    }
            data = {
                'message': "\n注意！現在溫度過高"
        }
        elif(float(temp) < low):
            topic = "temp/test/2023/12/18/2023/12/24/fan"
            client.publish(topic, 0)
            url = 'https://notify-api.line.me/api/notify'
            token = 'HAEEGV152YwCuL8tknqHwNs0OFhnUfhyUnoLd75S6wp'
            headers = {
                'Authorization': 'Bearer ' + token
                    }
            data = {
                'message': "\n注意！現在溫度過低"
        }
        return "Succeed"
    
    except Exception as e:
            return jsonify({'Error': str(e)})
    



# 主程式
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)