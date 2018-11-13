from firebase_admin import firestore

from linebot.models import *
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import *
from linebot import LineBotApi

import google.cloud.exceptions # thrown exception

# Fetch the service account key JSON file contents
import Botty_Main
import firebase_admin
from firebase_admin import credentials, firestore
FIREBASE_TOKEN = "bottyline-firebase-adminsdk-bmlr3-abeb3c8d54.json"
cred = credentials.Certificate( FIREBASE_TOKEN )

# Initialize the app with a service account, granting admin privileges
default_app = firebase_admin.initialize_app(cred)


# conncect to cloud firestore database
db = firestore.client()



def add(user_id, profile,event):

    check_user_exist(user_id, profile,event)


def check_user_exist(user_id, profile, event):
    # already_exist


    doc_ref = db.collection(u'user').document(user_id)
    doc = doc_ref.get()
    doc_single = doc.to_dict()
    # print(type(doc_single))
    # print(doc_single["bedroom"]["device"])

    # not_exist
    if doc_single is None:
        #Botty_Main.line_bot_api.reply_message(event.reply_token, TextSendMessage("Hello, Welcome to botty. Do you want to join us ?"))
        Confirm_template = TemplateSendMessage(
            alt_text='Confirm Notice',
            template=ConfirmTemplate(
                title='這是ConfirmTemplate',
                text='Hello, welcome to botty. Do you want to join us ?',
                actions=[
                    PostbackTemplateAction(
                        label='Sure',
                        text='Sure',
                        data='action=buy&itemid=1'
                    ),
                    MessageTemplateAction(
                        label='Later',
                        text='Later'
                    )
                ]
            )
        )
        Botty_Main.line_bot_api.reply_message(event.reply_token, Confirm_template)
        """"
        default = '*******'
        doc_ref = db.collection(u'user').document(user_id)
        doc_ref.set({
            u'lights.switch': True,
            u'lock' : True,
            u'heating' : True,
            u'device.switch': True
        })
        """
    else:
        Botty_Main.line_bot_api.reply_message(event.reply_token, "account is exist")


