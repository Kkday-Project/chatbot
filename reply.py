import pandas as pd
import numpy as np
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

user_state = {}
keyword_dict = np.load('keyword_id_dict.npy',allow_pickle='TRUE').item()
info = pd.read_csv('all_product_info.csv',encoding = 'utf-8')
word_score_dict = np.load('word_score_dict.npy',allow_pickle='TRUE').item()
template_list = ['行程推薦','地區資訊查詢','旅遊提醒','線上專人服務']
# key 為 我們定義的 value[0] 為回復 value[1] 為狀態
template_reply_dict = {
    template_list[0]:'您好，請問您目前有任何想法嗎?', #行程推薦
    template_list[1]:'您好，請問您想查詢哪個地區的資訊',
    template_list[2]:'您在10/20 台北社子島 寬板滑水＋快艇衝浪＋沙發衝浪 的行程，注意事項如下\n請穿著輕便服裝、合身泳裝、衝浪褲或排汗快乾材質衣物\n請於所選梯次前 20 分鐘報到\n請自行準備防曬用品、防磨衣、換洗用乾淨衣物、毛巾\n近視 400 度以上旅客需配戴隱形眼鏡\n下雨可照常體驗，發生打雷、閃電將暫停活動\n行程包含劇烈運動，不建議孕婦，身心障礙人士，傷患與病患參加\n\n當天天氣為 晴天 ，可以攜帶防曬前往。',
    template_list[3]:'請問您遇到了甚麼問題?'
    }
state_reply_dict = {
    template_list[1]:'目前資料還沒連起來XD',
    template_list[3]:'造成您的不便非常抱歉，會有專員立即回覆您，請稍等。'
    }
intro = TemplateSendMessage(
                            alt_text='Buttons template',
                            template=ButtonsTemplate(
                                title='您好，我是kkday旅遊秘書',
                                text='請先選擇需要哪種服務喔',
                                actions=[
                                    MessageTemplateAction(
                                        label=template_list[0],
                                        text=template_list[0]
                                    ),
                                    MessageTemplateAction(
                                        label=template_list[1],
                                        text=template_list[1]
                                    ),
                                    MessageTemplateAction(
                                        label=template_list[2],
                                        text=template_list[2]
                                    ),
                                    MessageTemplateAction(
                                        label=template_list[3],
                                        text=template_list[3]
                                    )
                                ]
                            )
                        )
"""
class state():
    def __init__(self):
        self.name = name
        self.level = level"""
        



def keywordSearch(text):
    product_score_dict = {}
    for i in range(len(text) - 1):
        word = text[i] + text[i+1]
        if word in keyword_dict:
            for pid in keyword_dict[word]:
                if pid in product_score_dict:
                    product_score_dict[pid] += word_score_dict[word]
                else:
                    product_score_dict[pid] = word_score_dict[word]
    if len(product_score_dict) == 0:
        return '沒有找到相關行程'
    itemMaxValue = max(product_score_dict.items(), key=lambda x: x[1])
    max_id_list = []
    for k,v in product_score_dict.items():
        if v == itemMaxValue[1]:
            max_id_list.append(k)
    
    # max_id_list 為關鍵字分數最高的那些行程id 可以從這邊接Bert(?)

    t = info[info["product_id"] == max_id_list[0]]["title"].to_numpy()[0]
    reply_message = t + "\n" +'https://www.kkday.com/zh-tw/product/' + str(i)
    return reply_message

def reply(user_message, user):
    if user_message in template_list:
        user_state[user] = user_message
        return template_reply_dict[user_message]
    
    elif user in user_state and user_state[user] in state_reply_dict: # 適用於單次回復就重來
        state = user_state[user]
        user_state[user] = 0 #隨便指定，只要在state_reply_dict 沒有就好
        return state_reply_dict[state]
    
    elif user in user_state and user_state[user] == template_list[0]: # 行稱推薦   (多階段問答就要再寫...)
        user_state[user] = 0
        return keywordSearch(user_message)
    else:
        return 0
