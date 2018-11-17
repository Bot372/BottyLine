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


from bs4 import BeautifulSoup
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


#add the smarthome file to current system path
from smarthome import smarthomeLight, smarthomeHeat, smarthomeDevice, smarthomeLock, weather, news
testdir = os.path.dirname(os.path.realpath(__file__)) + "\\smarthome"
sys.path.insert(0, testdir )


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
line_bot_api = LineBotApi(
    '8PhyG0TWWeOZ1hRJb4618e3UE6jSN+KNdpd8MJjaHUs/moHgGFfvyfv82whJQh0Ebw8fyKODATEbp8fNsFWzydi1S6VMssEB74m6nP2FCpqeOtkpLqfI+O6fx2aIwMma4sXFvw9dY9O53JpoTjda1wdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('e2a156e78a65ba2ffa4eb65c85da5b9f')

""" initailize amazon bucket """
ACCESS_KEY_ID = 'AKIAIJKNMECREABAM4EA'
ACCESS_SECRET_KEY = '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'
BUCKET_NAME = 'botty-bucket'


#Dialog flow Api
ai = apiai.ApiAI('35d3ac64264d445bb2fd9f04361149b8')

audio_result = ""

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
    doc = doc_ref.get()
    doc_single = doc.to_dict()

    smartHomeDict = {
        "lights-switch": doc_single["lights-switch"]["situation"],
        "lock": doc_single["lock"]["situation"],
        "heating": doc_single["heating"]["situation"],
        "device-switch": doc_single["device-switch"]["situation"],
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
    elif action[0:23] == "smarthome.lights-switch" and smartHomeDict["lights-switch"] == True:
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
    elif action[0:23] == "smarthome.device-switch" and smartHomeDict["device-switch"] == True:
        device = smarthomeDevice.Device(action, Diaresponse["result"], user_id)
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
    if doc_single_text is not None :
        print(  doc_single_text["stock"] )



    if event.message.text == "bot:add" or ( doc_single_text is not None and doc_single_text["stock"][0] == "ADD"  ) :

        # initailize botty text stock with array and timestamp
        # Step1
        if not check_userTextTree(user_id) :
            if check_user_exist(user_id) is True :
                Confirm_template = TemplateSendMessage(
                    alt_text='Confirm Notice',
                    template=ConfirmTemplate(title='這是ConfirmTemplate',text='Hello, welcome back to botty. Do you want add new device ?',
                        actions=[PostbackTemplateAction(label='Add New Device',text='Add new Device in your account',data='action=buy&itemid=1'),
                            MessageTemplateAction(label='No New Account',text='No need add in account')
                        ]
                    )
                )

                line_bot_api.reply_message(event.reply_token, Confirm_template)
            else :
                Confirm_template = TemplateSendMessage(
                    alt_text='Confirm Notice',
                    template=ConfirmTemplate(title='這是ConfirmTemplate',text='Hello, welcome to botty. Do you want to join us ?',
                        actions=[PostbackTemplateAction(label='Add New Account ',text='Add new Account',data='action=buy&itemid=1'),
                            MessageTemplateAction(label='No New Account',text='No New Account')
                        ]
                    )
                )

                line_bot_api.reply_message(event.reply_token, Confirm_template)

        # Step2-new Account
        #new Account( Yes / No )
        elif event.message.text == "Add new Account" and ( doc_single_text["stock"][0] == "ADD" ) :
            #create new user
            print( "Enter Add new Account" )
            doc_ref = db.collection(u'user').document(user_id)
            doc_ref.set({ u'device-switch' : { u'situation' : False, u'UUID' : "******", u'TimeStamp' : datetime.datetime.now()}
                         ,u'heating': {u'situation': False, u'UUID': "******", u'TimeStamp': datetime.datetime.now()}
                         ,u'light-switch': {u'situation': False, u'UUID': "******", u'TimeStamp': datetime.datetime.now()}
                         ,u'lock': {u'situation': False, u'UUID': "******", u'TimeStamp': datetime.datetime.now()}})

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
                    doc_ref.update({ u'device-switch': {u'situation': False, u'UUID': "******", u'TimeStamp': datetime.datetime.now()}})

                elif event.message.text == "heating" :
                    doc_ref.update({ u'heating': {u'situation': False, u'UUID': "******", u'TimeStamp': datetime.datetime.now()}})

                elif event.message.text == "light-switch" :
                    doc_ref.update({ u'light-switch': {u'situation': False, u'UUID': "******", u'TimeStamp': datetime.datetime.now()}})

                elif event.message.text == "lock" :
                    doc_ref.update({ u'lock': {u'situation': False, u'UUID': "******", u'TimeStamp': datetime.datetime.now()}})

                line_bot_api.reply_message(event.reply_token, TextSendMessage("Delete Successful"))
                db.collection(u'userTextTree').document(user_id).delete()

            else :
                line_bot_api.reply_message(event.reply_token, TextSendMessage("Please type in right device"))

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
                    """
                    if x == "lock":
                        url = 'https://botty.today/botty/lock.jpg'
                        reply = 'lock'

                    else:
                        url = 'https://botty.today/botty/light.jpeg'
                        reply = 'light'



                    Image_Carousel = TemplateSendMessage(
                        alt_text='Light has been added',
                        template=ImageCarouselTemplate(
                            columns=[
                                ImageCarouselColumn(
                                    image_url= url,
                                    action=PostbackTemplateAction(
                                        label= reply,
                                        text='-',
                                        data='-'
                                    )
                                ),
                            ]
                        )
                    )
                    """
                    line_bot_api.push_message(user_id, TextSendMessage(x))
            else :
                line_bot_api.reply_message(event.reply_token, TextSendMessage("Available Device is empty"))


    elif event.message.text == "beauty":
        content = ptt_beauty()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0


    # wait to fix
    elif doc_single_text is None :
        #line_bot_api.reply_message(event.reply_token, TextSendMessage(NLP(event, event.message.text, user_id)))
        line_bot_api.reply_message(event.reply_token,  TextSendMessage( "->" + event.message.text))


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
                        if doc_ref_devices.get().to_dict() is not None and doc_ref_devices.get().to_dict()["owner"] != profile.display_name :
                             doc_devices = doc_ref_devices.get().to_dict()
                             line_bot_api.push_message(user_id,TextSendMessage("Devive : " + code["UUID"] + "\nis already be registered to -" + doc_devices["owner"]))
                        else :
                            doc_user.update({code["type"]: {u'situation': True, u'UUID': code["UUID"], u'TimeStamp': datetime.datetime.now()}})
                            doc_ref_devices.set({ code["UUID"] : profile.display_name })
                            line_bot_api.reply_message(event.reply_token,TextSendMessage("Add Device Successful!"))
                            string_to_reply = "welcome"

                            if code["type"] == "lock" :
                                url = 'https://botty.today/botty/lock.jpg'
                            else:
                                url = 'https://botty.today/botty/light.jpeg'

                            Image_Carousel = TemplateSendMessage(
                                alt_text='Light has been added',
                                template=ImageCarouselTemplate(
                                    columns=[
                                        ImageCarouselColumn(
                                            image_url=url,
                                            action=PostbackTemplateAction(
                                                label= string_to_reply,
                                                text='-',
                                                data='-'
                                            )
                                        ),
                                    ]
                                )
                            )
                            line_bot_api.push_message(user_id,Image_Carousel)
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



    line_bot_api.reply_message(event.reply_token, TextSendMessage( NLP(event, audio_result, user_id)  ) )

def add_dataAction(user_id, profile,event):

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


    
    
    

