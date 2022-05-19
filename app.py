
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

    
    line_bot_api.reply_message(
        event.reply_token,
        # TextSendMessage(text=event.message.text)
        ImageSendMessage(url,url)
        )
def add_firebase(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    # profile.user_idでid取得
    id=profile.user_id
    


def getpokebyid(id):
    url =f' https://pokeapi.co/api/v2/pokemon/{id}'
    res = requests.get(url).json()

    print(res['sprites']['front_default'])
    return res['sprites']['front_default']

if __name__ == "__main__":
    app.run()
