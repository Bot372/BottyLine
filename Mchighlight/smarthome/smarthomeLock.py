import json
import requests
import firebase_admin
from firebase_admin import firestore
import google.cloud.exceptions # thrown exception


class Lock:
    speech = ""


    def __init__( self, action, result, userId ) :
        self.action = action
        #dialog flow parameter
        self.parameter = result["parameters"]
        # Line user Id
        self.userId = userId
        # conncect to cloud firestore database
        db = firestore.client()
        # fetch userId database
        self.doc_ref = db.collection(u'lock').document( self.userId )
        self.doc = self.doc_ref.get().to_dict()
        print( "Enter Lock" )

    def runSmarthome_Lock(self) :
        print( self.action )
        if (  self.action == "smarthome.locks.check" ) :
            self.smarthome_locks_check()
        elif( self.action == "smarthome.locks.check.close" or
              self.action == "smarthome.locks.check.lock" ) :
            self.smarthome_locks_check_lock_unlock( False )
        elif( self.action == "smarthome.locks.check.open" or 
              self.action == "smarthome.locks.check.unlock"  ) :
            self.smarthome_locks_check_lock_unlock( True )
        elif( self.action == "smarthome.locks.close" or 
              self.action == "smarthome.locks.lock"  ) :
            self.smarthome_locks_lock_unlock( False )
        elif( self.action == "smarthome.locks.open" or 
              self.action == "smarthome.locks.unlock" ) :
            self.smarthome_locks_lock_unlock( True )
        elif( self.action == "smarthome.locks.schedule.close" or
              self.action == "smarthome.locks.schedule.lock" ) :
            self.smarthome_locks_schedule_lock_unlock( False )
        elif( self.action == "smarthome.locks.schedule.open"  or 
              self.action == "smarthome.locks.schedule.unlock" ) :
            self.smarthome_locks_schedule_lock_unlock( True )
        else :
            self.speech = "error smarthome Lock action"
            print( self.speech )



    def printCheck( self ) :
        sOutput = "The "
        if self.parameter["lock"]  != "" :
            sOutput = sOutput + self.parameter["lock"]  + " "
        #Check the room
        if self.parameter["room"] != "" and self.parameter["lock"] != "" :
            sOutput = sOutput + "in the " + self.parameter["room"] + " is "            
        elif self.parameter["room"] != "" and self.parameter["lock"] == "" :
            sOutput = sOutput + self.parameter["room"] + " is " 
        else :
            sOutput = sOutput + "is "
        #Check lock status
        if ( self.doc[self.parameter["lock"]] == True ) :
            sOutput = sOutput + "on"
        else :
            sOutput = sOutput + "off"

        return sOutput  

    def printCheckAll( self ) :
        sOutput = "The "
       
        if self.doc["backdoor"] == True and self.doc["frontdoor"] == True and self.doc["windows"] == True :
            sOutput = "all of the room is opened"
        elif self.doc["backdoor"] == False and self.doc["frontdoor"] == False and self.doc["windows"] == False :
            sOutput = "all of the room is closed"
        else :
            sOutput = sOutput + "backdoor " + "is " 
            if ( self.doc["backdoor"] == True ) :
                sOutput = sOutput + "opened, "
            else :
                sOutput = sOutput + "closed, "

            sOutput = sOutput + "the frontdoor " + "is " 
            if ( self.doc["frontdoor"] == True ) :
                sOutput = sOutput + "opended, "
            else :
                sOutput = sOutput + "closed, "

            sOutput = sOutput + "the windows " + "is " 
            if ( self.doc["windows"] == True ) :
                sOutput = sOutput + "opended"
            else :
                sOutput = sOutput + "closed"
        
        return sOutput

    def smarthome_locks_check(self) :  

        if  self.parameter["lock"] == "backdoor"  :
            self.speech = self.printCheck()            
        elif self.parameter["lock"] == "frontdoor"   :
            self.speech = self.printCheck()   
        elif self.parameter["lock"] == "windows"   :
            self.speech = self.printCheck()   
        else :
            self.speech = self.printCheckAll()



        print( self.speech )       
        return print("[ Do Mission locks_check ]")

    def smarthome_locks_check_lock_unlock(self, isOn) :
        if  self.parameter["lock"] == "backdoor"  :
            self.speech = self.printCheck()             
        elif self.parameter["lock"] == "frontdoor"   :
            self.speech = self.printCheck()     
        elif self.parameter["lock"] == "windows"   :
            self.speech = self.printCheck()      
        else :
            self.speech = self.printCheckAll()

        print( self.speech ) 
        if isOn is True :
            return print("[ Do Mission locks_check_unlock ]")
        else :
            return print("[ Do Mission locks_check_lock ]")

    def smarthome_locks_lock_unlock(self, isOn ) :
        try :
            if  self.parameter["lock"] == "backdoor"  :
                self.doc_ref.update({u'backdoor' : isOn})             
            elif self.parameter["lock"] == "frontdoor"   :
                self.doc_ref.update({u'frontdoor' : isOn})     
            elif self.parameter["lock"] == "windows"   : 
                self.doc_ref.update({u'windows' : isOn })
            else :
                self.doc_ref.update({
                    u'backdoor' : isOn,
                    u'frontdoor': isOn,
                    u'windows' :  isOn,
                })
        except :
            self.smarthome_locks_lock_unlock( isOn )

        if isOn is True :
            if self.parameter["lock"] == "backdoor" or self.parameter["lock"] == "frontdoor" or self.parameter["lock"] == "windows" :
                self.speech = "Unlock the " + str(self.parameter["lock"])
            else :
                self.speech = "Unlock all the door" 
            return print("[ Do Mission locks_lock ]")
        else :
            if self.parameter["lock"] == "backdoor" or self.parameter["lock"] == "frontdoor" or self.parameter["lock"] == "windows"  :
                self.speech = "lock the " + str(self.parameter["lock"])
            else :
                self.speech = "lock all the door"
            return print("[ Do Mission locks_unlock ]")
 
    def smarthome_locks_schedule_lock_unlock( self, isOn ) :
        try :
            if  self.parameter["lock"] == "backdoor"  :
                self.doc_ref.update({u'backdoor' : isOn})             
            elif self.parameter["lock"] == "frontdoor"   :
                self.doc_ref.update({u'frontdoor' : isOn})     
            elif self.parameter["lock"] == "windows"   :
                self.doc_ref.update({u'windows' : isOn})
            else :
                self.doc_ref.update({
                    u'backdoor' : isOn,
                    u'frontdoor': isOn,
                    u'windows'  : isOn,
                    u'time'    : 50
                })
        except :
            self.smarthome_locks_schedule_lock_unlock( isOn )

        if isOn is True :
            if self.parameter["lock"] == "backdoor" or self.parameter["lock"] == "frontdoor" or self.parameter["lock"] == "windows" :
                self.speech = "Unlock the " + str(self.parameter["lock"])
            else :
                self.speech = "Unlock all the door" 
            return print("[ Do Mission locks_schedule_unlock ]")
        else :
            if self.parameter["lock"] == "backdoor" or self.parameter["lock"] == "frontdoor" or self.parameter["lock"] == "windows" :
                self.speech = "lock the " + str(self.parameter["lock"])
            else :
                self.speech = "lock all the door"
            return print("[ Do Mission locks_schedule_lock ]")

    def getSpeech( self ):
        return self.speech

    

