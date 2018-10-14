import speech_recognition as sr
import os
import shutil



##Variables declare
audio_result = ""



def Speech_Recognition():   
    audio_dirpath = os.path.dirname(os.path.realpath(__file__)) + "\\music"
    AUDIO_FILE_EN = os.path.join(audio_dirpath, "fuckyouM4a.wav")
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
        return audio_result 
    except sr.RequestError as e:
        audio_result = str( "Sphinx error; {0}".format(e) )
        return audio_result 

#Speech_Recognition()

def WriteResult( audio_result_1 ):
    txt_dirpath = os.path.dirname(os.path.realpath(__file__)) + "\\static\\result"
    name_of_file = "AudioResult"
    completeName = os.path.join( txt_dirpath, name_of_file + ".txt")         
    file1 = open(completeName, "w")
    file1.write( audio_result_1 )
    file1.close()
    print( "output the result -->", audio_result  )


def CleanData():
    audio_dirpath = os.path.dirname(os.path.realpath(__file__)) + "\\music"
    shutil.rmtree( audio_dirpath )
    os.makedirs(audio_dirpath)



#if __name__ == '__main__':
#    uploadMusic.app.run()
#    audio_result = Speech_Recognition()
#    WriteResult()
#    CleanData()
    