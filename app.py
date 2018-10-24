from Model.dModel import *
import uuid

id = str(uuid.uuid4())
line_id = "sss"


insert_data = UserData(id=id
                          , line_id=line_id
                          )
db.session.add(insert_data)
db.session.commit()
print("DONE")


# import new data