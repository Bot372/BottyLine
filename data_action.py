def add_dataAction(user_id, profile,event):

    check_user_exist(user_id, profile,event)


def check_user_exist(user_id, profile, event):
    # already_exist

    # conncect to cloud firestore database
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


