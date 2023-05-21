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
    try:
        if request.method == 'GET':
            sb = EmployeeProfileDAL()
            rowReturn = sb.read_employee()
            projectList=get_project_list()
            return render_template("Dashboard.html", rowTable=rowReturn, projectList=projectList)
        if request.method == 'POST':
            corpid=request.form['corpId']
            corppass = request.form['corppass']
            sb = EmployeeProfileDAL()
            EmployeeName = (sb.get_current_employee_Info(corpid))
            print(f'EmployeeName : {EmployeeName}')
            rowReturn = sb.read_employee()
            loginfailedmsg = "Invalid credentials"
            projectList=get_project_list()
            if corpid:
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
    except Exception as e:
        return str(e)


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


@app.route('/employee details')
def list_all_users():
    if 'user' in session:
        sb = EmployeeProfileDAL()
        corpid=session['user']
        EmployeeName = corpid
        row_return = sb.read_employee()
        projectList = get_project_list()
        employeeLevelList = get_employeeLevel_list()
        app.logger.info('Employee Details page viewed by : %s', corpid)
        AdminReturn = Admin()
        if AdminReturn == "Yes":
            return render_template("Dashboard.html", rowTable=row_return, **locals())
        else:
            return render_template("Dashboard.html", rowTable=row_return, EmployeeName=EmployeeName,corpid=corpid, projectList=projectList, employeeLevelList = employeeLevelList)
    return redirect(url_for('home'))


@app.route('/add profile', methods=['POST'])
def add_profile():
    if 'user' in session:
        employee_id = request.form['employeeId']
        employee_name = request.form['employeeName']
        project_name = request.form['ProjectName']
        corpid = session['user']
        email = request.form['Mail']
        corp_idM = request.form['CorpID']
        department = request.form['Department']
        employeeODCStatus="Assigned"
        expertise=request.form['Expertise']
        employeeLevel=request.form['EmployeeLevel']
        sb = EmployeeProfileDAL()
        project_id = sb.get_project_id(project_name=project_name)
        EmployeeName = corpid
        employee = Employee(employee_id, employee_name, project_id, project_name, corp_idM, email, department, employeeODCStatus,expertise, employeeLevel)
        sb.add_employee(employee)
        rowReturn = sb.read_employee()
        sb.c.close()
        projectList = get_project_list()
        employeeLevelList = get_employeeLevel_list()
        app.logger.info('%s added by: %s',employee_id, corpid)
        AdminReturn = Admin()
        if AdminReturn == "Yes":
            return render_template("Dashboard.html", rowTable=rowReturn, **locals())
        else:
            return render_template("Dashboard.html", rowTable=rowReturn, EmployeeName=EmployeeName, employee=employee, corpid=corpid,projectList=projectList, employeeLevelList = employeeLevelList)
    return redirect(url_for('home'))



@app.route('/Update profile/0', methods=['POST'])
def update_profile():
    # Create cursor
    if 'user' in session:
        sb = EmployeeProfileDAL()
        corpid = session['user']
        # EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
        EmployeeName = corpid
        employee_id = request.form['employeeId']
        employee_name = request.form['employeeName']
        project_name = request.form['projectNameUpdate']
        corpIdM = request.form['corpIdUpdate']
        email = request.form['emailIdUpdate']
        employeeODCStatus= 'Assigned'
        department = request.form['DepartmentUpdate']
        expertise = request.form['expertiseUpdateName']
        employeeLevelUpdate = request.form['employeeLevelUpdate']
        project_id = sb.get_project_id(project_name=project_name)
        employee = Employee(employee_id, employee_name, project_id, project_name, corpIdM, email, department, employeeODCStatus,expertise, employeeLevelUpdate)
        sb.update_employee(employee)
        rowReturn = sb.read_employee()
        sb.c.close()
        print("DataBase is closed")
        projectList = get_project_list()
        employeeLevelList = get_employeeLevel_list()
        # return "Values Submitted to database"
        app.logger.info('%s updated profile details', corpid)
        AdminReturn = Admin()
        if AdminReturn == "Yes":
            return render_template("Dashboard.html", rowTable=rowReturn, **locals())
        else:
            return render_template("Dashboard.html", rowTable=rowReturn, EmployeeName=EmployeeName, employee=employee,projectList=projectList, employeeLevelList = employeeLevelList)
    return redirect(url_for('home'))


@app.route('/compare', methods=['POST'])
def compare():
    print("inside compare method serverside validation")
    formElement = request.json
    # print(type(formElement))
    # print(request.get_json())
    sb = EmployeeProfileDAL()
    for keyFromDict in formElement:
        key = keyFromDict
    # gettting id from DB
    idFromDB = sb.gettingEmployeeDetailsForRepeatedEntries(formElement)
    # comparing id for duplicate entries
    if idFromDB == 1:
        msg = key + " is already exist in the system.Please try another."
        return jsonify({'error': msg})
    else:
        return jsonify({'success': 'true'})













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

def get_employeeLevel_list():
    employeeLevelList = []
    for value in ReadJson()['EmployeeLevelDetails']:
        employeeLevelList.append(value['levelName'])
    return employeeLevelList


if __name__ == '__main__':
   app.run(host='0.0.0.0',port=80)