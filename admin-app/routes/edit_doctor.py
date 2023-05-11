from flask import Flask, request, render_template, abort, url_for, session, escape, redirect
from invokes import invoke_http
from os import environ

from __main__ import app

#microservice endpoints
get_doctor_api = environ.get('doctor_service_URL')+'/doctor'
update_doctor_api = environ.get('doctor_service_URL') + '/update_doctor'

#redirect the user to the edit_doctor.html with the data of the respective doctor
@app.route("/edit_doctor/<int:doctor_id>")
def edit_doctor(doctor_id):
    if 'username' in session:
        try:
            doctor = retrieve_doctor(doctor_id)
            #print(doctor)
            return render_template('edit_doctor.html', doctor=doctor)
        except Exception as e:
            print(e)
            return render_template('edit_doctor.html', doctor=doctor)
    else:
        abort(404)

#update the data of the respective doctor 
@app.route("/update_doctor/<int:doctor_id>", methods=['PUT'])
def update_doctor(doctor_id):
    try:
        data = request.get_json()
        #print(data)
        update_doctor_info = invoke_http(url=update_doctor_api + '/' + str(doctor_id), method='PUT', json=data)
        return update_doctor_info,update_doctor_info['code']
    except Exception as e:
      return {"message":"An error occurred","data":e},500

#retrieve data of a particular data using doctor_id 
def retrieve_doctor(doctor_id):
    try:
        doctor = invoke_http(url=get_doctor_api + '/' + str(doctor_id))
        return doctor["data"]
    except Exception as e:
        raise e 
