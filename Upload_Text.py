from flask import Flask, render_template, request
from flask_uploads import UploadSet, configure_uploads, IMAGES, AUDIO, TEXT
import os
import shutil

#os.chdir('C:\\Users\\Mchig\\Desktop\\DeepSpeach')
#print (os.getcwd(), "FUCK YOU ALL")

app = Flask(__name__)

photos = UploadSet('photos', TEXT )

app.config['UPLOADED_PHOTOS_DEST'] =  os.path.dirname(os.path.realpath(__file__)) + '/test_Result'
configure_uploads(app, photos)

def openlight():
    return "Open the Light Success"

def closelight():
    return "Close the Light Success"

def Lock():
    return "Lock the Key Success"

def UnLock():
    return "Unlock the Key Success"

def OpenFile(   ):
    FileDir = os.path.dirname(os.path.realpath(__file__)) + '/test_Result'
    FileName =  os.path.join( FileDir, "test.txt")
    file = open( FileName, 'r' )
    order = file.readlines()
    print( order )
    file.close()
    return order

def CleanFile():
    File_dirpath = os.path.dirname(os.path.realpath(__file__)) + '/test_Result'
    shutil.rmtree( File_dirpath )
    os.makedirs(File_dirpath)


@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        filename = photos.save(request.files['photo'], name= "test.txt")
        #print( type(fliename) )
        order = OpenFile()
        CleanFile()
        #app.logger.info( "Request body: " + order[0] )
        return order[0]
    return render_template('upload.html')


if __name__ == '__main__':
	app.run(debug=True)