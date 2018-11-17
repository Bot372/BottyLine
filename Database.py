from firebase_admin import firestore




def addSmarthome( collection ,userId ) :
    db = firestore.client()
    # Add Data Base
    if collection == 'light' :
        #Add light
        doc_ref = db.collection(u'light').document( userId )
        doc_ref.set({
            u'bathroom' : False,
            u'bedroom'  : False,
            u'kitchen'  : False,
            u'time'     : 79
        })
    elif collection == 'lock' :
        #Add lock
        doc_ref = db.collection(u'lock').document( userId )
        doc_ref.set({
            u'backdoor'   : False,
            u'frontdoor'  : False,
            u'windows'    : False,
            u'time'       : 79
        })
    elif collection == 'heating' :
        #Add heating
        doc_ref = db.collection(u'heating').document( userId )
        doc_ref.set({
            u'bedroom'     : {
                u'device' : {
                    u'status' : False,
                    u'time'   : 30,
                    u'value'  : 30
                },
                u'temp' : 30
            },
            u'diningroom'  : {
                u'device' : {
                    u'status': False,
                    u'time': 30,
                    u'value': 30
                },
                u'temp' : 30
            },
            u'livingroom'  : {
                u'device' : {
                    u'status': False,
                    u'time': 30,
                    u'value': 30
                },
                u'temp' : 30
            }
        })
    elif collection == 'device' :
        #Add device
        doc_ref = db.collection(u'device').document( userId )
        doc_ref.set({
            u'bedroom'     : {
                u'fan' : {
                    u'status' : False,
                    u'time'   : 30,
                    u'value'  : 30
                },
                u'turnable' : {
                    u'status' : False,
                    u'time'   : 30,
                    u'value'  : 30
                },
                u'tv': {
                    u'status': False,
                    u'time': 30,
                    u'value': 30
                }
            },
            u'diningroom'  : {
                u'fan' : {
                    u'status' : False,
                    u'time'   : 30,
                    u'value'  : 30
                },
                u'turnable' : {
                    u'status' : False,
                    u'time'   : 30,
                    u'value'  : 30
                },
                u'tv': {
                    u'status': False,
                    u'time': 30,
                    u'value': 30
                }
            },
            u'livingroom'  : {
                u'fan' : {
                    u'status' : False,
                    u'time'   : 30,
                    u'value'  : 30
                },
                u'turnable' : {
                    u'status' : False,
                    u'time'   : 30,
                    u'value'  : 30
                },
                u'tv': {
                    u'status': False,
                    u'time': 30,
                    u'value': 30
                }
            }
        })
    return print( "add " + collection + " smarthome in the database"   )

def deleteSmarthome( collection, userId ) :
    db = firestore.client()
    db.collection( collection ).document( userId ).delete()
    return print( "delete" + collection + " smarthome in the database" )