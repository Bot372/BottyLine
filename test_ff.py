import os
import subprocess
from flask import Flask, redirect, render_template, request, session, url_for
from flask_dropzone import Dropzone
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class,AUDIO
import S_R_Upload


app = Flask(__name__)
dropzone = Dropzone(app)
# Dropzone settings
app.config['DROPZONE_UPLOAD_MULTIPLE'] = True
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = '.m4a'
#app.config['DROPZONE_REDIRECT_VIEW'] = 'results'

app.config['SECRET_KEY'] = 'supersecretkeygoeshere'
audio_result = ""

# Uploads settings
app.config['UPLOADED_PHOTOS_DEST'] = os.path.dirname(os.path.realpath(__file__)) + '/music'

photos = UploadSet('photos', AUDIO)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB



def converFile():
    testdir = os.path.dirname(os.path.realpath(__file__)) + '/music'
    testfile = os.path.join(testdir,"fuckyou.wav")
    outputpath = os.path.dirname(os.path.realpath(__file__)) + '/music'
    outputFile = os.path.join(outputpath,"fuckyouM4a.wav")
    print( outputFile, "\n", testfile )
    cmd = [ "ffmpeg", "-i", testfile, outputFile ]
    #subprocess.call(cmd, shell = True)
    subprocess.run( cmd )


    #process = Popen(command, shell=True)
    #subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=process.pid))
    print("Convert m4a to wav Success")

@app.route('/', methods=['GET', 'POST'])
def index():
    
    # set session for image results
    if "file_urls" not in session:
        session['file_urls'] = []
    # list to hold our uploaded image urls
    file_urls = session['file_urls']
    # handle image upload from Dropzone
    if request.method == 'POST':
        file_obj = request.files
        for f in file_obj:
            file = request.files.get(f)
            
            # save the file with to our photos folder
            
            filename = photos.save(
                file,
                name= "fuckyou.wav"    
            )
 
            # append image urls
            file_urls.append(photos.url(filename))
            
        session['file_urls'] = file_urls
        converFile()
        audio_result = S_R_Upload.Speech_Recognition()
        app.logger.info( "Audio Result: " + audio_result )
        print(audio_result)
        S_R_Upload.CleanData()
        return "uploading..."
    # return dropzone template on GET request    
    return render_template('index.html')


if __name__ == '__main__':
	app.run()








