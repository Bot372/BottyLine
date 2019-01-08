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
import google.cloud.exceptions # thrown exception( fire-base )

import requests
import json
import random

import apiai # Dialog Flow Api
import ast # deal with str covert to dict
import sys # adding path to system
import os 

#add the smarthome file to current system path
testdir = os.path.dirname(os.path.realpath(__file__)) + "\\smarthome"
sys.path.insert(0, testdir )

import smarthomeLight, smarthomeHeat, smarthomeDevice, smarthomeLock # Do the IoT instruction
import weather, news # check weather, news

app = Flask(__name__)

#Line Api
line_bot_api = LineBotApi(
    'FLgVPOzYrETTuyRv6htAbvtmpNnrmt8oK8JslYKB09AUBuzxmtllB47X834qtwehhQrSgZCPjHGh2cK/vE6uzuwSSx4JhC6Qb0W6vsKouHDwD0Ubt5BpF5ebzPS6CpGdmAfybyIn2d2Lkej6Oe9lZwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('db914cf0eb0b523b339e531206cf6c98')

#Dialog flow Api
ai = apiai.ApiAI('411c390e69104ae69e51052c92c8ad5a')


#Firebase Api Fetch the service account key JSON file contents
FIREBASE_TOKEN = "botty37-2ba0a-firebase-adminsdk-xgiw8-71b442f26b.json"
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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #get Line User Id
    event_S =  str(event)
    event_S = ast.literal_eval(event_S)
    event_S = event_S['source']['userId']
    print( event_S )
 

    
    #Check the product in the Database
    # 1. fetch the Product list in the database to dict
        # smartHomeDict = AWS()
    smartHomeDict = {
        "lights.switch"   : True, 
        "lock"            : True,
        "heating"         : True,
        "device.switch"   : True,
    }

    #NLP analyze 1.Weather 2.news Iot-1.Light Iot-2.Lock Iot-3.Heating Iot-4.Device on off 6.Other Type
    Diaresponse = parse_user_text( event.message.text )
    

    responseMessenge = ""
    #Check the Action is define or not
    action = ""
    try :
        action    = Diaresponse["result"]["action"]
    except KeyError :
        action    = "otherType"

    print( action )
    #(1) other Type
    if   action == "otherType"  :   
        stickerId =  random.randint(1, 300)
        sticker_message = StickerSendMessage(
            package_id='1',
            sticker_id= stickerId
        )
        line_bot_api.reply_message( event.reply_token, sticker_message )
    #(2) small talk
    elif action[0:9] == "smalltalk" :   
        responseMessenge = Diaresponse["result"]["fulfillment"]["messages"]
        responseMessenge = { i : responseMessenge[i] for i in range(0, len(responseMessenge) ) }
        responseMessenge = responseMessenge[0]["speech"]
    #(Iot-1) smart home Light
    elif action[0:23] == "smarthome.lights.switch" and smartHomeDict["lights.switch"] == True :
        light = smarthomeLight.Light( action, Diaresponse["result"], event_S )
        light.runSmarthome_Light()
        responseMessenge = light.getSpeech() 
    #(Iot-2) smart home Lock
    elif action[0:15] == "smarthome.locks" and smartHomeDict["lock"] == True :     
        lock  = smarthomeLock.Lock( action, Diaresponse["result"], event_S )
        lock.runSmarthome_Lock()
        responseMessenge = lock.getSpeech()
    #(Iot-3) smart home heat
    elif action[0:17] == "smarthome.heating" and smartHomeDict["heating"] == True :
        heat  = smarthomeHeat.Heat( action, Diaresponse["result"], event_S )
        heat.runSmarthome_Heat()
        responseMessenge = heat.getSpeech()
    #(Iot-4) smart home device
    elif action[0:23] == "smarthome.device.switch" and smartHomeDict["device.switch"] == True :
        device  = smarthomeDevice.Device( action, Diaresponse["result"], event_S )
        device.runSmarthome_Device()
        responseMessenge = device.getSpeech()
    # check the weather
    elif action == "check.weather" :
        responseMessenge = weather.runWeather() 
    # check the news
    elif action == "check.news" :
        responseMessenge = news.runNews()
    # Ask about adding new device
    else :
        responseMessenge = "Do you want to add the new IoT device"
     
    if action != "otherType"    :
        line_bot_api.reply_message( event.reply_token, TextSendMessage( text =  responseMessenge ) )



    return 'OK_message'




if __name__ == "__main__":
    app.run( debug = True, port = 80  )
