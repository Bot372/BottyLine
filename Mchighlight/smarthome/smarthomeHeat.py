import json
import requests
import firebase_admin
from firebase_admin import firestore
import google.cloud.exceptions # thrown exception


class Heat:
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
        self.doc_ref = db.collection(u'heating').document( self.userId )
        self.doc = self.doc_ref.get().to_dict()
        print( "Enter Heat" )


    def runSmarthome_Heat(self) :
        print( self.action )
        if (  self.action == "smarthome.heating.check"  ) :
            self.smarthome_heating_check()
        elif( self.action == "smarthome.heating.switch.off" ) :
            self.smarthome_heating_switch_on_off( False )
        elif( self.action == "smarthome.heating.switch.on" ) :
            self.smarthome_heating_switch_on_off( True )
        elif( self.action == "smarthome.heating.switch.schedule.off" ) :
            self.smarthome_heating_switch_schedule_on_off( False )
        elif( self.action == "smarthome.heating.switch.schedule.on" ) :
            self.smarthome_heating_switch_schedule_on_off( True )
        elif( self.action == "smarthome.heating.down" ) :
            self.smarthome_heating_down_up( False )
        elif( self.action == "smarthome.heating.up" ) :
            self.smarthome_heating_down_up( True )
        elif( self.action == "smarthome.heating.set" ) :
            self.smarthome_heating_set()
        elif( self.action == "smarthome.heating.schedule.down" ) :
            self.smarthome_heating_schedule_down_up( False )
        elif( self.action == "smarthome.heating.schedule.up" ) :
            self.smarthome_heating_schedule_down_up( True )
        elif( self.action == "smarthome.heating.schedule.set" ) :
            self.smarthome_heating_schedule_set()
        else :
            self.speech = "error smarthome heating action"
            print( self.speech )



    def printCheck( self ) :
        sOutput = ""
        # check the temperature
        if self.parameter["device"] == "" :
            # check all the room temperature
            if self.parameter["room"] == "" :
                # check all room specific temperature
                if self.parameter["value"] == "" :
                    sOutput = self.printCheckAll( False )
                # check all room status compare to value
                else :
                    tempValue = self.parameter["value"]
                    if self.doc["bedroom"]["temp"] > tempValue and self.doc["diningroom"]["temp"] > tempValue and self.doc["livingroom"]["temp"] > tempValue :
                       sOutput = "All of the room temperature is higher than " + tempValue + " degree"
                    elif self.doc["bedroom"]["temp"] < tempValue and self.doc["diningroom"]["temp"] < tempValue and self.doc["livingroom"]["temp"] < tempValue :
                        sOutput = "All of the room temperature is under " + tempValue + " degree"
                    elif self.doc["bedroom"]["temp"] == tempValue and self.doc["diningroom"]["temp"] == tempValue and self.doc["livingroom"]["temp"] == tempValue :
                        sOutput = "All of the room temperature is equal to " + tempValue + " degree"
                    else :
                        sOutput = self.printCheckAll( False )
            # check specific room temperature
            else :
                # Check the room specific temperature
                if self.parameter["value"] == "" :
                    sOutput = "The " + self.parameter["room"] + " temperature is " + self.doc[self.parameter["room"]]["temp"] + " degree"
                # Check the room is status compare to value
                else :
                    if self.parameter["value"] > self.doc[self.parameter["room"]]["temp"] :
                        sOutput = "The " + self.parameter["room"] + " temperature is " + "under " + self.parameter["value"] + " degree"
                    elif self.parameter["value"] < self.doc[self.parameter["room"]]["temp"] :
                        sOutput = "The " + self.parameter["room"] + " temperature is " + "higher than " + self.parameter["value"] + " degree"
                    else :
                        sOutput = "The " + self.parameter["room"] + " temperature is " + "equal to " + self.parameter["value"] + " degree"
        # check device status
        else : 
            # check all the room temperature
            if self.parameter["room"] == "" :
                # check all room specific temperature
                if self.parameter["value"] == "" :
                    sOutput = self.printCheckAll( True )
                # check all room status compare to value
                else :
                    tempValue = self.parameter["value"]
                    if self.doc["bedroom"]["device"]["value"] > tempValue and self.doc["bedroom"]["device"]["value"] > tempValue and self.doc["bedroom"]["device"]["value"] > tempValue :
                        sOutput = "All of the " + self.parameter["device"] + " in the room is setted higher than " + tempValue + " degree"
                    elif self.doc["bedroom"]["device"]["value"] < tempValue and self.doc["bedroom"]["device"]["value"] < tempValue and self.doc["bedroom"]["device"]["value"] < tempValue :
                        sOutput = "All of the " + self.parameter["device"] + " in the room is setted  under " + tempValue + " degree"
                    elif self.doc["bedroom"]["device"]["value"] == tempValue and self.doc["bedroom"]["device"]["value"] == tempValue and self.doc["bedroom"]["device"]["value"] == tempValue :
                        sOutput = "All of the " + self.parameter["device"] + " in the room is setted  equal to " + tempValue + " degree"
                    else :
                        sOutput = self.printCheckAll( True )
            # check specific room temperature
            else :
                # Check the room specific temperature
                if self.parameter["value"] == "" :
                    if self.doc[self.parameter["room"]]["device"]["status"] == False :
                        sOutput = "The " + self.parameter["device"] + " in the " + self.parameter["room"] + " is turned off"
                    else :
                        sOutput = "The " + self.parameter["device"] + " in the " + self.parameter["room"] + " is setted as " + self.doc[self.parameter["room"]]["device"]["value"] + " degree"
                # Check the room is status compare to value
                else :
                    if self.parameter["value"] > self.doc[self.parameter["room"]]["device"]["value"] :
                        sOutput = "The " + self.parameter["device"] + " in the " + self.parameter["room"]  + "is under " + self.parameter["value"] + " degree"
                    elif self.parameter["value"] < self.doc[self.parameter["room"]]["device"]["value"] :
                        sOutput = "The " + self.parameter["device"] + " in the " + self.parameter["room"]  + "is higher than " + self.parameter["value"] + " degree"
                    else :
                        sOutput = "The " + self.parameter["device"] + " in the " + self.parameter["room"]  + "is equal to " + self.parameter["value"] + " degree"
        return sOutput  

    def printCheckAll( self, isDevice ) :
        sOutput = ""
        if isDevice == True :
            sOutput = sOutput + " the " + self.parameter["device"] + "'s temperature in the bedroom set as " + self.doc["bedroom"]["device"]["value"] + " degree, the dining room is " + self.doc["diningroom"]["device"]["value"] + " degree, and the living room is " + self.doc["livingroom"]["device"]["value"]
        else :
            sOutput = sOutput + "The bedroom temperature is " + self.doc["bedroom"]["temp"] + " degree, the  dining room temperature is " + self.doc["diningroom"]["temp"] + " degree, and the living room is " + self.doc["livingroom"]["temp"] + " degree"

        return sOutput

    def smarthome_heating_check(self) :  
        self.speech = self.printCheck()
        print( self.speech )       
        return print("[ Do Mission light_check ]")

    def smarthome_heating_switch_on_off(self, isOn) :
        try :
            if  self.parameter["room"] == "bedroom" or self.parameter["room"] == "diningroom" or self.parameter["room"] == "livingroom" :
                self.doc_ref.update( {self.parameter["room"] + 'device.status' : isOn } )     
            else :
                self.doc_ref.update({
                    u'bedroom.device.status'    : isOn,
                    u'diningroom.device.status' : isOn,
                    u'livingroom.device.status' : isOn
                })
        except :
            self.smarthome_heating_switch_on_off( isOn )
            
        sInstruction = str()
        if isOn == True :
            sInstruction = "on" 
        else : 
            sInstruction = "off"
        self.speech = "Do the switch " + sInstruction + " heating instruction"
        print( self.speech ) 
        return print("[ Do heating_switch_on_off ]")


    def smarthome_heating_switch_schedule_on_off(self, isOn ) :
        try :
            if  self.parameter["room"] == "bedroom" or self.parameter["room"] == "diningroom" or self.parameter["room"] == "livingroom" :
                self.doc_ref.update( {self.parameter["room"] + 'device.status' : isOn } )     
            else :
                self.doc_ref.update({
                    u'bedroom.device.status'    : isOn,
                    u'diningroom.device.status' : isOn,
                    u'livingroom.device.status' : isOn
                })
        except :
            self.smarthome_heating_switch_schedule_on_off( isOn )
            
        sInstruction = str()
        if isOn == True :
            sInstruction = "on" 
        else : 
            sInstruction = "off"
        self.speech = "Do the switch " + sInstruction + " heating with time instruction"
        print( self.speech ) 
        return print("[ Do heating_switch_schedule_on_off ]")

    def setHeatingUp_Down( self, isUp, isAllRoom ) :
        tempChangeValue = int()
        try :
            if isAllRoom != "" :
                #Set Final value
                if self.parameter["final-value"] != "" :
                    self.doc_ref.update( { self.parameter["room"] + '.device.value' : self.parameter["final-value"] } )
                #Set change value
                else :
                    # Calculate giving change value
                    if self.parameter["change-value"] != "" :
                        if isUp is True :
                            tempChangeValue = 0 - self.parameter["change-value"]
                        finalValue = self.doc[self.parameter["room"]]["device"]["value"] - tempChangeValue
                        self.doc_ref.update( { self.parameter["room"] + '.device.value' : finalValue } )
                    # Calculate reasoning domain
                    else :                   
                        if isUp is True :
                            tempChangeValue = -1.5
                        else :
                            tempChangeValue = 1.5 
                        finalValue = self.doc[self.parameter["room"]]["device"]["value"] - tempChangeValue
                        self.doc_ref.update( { self.parameter["room"] + '.device.value' : finalValue } )
            # All the room
            else :
                #Set Final Value
                if self.parameter["final-value"] != "" :
                    self.doc_ref.update( { 
                        u'bedroom.device.value'    : self.parameter["final-value"],
                        u'diningroom.device.value' : self.parameter["final-value"],
                        u'livingroom.device.value' : self.parameter["final-value"]
                    } )
                #Set Change Value
                else :
                    # Calculate giving change value 
                    if self.parameter["change-value"] != "" :
                        if isUp is True :
                            tempChangeValue = 0 - self.parameter["change-value"]
                        self.doc_ref.update( { 
                            u'bedroom.device.value'    : self.doc["bedroom"]["device"]["value"]    - tempChangeValue,
                            u'diningroom.device.value' : self.doc["diningroom"]["device"]["value"] - tempChangeValue,
                            u'livingroom.device.value' : self.doc["livingroom"]["device"]["value"] - tempChangeValue
                        } )
                    # Calculate reasoning domain
                    else :
                        if isUp is True :
                            tempChangeValue = -1.5
                        else :
                            tempChangeValue = 1.5
                        self.doc_ref.update( { 
                            u'bedroom.device.value'    : self.doc["bedroom"]["device"]["value"]    - tempChangeValue,
                            u'diningroom.device.value' : self.doc["diningroom"]["device"]["value"] - tempChangeValue,
                            u'livingroom.device.value' : self.doc["livingroom"]["device"]["value"] - tempChangeValue
                        } )
        except :
            self.setHeatingUp_Down( isUp, isAllRoom )       
        return "0"
  
    
    def smarthome_heating_down_up( self, isOn ) :
        self.setHeatingUp_Down( isOn, self.parameter["room"] )
        
        sInstruction = str()
        if isOn == True :
            sInstruction = "up" 
        else : 
            sInstruction = "down"
        self.speech = "Do the heating " + sInstruction + " instruction"
        return print("heating_down_up")

    def smarthome_heating_set( self ) :
        try :
            if self.parameter["room"] != "" :
                if self.parameter["final-value"] != "" :
                    self.doc_ref.update( { self.parameter["room"] + '.device.value' : self.parameter["final-value"] } )
                else :
                    self.doc_ref.update( { self.parameter["room"] + '.device.value' : self.doc[self.parameter["room"]]["device"]["value"] - 1.5 } )
            else :
                if self.parameter["final-value"] != "" :
                    self.doc_ref.update( { 
                        u'bedroom.device.value'    : self.parameter["final-value"],
                        u'diningroom.device.value' : self.parameter["final-value"],
                        u'livingroom.device.value' : self.parameter["final-value"]
                    } )
                else :
                    self.doc_ref.update( { 
                        u'bedroom.device.value'    : self.doc["bedroom"]["device"]["value"]    - 1.5,
                        u'diningroom.device.value' : self.doc["diningroom"]["device"]["value"] - 1.5,
                        u'livingroom.device.value' : self.doc["livingroom"]["device"]["value"] - 1.5
                    })
        except :
            self.smarthome_heating_set() 
        
        self.speech = "Do the Setting heating instruction"
        return print( "heating_set" )

    def smarthome_heating_schedule_down_up( self, isOn ) :
        self.setHeatingUp_Down( isOn, self.parameter["room"] )
        
        sInstruction = str()
        if isOn == True :
            sInstruction = "up" 
        else : 
            sInstruction = "down"
        self.speech = "Do the heating " + sInstruction + " instruction with time "
        return print("heating_down_up_Schedule")

    def smarthome_heating_schedule_set( self ) :
        self.smarthome_heating_set()        
        self.speech = "Do the Setting heating instruction with time"
        return print( "heat_schedule_set" )      

    def getSpeech( self ):
        return self.speech

    

