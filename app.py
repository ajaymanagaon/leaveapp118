import random

from Employee import AttendanceDetails, Employee
from EmployeeProfileDAL import EmployeeProfileDAL
from flask import Flask,jsonify,json,redirect,url_for
from flask import request , send_file , after_this_request
from flask import render_template
import os
import datetime as importDateTime
from datetime import timedelta,date, datetime
import calendar
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

@app.route('/deleteEmployee',methods=['GET'])
def deleteemp():
    if 'user' in session:
        print(f"Delete Request Initiated for Employee Id : {request.args['employeeId']}")
        employeeId = request.args['employeeId']
        sb = EmployeeProfileDAL()
        delete_status = sb.delete_employee(employeeId)
        return delete_status



@app.route('/compare', methods=['POST'])
def compare():
    formElement = request.json
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

@app.route('/personalLeave')
def personalLeave():
    if 'user' in session:
        corpid = session['user']
        sb = EmployeeProfileDAL()
        EmployeeName=(sb.get_current_employee_Info(corpid))[0][0]
        EmployeeName = corpid
        AdminReturn = Admin()
        if AdminReturn == "Yes":
          return render_template('personalCal.html', **locals())
        else:
            return render_template('personalCal.html', EmployeeName=EmployeeName,corpid=corpid)
    return render_template('login.html', **locals())


@app.route('/showPersonalLeave',methods=["POST","GET"])
def showPersonalLeave():
    sb = EmployeeProfileDAL()
    corp_id_org=request.args.get('corpid')
    if corp_id_org is not None:
        rowsForManagerEmployee = sb.readTotalLeavesForAnEmployee(corp_id_org)
        return jsonify(rowsForManagerEmployee)
    return render_template('login.html', **locals())

@app.route('/getCurrentUser', methods=["GET"])
def getCurrentUser():
    if 'user' in session:
        corpid=session['user']
        return jsonify(corpid)
    return jsonify("false")


@app.route('/applyLeave' ,methods=["POST", "GET"])
def applyLeave():
    if 'user' in session:
        date = request.form['Date']
        leaveType=request.form['LeaveType']
        corpid=request.form['CorpID']
        sb = EmployeeProfileDAL()
        sb.submit_leaves(date, corpid,leaveType)
        EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
        app.logger.info('Leave applied for %s on %s by: %s', corpid, date, corpid)
        return jsonify(success='true')
    return render_template('login.html', **locals())


@app.route('/dj',methods=["GET"])
def jsondata():
    with open("static/json/pi.json",'r', encoding='utf-8-sig') as json_file:
        json_data = json.load(json_file)
        sb=EmployeeProfileDAL()
    return jsonify(json_data)


@app.route('/labRequest')
def labRequest():
    if 'user' in session:
        corpid = session['user']
        sb = EmployeeProfileDAL()
        EmployeeName=(sb.get_current_employee_Info(corpid))[0][0]
        EmployeeName = corpid
        projectList = get_project_list()
        sb = EmployeeProfileDAL()
        rowTable = sb.read_lab_requests()
        AdminReturn = Admin()
        if AdminReturn == "Yes":
          return render_template('Lab.html', **locals())
        else:
            return render_template('Lab.html', EmployeeName=EmployeeName,corpid=corpid, projectList=projectList, rowTable=rowTable)
    return render_template('login.html', **locals())


@app.route('/add lab request', methods=['POST'])
def add_lab_request():
    if 'user' in session:
        request_description = request.form['description']
        project_name = request.form['ProjectName']
        corpid = session['user']
        sb = EmployeeProfileDAL()
        today = date.today().strftime('%m/%d/%Y')
        EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
        projectList = get_project_list()
        id = int(random.random() * 100000.0)
        sb.add_lab_request(request_description,EmployeeName,project_name, today, id)
        rowReturn = sb.read_lab_requests()
        rowTable = sb.read_lab_requests()
        AdminReturn = Admin()
        if AdminReturn == "Yes":
          return render_template('Lab.html', **locals())
        else:
            return render_template('Lab.html', EmployeeName=EmployeeName,corpid=corpid, projectList=projectList, rowTable=rowTable)
    return render_template('login.html', **locals())

