from flask import Flask, request, render_template, abort, url_for, session, escape, redirect
from invokes import invoke_http
from os import environ

from __main__ import app

#microservice endpoints
add_doctor_api = environ.get('doctor_service_URL')+'/add_doctor'

#redirect user to the add_doctor.html
@app.route('/add_doc_form')
def add_doctor_form():
    if 'username' in session:
        try:
            return render_template('add_doctor.html')
        except Exception as e:
            print(e)
            return render_template('add_doctor.html')
    else:
        abort(404)
        
#add doctor 
@app.route('/add_doctor', methods=['POST'])
def add_doctor():
    try:
        doctor = request.get_json()
        res = invoke_http(url=add_doctor_api, method='POST', json=doctor)
        return res, res['code']
    except Exception as e:
        return {"message": "An error occurred", "data":e}, 500