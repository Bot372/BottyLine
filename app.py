from Model.dModel import *
import uuid


def newData(user_id):
    ids = str(uuid.uuid4())
    line_id = user_id
    insert_data = UserData(id=ids, line_id=line_id)
    db.session.add( insert_data )
    db.session.commit()
    print("DONE")