@app.route('/Delete Request', methods=['POST'])
def delete_lab_request():
    try:
        corpid = session['user']
        sb = EmployeeProfileDAL()
        EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
        request_id = request.form['requestId']
        sb.delete_lab_request(request_id)
        rowTable = sb.read_lab_requests()
        projectList = get_project_list()
        AdminReturn = Admin()
        if AdminReturn == "Yes":
          return render_template('Lab.html', **locals())
        else:
            return render_template('Lab.html', EmployeeName=EmployeeName,corpid=corpid, projectList=projectList, rowTable=rowTable)
    except Exception as e:
        return str(e)


@app.route('/teambuilder')
def CreateOrg():
    if 'user' in session:
        corpid = session['user']
        sb=EmployeeProfileDAL()
        EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
        return render_template("CreateOrg.html", **locals())
    return render_template('login.html', **locals())


@app.route('/orgDetails',methods=['GET', 'POST'])
def showdataforManagers():
    if 'user' in session:
        corp_id=session['user']
        sb = EmployeeProfileDAL()
        manager_id = (sb.get_current_employee_Info(corp_id))[0][2]
        if request.method == 'GET':
            EmployeeDetails = sb.read_employee_in_dict()
            return jsonify(EmployeeDetails)
        else:
            formElement = request.json
            sb = EmployeeProfileDAL()
            result=sb.AssiningToManager(manager_id, formElement)
            return jsonify({"result": result})
    return render_template('login.html', **locals())


@app.route('/updateStatus',methods=["GET","POST"])
def updateEmployeeStatus():
    if 'user' in session:
        if request.method=="POST":
            formElement = request.json
            corp_id = session['user']
            sb = EmployeeProfileDAL()
            manager_id = (sb.get_current_employee_Info(corp_id))[0][2]
            status=sb.update_status(formElement)
            return jsonify(status)
    return render_template('login.html', **locals())

@app.route('/getsetviewdata',methods=['GET', 'POST'])
def getsetDataforteam():
    if 'user' in session:
        corp_id = session['user']
        obj = EmployeeProfileDAL()
        EmployeeName=obj.get_current_employee_Info(corp_id)[0][0]
        manager_id = (obj.get_current_employee_Info(corp_id))[0][2]
        if request.method == 'GET':
            orglist = obj.gettingAssignedEmployeeToManager(manager_id=manager_id)
            return jsonify(orglist)
    return render_template('login.html', **locals())



@app.route('/currentMonth')
def currentMonthDetails():
    if 'user' in session:
            # and (session['user'] == "conngo" or session['user'] == "consys" or session["user"] == "conddas" or session["user"] == "conravh" ):
        corpid = session['user']
        #now = datetime.datetime.now()
        v = request.args.get('mon')
        if v is not None:
            v = v.split("-")
            sb = EmployeeProfileDAL()
            EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
            d = importDateTime.date.today()
            month = v[1]
            year = v[0]
            dateArray = []
            dateArray = dateArrayMethod(int(year), int(month))
            employeeStatusListView = gettingInfo(month, int(year))
            AdminReturn = Admin()
            if AdminReturn == "Yes":
                return render_template("LeaveAppPart2.html", **locals())
            else:
                return render_template("LeaveAppPart2.html",dateArray=dateArray,employeeStatusListView=employeeStatusListView, EmployeeName=EmployeeName, corpid=corpid)
        else:
            sb = EmployeeProfileDAL()
            EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
            d = importDateTime.date.today()
            month = d.strftime('%m')
            year = d.strftime('%Y')
            dateArray = []
            dateArray = dateArrayMethod(int(year), int(month))
            employeeStatusListView = []
            employeeStatusListView = gettingInfo(month, int(year))
            AdminReturn = Admin()
            if AdminReturn == "Yes":
                for employeelist in employeeStatusListView:
                    for value in employeelist:
                        if value is None:
                            print(employeelist[2])

                return render_template("LeaveAppPart2.html", **locals())
            else:
                return render_template("LeaveAppPart2.html", dateArray=dateArray,
                                       employeeStatusListView=employeeStatusListView, EmployeeName=EmployeeName,
                                       corpid=corpid)
    return render_template('login.html', **locals())




