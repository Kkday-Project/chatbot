from __future__ import unicode_literals

import pandas as pd
import configparser
from transformer import Bert

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent

app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

# 這個bert會根據用戶所說的話推薦對應的產品
bert = Bert(max_len=30)
prod_df = pd.read_csv("./all_product_info.csv", encoding = 'utf-8')

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
        # 這裡將predict出來的產品id轉換成產品名稱 + 對應連結
        best_prod_id = bert.predict(user_message)
        link = 'https://www.kkday.com/zh-tw/product/' + str(best_prod_id)
        product_title = prod_df[prod_df["product_id"] == best_prod_id]["title"].to_numpy()[0]
        # reply_message就是bot要回傳的話
        reply_message = "為您推薦:" + product_title + "\n" + link
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message)
        )

# 第一次加好友會說的話
@handler.add(FollowEvent)
def handle_add_friend(event):
    line_bot_api.push_message(
        event.source.user_id,
        TextMessage(text="Hello world !\nNice to meet you, my friend (?")
    )

if __name__ == "__main__":
    app.run()