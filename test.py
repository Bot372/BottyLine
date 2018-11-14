
import json
import requests
import firebase_admin
from firebase_admin import credentials, firestore
import google.cloud.exceptions # thrown exception
import datetime
# Fetch the service account key JSON file contents
FIREBASE_TOKEN = "bottyline-firebase-adminsdk-bmlr3-abeb3c8d54.json"
cred = credentials.Certificate( FIREBASE_TOKEN )

# Initialize the app with a service account, granting admin privileges
default_app = firebase_admin.initialize_app(cred)

# conncect to cloud firestore database
db = firestore.client()
"""
doc_ref = db.collection(u'userTextTree').document(u'455544544')
doc = doc_ref.get()
doc_single = doc.to_dict()
print( type( doc_single["time"] ) )

#array get
testArray = doc_single["abc"]
print( testArray )
print(  type( testArray )  )
print( testArray )

# array update//////////////////////////////////////////////
testArray.append( 'Add' )
#testDict  = dict( testArray )
#print( aye )
doc_ref.update({u'test' : testArray})

# array delete
#testArray.pop(1)
#testArray.remove("Add")

#print( doc_single )
"""
doc_ref_text = db.collection(u'userTextTree').document("455544544")
doc_text = doc_ref_text.get()
doc_single_text = doc_text.to_dict()

tempArray = list()
tempArray.append("ADD")

now = datetime.datetime.now()
print(now)
doc_ref_text.set({u'stock': tempArray, u'time' : now})

'''
# Add Data Base
doc_ref = db.collection(u'user').document(u'Uea3e3f87d6adaf08043d5fcaee99d54e')
doc_ref.set({
    u'bedroom' : {
        u'device' : {
            'status' : False,
            'time' : {
                'second' : 123,
                'hour' : 123
            },
            'value': 30
        },
        u'temp' : 30
    },
    u'diningroom': {
        'device' : {
            'status' : False,
            'time' : 30,
            'value': 30
        },
        'temp' : 30
    },
    u'livingroom' : {
        'device' : {
            'status' : False,
            'time' : 30,
            'value': 30
        },
        'temp' : 30
    },
})
'''

'''
# Update Data base

id = "Uea3e3f87d6adaf08043d5fcaee99d54e"
doc_ref = db.collection(u'user').document( id )
doc_ref.update({u'bedroom.device.time' : 1000, u'livingroom.time' :6969 })



#Update Multiple Data base
doc_ref.update({
    u'bedroom' : False,
    u'bathroom': False,
    u'kitchen' : False,
    u'time'    : 79
})
'''


#get_check exists()
#doc_ref = db.collection(u'light').document(u'Ezp9UP0F5dMQiASHLvAZ')
'''
try:
    id = "8IGNabyDCYnDK3Nb5UtL"
    doc_ref = db.collection(u'heating').document( id )
    doc = doc_ref.get()
    doc_single = doc.to_dict()
    #print(doc_single)
    print(doc_single["bedroom"]["device"])
except google.cloud.exceptions.NotFound:
    print( u'No such Document!' )
'''





'''
# fetch all the data
try:
    users_ref = db.collection(u'heating')
    docs = users_ref.get()
    for doc in docs:
        print(u'{} => {}'.format(doc.id, doc.to_dict()))
    #get the Data from firebase
except google.cloud.exceptions.NotFound:
    print( u'NO such document!' )
'''


'''
# delete single doc
db.collection(u'user').document(u'Uea3e3f87d6adaf08043d5fcaee99d54e').delete()
'''


"""
#delete field
doc_ref = db.collection(u'user').document(u'KzB4qhkkLp5a6VWEyX81')
doc_ref.update({
    u'device.device' : firestore.DELETE_FIELD
})
"""

"""
#delete_full_collection
def delete_full_collection():
    db = firestore.Client()

    # [START delete_full_collection]
    def delete_collection(coll_ref, batch_size):
        docs = coll_ref.limit(10).get()
        deleted = 0

        for doc in docs:
            print(u'Deleting doc {} => {}'.format(doc.id, doc.to_dict()))
            doc.reference.delete()
            deleted = deleted + 1

        if deleted >= batch_size:
            return delete_collection(coll_ref, batch_size)
    # [END delete_full_collection]

    delete_collection(db.collection(u'cities'), 10)
"""

 