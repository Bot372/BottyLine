import json
import requests
import firebase_admin
from firebase_admin import firestore
import google.cloud.exceptions # thrown exception
from google.api_core.exceptions import AlreadyExists


class Light:
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
        self.doc_ref = db.collection(u'light').document( self.userId )
        self.doc = self.doc_ref.get().to_dict()
        print( "Enter Light" )


    def runSmarthome_Light(self) :
        print( self.action )
        if (  self.action == "smarthome.lights.switch.check" ) :
            self.smarthome_lights_switch_check()
        elif( self.action == "smarthome.lights.switch.check.off" ) :
            self.smarthome_lights_switch_check_on_off( False )
        elif( self.action == "smarthome.lights.switch.check.on" ) :
            self.smarthome_lights_switch_check_on_off( True )
        elif( self.action == "smarthome.lights.switch.off" ) :
            self.smarthome_lights_switch_on_off( False )
        elif( self.action == "smarthome.lights.switch.on" ) :
            self.smarthome_lights_switch_on_off(  True )
        elif( self.action == "smarthome.lights.switch.schedule.off" ) :
            self.smarthome_lights_switch_schedule_on_off( False )
        elif( self.action == "smarthome.lights.switch.schedule.on" ) :
            self.smarthome_lights_switch_schedule_on_off( True )
        else :
            self.speech = "error smarthome action"
            print( self.speech )



    def printCheck( self ) :
        sOutput = "The "
        if self.parameter["color"]  != "" :
            sOutput = sOutput + self.parameter["color"]  + " "
        if self.parameter["device"] != "" :
            sOutput = sOutput + self.parameter["device"] + " "            
        sOutput = sOutput + "light in the " + self.parameter["room"] + " is " 
        if ( self.doc[self.parameter["room"]] == True ) :
            sOutput = sOutput + "on"
        else :
            sOutput = sOutput + "off"
        return sOutput  

    def printCheckAll( self ) :
        sOutput = "The "
        if self.parameter["color"]  != "" :
            sOutput = sOutput + self.parameter["color"]  + " "
        if self.parameter["device"] != "" :
            sOutput = sOutput + self.parameter["device"] + " " 
        sOutput = sOutput + "light in the " 
        
        if self.doc["kitchen"] == True and self.doc["bathroom"] == True and self.doc["bedroom"] == True :
            sOutput = sOutput + "all of the room is turned on"
        elif self.doc["kitchen"] == False and self.doc["bathroom"] == False and self.doc["bedroom"] == False :
            sOutput = sOutput + "all of the room is turned off"
        else :
            sOutput = sOutput + "kitchen " + "is " 
            if ( self.doc["kitchen"] == True ) :
                sOutput = sOutput + "on, "
            else :
                sOutput = sOutput + "off, "

            sOutput = sOutput + "the bathroom " + "is " 
            if ( self.doc["bathroom"] == True ) :
                sOutput = sOutput + "on, "
            else :
                sOutput = sOutput + "off, "

            sOutput = sOutput + "the bedroom " + "is " 
            if ( self.doc["bedroom"] == True ) :
                sOutput = sOutput + "on"
            else :
                sOutput = sOutput + "off"
        
        return sOutput

    def smarthome_lights_switch_check(self) :  

        if  self.parameter["room"] == "bathroom"  :
            self.speech = self.printCheck()            
        elif self.parameter["room"] == "bedroom"   :
            self.speech = self.printCheck()   
        elif self.parameter["room"] == "kitchen"   :
            self.speech = self.printCheck()   
        else :
            self.speech = self.printCheckAll()



        print( self.speech )       
        return print("[ Do Mission light_check ]")

    def smarthome_lights_switch_check_on_off(self, isOn  ) :
        if  self.parameter["room"] == "bathroom"  :
            self.speech = self.printCheck()            
        elif self.parameter["room"] == "bedroom"   :
            self.speech = self.printCheck()      
        elif self.parameter["room"] == "kitchen"   :
            self.speech = self.printCheck()     
        else :
            self.speech = self.printCheckAll()

        print( self.speech ) 
        if isOn is True :
            return print("[ Do Mission light_check_off ]")
        else :
            return print("[ Do Mission light_check_on ]")

    def smarthome_lights_switch_on_off(self, isOn  ) :
        try :
            if  self.parameter["room"] == "bathroom"  :
                self.doc_ref.update({u'bathroom' : isOn})           
            elif self.parameter["room"] == "bedroom"   :
                self.doc_ref.update({u'bedroom' : isOn})     
            elif self.parameter["room"] == "kitchen"   :
                self.doc_ref.update({u'kitchen' : isOn})
            else :
                self.doc_ref.update({
                    u'bedroom' : isOn,
                    u'bathroom': isOn,
                    u'kitchen' : isOn,
                })
        except :
            print( "permission error do it again" )
            print( "is On is : ", isOn   )
            self.smarthome_lights_switch_on_off( isOn )


        if isOn is True :
            self.speech = "Do the turn on instruction"
            return print("lights_switch_on")
        else :
            self.speech = "Do the turn off instruction"
            return print("lights_switche_off")
    
    def smarthome_lights_switch_schedule_on_off( self, isOn ) :
        try :
            if  self.parameter["room"] == "bathroom"  :
                self.doc_ref.update({u'bathroom' : isOn})             
            elif self.parameter["room"] == "bedroom"   :
                self.doc_ref.update({u'bedroom' : isOn})     
            elif self.parameter["room"] == "kitchen"   :
                self.doc_ref.update({u'kitchen' : isOn})
            else :
                self.doc_ref.update({
                    u'bedroom' : isOn,
                    u'bathroom': isOn,
                    u'kitchen' : isOn,
                    u'time'    : 123
                })
        except :
            print( "permission error do it again" )
            self.smarthome_lights_switch_schedule_on_off( isOn )

        if isOn is True :
            self.speech = "Do the turn on with time instruction"
            return print("lights_switch_schedule_on")
        else :
            self.speech = "Do the turn off with time instruction"
            return print("lights_switch_schedule_on")
        

    def getSpeech( self ):

        return self.speech

    

