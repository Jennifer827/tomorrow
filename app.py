
# DB
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

cur.execute('SELECT poke_id FROM zukan WHERE line_id =1234567890') 
rows = cur.fetchall() 
print(rows)
# commitが必要
conn.commit()
 


# cur.close() 
# conn.close()

# Linebot

import os,requests
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageSendMessage
)

app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]


line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


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



@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    url = getpokebyid(event.message.text)
    print(event.source.user_id)

    cur.execute('INSERT INTO zukan (line_id, poke_id) VALUES (1, 987);')
    conn.commit()

    print('わーい')
    
    line_bot_api.reply_message(
        event.reply_token,
        # TextSendMessage(text=event.message.text)
        ImageSendMessage(url,url)
        )
    

def getpokebyid(id):
    url =f' https://pokeapi.co/api/v2/pokemon/{id}'
    res = requests.get(url).json()

    print(res['sprites']['front_default'])
    return res['sprites']['front_default']

if __name__ == "__main__":
    app.run()


cur.close() 
conn.close()