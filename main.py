from flask import *
import csv
import io
import os
from twilio.rest import Client
from datetime import date
import smtplib

app = Flask(__name__)


@app.route("/")
def index():
    try:
        os.remove("class_data.csv")
    except:
        pass
    return render_template("home.html")


@app.route("/attendance_management")
def attendance_management():
    data1 = []
    header = []
    data = []
    try:
        f = open("class_data.csv", "r+")
        for i in f.readlines():
            data1.append(i.split(","))

        class_info = data1[0]
        header = data1[2]
        data = data1[3:]
    except:
        pass
    return render_template("attendance.html", data=data, header=header[:4], leng=len(data))


@app.route("/getdata", methods=['POST'])
def getdata():

    if request.method == 'POST':
        class_name = request.form['class_name']
        class_data = request.files['class_data']
        email = request.form['email']
        password = request.form['password']
        file_data = class_data.read().decode("utf-8")
        lines = file_data
        f = open("class_data.csv", "w+")
        f.write("Classname,"+class_name+"\n")
        f.write(email+","+password+"\n")
        for i in lines.split("\n"):
            f.write(i)
        f.close()
        return redirect("/attendance_management")

    return "404"


@app.route("/getabstent", methods=['POST'])
def getabstent():
    if (request.method == 'POST'):
        data1 = []
        f = open("class_data.csv", "r+")
        class_info = []
        for i in f.readlines():
            data1.append(i.split(","))
        class_info = data1[0]
        user_info = data1[1]
        data = data1[3:]
        absent = []
        new_data = []
        att_list = []

        for i in range(3, len(data1)):
            s = data1[i][-1]
            data1[i][-1] = s[:-1]
            c = int(data1[i][2])
            c += 1
            data1[i][2] = str(c)

        for i in range(len(data)):
            check = request.form.get(data[i][0])
            new_data = []
            if (check != None):
                new_data.append(check)
                new_data.append(data[i][0])
                absent.append(new_data)
                att_list.append('0')
            else:
                att_list.append('1')

        head = data1[2]
        data_2 = data1[3:]
        for i in range(len(data_2)):
            data_2[i].append(att_list[i])
        data2 = data_2
        s = head[-1]
        head[-1] = s[:-1]
        head.append(str(date.today()))
        att_present = []

        for i in range(len(data2)):
            li = data2[i][4:]
            data2[i][3] = str(li.count('1'))

        f1 = open("final_attendance_" + str(date.today()) + ".csv", "w+")
        f1.write(head[0])
        for i in head[1:]:
            f1.write("," + str(i))
        f1.write("\n")
        for i in data2:
            f1.write(str(i[0]))
            for j in i[1:]:
                f1.write("," + str(j))
            f1.write("\n")
        f1.close()
        file_path = f1.name

        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(user_info[0], user_info[1])
            for i in absent:
                subject = f'{i[1]} is absent for todays class'
                content = f'{i[1]} is absent for todays {class_info[1]} class. {date.today()}'

                msg = f'Subject: {subject}\n\n{content}'
                smtp.sendmail(user_info[0], i[0], msg)
            smtp.close()

        return send_file(file_path, as_attachment=True)

    return "Completed"
