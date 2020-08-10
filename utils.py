from flask import Flask

UPLOAD_FOLDER = 'E:/Project Akhir/api-absen-sd-v2/data_wajah/'
UPLOAD_FOLDER2 = 'E:/Project Akhir/api-absen-sd-v2/data_lokasi/'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER2'] = UPLOAD_FOLDER2
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024