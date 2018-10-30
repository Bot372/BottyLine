from Model.dModel import *



def newData(user_id):

    line_id = str(user_id)
    insert_data = UserData(line_id=line_id)
    db.session.add( insert_data )
    db.session.commit()
    print("DONE")





