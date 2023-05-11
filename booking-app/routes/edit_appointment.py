import json
from flask import Flask, request, render_template, abort
from invokes import invoke_http
from os import environ
from datetime import datetime

# Import app instance from main file
from __main__ import app

# Microservice endpoints
get_appointment_api = environ.get('appointment_service_URL')+'/appointment'
get_all_doctors_api = environ.get('doctor_service_URL')+'/doctor'
edit_appointment_booking_api = environ.get('appointment_booking_service_URL')+'/edit_appointment'
analytics_service_URL = environ.get('analytics_service_URL')+'/weekly_average_patient/all'

@app.route('/editAppointment/<int:appointment_id>')
def edit_appointment(appointment_id):
    try:
        appointment = retrieve_appointment(appointment_id)
        doctors = retrieveDoctors()
        appointment['date'] = datetime.strptime(appointment['date'], '%a, %d %b %Y %H:%M:%S %Z').strftime("%d-%m-%Y")
        appointment['date'] = datetime.strptime(appointment['date'], '%d-%m-%Y').date()
        res = invoke_http(url=get_all_doctors_api+f"/{appointment['doctor_id']}",method='GET')
        timeslots = list(range(int(res['data']['start_time']),int(res['data']['end_time'])))
        select = ""
        for time in timeslots:
            print(time, appointment['time'])
            strtime = format_time(time)
            print(strtime)
            if time != appointment['time']:
                select += "<option value="+str(time)+">"+strtime+"</option>"
            else:
                select += "<option selected value="+str(time)+">"+strtime+"</option>"
        return render_template('edit_appointment.html',appointment=appointment, doctors=doctors, appointment_id=appointment_id, select=select)
    except Exception as e:
        print(e)
        # return render_template('edit_appointment.html',appointment=appointment, doctors=doctors)  
        return render_template('index.html')

@app.route('/submit_editAppointment',methods=['POST'])
def submit_editAppointment():
    try:
        print(request.get_data(),request.get_json(force=True))
        appointment = request.get_json()
        # print(appointment)
        appointment['appointment_id'] = int(appointment['appointment_id'].strip())
        # appointment = json.dumps(appointment)
        # print(appointment, type(appointment))
        # print(request.get_data(), type(request.get_data()))
        res = invoke_http(url=edit_appointment_booking_api, method='POST', json=appointment)
        return res,res['code']
    except Exception as e:
        return {"message":"An error occurred","data": e},500

@app.route('/doctor_timeslots/<int:id>',methods=['GET'])
def doctorTimeslots(id):
    try:
        res = invoke_http(url=get_all_doctors_api+f"/{id}",method='GET')
        print(res)
        timeslots = list(range(int(res['data']['start_time']),int(res['data']['end_time'])))
        return {'data':timeslots},200
    except Exception as e:
        return {"message":"An error occurred","data":e},500

# Retrieve appointment by appointment id
def retrieve_appointment(appointment_id):
    try:
        appointment = invoke_http(url=get_appointment_api+'/' + str(appointment_id))
        return appointment['data']
    except Exception as e:
        raise e

def retrieveDoctors():
    try:
        res = invoke_http(url=get_all_doctors_api,method='GET')
        return res['data']['doctors']
    except Exception as e:
        raise e 

@app.route('/get_analytics',methods=['GET'])
def getAnalytics():
    try:
        res = invoke_http(url=analytics_service_URL, method='GET')
        return res['data']
    except Exception as e:
        raise e 

def format_time(time):  
    if time == 0:
        return "12 am"
    elif time < 12:
        return str(time)+" am"
    elif time == 12:
        return "12 pm"
    else:
        return str((time-12))+" pm" 
