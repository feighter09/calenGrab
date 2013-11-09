import datetime, time
from flask import *
from werkzeug import secure_filename
from PIL import Image
import subprocess
import enchant
import re

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
  square = img.crop((data['startX'], data['startY'], data['endX'], data['endY']))
  square.save('square.png', 'png')
  
  convert("square.png", "square.png")
  cal_ocr = ocr(filename)
  square_ocr = ocr("square.png")
  subprocess.Popen("rm square.png", shell = True)

  print "cal: " + cal_ocr
  print "square: " + square_ocr
  print ""

  year = find_year(cal_ocr)
  print "year:"
  print year

  month = find_month(cal_ocr)
  print "month:"
  print month

  (day, square_ocr) = find_day(square_ocr)
  print "day:"
  print day

  (start_times, end_times, titles) = find_times(square_ocr, year, month, day)
  print "times:"
  to_jsonify = []
  for i in range(0,len(titles)):
    print start_times[i]
    print end_times[i]
    print titles[i]
    event = {"start": start_times[i], "end": end_times[i], "summary": titles[i]}
    to_jsonify.append(event)

  return jsonify(results = to_jsonify)

@main.route('/tmp/pictures/<photoFile>', methods=['GET'])
def picture_route(photoFile):
  return send_file(request.path[1:])

def getFileExtension(file):
  filename = secure_filename(file.filename)
  return filename.rsplit('.', 1)[1];


def convert(filename, outputname=""):
  if outputname is "": 
    outputname = filename
  convert = subprocess.Popen("convert -colorspace Gray -sharpen 1 -brightness-contrast 10X50 " + filename + " " + outputname, shell = True)
  convert.communicate()
  return

def ocr(filename):
  proc = subprocess.Popen("tesseract " + filename + " output -l eng -psm 6", shell = True)
  proc.communicate()
  lines = [line.strip() for line in open('output.txt')]
  subprocess.Popen("rm output.txt", shell = True)
  ocr = " " 
  for line in lines:
    ocr += line + ' ' 
  return ocr 

month_mappings = {'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3, 'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7, 'aug': 8, 'august': 8, 'sep': 9, 'september': 9, 'oct': 10, 'october': 10, 'nov': 11, 'november': 11, 'dec': 12, 'december': 12}

def find_year(ocr):
  result = re.search("(([J|j]anuary|[F|f]ebruary|[M|m]arch|[A|a]pril|[M|m]ay|[J|j]une|[J|j]uly|[A|a]ugust|[S|s]eptember|[O|o]ctober|[N|n]ovember|[D|d]ecember)|(([J|j]an|[F|f]eb|[M|m]ar|[A|a]pr|[M|m]ay|[J|j]un|[J|j]ul|[A|a]ug|[S|s]ept?|[O|o]ct|[N|n]ov|[D|d]ec)\.?))?([ ]?(,|-|--|of|)?[ ]?(?P<year>20[0-9][0-9]))", ocr)
  if result:
    return int(result.group('year'))
  else:
    return int(datetime.date.today().year)

def find_month(ocr):
  result = re.search("(Month:?)? (?P<month>([J|j]anuary|[F|f]ebruary|[M|m]arch|[A|a]pril|[M|m]ay|[J|j]une|[J|j]uly|[A|a]ugust|[S|s]eptember|[O|o]ctober|[N|n]ovember|[D|d]ecember)|(([J|j]an|[F|f]eb|[M|m]ar|[A|a]pr|[M|m]ay|[J|j]un|[J|j]ul|[A|a]ug|[S|s]ept?|[O|o]ct|[N|n]ov|[D|d]ec)\.?))([ ]?(,|-|--|of|)?[ ]?(20)?[0-9][0-9])?", ocr)
  if result:
    month = result.group('month').strip().lower()
    return int(month_mappings[month])
  else:
    return int(datetime.date.today().month)

def find_day(ocr):
  result = re.search("(?P<day>[0-3]?[0-9])", ocr)
  if result:
    ocr = ocr[result.end():]
    return (int(result.group('day')), ocr)
  else:
    return (1, ocr)

def find_times(ocr, year, month, day):
  start_times = []
  end_times = []
  titles = []
  while True:
    match = re.search("(from)?[ ](?P<hour_1>[0-2]?[0-9])([:=](?P<min_1>[0-5][0-9]))?(?P<am_pm_1>[a|A|p|P][m|M])?[ ]?(-|to|until|through)[ ]?(?P<hour_2>[0-2]?[0-9])([:=](?P<min_2>[0-5][0-9]))?(?P<am_pm_2>[a|A|p|P][m|M])?[ ]", ocr)
    if not match:
      break

    hour_one = int(match.group('hour_1'))
    raw_minute_one = match.group('min_1')
    raw_hour_two = match.group('hour_2')
    raw_minute_two = match.group('min_2')
    if not raw_minute_one: minute_one=0
    else: minute_one = int(raw_minute_one)
    if not raw_hour_two: hour_two=hour_one+1
    else: hour_two = int(raw_hour_two)
    if not raw_minute_two: minute_two=0
    else: minute_two = int(raw_minute_two)

    start_times.append(datetime.datetime(year, month, day, hour_one, minute_one))
    end_times.append(datetime.datetime(year, month, day, hour_two, minute_two))
    titles.append(ocr[:match.start()].strip())
    ocr = ocr[match.end():]

  # If no events found, must use start times
  if not titles:
    match = re.search("(at|@|starting at)?[ @](?P<hour_1>[0-2]?[0-9])(:(?P<min_1>[0-5][0-9]))?([a|A|p|P][m|M])?", ocr)
    if match:

      hour_one = int(match.group('hour_1'))
      raw_minute_one = match.group('min_1')
      if not raw_minute_one: minute_one=0
      else: minute_one = int(raw_minute_one)
      hour_two = hour_one + 1
      minute_two = minute_one

      start_times.append(datetime.datetime(year, month, day, hour_one, minute_one))
      end_times.append(datetime.datetime(year, month, day, hour_two, minute_two))
      match = re.search("-", ocr)
      titles.append(ocr[match.end():].strip())
      ocr = ocr[match.end():]

  return (start_times, end_times, titles)


