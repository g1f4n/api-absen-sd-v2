from utils import app
from upload import Upload
from flask import Flask, redirect, jsonify, session
from flask import flash, request, Response
from flask import send_from_directory
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import requests
import numpy as np
from time import strftime
import datetime
from datetime import datetime
import cv2
import json
import jsonpickle
import mysql.connector

# init flask
# app = Flask(__name__)

# connect db
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="sadewa_absensi"
)

# extension yang di izinkan
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# dapatkan nama file dan extensinya


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# get siswa by id


@app.route('/siswaById')
def dataSiswaById():
    id = request.args.get('nis')
    mycursor = mydb.cursor()
    sql = "SELECT nama_siswa, nis, kelas FROM tbl_siswa WHERE tbl_siswa.nis = %s"
    # sql = "SELECT * FROM tbl_siswa WHERE nis = %s"
    val = (id,)
    mycursor.execute(sql, val)
    row_headers = [x[0] for x in mycursor.description]
    myresult = mycursor.fetchall()
    json_data = []
    for result in myresult:
        json_data.append(dict(zip(row_headers, result)))
    resp = jsonify({
        'status': True,
        'data_siswa': json_data
    })
    resp.status_code = 200
    return resp

# get absen by id


@app.route('/absenById')
def dataAbsenById():
    id = request.args.get('nis')
    mycursor = mydb.cursor()
    sql = "SELECT tbl_absen.data_lokasi, tbl_absen.jam_masuk, tbl_siswa.nama_siswa, tbl_siswa.nis, tbl_kelas.nama_ruang FROM tbl_siswa JOIN tbl_kelas JOIN tbl_absen ON tbl_siswa.nis = tbl_absen.nis AND tbl_siswa.kelas = tbl_kelas.id_kelas WHERE tbl_siswa.nis = %s ORDER BY jam_masuk DESC"
    # sql = "SELECT * FROM tbl_siswa WHERE nis = %s"
    val = (id,)
    mycursor.execute(sql, val)
    row_headers = [x[0] for x in mycursor.description]
    myresult = mycursor.fetchall()
    json_data = []
    for result in myresult:
        json_data.append(dict(zip(row_headers, result)))
    resp = jsonify({
        'status': True,
        'data_absen': json_data
    })
    resp.status_code = 200
    return resp

# get absen by id Limit


@app.route('/absenByIdLimit')
def dataAbsenByIdLimit():
    id = request.args.get('nis')
    mycursor = mydb.cursor()
    sql = "SELECT jam_masuk FROM tbl_absen WHERE nis = %s ORDER BY jam_masuk DESC LIMIT 1"
    # sql = "SELECT * FROM tbl_siswa WHERE nis = %s"
    val = (id,)
    mycursor.execute(sql, val)
    row_headers = [x[0] for x in mycursor.description]
    myresult = mycursor.fetchall()
    json_data = []
    for result in myresult:
        json_data.append(dict(zip(row_headers, result)))
    resp = jsonify({
        'status': True,
        'data_absen': json_data
    })
    resp.status_code = 200
    return resp

# add siswa


@app.route('/add-siswa', methods=['POST'])
def upload():
    nis = request.form['nis']
    name = request.form['name']
    kelas = request.form['kelas']

    if 'data_wajah' not in request.files:
        response = jsonify({'message': 'tidak ada gambar'})
        response.status_code = 400
        return response

    file = request.files['data_wajah']
    if file == '':
        response = jsonify({'message': 'gambar belum di upload'})
        response.status_code = 400
        return response
    if allowed_file(file.filename) == True:
        Upload(nis, name, kelas, file)
        data = {
            'status': True,
            'message': 'Data Berhasil Di Simpan',
            'data': {
                'name': name,
                'nis': nis
            }
        }
    return data

# add data kelas


@app.route('/add_kelas', methods=['POST'])
def addKelas():
    # try:
    _ruang_kelas = request.form['ruang_kelas']
    _jml_siswa = request.form['jml_siswa']

    if _ruang_kelas and _jml_siswa and request.method == 'POST':

        # insert data
        mycursor = mydb.cursor()
        sql = """INSERT INTO tbl_kelas (nama_ruang, jumlah_siswa) VALUES (%s, %s)"""
        val = (_ruang_kelas, _jml_siswa)
        mycursor.execute(sql, val)
        mydb.commit()
        resp = jsonify("Data Berhasil Di Simpan")
        resp.status_code = 200
        return resp
    # except Exception as e:
    #     print(e)
    # finally:
    mycursor.close()

