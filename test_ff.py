import os
import subprocess
import speech_recognition as sr


def converFile():
    testdir = os.path.dirname(os.path.realpath(__file__))
    testfile = os.path.join(testdir,"fuckyou.m4a")
    outputpath = os.path.dirname(os.path.realpath(__file__)) 
    outputFile = os.path.join(outputpath,"fuckyou.wav")
    print( outputFile, "\n", testfile )
    cmd = [ "ffmpeg", "-i", testfile, outputFile ]
    #subprocess.call(cmd, shell = True)
    subprocess.Popen( cmd, shell= True )
    print("Convert m4a to wav Success")

audio_result = ""



def Speech_Recognition():   
    audio_dirpath = os.path.dirname(os.path.realpath(__file__))
    AUDIO_FILE_EN = os.path.join(audio_dirpath, "fuckyou.wav")
    r = sr.Recognizer()
    # use the audio file as the audio source
    with sr.AudioFile(AUDIO_FILE_EN) as source:
        audio_en = r.record(source)  # read the entire audio file
    
    # grammar example using Sphinx
    try:
        print("My own voice file")
        audio_result = str( r.recognize_google(audio_en) )
        return audio_result
    except sr.UnknownValueError:
        audio_result = "Sphinx could not understand audio"
        print( audio_result )
    except sr.RequestError as e:
        audio_result = str( "Sphinx error; {0}".format(e) )
        print( audio_result )

converFile()
Speech_Recognition()