@app.route('/monthlyOtherDeductions')
def monthlyOtherDeductions():
    if 'user' in session:
        # and (session['user'] == "conngo" or session['user'] == "consys" or session["user"] == "conddas" or session["user"] == "conravh" ):
        corpid = session['user']
        # now = datetime.datetime.now()
        v = request.args.get('mon')
        if v is not None:
            v = v.split("-")
            sb = EmployeeProfileDAL()
            EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
            d = importDateTime.date.today()
            month = v[1]
            year = v[0]
            dateArray = []
            dateArray = dateArrayMethod(int(year), int(month))
            # getting selected month
            # total days in current month
            employeeStatusListView = []
            employeeStatusListView = gettingOtherDeductionsInfo(month, int(year))
            AdminReturn = Admin()
            if AdminReturn == "Yes":
                return render_template("OtherDeductions.html", **locals())
            else:
                return render_template("OtherDeductions.html", dateArray=dateArray,
                                       employeeStatusListView=employeeStatusListView, EmployeeName=EmployeeName,
                                       corpid=corpid)
        else:
            sb = EmployeeProfileDAL()
            EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
            d = importDateTime.date.today()
            month = d.strftime('%m')
            year = d.strftime('%Y')
            dateArray = []
            dateArray = dateArrayMethod(int(year), int(month))
            # getting selected month
            # total days in current month
            employeeStatusListView = []
            employeeStatusListView = gettingOtherDeductionsInfo(month, int(year))
            AdminReturn = Admin()
            if AdminReturn == "Yes":
                return render_template("OtherDeductions.html", **locals())
            else:
                return render_template("OtherDeductions.html", dateArray=dateArray,
                                       employeeStatusListView=employeeStatusListView, EmployeeName=EmployeeName,
                                       corpid=corpid)
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


def dateArrayMethod(year, month):
    dateArray = []
    dict = {'0': 'Mon', '1': 'Tue', '2': 'Wed', '3': 'Thu', '4': 'Fri', '5': 'Sat', '6': 'Sun'}
    cal = calendar.Calendar()

    for x in cal.itermonthdays2(year, month):
        if x[0] != 0:
            dateArray.append(calendar.month_name[month][:3] + " " + str(x[0]) + " " + dict[str(x[1])])
    return dateArray


def gettingInfo(month,year):
    #corpid=session['user']
    today = date.today()
    numOfDays = calendar.monthrange(year, int(month))
    numOfDaysCfCurrentMonth = numOfDays[1]
    sb = EmployeeProfileDAL()
    # EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]
    employee_list = sb.read_employee()
    employeeStatusListView = []
    HolidayList = []
    HolidayMonth = []
    HolidayDates = []
    listOfDays = list(range(1, numOfDaysCfCurrentMonth+1))
    # get the current month
    # get the month from holiday
    # and compare
    dateArray = dateArrayMethod(year, int(month))
    i=0
    for value in ReadJson()['waters holidays']:
        HolidayList.append(value['date'].split("/"))
        HolidayMonth.append(HolidayList[i][1])
        # filter out the dates of relevent month
        if month in HolidayMonth:
            if HolidayList[i][1] == month:
                HolidayDates.append(int(HolidayList[i][0]))
                # getHolidayDates
        i=i+1

    for employee in employee_list:
        employeeWorkStatus = []
        counterForOn = 0
        # employeeWorkStatus.append(str(employee[7]))
        employeeWorkStatus.append(str(employee[0]))
        employeeWorkStatus.append(str(employee[1]))
        employeeWorkStatus.append(employee[2])
        employeeWorkStatus.append(employee[3])
        employeeWorkStatus.append(employee[4])
        employeeWorkStatus.append(employee[5])
        employeeWorkStatus.append(" ")
        employeeWorkStatus.append(" ")
        employeeWorkStatus.append(" ")
        employeeWorkStatus.append(" ")

        with open("static/json/pi.json", 'r', encoding='utf-8-sig') as json_file:
            json_data = json.load(json_file)

        dateArray = dateArrayMethod(year,int(month))
        

        for i in range(numOfDaysCfCurrentMonth):
            dateloop = date(year,int(month),i+1)
            if dateArray[i][-3:] == 'Sat' or dateArray[i][-3:] == 'Sun' or (i+1 in HolidayDates) or (dateloop > today):
                employeeWorkStatus.append(" ")
            else:
                employeeWorkStatus.append("Present")
                counterForOn += 1


        employee_leave_list = sb.read_leaves_type(employee[7], month, year)
        if employee_leave_list is not None:
            counterForFullDay = 0
            counterForHalfDay = 0
            for leave in employee_leave_list:
                numOfDays = calendar.monthrange(year, int(month))
                numOfDaysCfCurrentMonth = numOfDays[1]
                leave_date = str(leave[0])                
                leave_type = leave[1]                
                leavedate = leave_date.split('/')                
                if leave_type == '1' or leave_type == '4':                    
                    employeeWorkStatus[int(leavedate[0]) + 8] = 'FullDayLeave'
                    counterForFullDay += 1                    
                elif leave_type == '2' or leave_type == '5':
                    employeeWorkStatus[int(leavedate[0]) + 8] = 'HalfDayLeave'
                    counterForHalfDay += 1
                elif leave_type == '3':
                    employeeWorkStatus[int(leavedate[0]) + 8] = 'Non-WIPL'
                    # counterForHalfDay += 1
        totalDayOfFullDays = counterForFullDay
        totalDayOfHalfDays = counterForHalfDay
        totalhoursofWork = (counterForOn*8 - (counterForFullDay*8 + counterForHalfDay*4))
        employeeWorkStatus.append(" ")
        employeeWorkStatus.append(str(totalDayOfFullDays))
        employeeWorkStatus.append(str(totalDayOfHalfDays))
        employeeWorkStatus[7] = str(totalhoursofWork)
        employeeWorkStatus[5] = str(round(21.85 * totalhoursofWork, 1))
        employeeWorkStatus[6] = str(21.85)
        employeeStatusListView.append(employeeWorkStatus)
    return employeeStatusListView


