from __future__ import unicode_literals

import pandas as pd
import configparser
from transformer import Bert

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import  TextMessage, FollowEvent, QuickReply, QuickReplyButton
from linebot.models import (
    MessageEvent,
    TextSendMessage,
    TemplateSendMessage,
    ButtonsTemplate,
    MessageTemplateAction
)
import configparser
from transformer import Bert
import reply
import json
import random 
import numpy as np
import pandas as pd
app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini',encoding='utf-8')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))




# 這個bert會根據用戶所說的話推薦對應的產品
bert = Bert()

# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# 回覆用戶
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        
        # user_message是使用者說的話
        user_message = event.message.text

                                    MessageTemplateAction(
        # 判斷條件
        text = reply.reply(user_message, event.source.user_id)
        if text != 0:
            line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=text))

        else:
            line_bot_api.reply_message(event.reply_token, reply.intro)




# 第一次加好友會說的話
@handler.add(FollowEvent)
def handle_add_friend(event):
    line_bot_api.push_message(event.source.user_id, reply.intro)

if __name__ == "__main__":
    app.run()


