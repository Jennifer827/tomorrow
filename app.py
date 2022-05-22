
import psycopg2
 
# DB接続情報 
DB_HOST = 'ec2-44-194-117-205.compute-1.amazonaws.com'
DB_PORT = '5432'
DB_NAME = 'dc7od5nmrchj7v'
DB_USER = 'hhmknwhvgzumpl'
DB_PASS = 'a73d257bee5fa277fae92b19c7cbca419da491070fbbac4e16ac00a99476f7c5'
 
# DB接続関数 
def get_connection(): 
    return psycopg2.connect('postgresql://{user}:{password}@{host}:{port}/{dbname}'
        .format( 
            user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT, dbname=DB_NAME 
        ))



# Linebot

import os,requests,datetime,cv2,numpy as np

from flask import Flask, request, abort
from random import randint 



from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageSendMessage
)
from random import randint




app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

all_poke = 151
app_url = 'https://pokemonbot00.herokuapp.com'


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
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'




def getrandom():


    # now = datetime.datetime.now()
    # y = now.year 
    # m = now.month 
    # h = now.hour
    # d = now.weekday()
    # n = now.minute

    # return (y + m + h + d) % all_poke + 1
    with open('id.txt') as f:
        s = f.read()
        print(s)
        s = int(s)
    
    return s

def get_realrandom():
    now = datetime.datetime.now()
    y = now.year 
    m = now.month 
    h = now.hour
    d = now.weekday()
    n = now.minute

    return str((n + y + m + h + d) % all_poke + 1)



@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # data = getpokebyid(event.message.text)
    # print(event.source.user_id)

    id = event.source.user_id
    
    message = event.message.text
    data = getpokebyid(getrandom())
    is_correct = False
    is_zukan = False

    height=data["height"]/10
    weight=data["weight"]/10

    if message == 'ポケモンクイズ':
        message_to_send = f'''{data["name_eng"]}\n{data["kind_eng"]}'''
        line_bot_api.push_message(
            id,
            TextSendMessage(text=message_to_send)
        )
    
    elif message == '小ヒント':
        message_to_send = f'高さ：{height}m\n重さ：{weight}kg'    
        line_bot_api.push_message(
            id,
            TextSendMessage(text=message_to_send)
        )
    
    elif message == '中ヒント':
        message_to_send = f'タイプ：{data["type"]}'   
        line_bot_api.push_message(
            id,
            TextSendMessage(text=message_to_send)
            ) 
    elif message == '大ヒント':
        makegray(data['id'])
        message_to_send = f'こんなシルエットだよ！！'   
        line_bot_api.push_message(
            id,
            TextSendMessage(text=message_to_send)
            )
        gray_url = app_url + '/static/gray.png'
        line_bot_api.push_message(
            id,
            ImageSendMessage(gray_url,gray_url)
        )
    
    elif message == '答え':
        message_to_send = f'''<英語>\n名前：{data["name_eng"]}\n種類：{data["kind_eng"]}\n<日本語>\n名前：{data["name_jp"]}\n種類：{data["kind_jp"]}\n重さ：{weight}kg\n高さ：{height}m '''
        line_bot_api.push_message(
            id,
            TextSendMessage(text=message_to_send)
             )
    
    elif message == f'{data["name_jp"]}':
        message_to_send = f'やった〜！！！\n{data["name_jp"]}を捕まえたぞ！\n図鑑に登録しました。\n\n「図鑑」と送信してみてね！'
        line_bot_api.push_message(
            id,
            TextSendMessage(text=message_to_send)
             )
        
        # line_bot_api.push_message(
        #     id,
        #     ImageSendMessage(data['img'],data["img"])
        #     )

        is_correct = True

    elif message == '図鑑':
        makezukan(id)
        message_to_send = '図鑑を送るよ！'
        line_bot_api.push_message(
            id,
            TextSendMessage(text=message_to_send)
             )
        
        is_zukan = True

    elif message == 'omni_broadcast':
        message_to_send = '問題が変わるよ！'
        line_bot_api.push_message(
            id,
            TextSendMessage(text=message_to_send)
             )
        with open('id.txt',mode='w') as f:
            f.write(get_realrandom())


    else:
        message_to_send = f'''「ポケモンクイズ」：ポケモンクイズを出すよ！　日本語名で答えてね！\n\n 分からない場合は「小ヒント」「中ヒント」「大ヒント」を聞いてみてね！\n\n 「図鑑」：自分の図鑑を表示するよ\n\n「答え」：答えを表示するよ！\n\n\n(クイズ中の場合は「不正解」だよ！！)'''
        line_bot_api.push_message(

            id,
            TextSendMessage(text=message_to_send)
            )

    
    print(id)

    print('lets send second message')

    if is_correct:
       conn = get_connection() 
       cur = conn.cursor()

       cur.execute("INSERT INTO pokezukan (line_id, poke_id) VALUES ('%s', '%s')"%(id,data["id"]))
       cur.execute("SELECT poke_id FROM pokezukan WHERE line_id ='%s'"%(id)) 
       
       rows0 = cur.fetchall()
       rows=[i[0] for i in rows0] 
       print(rows)


       cur.close() 
       conn.commit()
       conn.close() 

       line_bot_api.push_message(id, ImageSendMessage(data['img'], data['img']))


    if is_zukan:
       zukan_url = app_url + '/static/img/zukan.png'
       line_bot_api.push_message(
           id,
           ImageSendMessage(zukan_url,zukan_url)
           )

