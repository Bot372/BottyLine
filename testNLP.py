from flask import Flask, request, abort, make_response, jsonify

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import *

from linebot import LineBotApi

import firebase_admin
from firebase_admin import credentials

import json
import ast  # deal with str covert to dict
import apiai  # Dialog Flow Api


# add the smarthome file to current system path


app = Flask(__name__)

# Line Api
line_bot_api = LineBotApi(
    'Your Line Bot Api')
handler = WebhookHandler('Your Line Bot Channel')

# Dialog flow Api
ai = apiai.ApiAI('YOur Dialog flow Project Id')

# Firebase Api Fetch the service account key JSON file contents
FIREBASE_TOKEN = "bottyline-firebase-adminsdk-bmlr3-abeb3c8d54.json"
cred = credentials.Certificate(FIREBASE_TOKEN)
# Initialize the app with a service account, granting admin privileges
default_app = firebase_admin.initialize_app(cred)


@app.route("/", methods=['GET'])
def hello():
    return "Hello World!"


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    print("Request body: " + body, "Signature: " + signature)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


def parse_user_text(user_text):
    '''
    Send the message to API AI which invokes an intent
    and sends the response accordingly
    '''
    request = ai.text_request()
    request.query = user_text
    # request.session_id = "123456789"
    response = request.getresponse().read().decode('utf-8')
    responseJson = json.loads(response)
    # print( json.dumps(responseJson["result"]["parameters"], indent=4) )
    return responseJson

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # get Line User Id
    event_S = str(event)
    event_S = ast.literal_eval(event_S)
    event_S = event_S['source']['userId']
    print(event_S)

    # Check the product in the Database
    # 1. fetch the Product list in the database to dict
    # smartHomeDict = AWS()
    smartHomeDict = {
        "lights-switch": True,
        "lock": True,
        "heating": True,
        "device-switch": True,
    }

    # NLP analyze 1.OtherType 2.smalltalk Iot-1.Light Iot-2.Lock Iot-3.Heating Iot-4.Device on off 3.weather 4.news
    Diaresponse = parse_user_text(event.message.text)

    responseMessenge = ""
    # Check the Action is define or not
    action = ""
    try:
        action = Diaresponse["result"]["action"]
    except KeyError:
        action = "otherType"

    print(action)


    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=responseMessenge))

    return 'OK_message'


if __name__ == "__main__":
    app.run(debug=True, port=80)