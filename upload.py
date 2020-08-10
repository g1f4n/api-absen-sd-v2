import pickle
import face_recognition as fr
import mysql.connector
import os

# connection to database
connection = mysql.connector.connect(host='localhost',user='root',passwd='',database='sadewa_absensi')
# create cursor
cursor = connection.cursor()
# base directory
base_dir = 'data_wajah/'

def Upload(nis, name, kelas, dataWajah):
    # cek directori pada dataset
    if os.path.isdir(base_dir + nis + name):
        # save image to dataset
        with open(base_dir + nis + name + '/' + name + '.jpg', 'wb') as f:
            for i in dataWajah:
                f.write(i)
        
        # encoding image
        known_image = fr.load_image_file(base_dir + nis + name + '/' + name + '.jpg')
        known_encoding = fr.face_encodings(known_image)[0]

        # pickle the list into string
        face_pickled_data = pickle.dumps(known_encoding)
        
        # insert to database
        sql = "INSERT INTO tbl_siswa (nis, nama_siswa, kelas, data_wajah) VALUES (%s, %s, %s, %s)"
        val = (nis, name, kelas, face_pickled_data)
        cursor.execute(sql, val)
        connection.commit()
    else :
        os.mkdir(base_dir + nis + name)
        with open(base_dir + nis + name + '/' + name + '.jpg', 'wb') as f:
            for i in dataWajah:
                f.write(i)
        
        # encoding image
        known_image = fr.load_image_file(base_dir + nis + name + '/' + name + '.jpg')
        known_encoding = fr.face_encodings(known_image)[0]

        # pickle the list into string
        face_pickled_data = pickle.dumps(known_encoding)
        
        # insert to database
        sql = "INSERT INTO tbl_siswa (nis, nama_siswa, kelas, data_wajah) VALUES (%s, %s, %s, %s)"
        val = (nis, name, kelas, face_pickled_data)
        cursor.execute(sql, val)
        connection.commit()