""" Design by BottyLab"""

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

""" Qrcode """

from pyzbar.pyzbar import *
from PIL import Image

import S_R_Upload
import boto3
from botocore.client import Config

import os, sys, random, ast, json, datetime
import apiai  # Dialog Flow Apis
from googletrans import Translator # Google translate

from bs4 import BeautifulSoup
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from datetime import timezone

#add the smarthome file to current system path
testdir = os.path.dirname(os.path.realpath(__file__)) + "\\smarthome"
sys.path.insert(0, testdir )
from smarthome import smarthomeLight, smarthomeHeat, smarthomeDevice, smarthomeLock, weather, news
import Database, Party


# Initialize the app with a service account, granting admin privileges
import firebase_admin
from firebase_admin import credentials, firestore
#Firebase Api Fetch the service account key JSON file contents
FIREBASE_TOKEN = "bottyline-firebase-adminsdk-bmlr3-abeb3c8d54.json"
cred = credentials.Certificate(FIREBASE_TOKEN)
default_app = firebase_admin.initialize_app(cred)

# conncect to cloud firestore database
db = firestore.client()  # conncect to cloud firestore database


app = Flask(__name__)
line_bot_api = LineBotApi('YOUR_LINE_CHATBOT Channel access token ')
handler = WebhookHandler('YOUR_LINE_CHATBOT Channel secret')

""" initailize amazon bucket """
ACCESS_KEY_ID = 'AKIAIJKNMECREABAM4EA'
ACCESS_SECRET_KEY = 'N9IyWNXbNM7f1LzBrKJBfWeOkSGTcIxJHNaOuMk+'
BUCKET_NAME = 'botty-bucket'


#Dialog flow Api
#Dialog flow Api
#smartHome, translate APi : 411c390e69104ae69e51052c92c8ad5a
#weather   Api : bf94e2e4f04243c4b5353fc559c39ad0
ai = apiai.ApiAI('411c390e69104ae69e51052c92c8ad5a')

audio_result = ""

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