# add data ortu


@app.route('/add_ortu', methods=['POST'])
def addOrtu():
    # try:
    _username = request.form['username']
    _password = request.form['password']
    _nis = request.form['nis']
    _nama_ortu = request.form['nama_ortu']

    if _username and _password and _nis and _nama_ortu and request.method == 'POST':
        _hashed_password = generate_password_hash(_password)
        # insert data
        mycursor = mydb.cursor()
        sql = "INSERT INTO tbl_ortu (nama_ortu, nis, username, password) VALUES (%s, %s, %s, %s)"
        val = (_nama_ortu, _nis, _username, _hashed_password)
        mycursor.execute(sql, val)
        mydb.commit()
        resp = jsonify("Data Berhasil Di Simpan")
        resp.status_code = 200
        return resp

# Absen


@app.route('/absen/<string:username>', methods=['POST'])
def absen(username):
    r = request

    # convert string of image data to uint8
    nparr = np.fromstring(r.data, np.uint8)

    # decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # # do some fancy processing here....
    # timeImg = strftime("%Y%m%d%H%M%S")
    time = strftime("%Y-%m-%d %H:%M:%S")
    # print(username)
    splitUsername = username.split("_")
    imgName = splitUsername[2]
    # nama = splitUsername[1]
    nis = splitUsername[0]

    # # check if was 5 minutes
    # dataAbsen = requests.get(
    #     "http://192.168.43.38:4000/absenByIdLimit?nis=" + nis)
    # resultAbsen = json.loads(dataAbsen.text)

    # formatTime1 = resultAbsen['data_absen'][0]['jam_masuk']
    # pastTime = datetime.datetime.strptime(
    #     formatTime1, '%a, %b %d %Y %H:%M:%S').strftime("%Y-%m-%d %H:%M:%S")
    # print(pastTime)

    # p = os.path.sep.join([app.config['UPLOAD_FOLDER'] + imgName])
    loc = os.path.sep.join([app.config['UPLOAD_FOLDER2'] + imgName])
    # cv2.imwrite(p, img)
    cv2.imwrite(loc, img)

    mycursor = mydb.cursor()
    if strftime("%H:%M:%S") >= "12:00:00":
        sql = "INSERT INTO tbl_absen(jam_masuk, nis, data_lokasi) VALUES (%s, %s, %s)"
        val = (time, nis, imgName)
    else:
        sql = "INSERT INTO tbl_absen(jam_masuk, nis, data_lokasi) VALUES (%s, %s, %s)"
        val = (time, nis, imgName)
    mycursor.execute(sql, val)
    mydb.commit()

    # build a response dict to send back to client
    response = {'message': 'Absent Done!!'.format(img.shape[1], img.shape[0])
                }
    # encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)

    return Response(response=response_pickled, status=200, mimetype="application/json")

# image from url


@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    path = os.path.join(current_app.root_path, 'data_lokasi/')
    return send_from_directory(directory=path, filename=filename)

# login ortu


@app.route('/login_ortu', methods=['POST'])
def login_ortu():
    mycursor = None
    try:
        _username = request.form['username']
        _password1 = request.form['password']

        # validasi username dari tbl username
        if _username != '' and _password1 != '':
            mycursor = mydb.cursor()
            sql = "SELECT * FROM tbl_ortu WHERE username = %s"
            sql_where = (_username,)
            mycursor.execute(sql, sql_where)
            row = mycursor.fetchone()
            # hashpass = generate_password_hash(_password1)
            # print(check_password_hash(row[1], _password1))
            # print(row[1] + " " + _password1)

            if row:
                if check_password_hash(row[4], _password1):
                    session['username_ortu'] = row[3]
                    session['nis_siswa'] = row[2]
                    session['nama_ortu'] = row[1]
                    mycursor.close()
                    return jsonify({
                        "message": "login berhasil",
                        'nis_siswa': session['nis_siswa'],
                        'nama_ortu': session['nama_ortu']
                    })
                else:
                    # print(_username + " " + _password)
                    resp = jsonify({"message": "login gagal"})
                    resp.status_code = 400
                    return resp
            else:
                resp = jsonify({"message": "username tidak di temukan"})
                resp.status_code = 400
                return resp
        else:
            resp = jsonify(
                {"message": "username / password tidak boleh kosong"})
            resp.status_code = 400
            return resp
    except Exception as e:
        print(e)
    finally:
        if mycursor:
            mycursor.close()


# run app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)
