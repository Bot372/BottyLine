from faker import Factory
from firebase_admin import firestore
from threading import Timer, Event


def runParty(userId):

    def PartyOver():
        print("Party Over")
        ev.set()

    t = Timer(60, PartyOver)
    ev = Event()
    t.start()
    i = 0
    #userId = 'U6e3f595a7fe48e3c9622cbb1169ff461'
    db = firestore.client()
    doc_ref = db.collection(u'light').document(userId)
    doc_ref2 = db.collection(u'lock').document(userId)
    while not ev.isSet():

        fake = Factory.create()
        doc_ref2.update(
            {u'frontdoor': fake.boolean(chance_of_getting_true=50)})
        doc_ref.update({u'bedroom': fake.boolean(chance_of_getting_true=50)})
        doc_ref.update({u'bathroom': fake.boolean(chance_of_getting_true=50)})
        doc_ref2.update({u'windows': fake.boolean(chance_of_getting_true=50)})
        doc_ref.update({u'kitchen': fake.boolean(chance_of_getting_true=50)})
        doc_ref2.update({u'backdoor': fake.boolean(chance_of_getting_true=50)})

    return "Party is over "
