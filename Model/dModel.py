from Entity.Entity import *


class UserData(db.Model):
    __tablename__ = 'UserData'

    def __init__(self, line_id):
        #self.id = id
        self.line_id = line_id