def NLP(  event, user_text, user_id ) :
    # NLP analyze 1.OtherType 2.smalltalk Iot-1.Light Iot-2.Lock Iot-3.Heating Iot-4.Device on off 3.weather 4.news
    Diaresponse = parse_user_text(user_text)
    responseMessenge = ""
    action = Diaresponse["result"]["action"]
    # print( json.dumps(  Diaresponse, indent=4 ) )

    # Check the product in the Database
    # 1. fetch the Product list in the database to dict
    doc_ref = db.collection(u'user').document(user_id)
    user_UUID = str()
    if doc_ref is not None :
        doc = doc_ref.get()
        doc_single = doc.to_dict()
        smartHomeDict = {
            "light-switch": doc_single["light-switch"]["situation"],
            "lock": doc_single["lock"]["situation"],
            "heating": doc_single["heating"]["situation"],
            "device-switch": doc_single["device-switch"]["situation"],
        }
    else :
        smartHomeDict = {
            "light-switch": False,
            "lock": False,
            "heating": False,
            "device-switch": False,
        }

    print(action)
    print( smartHomeDict )
    if ("PARTY" in user_text.upper()) is True and (smartHomeDict["light-switch"] == True):
        #line_bot_api.push_message(user_id, TextSendMessage("https://www.youtube.com/watch?v=LlUKzktFYQA"))
        responseMessenge = "https://www.youtube.com/watch?v=LlUKzktFYQA"
        # 戰隊歌
    elif user_text == "南無阿彌陀佛" :
        responseMessenge = "歡迎加入戰隊"
    # (1) other Type send sticker or telling a joke
    elif action == "input.unknown":
        responseMessenge = Diaresponse["result"]["fulfillment"]["messages"]
        responseMessenge = {i: responseMessenge[i] for i in range(0, len(responseMessenge))}
        responseMessenge = responseMessenge[0]["speech"]
    # (2) small talk
    elif action[0:9] == "smalltalk":
        responseMessenge = Diaresponse["result"]["fulfillment"]["messages"]
        responseMessenge = {i: responseMessenge[i] for i in range(0, len(responseMessenge))}
        responseMessenge = responseMessenge[0]["speech"]
    # (Iot-1) smart home Light
    elif action[0:23] == "smarthome.lights.switch" and smartHomeDict["light-switch"] == True :
        user_UUID = doc_single["light-switch"]["UUID"]
        print( user_UUID )
        light = smarthomeLight.Light(action, Diaresponse["result"], user_UUID )
        light.runSmarthome_Light()
        responseMessenge = light.getSpeech()
        # (Iot-2) smart home Lock
    elif action[0:15] == "smarthome.locks" and smartHomeDict["lock"] == True:
        user_UUID = doc_single["lock"]["UUID"]
        lock = smarthomeLock.Lock(action, Diaresponse["result"], user_UUID )
        lock.runSmarthome_Lock()
        responseMessenge = lock.getSpeech()
    # (Iot-3) smart home heat
    elif action[0:17] == "smarthome.heating" and smartHomeDict["heating"] == True:
        user_UUID = doc_single["heating"]["UUID"]
        heat = smarthomeHeat.Heat(action, Diaresponse["result"], user_UUID )
        heat.runSmarthome_Heat()
        responseMessenge = heat.getSpeech()
    # (Iot-4) smart home device
    elif action[0:23] == "smarthome.device.switch" and smartHomeDict["device-switch"] == True:
        user_UUID = doc_single["device-switch"]["UUID"]
        device = smarthomeDevice.Device(action, Diaresponse["result"], user_UUID )
        device.runSmarthome_Device()
        responseMessenge = device.getSpeech()
    # (3) check the weather
    elif action == "check.weather":
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
            print( lanCode[destCode] )
            afterText = translator.translate( originalText, dest= lanCode[destCode] )
            print(afterText)
            return afterText.text

        try :
            originalText = Diaresponse["result"]["parameters"]["text"]
            print( originalText )
            destCode     = Diaresponse["result"]["parameters"]["lang-to"]
            print( destCode )
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
    #line_bot_api.reply_message(event.reply_token, TextSendMessage("hello text"))

    user_id = str(event)
    user_id = ast.literal_eval(user_id)
    user_id = user_id['source']['userId']

    profile = line_bot_api.get_profile(user_id)

    doc_ref_text = db.collection(u'userTextTree').document(user_id)
    doc_text = doc_ref_text.get()
    doc_single_text = doc_text.to_dict()


    #print( delta .total_seconds() )

    # one conversation is alive in only 5 minutes



    if doc_single_text is not None :
        print(  doc_single_text["stock"] )


    if event.message.text == "bot:add" or ( doc_single_text is not None and doc_single_text["stock"][0] == "ADD"  ) :

        # initailize botty text stock with array and timestamp
        # Step1
        if not check_userTextTree(user_id) :
            if check_user_exist(user_id) is True :
                Confirm_template_exist_account = TemplateSendMessage(
                    alt_text='Confirm Notice',
                    template=ButtonsTemplate(
                        title='Welcome Back to Botty ' + profile.display_name,
                        text='Do you want add new device ?',
                        thumbnail_image_url='https://botty.today/botty/welcome.jpg',
                        actions=[
                            PostbackTemplateAction(
                                label='Add Device',
                                text='Add new Device in your account',
                                data='postback1'
                            ),
                            PostbackTemplateAction(
                                label='No new Device',
                                text='No need add in account',
                                data='postback2'
                            )
                        ]
                    )
                )
                line_bot_api.reply_message(event.reply_token, Confirm_template_exist_account)
            else :
                Confirm_template_welcome_to_join = TemplateSendMessage(
                    alt_text='Confirm Notice',
                    template=ButtonsTemplate(
                        title='Hello, Welcome to botty, ' + profile.display_name,
                        text='Do you want to join us ?',
                        thumbnail_image_url='https://botty.today/botty/welcome_1.JPG',
                        actions=[
                            PostbackTemplateAction(
                                label='New Account',
                                text='Add New Account',
                                data='postback1'
                            ),
                            PostbackTemplateAction(
                                label='No New Account',
                                text='No New Account',
                                data='postback2'
                            )
                        ]
                    )
                )
                line_bot_api.reply_message(event.reply_token, Confirm_template_welcome_to_join)

        # Step2-new Account
        #new Account( Yes / No )
        elif event.message.text == "Add New Account" and ( doc_single_text["stock"][0] == "ADD" ) :
            #create new user
            print( "Enter Add new Account" )
            doc_ref = db.collection(u'user').document(user_id)
            doc_ref.set({ u'user_name' : profile.display_name,
                          u'device-switch' : { u'situation' : False, u'UUID' : "******", u'TimeStamp' : datetime.datetime.now()}
                         ,u'heating': {u'situation': False, u'UUID': "******", u'TimeStamp': datetime.datetime.now()}
                         ,u'light-switch': {u'situation': False, u'UUID': "******", u'TimeStamp': datetime.datetime.now()}
                         ,u'lock': {u'situation': False, u'UUID': "******", u'TimeStamp': datetime.datetime.now()}})

            #Database.addSmarthome( user_id ) # Add Empty SmartHome to Database
            #fetch userTextTree and push "AddnewAccount"
            doc_ref_text = db.collection(u'userTextTree').document(user_id)
            doc_text = doc_ref_text.get().to_dict()["stock"]
            doc_text.append( "Add new Account" )
            doc_text.append("Qrcode")
            doc_ref_text.update({u'stock' : doc_text})

            line_bot_api.reply_message(event.reply_token, TextSendMessage("Account Create Successful! Please scan the device Qrcode"))



        elif event.message.text == "No New Account" and doc_single_text["stock"][0] == "ADD" :
            db.collection(u'userTextTree').document(user_id).delete()
            line_bot_api.reply_message(event.reply_token, TextSendMessage("Thank you"))


        # Step2-exist Account
        # Exist Account( Yes / No )
        elif event.message.text == "Add new Device in your account" and ( doc_single_text["stock"][0] == "ADD" ) :


            doc_ref_text = db.collection(u'userTextTree').document(user_id)
            doc_text = doc_ref_text.get().to_dict()["stock"]
            doc_text.append( "Qrcode" )
            doc_ref_text.update({u'stock' : doc_text})
            line_bot_api.reply_message(event.reply_token, TextSendMessage("Please scan the device Qrcode!"))

        elif event.message.text == "No need add in account" and doc_single_text["stock"][0] == "ADD" :
            db.collection(u'userTextTree').document(user_id).delete()
            line_bot_api.reply_message(event.reply_token, TextSendMessage("Thank you"))

    elif event.message.text == "bot:delete" or ( doc_single_text is not None and doc_single_text["stock"][0] == "DELETE"  ) :
        print("bot:delete")
        # delete()

        doc_ref = db.collection(u'user').document(user_id)
        doc= doc_ref.get()
        doc_single = doc.to_dict()

        doc_ref_text = db.collection(u'userTextTree').document(user_id)
        doc_text = doc_ref_text.get()
        doc_single_text = doc_text.to_dict()

        #list()
        if doc_single is not None :
            if doc_single_text is None :
                templist = list()
                if doc_single["device-switch"]["situation"] is True :
                    templist.append("device-switch")

                if doc_single["heating"]["situation"] is True:
                    templist.append("heating")

                if doc_single["light-switch"]["situation"] is True:
                    templist.append("light-switch")

                if doc_single["lock"]["situation"] is True:
                    templist.append("lock")

                tempArray = list()
                tempArray.append("DELETE")
                now = datetime.datetime.now()

                doc_ref_text.set({u'stock': tempArray, u'time': now})
                if (len(templist) > 0):
                    line_bot_api.reply_message(event.reply_token, TextSendMessage("Please type device in one-time"))

                    for x in templist :
                        line_bot_api.push_message(user_id, TextSendMessage("Availible Device : " + x ))
                else :
                    line_bot_api.reply_message(event.reply_token, TextSendMessage("Available Device is empty"))
                    db.collection(u'userTextTree').document(user_id).delete()

            elif doc_single_text["stock"][0] == "DELETE" and event.message.text == "device-switch" or  event.message.text == "heating" or event.message.text == "light-switch" or event.message.text == "lock":
                if event.message.text == "device-switch" :
                    Database.deleteSmarthome("device", doc_single["device-switch"]["UUID"] )  # DELETE DATABASE
                    doc_ref.update({ u'device-switch': {u'situation': False, u'UUID': "******", u'TimeStamp': datetime.datetime.now()}})
                elif event.message.text == "heating" :
                    Database.deleteSmarthome( "heating", doc_single["heating"]["UUID"] )  # DELETE DATABASE
                    doc_ref.update({ u'heating': {u'situation': False, u'UUID': "******", u'TimeStamp': datetime.datetime.now()}})
                elif event.message.text == "light-switch" :
                    Database.deleteSmarthome( "light", doc_single["light-switch"]["UUID"] )  # DELETE DATABASE
                    doc_ref.update({ u'light-switch': {u'situation': False, u'UUID': "******", u'TimeStamp': datetime.datetime.now()}})
                elif event.message.text == "lock" :
                    Database.deleteSmarthome("lock", doc_single["lock"]["UUID"]  )  # DELETE DATABASE
                    doc_ref.update({ u'lock': {u'situation': False, u'UUID': "******", u'TimeStamp': datetime.datetime.now()}})
                line_bot_api.reply_message(event.reply_token, TextSendMessage("Delete Successful"))
                db.collection(u'userTextTree').document(user_id).delete()

            else :
                line_bot_api.reply_message(event.reply_token, TextSendMessage("Please type in right device ! "))

        else :
            line_bot_api.reply_message(event.reply_token, TextSendMessage("you haven't join in our botty"))

    elif event.message.text == "bot:list":
        doc_ref = db.collection(u'user').document(user_id)
        doc = doc_ref.get()
        doc_single = doc.to_dict()

        if doc_single is not None :
            templist = list()
            if doc_single["device-switch"]["situation"] is True:
                templist.append("device-switch")

            if doc_single["heating"]["situation"] is True:
                templist.append("heating")

            if doc_single["light-switch"]["situation"] is True:
                templist.append("light-switch")

            if doc_single["lock"]["situation"] is True:
                templist.append("lock")

            if ( len(templist) > 0 ) :
                line_bot_api.push_message(user_id, TextSendMessage("Availible Device : "))
                for x in templist:
                    line_bot_api.push_message(user_id, TextSendMessage(x))
            else :
                line_bot_api.reply_message(event.reply_token, TextSendMessage("Available Device is empty"))

        else :
            line_bot_api.reply_message(event.reply_token, TextSendMessage("you haven't join in our botty"))

    elif event.message.text == "beauty":
        content = ptt_beauty()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

    elif event.message.text == "test":
        bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url='https://botty.today/botty/light.jpeg',
                size='full',
                aspect_ratio='20:13',
                aspect_mode='cover',
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    # title
                    TextComponent(text='Brown Cafe', weight='bold', size='xl'),
                    # info
                    BoxComponent(
                        layout='vertical',
                        margin='lg',
                        spacing='sm',
                        contents=[
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Place',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text='Shinjuku, Tokyo',
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5
                                    )
                                ],
                            )
                        ],
                    )
                ],
            ),
        )
        message = FlexSendMessage(alt_text="hello", contents=bubble)
        line_bot_api.reply_message(
            event.reply_token,
            message
        )

    # wait to fix
    elif doc_single_text is None :
        line_bot_api.reply_message(event.reply_token, TextSendMessage(NLP(event, event.message.text, user_id)))
        #line_bot_api.reply_message(event.reply_token,  TextSendMessage( "->" + event.message.text))


    else :
        line_bot_api.reply_message(event.reply_token, TextSendMessage( "Internal Error" ))

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


    # get data
    user_id = str(event)
    user_id = ast.literal_eval(user_id)
    user_id = user_id['source']['userId']

    doc_ref_text = db.collection(u'userTextTree').document(user_id)
    doc_text = doc_ref_text.get()
    doc_single_text = doc_text.to_dict()

    if doc_single_text is not None and doc_single_text["stock"][len( doc_single_text["stock"] ) - 1 ] == "Qrcode":
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
        code = decode(Image.open('result.png'))

        # make sure it's a Qrcode
        if len(code) > 0 :
            for x in code:
                print(x)

            string_of_code = str(code[0][0])
            code = string_of_code[2:len(string_of_code) - 1 ]
            code = ast.literal_eval(code)

            try:
                code = string_of_code[2:len(string_of_code) - 1 ]
                code = ast.literal_eval( code  )
                if os.path.exists(file_path):
                    os.remove(file_path)
                else:
                    print("The file does not exist")

                if os.path.exists('result.png'):
                    os.remove('result.png')
                else:
                    print("The file does not exist")

                doc_user = db.collection(u'user').document(user_id)
                doc_ref_devices = db.collection(u'devices_id').document(code["UUID"])


                try :
                    #print(type(code))
                    #print(code["type"])

                    # not finish
                    # 1 check device whether has been register before.
                    # 2 use flex-message to reply( to be more design) - use photos
                    profile = line_bot_api.get_profile(user_id)


                    #line_bot_api.reply_message(event.reply_token, Image_Carousel)


                    if doc_user.get().to_dict()[code["type"]]["situation"] is False:
                        if doc_ref_devices.get().to_dict() is not None and doc_ref_devices.get().to_dict()[code["UUID"]]["owner"] != profile.display_name :
                             doc_devices = doc_ref_devices.get().to_dict()
                             line_bot_api.push_message(user_id,TextSendMessage("Devive : " + code["UUID"] + "\nis already be registered to -" + doc_devices[code["UUID"]]["owner"]))
                        else :
                            doc_user.update({code["type"]: {u'situation': True, u'UUID': code["UUID"], u'TimeStamp': datetime.datetime.now()}})
                            userToDeviceDict = {'device-switch': 'device', 'heating': 'heating', 'light-switch': 'light', 'lock' : 'lock'  }
                            Database.addSmarthome(  userToDeviceDict[ code["type"] ] , code["UUID"], profile.display_name ) # ADD SmartHOme to Database
                            doc_ref_devices.set({ code["UUID"] : { u'owner' : profile.display_name } })
                            line_bot_api.reply_message(event.reply_token,TextSendMessage("Add Device Successful!"))
                            string_to_reply = "welcome"

                            owner = "Owner : "+ profile.display_name
                            if code["type"] == "lock" :
                                urla = 'https://botty.today/botty/lock.jpg'
                                typea = 'lock'
                            else:
                                urla = 'https://botty.today/botty/light.jpeg'
                                typea = 'light'

                            bubble = BubbleContainer(
                                direction='ltr',
                                hero=ImageComponent(
                                    url= urla,
                                    size='full',
                                    aspect_ratio='20:13',
                                    aspect_mode='cover',
                                ),
                                body=BoxComponent(
                                    layout='vertical',
                                    contents=[
                                        # title
                                        TextComponent(text=owner, weight='bold', size='xl'),
                                        # info
                                        BoxComponent(
                                            layout='vertical',
                                            margin='lg',
                                            spacing='sm',
                                            contents=[
                                                BoxComponent(
                                                    layout='baseline',
                                                    spacing='sm',
                                                    contents=[
                                                        TextComponent(
                                                            text='Device : ',
                                                            color='#aaaaaa',
                                                            size='sm',
                                                            flex=2
                                                        ),
                                                        TextComponent(
                                                            text= typea,
                                                            wrap=True,
                                                            color='#666666',
                                                            size='sm',
                                                            flex=5
                                                        )
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                ),
                            )


                            message = FlexSendMessage(alt_text="Add Device ", contents=bubble)
                            line_bot_api.push_message(user_id,message)
                    else:
                        line_bot_api.reply_message(event.reply_token, TextSendMessage("Scan success, But you have existed Device"))


                    db.collection(u'userTextTree').document(user_id).delete()

                except TypeError :
                    line_bot_api.reply_message(event.reply_token,TextSendMessage("Scan Failure,This is not our Qrcode . please scan device qrcode again!"))

            except SyntaxError :
               line_bot_api.reply_message(event.reply_token,TextSendMessage("Scan Failure,This is not our Qrcode( Value Error ) . please scan device qrcode again!"))



        else :
            line_bot_api.reply_message(event.reply_token, TextSendMessage("Scan Failure, please scan device qrcode again!"))

    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage( "Nice pic" ))

@handler.add(MessageEvent, message=AudioMessage)
def handle_message(event):

    id = event.message.id
    message_content = line_bot_api.get_message_content(id)

    #print( event )
    user_id = str(event)
    user_id= ast.literal_eval(user_id)
    user_id = user_id['source']['userId']


    #line_bot_api.reply_message(event.reply_token, TextSendMessage("hello Audio"))
    #Save Audio File#######################################

    file_path = user_id + ".wav"
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
    S_R_Upload.converFile(user_id)
    audio_result = S_R_Upload.Speech_Recognition(user_id)
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



    line_bot_api.reply_message(event.reply_token, TextSendMessage( NLP(event, audio_result, user_id)  ) )

def add_dataAction(user_id):

    check_user_exist(user_id)

def check_user_exist(user_id):
    # already_exist

    doc_ref = db.collection(u'user').document(user_id)
    doc = doc_ref.get()
    doc_single = doc.to_dict()


    # not_exist
    if doc_single is not None:
        return True
    else :
        return False

def check_userTextTree(user_id):
    doc_ref_text = db.collection(u'userTextTree').document(user_id)
    doc_text = doc_ref_text.get()
    doc_single_text = doc_text.to_dict()

    if doc_single_text is None:
        tempArray = list()
        tempArray.append("ADD")

        now = datetime.datetime.now()
        doc_ref_text.set({u'stock' : tempArray, u'time' : now })

        return False
    else :
        return True





""" ptt beauty """
def get_page_number(content):
    start_index = content.find('index')
    end_index = content.find('.html')
    page_number = content[start_index + 5: end_index]
    return int(page_number) + 1

def craw_page(res, push_rate):
    soup_ = BeautifulSoup(res.text, 'html.parser')
    article_seq = []
    for r_ent in soup_.find_all(class_="r-ent"):
        try:
            # 先得到每篇文章的篇url
            link = r_ent.find('a')['href']
            if link:
                # 確定得到url再去抓 標題 以及 推文數
                title = r_ent.find(class_="title").text.strip()
                rate = r_ent.find(class_="nrec").text
                url = 'https://www.ptt.cc' + link
                if rate:
                    rate = 100 if rate.startswith('爆') else rate
                    rate = -1 * int(rate[1]) if rate.startswith('X') else rate
                else:
                    rate = 0
                # 比對推文數
                if int(rate) >= push_rate:
                    article_seq.append({
                        'title': title,
                        'url': url,
                        'rate': rate,
                    })
        except Exception as e:
            # print('crawPage function error:',r_ent.find(class_="title").text.strip())
            print('本文已被刪除', e)
    return article_seq

def ptt_beauty():
    rs = requests.session()
    res = rs.get('https://www.ptt.cc/bbs/Beauty/index.html', verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    all_page_url = soup.select('.btn.wide')[1]['href']
    start_page = get_page_number(all_page_url)
    page_term = 2  # crawler count
    push_rate = 10  # 推文
    index_list = []
    article_list = []
    for page in range(start_page, start_page - page_term, -1):
        page_url = 'https://www.ptt.cc/bbs/Beauty/index{}.html'.format(page)
        index_list.append(page_url)

    # 抓取 文章標題 網址 推文數
    while index_list:
        index = index_list.pop(0)
        res = rs.get(index, verify=False)
        # 如網頁忙線中,則先將網頁加入 index_list 並休息1秒後再連接
        if res.status_code != 200:
            index_list.append(index)
            # print u'error_URL:',index
            # time.sleep(1)
        else:
            article_list = craw_page(res, push_rate)
            # print u'OK_URL:', index
            # time.sleep(0.05)
    content = ''
    for article in article_list:
        data = '[{} push] {}\n{}\n\n'.format(article.get('rate', None), article.get('title', None),
                                             article.get('url', None))
        content += data
    return content

""" ptt beauty """

if __name__ == "__main__":
    app.run()


    
    
    

