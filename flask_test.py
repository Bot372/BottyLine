from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import *

from linebot import LineBotApi


import S_R_Upload
import boto3
from botocore.client import Config
import requests

app = Flask(__name__)

line_bot_api = LineBotApi(
    '8PhyG0TWWeOZ1hRJb4618e3UE6jSN+KNdpd8MJjaHUs/moHgGFfvyfv82whJQh0Ebw8fyKODATEbp8fNsFWzydi1S6VMssEB74m6nP2FCpqeOtkpLqfI+O6fx2aIwMma4sXFvw9dY9O53JpoTjda1wdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('e2a156e78a65ba2ffa4eb65c85da5b9f')


audio_result = ""

ACCESS_KEY_ID = 'AKIAIJKNMECREABAM4EA'
ACCESS_SECRET_KEY = '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'
BUCKET_NAME = 'botty-bucket'


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    #print("Request body: " + body, "Signature: " + signature)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=AudioMessage)
def handle_message(event):
    # audio_message = AudioSendMessage(
    # original_content_url='https://api.line.me/v2/bot/message/event.message.id.m4a',
    # duration=240000
    # )
    # app.logger.info(  audio_message.type, "     ", audio_message  )
    #line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))
    #print("message.id_type: " + str(event.message.id))
    id = event.message.id
    #print(type(id))

    message_content = line_bot_api.get_message_content(id)


    #Save Audio File#######################################
    file_path = "fuckyou.wav"
    with open(file_path, 'wb') as fd:
        for chunk in message_content.iter_content(chunk_size=1024):
            if chunk:
                fd.write(chunk)

    data = open('fuckyou.wav', 'rb')
    s3 = boto3.resource(
        's3',
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=ACCESS_SECRET_KEY,
        config = Config(signature_version='s3v4')
    )
    s3.Bucket(BUCKET_NAME).put_object(Key='fuckyou.wav', Body=data)
    #print("Upload Successful")
    #########################################################

    #Get File From AWS#######################################

    url = "https://s3-ap-northeast-1.amazonaws.com/botty-bucket/fuckyou.wav"
    audilFile = requests.get(url)

    #s3.Bucket(BUCKET_NAME).download_file( file_path, '.')



    file_path = '/music/fuckyou.wav'
    with open(file_path, 'wb') as fd:
        for chunk in audilFile.iter_content(chunk_size=1024):
            if chunk:
                fd.write(chunk)

    #########################################################


    #Speech_Recognition###
    S_R_Upload.converFile()
    audio_result = S_R_Upload.Speech_Recognition()
    S_R_Upload.CleanData()
    print("Audio Result: " + audio_result)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(audio_result))
    #######################

    #file_delete#########################################################





if __name__ == "__main__":
    app.run()
