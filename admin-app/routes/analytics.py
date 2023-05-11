from flask import Flask, request, render_template, abort, url_for, session, escape, redirect
from invokes import invoke_http
from os import environ

from __main__ import app

#microservice endpoints
get_all_doctors_api = environ.get('doctor_service_URL')+'/doctor'
get_patient_hr_api = environ.get('analytics_service_URL')+'/weekly_average_patient/all'

#redirect users to the analytics.html page with data of all the existing doctors
@app.route('/')
def index():
    if 'username' in session:
        try:
            doctors_info = retrieve_doctors()
            #print(doctors_info)
            return render_template('analytics.html', doctors_info=doctors_info)
        except Exception as e:
            print(e)
            abort(500)
    else:
        return redirect(url_for('login'))

#get data of all the existing doctors 
def retrieve_doctors():
    try:
        doctors_info = invoke_http(url=get_all_doctors_api,method='GET')
        return doctors_info['data']['doctors']
    except Exception as e:
        raise e 

#get data of the chart 
@app.route('/get_overall_chart')
def retrieve_chart_info():
    if 'username' in session:
        try:
            chart_info = invoke_http(url=get_patient_hr_api,method='GET')
            return chart_info
        except Exception as e:
            return {"message":"An error occurred","data":e},500
    else:
        abort(404)
