import os, time
from flask import *
from werkzeug import secure_filename
from PIL import Image
import subprocess
import enchant

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
  data = json.loads(request.data)
  filename = data['pic']
  img = Image.open(filename)

  area = img.crop((data['startX'], data['startY'], data['endX'], data['endY']))
  area.save('square.png', 'png')

  convert = subprocess.Popen("convert -colorspace Gray -sharpen 1 -brightness-contrast 3X30 square.png square.png", shell = True)
  convert.communicate()
  ocr = subprocess.Popen("tesseract square.png output -l eng -psm 6", shell = True)
  ocr.communicate()
  response = open('output.txt').read()
  subprocess.Popen("rm square.png output.txt", shell = True)

  # for spellchecking:
  #d = enchant.Dict("en_US")
  #d.check('str')
  #d.suggest('str')

  return response

@main.route('/tmp/pictures/<photoFile>', methods=['GET'])
def picture_route(photoFile):
  return send_file(request.path[1:])

def getFileExtension(file):
  filename = secure_filename(file.filename)
  return filename.rsplit('.', 1)[1];

