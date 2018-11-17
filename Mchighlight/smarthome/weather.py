import json
import requests
import os

class Weather :
    speech = ""

    #Entities @activity @outfit @temperature @unit-temperature @weather-condition
    # @activity :           皆是戶外活動
    # @outfit   :           超多種
    # @temperature :        1.warm 2.hot 3.cold 4.chilly
    # @unit-temperature:    1.C    2.K   3.F    4.F 
    # @weather-condition:   twenty-one type
    # @address          :   sys-location
    # @date-time        :   sys.date-time
    

    def __init__( self, action,result ) :
        #Dialogflow Action
        self.action = action
        self.result = result 
        #Initialize address entity
        #print( json.dumps(self.result["parameters"], indent=4) )
        if bool( self.result ["parameters"]["address"] ) is True :
            self.address = result["parameters"]["address"]
        else :
            self.address = None
        #Initialize data_time entity
        if bool( self.result ["parameters"]["date-time"] ) is True :           
            self.date_time = result["parameters"]["date-time"]
        else :
            self.date_time = None

        #Intitialize other Entity
        self.activity    = None
        self.outfit      = None
        self.temperature = None
        self.unit        = None
        self.condition   = None
        #Get the Entity Dict()
        self.activityJson       =  self.getDict( "//activity.json" )
        self.outfitJson         =  self.getDict( "//outfit.json" ) 
        self.temperatureJson    =  self.getDict( "//temperature.json" ) 
        self.unitJson           =  self.getDict( "//unit.json" ) 
        self.weatherConditionJson =  self.getDict( "//weatherCondition.json" ) 



    def getDict( self, FileName ) :
        testdir =  os.path.dirname(os.path.realpath(__file__)) + FileName
        with open( testdir, 'r') as fp:
            lanCode = json.load(fp)
        return lanCode


    def runWeather( self ) :
        print( self.action )
        if (  self.action == "weather" ) :
            self.weather()
        elif( self.action == "weather.activity" ) :
            #Initialize activity entity
            if bool( self.result["parameters"]["activity"] ) is True :           
                self.activity    = self.result["parameters"]["activity"]
            else :
                self.activity    = None
            #Run the Function 
            self.weather_activity()
        elif( self.action == "weather.condition" ) :
            #Initialize condition entity
            print( "enter weather Condition" )
            if bool( self.result["parameters"]["condition"] ) is True :           
                self.condition    = self.result["parameters"]["condition"]
            else :
                self.condition    = None
            #Run the Function 
            self.weather_condition()
        elif( self.action == "weather.outfit" ) :
            #Initialize outfit entity
            if bool( self.result["parameters"]["outfit"] ) is True :           
                self.outfit   = self.result["parameters"]["outfit"]
            else :
                self.outfit   = None
            #Run the Function 
            self.weather_outfit()
        elif( self.action == "weather.temperature" ) :
            #Initialize temperature entity
            if bool( self.result["parameters"]["temperature"] ) is True :           
                self.temperature   = self.result["parameters"]["temperature"]
            else :
                self.temperature   = None
            #Run the Function 
            self.weather_temperature()

    def weather( self ) : # Must needed
        # $data-time $address $unit
        self.speech = "Do the weather"
        return print( "Do the weather" )

    def weather_activity( self ) : #要是好天氣才能有活動 # must needed
        # $activity $date-time $address
        return print( "Do the weather_activity" )
    
    def weather_condition( self ) :
        # $data-time $condition $address
        self.speech = "Do the weather_condition"
        return print( "Do the weather_condition" )

    def weather_outfit( self ) :
        # $outfit $address $date-time
        self.speech = "Do the weather_outfit"
        return print( "Do the weather_outfit" )

    def weather_temperature( self) :# 1.warm 2.hot 3.cold 4.chilly #must needed 
        # $address $temperature $data-time $unit
        self.speech = "Do the weather_temperature"
        return print( "Do the weather_temperature" )


    def getSpeech( self ):
        return self.speech