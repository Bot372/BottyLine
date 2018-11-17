import json
import requests
import firebase_admin
from firebase_admin import firestore
import google.cloud.exceptions # thrown exception


class Device:
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
        self.doc_ref = db.collection(u'device').document( self.userId )
        self.doc = self.doc_ref.get().to_dict()
        print( "Enter Device" )


    def runSmarthome_Device(self) :
        print( self.action )
        if (  self.action == "smarthome.device.switch.check.off" ) :
            self.smarthome_device_switch_check_off_on( False )
        elif( self.action == "smarthome.device.switch.check.on" ) :
            self.smarthome_device_switch_check_off_on( True )
        elif( self.action == "smarthome.device.switch.off" ) :
            self.smarthome_device_switch_off_on( False )
        elif( self.action == "smarthome.device.switch.on" ) :
            self.smarthome_device_switch_off_on( True )
        elif( self.action == "smarthome.device.switch.schedule.off" ) :
            self.smarthome_device_switch_schedule_off_on( False )
        elif( self.action == "smarthome.device.switch.schedule.on" ) :
            self.smarthome_device_switch_schedule_off_on( True )
        else :
            self.speech = "error smarthome action"
            print( self.speech )



    def printCheck( self ) :
        sOutput = ""
        tempRoom = self.parameter["room"]
        tempDevice = self.parameter["device"]
        # check specific device
        if tempDevice == "fan" or tempDevice == "speaker" or tempDevice == "tv" :
            sOutput = "The " + tempDevice + " in the " + tempRoom + " is turned "
            if self.doc[tempRoom][tempDevice]["status"] == False :
                sOutput = sOutput + "off"
            else :
                sOutput = sOutput + "on"
        # check all device
        else :
            if self.doc[tempRoom]["fan"]["status"] == True and self.doc[tempRoom]["speaker"]["status"] == True and self.doc[tempRoom]["tv"]["status"] == True :
                sOutput = "All of devices in the " + tempRoom + " is turn on " 
            elif self.doc[tempRoom]["fan"]["status"] == False and self.doc[tempRoom]["speaker"]["status"] == False and self.doc[tempRoom]["tv"]["status"] == False :
                sOutput = "All of devices in the " + tempRoom + " is turn off "
            else :

                sOutput = "The fan " + "is " 
                if ( self.doc[tempRoom]["fan"]["status"] == True ) :
                    sOutput = sOutput + "on, "
                else :
                    sOutput = sOutput + "off, "

                sOutput = sOutput + "the speaker " + "is " 
                if ( self.doc[tempRoom]["fan"]["status"] == True ) :
                    sOutput = sOutput + "on, "
                else :
                    sOutput = sOutput + "off, "

                sOutput = sOutput + "the tv " + "is " 
                if ( self.doc[tempRoom]["fan"]["status"] == True ) :
                    sOutput = sOutput + "on"
                else :
                    sOutput = sOutput + "off" 

        return sOutput  

    def printRoomDevice( self, room ) :
        sOutput = "The fan in the " +  room + " is " 
        if self.doc[room]["fan"]["status"] == True :
            sOutput = sOutput + " on,"
        else :
            sOutput = sOutput + " off,"

        sOutput = sOutput + "the speaker is"
        if self.doc[room]["speaker"]["status"] == True :
            sOutput = sOutput + " on,"
        else :
            sOutput = sOutput + " off,"

        sOutput = sOutput + "the tv is"
        if self.doc[room]["tv"]["status"] == True :
            sOutput = sOutput + " on. "
        else :
            sOutput = sOutput + " off. "

        return sOutput


    def printCheckAll( self ) :
        sOutput = ""
        tempDevice = self.parameter["device"]
        if tempDevice == "fan" or tempDevice == "speaker" or tempDevice == "tv" :
            if self.doc["bedroom"][tempDevice]["status"] == True and self.doc["diningroom"][tempDevice]["status"] == True and self.doc["livingroom"][tempDevice]["status"] == True :
                sOutput = "All of devices in the room turn on " 
            elif self.doc["bedroom"][tempDevice]["status"] == False and self.doc["diningroom"][tempDevice]["status"] == False and self.doc["livingroom"][tempDevice]["status"] == False :
                sOutput = "All of devices in the room turn off " 
            else :
                sOutput = "The " + tempDevice + " in the bedroom " + "is " 
                if ( self.doc["bedroom"][tempDevice]["status"] == True ) :
                    sOutput = sOutput + "on, "
                else :
                    sOutput = sOutput + "off, "

                sOutput = "The " + tempDevice + " in the diningroom " + "is " 
                if ( self.doc["diningroom"][tempDevice]["status"] == True ) :
                    sOutput = sOutput + "on, "
                else :
                    sOutput = sOutput + "off, "

                sOutput = "The " + tempDevice + " in the living " + "is " 
                if ( self.doc["livingroom"][tempDevice]["status"] == True ) :
                    sOutput = sOutput + "on"
                else :
                    sOutput = sOutput + "off" 
        else :
            sOutput = sOutput + self.printRoomDevice( "bedroom" ) + "\n" + self.printRoomDevice("diningroom") + "\n" + self.printRoomDevice("livingroom")


        return sOutput


    def smarthome_device_switch_check_off_on( self, isOn ) :
        if  self.parameter["room"] == "bedroom" or self.parameter["room"] == "diningroom" or self.parameter["room"] == "livingroom"  :
            self.speech = self.printCheck()
        else :
            self.speech = self.printCheckAll()

        return print("[ Do Mission Device_check_off_on ]")


    def setDeviceOn_Off( self, isOn, allRoom) :
        sOutput = ""
        # Check Spicific room
        if allRoom != "" :
            if self.parameter["device"] != "" :
                self.doc_ref.update({ 
                    self.parameter["room"] :{
                            self.parameter["device"] : {
                                'status' : isOn
                            } 
                        } 
                })
            else :
                sOutput = "No device provided"
        # Check all the room
        else :
            if self.parameter["device"] != "" :
                self.doc_ref.update( { 
                    'bedroom' + '.' + self.parameter["device"]  + ".status" : isOn,
                    'diningroom' + '.' + self.parameter["device"]  + ".status" : isOn,
                    'livingroom' + '.' + self.parameter["device"]  + ".status" : isOn,
                 } )
            else :
                sOutput = "No device provided"

        return sOutput

    def smarthome_device_switch_off_on( self, isOn ) :
        tempSpeech = self.setDeviceOn_Off( isOn, self.parameter["room"] )



        sInstruction = str()
        if isOn == True :
            sInstruction = "on" 
        else : 
            sInstruction = "off"

        if self.parameter["room"] != "" :
            self.speech = "Do the device turn " + sInstruction + " instruction"
        else :
            self.speech = tempSpeech
        return print("device_switch_off_on")
    
    def smarthome_device_switch_schedule_off_on( self, isOn ) :
        tempSpeech = self.setDeviceOn_Off( isOn, self.parameter["room"] )

        sInstruction = str()
        if isOn == True :
            sInstruction = "on" 
        else : 
            sInstruction = "off"
        if self.parameter["room"] != "" :
            self.speech = "Do the device turn " + sInstruction + " instruction with time"
        else : 
            self.speech = tempSpeech
        return print("device_switch_schedule_off_on")

    def getSpeech( self ):
        return self.speech

    

