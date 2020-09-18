from __future__ import unicode_literals

import pandas as pd
import configparser
from transformer import Bert

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent
from linebot.models import (
    MessageEvent,
    TextSendMessage,
    TemplateSendMessage,
    ButtonsTemplate,
    MessageTemplateAction
)
from linebot.models import QuickReply, QuickReplyButton
import configparser
from transformer import Bert
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

keyword_dict = np.load('keyword_id_dict.npy',allow_pickle='TRUE').item()
info = pd.read_csv('all_product_info.csv',encoding = 'utf-8')
word_score_dict = np.load('word_score_dict.npy',allow_pickle='TRUE').item()


# 這個bert會根據用戶所說的話推薦對應的產品
bert = Bert()
num = 0
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
user_state = {}
# 回覆用戶
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        
        # user_message是使用者說的話
        user_message = event.message.text
        dict_event = json.loads(str(event.source))

        
        if 'bye' in user_message:
            try:
                if 'roomId' in dict_event:
                    line_bot_api.leave_room(dict_event['roomId'])  
                else:
                    line_bot_api.leave_group(dict_event['groupId']) 
            except:
                reply_message = '離開失敗'
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_message)
        )
        
        elif user_message == 'reset':
            line_bot_api.reply_message(
                event.reply_token,
                TemplateSendMessage(
                            alt_text='Buttons template',
                            template=ButtonsTemplate(
                                title='您好，我是kkday旅遊秘書',
                                text='請先選擇需要哪種服務喔',
                                actions=[
                                    MessageTemplateAction(
                                        label='行程推薦',
                                        text='行程推薦'
                                    ),
                                    MessageTemplateAction(
                                        label='地區資訊查詢',
                                        text='地區資訊查詢'
                                    ),
                                    MessageTemplateAction(
                                        label='旅遊提醒',
                                        text='旅遊提醒'
                                    ),
                                    MessageTemplateAction(
                                        label='線上專人服務',
                                        text='線上專人服務'
                                    )
                                ]
                            )
                        )
                    )
        elif user_message == '行程推薦':
            user_state[event.source.user_id] = ['recommend']
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='您好，請問您目前有任何想法嗎?'))
        elif user_message == '地區資訊查詢':
            user_state[event.source.user_id] = ['search']
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='您好，請問您想查詢哪個地區的資訊'))

        elif user_message == '旅遊提醒':
            user_state[event.source.user_id] = ['remind']
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='您在10/20 台北社子島 寬板滑水＋快艇衝浪＋沙發衝浪 的行程，注意事項如下\n請穿著輕便服裝、合身泳裝、衝浪褲或排汗快乾材質衣物\n請於所選梯次前 20 分鐘報到\n請自行準備防曬用品、防磨衣、換洗用乾淨衣物、毛巾\n近視 400 度以上旅客需配戴隱形眼鏡\n下雨可照常體驗，發生打雷、閃電將暫停活動\n行程包含劇烈運動，不建議孕婦，身心障礙人士，傷患與病患參加\n\n當天天氣為 晴天 ，可以攜帶防曬前往。'))
            user_state[event.source.user_id] = 0
        elif user_message == '線上專人服務':
            user_state[event.source.user_id] = ['angry']
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='請問您遇到了甚麼問題?'))
        elif event.source.user_id in user_state and user_state[event.source.user_id] != 0:
            if user_state[event.source.user_id] == ['angry']:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='造成您的不便非常抱歉，會有專員立即回覆您，請稍等。'))
                user_state[event.source.user_id] = 0
            elif user_state[event.source.user_id] == ['recommend']:
                text = user_message
                product_score_dict = {}
                for i in range(len(text) - 1):
                    word = text[i] + text[i+1]
                    if word in keyword_dict:
                        for pid in keyword_dict[word]:
                            if pid in product_score_dict:
                                product_score_dict[pid] += word_score_dict[word]
                            else:
                                product_score_dict[pid] = word_score_dict[word]

                itemMaxValue = max(product_score_dict.items(), key=lambda x: x[1])
                max_id_list = []
                for k,v in product_score_dict.items():
                    if v == itemMaxValue[1]:
                        max_id_list.append(k)
                
                t = info[info["product_id"] == max_id_list[0]]["title"].to_numpy()[0]
                reply_message = t + "\n" +'https://www.kkday.com/zh-tw/product/' + str(i)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=reply_message)
                )
                user_state[event.source.user_id] = 0
            elif user_state[event.source.user_id] == ['search']:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='目前資料還沒連起來XD'))
                user_state[event.source.user_id] = 0
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TemplateSendMessage(
                            alt_text='Buttons template',
                            template=ButtonsTemplate(
                                title='您好，我是kkday旅遊秘書',
                                text='請先選擇需要哪種服務喔',
                                actions=[
                                    MessageTemplateAction(
                                        label='行程推薦',
                                        text='行程推薦'
                                    ),
                                    MessageTemplateAction(
                                        label='地區資訊查詢',
                                        text='地區資訊查詢'
                                    ),
                                    MessageTemplateAction(
                                        label='旅遊提醒',
                                        text='旅遊提醒'
                                    ),
                                    MessageTemplateAction(
                                        label='線上專人服務',
                                        text='線上專人服務'
                                    )
                                ]
                            )
                        )
                    )




# 第一次加好友會說的話
@handler.add(FollowEvent)
def handle_add_friend(event):
    line_bot_api.push_message(
        event.source.user_id,
        TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                title='嗨您好，我是kkday旅遊秘書',
                text='請問您需要甚麼服務',
                actions=[
                    MessageTemplateAction(
                        label='行程推薦',
                        text='行程推薦'
                    ),
                    MessageTemplateAction(
                        label='地區資訊查詢',
                        text='地區資訊查詢'
                    ),
                    MessageTemplateAction(
                        label='旅遊提醒',
                        text='旅遊提醒'
                    ),
                    MessageTemplateAction(
                        label='客訴',
                        text='客訴'
                    )
                ]
            )
        )
    )

if __name__ == "__main__":
    app.run()


