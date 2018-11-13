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
import os
import sys
import random
import data_action
import ast
import json
import apiai  # Dialog Flow Apis


from pyzbar.pyzbar import *
from PIL import Image

#add the smarthome file to current system path
testdir = os.path.dirname(os.path.realpath(__file__)) + "\\smarthome"
sys.path.insert(0, testdir )

from smarthome import smarthomeLight, smarthomeHeat, smarthomeDevice, smarthomeLock, weather, news

import firebase_admin
from firebase_admin import credentials, firestore


#Firebase Api Fetch the service account key JSON file contents
FIREBASE_TOKEN = "bottyline-firebase-adminsdk-bmlr3-abeb3c8d54.json"
cred = credentials.Certificate( FIREBASE_TOKEN )
# Initialize the app with a service account, granting admin privileges
default_app = firebase_admin.initialize_app(cred)




app = Flask(__name__)

line_bot_api = LineBotApi(
    '8PhyG0TWWeOZ1hRJb4618e3UE6jSN+KNdpd8MJjaHUs/moHgGFfvyfv82whJQh0Ebw8fyKODATEbp8fNsFWzydi1S6VMssEB74m6nP2FCpqeOtkpLqfI+O6fx2aIwMma4sXFvw9dY9O53JpoTjda1wdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('e2a156e78a65ba2ffa4eb65c85da5b9f')


audio_result = ""

ACCESS_KEY_ID = 'AKIAIJKNMECREABAM4EA'
ACCESS_SECRET_KEY = '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'
BUCKET_NAME = 'botty-bucket'
#Dialog flow Api
ai = apiai.ApiAI('35d3ac64264d445bb2fd9f04361149b8')



@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    print("Request body: " + body, "Signature: " + signature)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'
"""
@handler.default()
def default(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage("Botty cannot read this type of message!! Please try audio or text message"))
"""

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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #line_bot_api.reply_message(event.reply_token, TextSendMessage("hello text"))

    user_id = str(event)
    user_id = ast.literal_eval(user_id)
    user_id = user_id['source']['userId']

    profile = line_bot_api.get_profile(user_id)

    # conncect to cloud firestore database
    db = firestore.client()# conncect to cloud firestore database
    db = firestore.client()

    doc_ref = db.collection(u'userTextTree').document(user_id)
    doc = doc_ref.get()
    doc_single = doc.to_dict()


    if event.message.text == "bot:add" and (  doc_single == None or doc_single["name"] == "add" ) :
        print("hello")
        if doc_single == None :
            doc_ref.set({
                u'child': {
                    u'name':  "default"
                },
                u'name': "add"
            })



        data_action.add(user_id, profile,event)
    elif event.message.text == "bot:delete" and (  doc_single == None or doc_single["name"] == "delete" )  :
        print("bot:delete")
        if doc_single == None :
            doc_ref.set({
                u'child': {
                    u'name':  "default"
                },
                u'name': "add"
            })
        # delete()
    elif event.message.text == "bot:list" and (  doc_single == None or doc_single["name"] == "list" ) :
        print("bot:list")
        if doc_single == None :
            doc_ref.set({
                u'child': {
                    u'name':  "default"
                },
                u'name': "add"
            })
        # list()
    else :
        # NLP analyze 1.OtherType 2.smalltalk Iot-1.Light Iot-2.Lock Iot-3.Heating Iot-4.Device on off 3.weather 4.news
        Diaresponse = parse_user_text(event.message.text)
        responseMessenge = ""
        action =  Diaresponse["result"]["action"]
        #print( json.dumps(  Diaresponse, indent=4 ) )


        # Check the product in the Database
        # 1. fetch the Product list in the database to dict
        doc_ref = db.collection(u'user').document(user_id)
        doc = doc_ref.get()
        doc_single = doc.to_dict()

        smartHomeDict = {
            "lights.switch": doc_single["lights.switch"],
            "lock": doc_single["lock"],
            "heating": doc_single["heating"],
            "device.switch": doc_single["device.switch"],
        }

        print(action)
        # (1) other Type send sticker or telling a joke
        if action == "input.unknown":
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
            light = smarthomeLight.Light(action, Diaresponse["result"], user_id  )
            light.runSmarthome_Light()
            responseMessenge = light.getSpeech()
            # (Iot-2) smart home Lock
        elif action[0:15] == "smarthome.locks" and smartHomeDict["lock"] == True:
            lock = smarthomeLock.Lock(action, Diaresponse["result"], user_id )
            lock.runSmarthome_Lock()
            responseMessenge = lock.getSpeech()
        # (Iot-3) smart home heat
        elif action[0:17] == "smarthome.heating" and smartHomeDict["heating"] == True:
            heat = smarthomeHeat.Heat(action, Diaresponse["result"], user_id )
            heat.runSmarthome_Heat()
            responseMessenge = heat.getSpeech()
        # (Iot-4) smart home device
        elif action[0:23] == "smarthome.device.switch" and smartHomeDict["device.switch"] == True:
            device = smarthomeDevice.Device(action, Diaresponse["result"], user_id )
            device.runSmarthome_Device()
            responseMessenge = device.getSpeech()
        # (3) check the weather
        elif action == "check.weather":
            responseMessenge = weather.runWeather()
            # (4) check the news
        elif action == "check.news":
            responseMessenge = news.runNews()
        # Ask about adding new device
        else:
            responseMessenge = "Do you want to add the new IoT device"

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=responseMessenge))



    # line_bot_api.reply_message(event.reply_token, TextSendMessage("Botty cannot read what you are talking about!"))
    


