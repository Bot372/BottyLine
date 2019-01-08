from firebase_admin import firestore


def addSmarthome(collection, userId, lineId):
    db = firestore.client()

    # Add Data Base
    if collection == 'light':
        # Add light
        doc_ref = db.collection(u'light').document(userId)
        doc_ref.set({
            u'bathroom': False,
            u'bedroom': False,
            u'kitchen': False,
            u'time': -1,
            u'lineId': lineId
        })
    elif collection == 'lock':
        # Add lock
        doc_ref = db.collection(u'lock').document(userId)
        doc_ref.set({
            u'backdoor': False,
            u'frontdoor': False,
            u'windows': False,
            u'time': -1,
            u'lineId': lineId
        })
    elif collection == 'heating':
        # Add heating
        doc_ref = db.collection(u'heating').document(userId)
        doc_ref.set({
            u'temperature': 0,
            u'humidity': 0,
            u'lineId': lineId
        })

    elif collection == 'device':
        # Add device
        doc_ref = db.collection(u'device').document(userId)
        doc_ref.set({
            u'tv': False,
            u'turntable': False,
            u'fan': False,
            u'time': -1,
            u'lineId': lineId
        })

    return print("add " + collection + " smarthome in the database")


def deleteSmarthome(collection, userId):
    db = firestore.client()
    db.collection(collection).document(userId).delete()
    return print("delete" + collection + " smarthome in the database")
