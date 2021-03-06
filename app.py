# -*- coding: UTF-8 -*-

import os
import random
import teachMode as teach
import game as game
import restaurant as restaurant
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
# Channel Secret
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

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

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    user_id = event.source.user_id
    user_is_playing_game = False

    try:
        if message.find('＠') == 0:
            message = message.replace('＠', '@')
        if message.find('＄') == 0:
            message = message.replace('＄', '$')

        # check if user is play game
        user_is_playing_game = game.check_is_playing_game(user_id)

        if message == '教我說話':
            content = '嗨嗨～只要照著 【@學習 指令 回覆】(ex: @學習 你好 哈囉~) 這個格式輸入就可以讓我學習說話哦!還不趕快試試嗎？'
            res_message = TextSendMessage(text=content)
            line_bot_api.reply_message(event.reply_token, res_message)
        elif message == '猜數字遊戲':
            confirm_template_message = TemplateSendMessage(
                alt_text='Buttons template',
                template=ButtonsTemplate(
                    thumbnail_image_url='https://compass-ssl.xbox.com/assets/dc/48/dc486960-701e-421b-b145-70d04f3b85be.jpg?n=Game-Hub_Content-Placement-0_New-Releases-No-Copy_740x417_02.jpg',
                    title='【猜數字】',
                    text='猜一個四位不重複的數字，A表示數字對位置對，B表示數字對位置錯，透過已知的線索，來看看你能多快猜到數字吧！',
                    actions=[
                        MessageTemplateAction(
                            label='我要玩',
                            text='#我要玩猜數字'
                        )
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, confirm_template_message)
        elif message == '#我要玩猜數字':
            game.start_game(user_id)
            content = '遊戲開始！請輸入「$」加上4位數字，如果想結束遊戲請輸入「結束遊戲」，如果像看答案請輸入「我投降」，加油啦~'
            res_message = TextSendMessage(text=content)
            line_bot_api.reply_message(event.reply_token, res_message)
        elif message == '觀看作品':
            content = '哈囉~這是我一部份的小作品，目前僅放上網站的作品，其他類型的作品因為不好呈現所以沒有放上，不過也歡迎到我的 GitHub 去看看哦:D 另外網站由於 RWD 並沒有做到很完整，所以使用電腦觀看會比較佳哦~'
            content_message = TextSendMessage(text=content)

            works_message = TemplateSendMessage(
                alt_text='Carousel template',
                template=CarouselTemplate(
                    columns=[
                        CarouselColumn(
                            thumbnail_image_url='https://www.smartone.com/services_and_apps/tchinese/Spotify.png',
                            title='【Spotify Demo】',
                            text='The Demo website using spotify api.',
                            actions=[
                                URIAction(
                                    label='Spotify Demo',
                                    uri='https://spotify-demo-by-harrison.herokuapp.com/index'
                                )
                            ]
                        ),
                        CarouselColumn(
                            thumbnail_image_url='https://i.imgur.com/CYcSKeP.jpg',
                            title='【New Sound Website】',
                            text='New Sound 公司官方網站.',
                            actions=[
                                URIAction(
                                    label='New Sound',
                                    uri='https://newsound.herokuapp.com/'
                                )
                            ]
                        ),
                        CarouselColumn(
                            thumbnail_image_url='https://i.imgur.com/wo3gJPi.jpg',
                            title='【momofit Website】',
                            text='個人健身記錄網站.\naccount:howard\npassword:9527',
                            actions=[
                                URIAction(
                                    label='momofit',
                                    uri='https://momofit.herokuapp.com/'
                                )
                            ]
                        )
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, [content_message, works_message])
        elif message == '尋找附近餐廳':
            confirm_template_message = TemplateSendMessage(
                alt_text='Buttons template',
                template=ButtonsTemplate(
                    thumbnail_image_url='https://i.imgur.com/Y1DWfaU.jpg',
                    title='【尋找附近餐廳】',
                    text='透過 Yelp 尋找出你附近的推薦餐廳，並且可以透過連結到 Yelp 網站上觀看評論以及更多資訊哦!',
                    actions=[
                        URITemplateAction(
                            label="傳送我現在的位置",
                            uri="line://nv/location"
                        )
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, confirm_template_message)
        else:
            if user_is_playing_game:
                if message.startswith('$'):
                    number_list = list(message)

                    if len(number_list) != 5 or len(set(number_list)) != 5:
                        content = '請輸入四位不同的數字哦！'
                        res_message = TextSendMessage(text=content)
                        line_bot_api.reply_message(event.reply_token, res_message)
                    else:
                        res = game.check_number(user_id, number_list[1], number_list[2], number_list[3], number_list[4])
                        res_message = TextSendMessage(text=res)
                        line_bot_api.reply_message(event.reply_token, res_message)
                elif message == '結束遊戲':
                    game.finish_game(user_id)
                    content = '遊戲結束囉~'
                    res_message = TextSendMessage(text=content)
                    line_bot_api.reply_message(event.reply_token, res_message)
                elif message == '我投降':
                    content = game.give_up_game(user_id)
                    res_message = TextSendMessage(text=content)
                    line_bot_api.reply_message(event.reply_token, res_message)
                else:
                    content = '還在遊戲中哦!如果想結束遊戲請輸入「結束遊戲」~'
                    res_message = TextSendMessage(text=content)
                    line_bot_api.reply_message(event.reply_token, res_message)
            else:
                if message.startswith('@學習 '):
                    res = teach.learn_new_word(message)
                else:
                    result = teach.responding(message)
                    if result is None:
                        res = '還沒學會哦！'
                    else:
                        res = result
                res_message = TextSendMessage(text=res)
                line_bot_api.reply_message(event.reply_token, res_message)
    except Exception as e:
        res_message = TextSendMessage(text=str(e))
        line_bot_api.reply_message(event.reply_token, res_message)

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    try:
        location = event.message.address
        restaurant_list = restaurant.find_near_restaurant(location)

        restaurant_message = TemplateSendMessage(
            alt_text='Carousel template',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url=restaurant_list[0]['image'],
                        title=restaurant_list[0]['name'],
                        text='地址：%s' % restaurant_list[0]['address'],
                        actions=[
                            URIAction(
                                label='前往網站',
                                uri=restaurant_list[0]['url']
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=restaurant_list[1]['image'],
                        title=restaurant_list[1]['name'],
                        text='地址：%s' % restaurant_list[1]['address'],
                        actions=[
                            URIAction(
                                label='前往網站',
                                uri=restaurant_list[1]['url']
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=restaurant_list[2]['image'],
                        title=restaurant_list[2]['name'],
                        text='地址：%s' % restaurant_list[2]['address'],
                        actions=[
                            URIAction(
                                label='前往網站',
                                uri=restaurant_list[2]['url']
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=restaurant_list[3]['image'],
                        title=restaurant_list[3]['name'],
                        text='地址：%s' % restaurant_list[3]['address'],
                        actions=[
                            URIAction(
                                label='前往網站',
                                uri=restaurant_list[3]['url']
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=restaurant_list[4]['image'],
                        title=restaurant_list[4]['name'],
                        text='地址：%s' % restaurant_list[4]['address'],
                        actions=[
                            URIAction(
                                label='前往網站',
                                uri=restaurant_list[4]['url']
                            )
                        ]
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, restaurant_message)
    except Exception as e:
        res_message = TextSendMessage(text=str(e))
        line_bot_api.reply_message(event.reply_token, res_message)

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    package = random.sample([1, 2, 11537, 11538, 11539], k=1)[0]
    if package == 1:
        sticker = random.sample([2, 10, 114, 119, 106], k=1)[0]
    elif package == 2:
        sticker = random.sample([125, 132, 137, 410, 138, 427, 148, 34, 156, 164, 176, 511, 516, 513], k=1)[0]
    elif package == 11537:
        sticker = random.sample([52002735, 52002736, 52002752, 52002768, 52002743, 52002747, 52002745, 52002734], k=1)[0]
    elif package == 11538:
        sticker = random.sample([51626512, 51626507, 51626496, 51626513], k=1)[0]
    elif package == 11539:
        sticker = random.sample([52114112, 52114115, 52114116, 52114124, 52114125, 52114131, 52114136], k=1)[0]

    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=package,
            sticker_id=sticker)
    )

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)