@handler.add(MessageEvent, message=StickerMessage)
def handle_message(event):
    print("package_id:", event.message.package_id)
    print("sticker_id:", event.message.sticker_id)
    # ref. https://developers.line.me/media/messaging-api/sticker_list.pdf
    sticker_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 21, 100, 101, 102, 103, 104, 105, 106,
                   107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125,
                   126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 401, 402]
    index_id = random.randint(0, len(sticker_ids) - 1)
    sticker_id = str(sticker_ids[index_id])
    print(index_id)
    sticker_message = StickerSendMessage(
        package_id='1',
        sticker_id=sticker_id
    )
    line_bot_api.reply_message(event.reply_token, sticker_message)

@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    #line_bot_api.reply_message(event.reply_token, TextSendMessage("hello image"))
    id = event.message.id
    message_content = line_bot_api.get_message_content(id)

    file_path = id + ".jpg"
    print( file_path )
    with open(file_path, 'wb') as fd:
        for chunk in message_content.iter_content(chunk_size=1024):
            if chunk:
                fd.write(chunk)

    im = Image.open(file_path)
    im.save('result.png')
    CODE = decode(Image.open('result.png'))

    for x in CODE :
        print(x)

    string_of_code= str(CODE[0][0])

    print(string_of_code)
    code = string_of_c

    ode[2:len(string_of_code)-1]
    print(code)

    if os.path.exists(file_path) :
        os.remove(file_path)
    else:
        print("The file does not exist")

    if os.path.exists('result.png'):
        os.remove('result.png')
    else:
        print("The file does not exist")

    line_bot_api.reply_message(event.reply_token, TextSendMessage(code))

@handler.add(MessageEvent, message=AudioMessage)
def handle_message(event):

    id = event.message.id
    message_content = line_bot_api.get_message_content(id)

    #print( event )
    event_s = str(event)
    event_s = ast.literal_eval(event_s)
    event_s = event_s['source']['userId']


    #line_bot_api.reply_message(event.reply_token, TextSendMessage("hello Audio"))
    #Save Audio File#######################################

    file_path = event_s + ".wav"
    print( file_path )
    with open(file_path, 'wb') as fd:
        for chunk in message_content.iter_content(chunk_size=1024):
            if chunk:
                fd.write(chunk)

    data = open(file_path, 'rb')
    s3 = boto3.resource(
        's3',
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=ACCESS_SECRET_KEY,
        config = Config(signature_version='s3v4')
    )
    s3.Bucket(BUCKET_NAME).put_object(Key= file_path, Body=data)
    #print("Upload Successful")
    #########################################################

    #Get File From AWS#######################################

    url = "https://s3-ap-northeast-1.amazonaws.com/botty-bucket/" + file_path
    audilFile = requests.get(url)

    with open(file_path, 'wb') as fd:
        for chunk in audilFile.iter_content(chunk_size=1024):
            if chunk:
                fd.write(chunk)

    #########################################################


    #Speech_Recognition###
    S_R_Upload.converFile(event_s)
    audio_result = S_R_Upload.Speech_Recognition(event_s)
    if os.path.exists(event_s + ".wav"):
       os.remove(event_s + ".wav")

    else:
        print("The file1 does not exist")

    if os.path.exists(event_s + "M4a.wav" ):
        os.remove(event_s + "M4a.wav" )
    else:
        print("The file2 does not exist")


    print("Audio Result: " + audio_result)



    #line_bot_api.reply_message(event.reply_token, TextSendMessage(audio_result))
    #######################
    
    #file_delete#########################################################


    # if result == bot add, bot delete, bot list call function


if __name__ == "__main__":
    app.run()
