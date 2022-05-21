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


conn = get_connection() 
cur = conn.cursor()
 
# SQL実行（tbl_sampleから全データを取得）
# cur.execute('INSERT INTO zukan (line_id, poke_id) VALUES (0, 1);')

# cur.execute('SELECT poke_id FROM pokezukan WHERE line_id =1234567890') 
# rows = cur.fetchall() 
# print(rows)

cur.close()
# commitが必要
# conn.commit()

# cur.close() 
# conn.close()


# Linebot


import os,requests,datetime
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


    now = datetime.datetime.now()
    y = now.year 
    m = now.month 
    h = now.hour
    d = now.weekday()

    return (y + m + h + d) % all_poke + 1




@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # data = getpokebyid(event.message.text)
    # print(event.source.user_id)

    ans = pokebyid(getrandom())

    is_correct = False
    
    id = event.source.user_id
    print(id)
    

    if event.message.text == "ポケモンクイズ":
        message = f"{ans['name_eng']}\n{ans['kind_eng']}"
        
    elif event.message.text == "ヒント":
        n = randint(0,3)
        if n == 0:
            message = f" 番号：{ans['id']}"
        if n == 1:
            message = f"たかさ：{ans['height']}(m)"
        if n == 2:
            message = f"おもさ：{ans['weight']}(kg)"
        if n == 3:
            message = f"英語の名前{ans['name_eng']}"

    elif event.message.text == "こたえ":
        message = f"<英語>\n名前:{ans['name_eng']}\n種類:{ans['kind_eng']}\n<日本語>\n名前:{ans['name_ja']}\n種類:{ans['kind_ja']}\n重さ:{ans['weight']}(kg)\n高さ:{ans['height']}(kg) "

    elif event.message.text == f"{ans['name_ja']}":
        message = f"やったー！{ans['name_ja']}を捕まえたぞ！図鑑に登録しました。"
        is_correct = True

    else:
        message = "「ポケモンクイズ：ポケモンクイズを出すよ！\n「ヒント」：重さ・高さ・種類・英語名のなかからランダムでヒントを出すよ！\n「こたえ」：こたえを表示するよ！"

    line_bot_api.push_message(id, TextSendMessage(message))

    if is_correct:
        conn = get_connection() 
        cur = conn.cursor()
    
        cur.execute("INSERT INTO pokezukan (line_id, poke_id) VALUES ('%s', '%s')"%(id,ans["id"]))
        cur.execute("SELECT poke_id FROM pokezukan WHERE line_id ='%s'"%(id)) 
        rows = cur.fetchall() 
        print(rows)
        
        cur.close() 
        conn.commit()
        conn.close() 
        
        line_bot_api.push_message(id, ImageSendMessage(ans['img'], ans['img']))




def pokebyid(id):

    res = requests.get(f"https://pokeapi.co/api/v2/pokemon/{id}")
    res_another = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{id}")

    res2 = res.json()
    res2_another = res_another.json()

    #print(type(res2))

    #print(res2.keys())

    id = res2['id']
    height =res2['height'] / 10
    weight = res2['weight'] / 100
    kind_ja = res2_another['genera'][0]['genus']
    kind_eng = res2_another['genera'][7]['genus']
    mayu = res2['types'][0]['type']['name']
    name_ja = res2_another['names'][0]['name']
    name_eng = res2_another['names'][7]['name']

    #print(id, height, weight, kind_ja, kind_eng, mayu, name_ja, name_eng)

    img =  res2['sprites']['front_default']

    #print(img)

    #print(res2.keys())

    ans = {"id" : id, "height": height, "weight" : weight, "kind_ja" : kind_ja, "kind_eng" : kind_eng, "type" : mayu, "name_ja" : name_ja, "name_eng" : name_eng, "img" : img }

    print(ans)
    return ans

pokebyid(25)



# cur.close() 
# conn.close()