def getpokebyid(id):
    eng = 7
    jp = 0

    url =f' https://pokeapi.co/api/v2/pokemon/{id}'
    res = requests.get(url).json()
    url2 = f'https://pokeapi.co/api/v2/pokemon-species/{id}'
    res2 = requests.get(url2).json()

    weight = res['weight']
    height = res['height']
    kind_eng = res2['genera'][eng]['genus']
    name_eng = res2['names'][eng]['name']
    kind_jp = res2['genera'][jp]['genus']
    name_jp = res2['names'][jp]['name']
    img =  res['sprites']['front_default']
    type = res['types'][0]['type']['name']

    ans = {'weight':weight,'height':height,'kind_eng':kind_eng,'name_eng':name_eng,'kind_jp':kind_jp,'name_jp':name_jp,'type':type,'img':img,'id':id}

    print(ans)
    return ans

def makezukan(id):

    
    conn = get_connection() 
    cur = conn.cursor()

    cur.execute("SELECT poke_id FROM pokezukan WHERE line_id ='%s'"%(id)) 
       
    rows0 = cur.fetchall()
    rows=[i[0] for i in rows0] 
    print(rows)


    cur.close() 
    conn.commit()
    conn.close() 
    
    w = 8
    all_poke = 151
    rows = set(rows)

    # #ブランク画像
    height,width = cv2.imread('static/img/1.png').shape[0:2]
    blank = np.zeros((height, width, 3))
    blank = blank.astype(np.int32)
    
    question = cv2.resize(cv2.imread('static/img/question.png'),dsize=(height,width))

    l1 = []
    l2 = []
    for i in range(1,152):
        if str(i) in rows:
            img =  cv2.imread(f'static/img/{i}.png')
        else:
            img = question
        l2.append(np.array(img).astype(np.int32))

        if i % w == 0 or i == all_poke:
            while len(l2) < w:
                l2.append(blank)

            line = cv2.hconcat(l2)
            l1.append(line)

            l2 = []

    ans = cv2.vconcat(l1)

    cv2.imwrite('static/img/zukan.png',ans)
    # return ans 

def makegray(id):
    img = cv2.imread(f'static/img/{id}.png')
    img = np.array(img)

    for i in range(len(img)):
        for j in range(len(img[i])):
            r,g,b = img[i,j]
            if r == g == b == 0:
                pass
            else:
                img[i,j] = np.array([100,100,100])
    cv2.imwrite('static/gray.png',img)


