import random

from Employee import AttendanceDetails, Employee
from EmployeeProfileDAL import EmployeeProfileDAL
from flask import Flask,jsonify,json,redirect,url_for
from flask import request , send_file , after_this_request
from flask import render_template
import os
import datetime as importDateTime
from datetime import timedelta,date, datetime
from calendar import monthrange
from calendar import mdays
from shutil import copy
from flask import Response
from flask import session,g
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def home():
   return render_template('login.html')


@app.route('/profile', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        sb = EmployeeProfileDAL()
        rowReturn = sb.read_employee()
        projectList=get_project_list()
        return render_template("Dashboard.html", rowTable=rowReturn, projectList=projectList)
    if request.method == 'POST':
        corpid=request.form['corpId']
        corppass = request.form['corppass']
        sb = EmployeeProfileDAL()
        EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
        print(f'EmployeeName : {EmployeeName}')
        print(f'os.getLogin() : {os.getlogin()}')
        rowReturn = sb.read_employee()
        loginfailedmsg = "Invalid credentials"
        projectList=get_project_list()
        if corpid == os.getlogin():
            if request.method == 'POST':
                session.pop('user', None)
                if EmployeeName:
                    session['user'] = request.form['corpId']
                    app.logger.info('-------------------------------------------------------------------------------------')
                    app.logger.info('Logged in by: %s', corpid)
                    admin_return= Admin()
                    if admin_return=="Yes":
                        return redirect(url_for("viewTeamfun"))
                    else:
                        return render_template("Dashboard.html", rowTable=rowReturn, projectList=projectList)
        app.logger.error('Failed to login for %s',corpid)
        return render_template("login.html", **locals())


@app.route('/viewteam')
def viewTeamfun():
    if 'user' in session:
        corp_id=session['user']
        sb=EmployeeProfileDAL()
        EmployeeName=sb.get_current_employee_Info(corp_id)[0][0]
        print("In view team")
        AdminReturn = Admin()
        if AdminReturn == "Yes":
            return render_template("viewteam.html", **locals())
        else:
            return render_template("LeaveAppPart2.html", EmployeeName=EmployeeName,
                                   corpid=corp_id)
    return render_template('login.html', **locals())




# private methods
def get_project_list():
    projectList = []
    for value in ReadJson()['project details']:
        projectList.append(value['projectName'])
    return projectList


def ReadJson():
    with open("static/json/pi.json",'r', encoding='utf-8-sig') as json_file:
        json_data = json.load(json_file)
    return json_data


def Admin():
    managers_corpid = []
    for cid in ReadJson()['ManagersList']:
        managers_corpid.append(cid['CorpID'])
    print(managers_corpid)
    for value in managers_corpid:
        if session['user'] == value:
            pass
            return "Yes"
    return "No"

if __name__ == '__main__':
   app.run(host='0.0.0.0',port=80)