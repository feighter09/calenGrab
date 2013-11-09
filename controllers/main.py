import os, time
from flask import Flask, request, redirect, url_for, Blueprint, render_template, send_file
from werkzeug import secure_filename

UPLOAD_FOLDER = 'static/tmp/pictures/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__, static_folder='static', template_folder='views')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

main = Blueprint('main', __name__, template_folder='views')

@main.route('/', methods=['GET', 'POST'])
def main_route():
  if request.method == 'GET':
    pass
  elif request.method == 'POST':
    pass

  return render_template("imageUpload.html")

@main.route('/upload', methods=['POST'])
def image_upload():
  file = request.files['pic']
  filename = secure_filename(file.filename)
  fileExtension = getFileExtension(file)
  picId = str(int( (time.time() * 1000) % 1000000000 ))

  fileLoc = UPLOAD_FOLDER + picId + '.'+ fileExtension
  file.save(fileLoc)

  return render_template("imageProcessor.html", fileLoc=fileLoc)

@main.route('/selection', methods=['POST'])
def handle_selection():
  print request.__dict__
  ## todo: 
  # open the file from url
  # crop
  # send to OCR
  # return response string(s) w/ JSON?
  return "success"

@main.route('/tmp/pictures/<photoFile>', methods=['GET'])
def picture_route(photoFile):
  return send_file(request.path[1:])

def getFileExtension(file):
  filename = secure_filename(file.filename)
  return filename.rsplit('.', 1)[1];