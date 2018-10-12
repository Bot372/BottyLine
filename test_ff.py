import os
import subprocess



def converFile():
    testdir = os.path.dirname(os.path.realpath(__file__)) + "\\static\\music"
    testfile = os.path.join(testdir,"fuckyou.m4a")
    outputpath = os.path.dirname(os.path.realpath(__file__)) +"\\static\\music"
    outputFile = os.path.join(outputpath,"fuckyou.wav")
    print( outputFile, "\n", testfile )
    cmd = [ "ffmpeg", "-i", testfile, outputFile ]
    #subprocess.call(cmd, shell = True)
    subprocess.Popen( cmd, shell= True )
    print("Convert m4a to wav Success")