def gettingOtherDeductionsInfo(month, year):
    # corpid=session['user']
    numOfDays = calendar.monthrange(year, int(month))

    startDate =  "1-" + str(month) +"-" + str(year)
    endDate = str(numOfDays[1]) + "-" + str(month) +"-" + str(year)

    otherDeductions = []
    for value in ReadJson()['OtherDeductions']:
        otherDeductions.append(value['PaymentRecovery'])
        otherDeductions.append(value['Amount'])
        otherDeductions.append(value['PaymentRecoveryTowards'])
        otherDeductions.append(value['LetterToBeIssued'])
        otherDeductions.append(value['ApprovalAttached'])
        otherDeductions.append(value['NameOftheAttachment'])
        otherDeductions.append(value['ApproverName'])
        otherDeductions.append(value['RemarksReason'])
        otherDeductions.append(value['TypeOfDeduction'])
        otherDeductions.append(value['MinimumWorkDays'])


    numOfDaysCfCurrentMonth = numOfDays[1]
    sb = EmployeeProfileDAL()
    # EmployeeName = (sb.get_current_employee_Info(corpid))[0][0]


    employee_list = sb.read_employee()
    employeeStatusListView = []
    for employee in employee_list:
        employeeWorkStatus = []
        counterForOn = 0
        dateArray = dateArrayMethod(year, int(month))
        for i in range(numOfDaysCfCurrentMonth):
            if dateArray[i][-3:] == 'Sat' or dateArray[i][-3:] == 'Sun':
                test = " "
            else:
                counterForOn += 1

        employee_leave_list = sb.read_leaves_type(employee[7], month, year)
        if employee_leave_list is not None:
            counterForFullDay = 0
            counterForHalfDay = 0
            for leave in employee_leave_list:
                numOfDays = calendar.monthrange(year, int(month))
                numOfDaysCfCurrentMonth = numOfDays[1]
                leave_date = str(leave[0])
                leave_type = leave[1]
                leavedate = leave_date.split('/')
                if leave_type == '1':
                    counterForFullDay += 1  #full day leave
                else:
                    counterForHalfDay += 1 #half day leave
        totalDayOfFullDays = counterForFullDay
        totalDayOfHalfDays = counterForHalfDay
        totalhoursofWork = 0
        totalhoursofWork = (counterForOn * 8 - (counterForFullDay * 8 + counterForHalfDay * 4))
        if(totalhoursofWork < (int(otherDeductions[9]) * 8)):   #if work days is less than 7 days
            continue
        else:
            employeeWorkStatus.append(str(employee[1]))
            employeeWorkStatus.append(otherDeductions[0])
            employeeWorkStatus.append(employee[2])
            employeeWorkStatus.append(otherDeductions[1])
            employeeWorkStatus.append(startDate)
            employeeWorkStatus.append(endDate)
            employeeWorkStatus.append(otherDeductions[2])
            employeeWorkStatus.append(otherDeductions[3])
            employeeWorkStatus.append(otherDeductions[4])
            employeeWorkStatus.append(otherDeductions[5])
            employeeWorkStatus.append(otherDeductions[6])
            employeeWorkStatus.append(otherDeductions[7])
            employeeStatusListView.append(employeeWorkStatus)
    return employeeStatusListView
















if __name__ == '__main__':
   app.run(host='0.0.0.0',port=80)