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
from firebase_admin import credentials, firestore
#import google.cloud.exceptions # thrown exception( fire-base )

import requests
import json
import random

import apiai # Dialog Flow Api
import ast # deal with str covert to dict
import sys # adding path to system
import os 

#add the smarthome file to current system path
testdirSmarthome = os.path.dirname(os.path.realpath(__file__)) + "\\smarthome"
sys.path.insert(0, testdirSmarthome )

from smarthome import smarthomeLight,  smarthomeHeat, smarthomeDevice, smarthomeLock, weather, news # Do the IoT instruction
import S_R_Upload

from googletrans import Translator # Google translate


app = Flask(__name__)

#Line Api
line_bot_api = LineBotApi(
    'pSltWIB3h+rPPPYtt/WiMJhz9mH2hmwsiX4FJWyGDEKuFitCmamgrvQsjZ/HddnbjO0PbyCbmQtUaTLoTKJIO3Vz7rINEVxtQAGuwrRC3E6v5WiLmWj3iv9Qt0fb2MucccO4ACWFM41upXn66fxLDwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('4f8304b2e19636e36b555a6e7099e5c6')

#Dialog flow Api
#smartHome, translate APi : 411c390e69104ae69e51052c92c8ad5a
#weather   Api : bf94e2e4f04243c4b5353fc559c39ad0
ai = apiai.ApiAI('bf94e2e4f04243c4b5353fc559c39ad0')


#Firebase Api Fetch the service account key JSON file contents
FIREBASE_TOKEN = "key.json"
cred = credentials.Certificate( FIREBASE_TOKEN )
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
    #request.session_id = "123456789"
    response = request.getresponse().read().decode('utf-8')
    responseJson = json.loads(response)
    #print( json.dumps(responseJson["result"]["parameters"], indent=4) )
    return responseJson

def parse_natural_event( event):
    e = apiai.events.Event(event)
    request = ai.event_request(e)
    #request.session_id = session_id  # unique for each user
    #request.contexts = contexts    # a list
    response = request.getresponse()
    #response = json.loads(request.getresponse().read().decode(‘utf-8’))
    print( response.read() )
    return response


def NLP(  event, user_text, user_id ) :
    # NLP analyze 1.OtherType 2.smalltalk Iot-1.Light Iot-2.Lock Iot-3.Heating Iot-4.Device on off 3.weather 4.news
    Diaresponse = parse_user_text(user_text)
    responseMessenge = ""
    action = Diaresponse["result"]["action"]


    smartHomeDict = {
        "lights.switch"   : True, 
        "lock"            : True,
        "heating"         : True,
        "device.switch"   : True,
    }

    print(action)
    if user_text == "南無阿彌陀佛" :
        responseMessenge = "歡迎加入戰隊"
    # (1) other Type send sticker or telling a joke
    elif action == "input.unknown" :
        responseMessenge = Diaresponse["result"]["fulfillment"]["messages"]
        responseMessenge = {i: responseMessenge[i] for i in range(0, len(responseMessenge))}
        responseMessenge = responseMessenge[0]["speech"]
    # (2) small talk
    elif action[0:9] == "smalltalk":
        responseMessenge = Diaresponse["result"]["fulfillment"]["messages"]
        responseMessenge = {i: responseMessenge[i] for i in range(0, len(responseMessenge))}
        responseMessenge = responseMessenge[0]["speech"]
    # (Iot-1) smart home Light
    elif action[0:23] == "smarthome.lights.switch" and smartHomeDict["lights.switch"] == True:
        light = smarthomeLight.Light(action, Diaresponse["result"], user_id)
        light.runSmarthome_Light()
        responseMessenge = light.getSpeech()
        # (Iot-2) smart home Lock
    elif action[0:15] == "smarthome.locks" and smartHomeDict["lock"] == True:
        lock = smarthomeLock.Lock(action, Diaresponse["result"], user_id)
        lock.runSmarthome_Lock()
        responseMessenge = lock.getSpeech()
    # (Iot-3) smart home heat
    elif action[0:17] == "smarthome.heating" and smartHomeDict["heating"] == True:
        heat = smarthomeHeat.Heat(action, Diaresponse["result"], user_id)
        heat.runSmarthome_Heat()
        responseMessenge = heat.getSpeech()
    # (Iot-4) smart home device
    elif action[0:23] == "smarthome.device.switch" and smartHomeDict["device.switch"] == True:
        device = smarthomeDevice.Device(action, Diaresponse["result"], user_id)
        device.runSmarthome_Device()
        responseMessenge = device.getSpeech()
    # (3) check the weather
    elif action[0:7] == "weather":
        weatherMain = weather.Weather( action, Diaresponse["result"]  )
        weatherMain.runWeather()
        responseMessenge = weatherMain.getSpeech()
        # (4) check the news
    elif action == "check.news":
        responseMessenge = news.runNews()
    # translate
    elif action == "translate.text" :
        def TranslateText( originalText, destCode ) :
            with open('translate.json', 'r') as fp:
                lanCode = json.load(fp)

            translator = Translator()
            afterText = translator.translate( originalText, dest= lanCode[destCode] )

            return afterText.text

        try :
            originalText = Diaresponse["result"]["parameters"]["text"]
            destCode     = Diaresponse["result"]["parameters"]["lang-to"]
            responseMessenge = TranslateText( originalText, destCode  )
        except :
            responseMessenge = "Sorry botty could not translate for you"

    # tell me a joke 
    elif action == "jokes.get" :
        responseMessenge = Diaresponse["result"]["fulfillment"]["speech"]
    # Ask about adding new device    
    else:
        responseMessenge = "Do you want to add the new IoT device"

    return responseMessenge

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #get Line User Id
    user_id=  str(event)
    user_id = ast.literal_eval(user_id)
    user_id = user_id['source']['userId']
    print( user_id )
 
    line_bot_api.reply_message(event.reply_token, TextSendMessage(NLP(event, event.message.text, user_id)))
    return 'OK_message'


@handler.add(MessageEvent, message=AudioMessage)
def handle_message(event):

    id = event.message.id
    message_content = line_bot_api.get_message_content(id)

    user_id = str(event)
    user_id= ast.literal_eval(user_id)
    user_id = user_id['source']['userId']
    print( user_id )

    file_path = user_id + ".wav"
    print( file_path )
    with open(file_path, 'wb') as fd:
        for chunk in message_content.iter_content(chunk_size=1024):
            if chunk:
                fd.write(chunk)


    #Speech_Recognition###
    S_R_Upload.converFile(user_id)
    audio_result = S_R_Upload.Speech_Recognition(user_id)
    #clean audio file
    if os.path.exists(user_id + ".wav"):
       os.remove(user_id + ".wav")
    else:
        print("The file1 does not exist")

    if os.path.exists(user_id+ "M4a.wav" ):
        os.remove(user_id + "M4a.wav" )
    else:
        print("The file2 does not exist")


    print("Audio Result: " + audio_result)
    if audio_result is not "Sphinx could not understand audio" : 
        line_bot_api.push_message( user_id, TextSendMessage( "->" + audio_result))

    #audio_result = "turn off the bedroom light"

    
    line_bot_api.reply_message(event.reply_token, TextSendMessage( NLP(event, audio_result, user_id)  ) )
    return "OKOK"


if __name__ == "__main__":
    app.run( debug = True, port = 80  )
