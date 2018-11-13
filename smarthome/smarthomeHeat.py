import json
import requests
import firebase_admin
from firebase_admin import firestore
import google.cloud.exceptions  # thrown exception


class Heat:
    speech = ""

    def __init__(self, action, result, userId):
        self.action = action
        # dialog flow parameter
        self.parameter = result["parameters"]
        # Line user Id
        self.userId = userId
        # conncect to cloud firestore database
        db = firestore.client()
        # fetch userId database
        self.doc_ref = db.collection(u'light').document(self.userId)
        self.doc = self.doc_ref.get().to_dict()
        print("Enter Heat")

    def runSmarthome_Heat(self):
        print(self.action)
        if (self.action == "smarthome.lights.switch.check"):
            self.smarthome_lights_switch_check()
        elif (self.action == "smarthome.lights.switch.check.off"):
            self.smarthome_lights_switch_check_off()
        elif (self.action == "smarthome.lights.switch.check.on"):
            self.smarthome_lights_switch_check_on()
        elif (self.action == "smarthome.lights.switch.off"):
            self.smarthome_lights_switch_off()
        elif (self.action == "smarthome.lights.switch.on"):
            self.smarthome_lights_switch_on()
        elif (self.action == "smarthome.lights.switch.schedule.off"):
            self.smarthome_lights_switch_schedule_off()
        elif (self.action == "smarthome.lights.switch.schedule.on"):
            self.smarthome_lights_switch_schedule_on()
        else:
            self.speech = "error smarthome action"
            print(self.speech)

    def printCheck(self):
        sOutput = "The "
        if self.parameter["color"] != "":
            sOutput = sOutput + self.parameter["color"] + " "
        if self.parameter["device"] != "":
            sOutput = sOutput + self.parameter["device"] + " "
        sOutput = sOutput + "light in the " + self.parameter["room"] + " is "
        if (self.doc[self.parameter["room"]] == True):
            sOutput = sOutput + "on"
        else:
            sOutput = sOutput + "off"
        return sOutput

    def printCheckAll(self):
        sOutput = "The "
        if self.parameter["color"] != "":
            sOutput = sOutput + self.parameter["color"] + " "
        if self.parameter["device"] != "":
            sOutput = sOutput + self.parameter["device"] + " "
        sOutput = sOutput + "light in the "

        if self.doc["kitchen"] == True and self.doc["bathroom"] == True and self.doc["bedroom"] == True:
            sOutput = sOutput + "all of the room is turned on"
        elif self.doc["kitchen"] == False and self.doc["bathroom"] == False and self.doc["bedroom"] == False:
            sOutput = sOutput + "all of the room is turned off"
        else:
            sOutput = sOutput + "kitchen " + "is "
            if (self.doc["kitchen"] == True):
                sOutput = sOutput + "on, "
            else:
                sOutput = sOutput + "off, "

            sOutput = sOutput + "the bathroom " + "is "
            if (self.doc["bathroom"] == True):
                sOutput = sOutput + "on, "
            else:
                sOutput = sOutput + "off, "

            sOutput = sOutput + "the bedroom " + "is "
            if (self.doc["bedroom"] == True):
                sOutput = sOutput + "on"
            else:
                sOutput = sOutput + "off"

        return sOutput

    def printCheckOn_Off(self, isOn):
        sOutput = ""
        if self.doc[self.parameter["room"]] == isOn:
            sOutput = "yes, it is"
        else:
            sOutput = "no, it is not"

        return sOutput

    def smarthome_lights_switch_check(self):

        if self.parameter["room"] == "bathroom":
            self.speech = self.printCheck()
        elif self.parameter["room"] == "bedroom":
            self.speech = self.printCheck()
        elif self.parameter["room"] == "kitchen":
            self.speech = self.printCheck()
        else:
            self.speech = self.printCheckAll()

        print(self.speech)
        return print("[ Do Mission light_check ]")

    def smarthome_lights_switch_check_off(self):
        if self.parameter["room"] == "bathroom":
            self.speech = self.printCheck()
        elif self.parameter["room"] == "bedroom":
            self.speech = self.printCheck()
        elif self.parameter["room"] == "kitchen":
            self.speech = self.printCheck()
        else:
            self.speech = self.printCheckAll()

        print(self.speech)
        return print("[ Do Mission light_check_off ]")

    def smarthome_lights_switch_check_on(self):
        if self.parameter["room"] == "bathroom":
            self.speech = self.printCheck()
        elif self.parameter["room"] == "bedroom":
            self.speech = self.printCheck()
        elif self.parameter["room"] == "kitchen":
            self.speech = self.printCheck()
        else:
            self.speech = self.printCheckAll()

        print(self.speech)
        return print("[ Do Mission light_check_on ]")

    def smarthome_lights_switch_off(self):
        print(self.parameter)
        if self.parameter["room"] == "bathroom":
            self.doc_ref.update({u'kitchen': False})
        elif self.parameter["room"] == "bedroom":
            self.doc_ref.update({u'kitchen': False})
        elif self.parameter["room"] == "kitchen":
            # self.speech = self.printCheck()
            self.doc_ref.update({u'kitchen': False})
        else:
            self.doc_ref.update({
                u'bedroom': False,
                u'bathroom': False,
                u'kitchen': False,
            })

        self.speech = "Do the turn off instruction"
        return print("light_switch_off")

    def smarthome_lights_switch_on(self):
        print(self.parameter)
        if self.parameter["room"] == "bathroom":
            self.doc_ref.update({u'kitchen': True})
        elif self.parameter["room"] == "bedroom":
            self.doc_ref.update({u'kitchen': True})
        elif self.parameter["room"] == "kitchen":
            # self.speech = self.printCheck()
            self.doc_ref.update({u'kitchen': True})
        else:
            self.doc_ref.update({
                u'bedroom': True,
                u'bathroom': True,
                u'kitchen': True,
            })

        self.speech = "Do the turn on instruction"
        return print("lights_switch_on")

    def smarthome_lights_switch_schedule_off(self):
        print(self.parameter)
        if self.parameter["room"] == "bathroom":
            self.doc_ref.update({u'kitchen': False})
        elif self.parameter["room"] == "bedroom":
            self.doc_ref.update({u'kitchen': False})
        elif self.parameter["room"] == "kitchen":
            # self.speech = self.printCheck()
            self.doc_ref.update({u'kitchen': False})
        else:
            self.doc_ref.update({
                u'bedroom': False,
                u'bathroom': False,
                u'kitchen': False,
                u'time': 50
            })

        self.speech = "Do the turn off with time instruction"
        return print("lights_switch_schedule_off")

    def smarthome_lights_switch_schedule_on(self):
        print(self.parameter["color"])
        if self.parameter["room"] == "bathroom":
            self.doc_ref.update({u'kitchen': True})
        elif self.parameter["room"] == "bedroom":
            self.doc_ref.update({u'kitchen': True})
        elif self.parameter["room"] == "kitchen":
            # self.speech = self.printCheck()
            self.doc_ref.update({u'kitchen': True})
        else:
            self.doc_ref.update({
                u'bedroom': True,
                u'bathroom': True,
                u'kitchen': True,
                u'time': 69
            })

        self.speech = "Do the turn on with time instruction"
        return print("lights_switch_schedule_on")

    def getSpeech(self):
        return self.speech