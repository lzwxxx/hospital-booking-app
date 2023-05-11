#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
# from invokes import invoke_http
from os import environ

# from datetime import datetime
import json

app = Flask(__name__)

# RMB TO CHANGE CONFIG BASED ON DB
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('appointment_dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

CORS(app)

class Appointment(db.Model):
    __tablename__ = 'appointment'

    appointment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, nullable=False)
    doctor_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    time = db.Column(db.Integer, nullable=False)

    def json(self):
        dto = {
            'appointment_id': self.appointment_id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'date': self.date,
            'time': self.time
        }
        return dto

# Get all Appointments
@app.route("/appointment", methods=['GET'])
def get_all():
    try:
        args = request.args
        patient_id = args.get('patient_id') 
        doctor_id = args.get('doctor_id') 
        appointmentlist = Appointment.query.all()
        # If patient_id exists, get patient's history
        if patient_id != None:
            appointmentlist = Appointment.query.filter_by(patient_id=int(patient_id)).all()
        
        # If doctor_id exists, get all appointments by that doctor
        elif doctor_id != None:
            appointmentlist = Appointment.query.filter_by(doctor_id=int(doctor_id)).all() 

        #return appointmentlist
        if len(appointmentlist):
            return jsonify(
                {
                    "code": 200,
                    "data": {
                        "appointments": [appointment.json() for appointment in appointmentlist]
                    }
                }
            )
        return jsonify(
            {
                "code": 404,
                "message": "There are no appointments found."
            }
        ), 404
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "appointment.py internal error: " + str(e)
            }
        ), 500

# Add an Appointment
@app.route("/appointment", methods=['POST'])
def add_appointment():
    try:
        patient_id = request.json.get('patient_id', None)
        doctor_id = request.json.get('doctor_id', None)
        date = request.json.get('date', None)
        time = request.json.get('time', None)

        #check if appointment timing is available
        conflictDoctor,conflictPatient = checkAppointmentConflict(date, time, doctor_id, patient_id)
        
        if conflictDoctor:
            return jsonify(
                {
                    "code": 400,
                    "message": "Timeslot is already taken"
                }
            ), 400
        elif conflictPatient:
            return jsonify(
                {
                    "code": 400,
                    "message": "You have an existing appointment at that timing"
                }
            ), 400
        else:
            appointment = Appointment(patient_id=patient_id, doctor_id=doctor_id,
            date=date, time=time)
            try:
                db.session.add(appointment)
                db.session.commit()
            except Exception as e:
                return jsonify(
                    {
                        "code": 500,
                        "message": "An error occurred while creating the appointment. " + str(e)
                    }
                ), 500

            print(json.dumps(appointment.json(), default=str)) # convert a JSON object to a string and print

            return jsonify(
                {
                    "code": 201,
                    "data": appointment.json()
                }
            ), 201
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "appointment.py internal error: " + str(e)
            }
        ), 500

# Validate if requested appointment timing is
# - not conflicting with any of doctor's appointment 
# - not conflicting with any of the requesting patient's appointment 
def checkAppointmentConflict(date_inp,time_inp,doctor_id,patient_id,appointment_id=None):
    try:
        try: 
            # Get all appointment by doctor and patient
            if appointment_id == None:
                appt_doctor = Appointment.query.filter_by(doctor_id=doctor_id).all()
                appt_patient = Appointment.query.filter_by(patient_id=patient_id).all()
            else:
                # If appointment id is supplied, exclude that from conflict checks
                appt_doctor = Appointment.query.filter(Appointment.doctor_id == doctor_id, Appointment.appointment_id != appointment_id).all()
                appt_patient = Appointment.query.filter(Appointment.patient_id == patient_id, Appointment.appointment_id != appointment_id).all()
            
            date_inp = datetime.strptime(date_inp, '%Y-%m-%d').date()

            conflictDoctor = False
            for doctor_appt in appt_doctor:
                # print(time_inp,doctor_appt.time,date_inp,doctor_appt.date)
                # print(int(time_inp) == int(doctor_appt.time) , date_inp == doctor_appt.date)
                if int(time_inp) == doctor_appt.time and date_inp == doctor_appt.date:
                    print('conflict',time_inp,doctor_appt.time,date_inp,doctor_appt.date)
                    conflictDoctor = True
                    break
            
            conflictPatient = False
            for patient_appt in appt_patient:
                # print(time_inp,patient_appt.time,date_inp,patient_appt.date)
                # print(int(time_inp) == int(patient_appt.time) , date_inp == patient_appt.date)
                if int(time_inp) == patient_appt.time and date_inp == patient_appt.date:
                    print('conflict',time_inp,patient_appt.time,date_inp,patient_appt.date)
                    conflictPatient = True
                    break

            return conflictDoctor,conflictPatient
        except Exception as e:
            raise e
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "appointment.py internal error: " + str(e)
            }
        ), 500

# Get an Appointment
@app.route("/appointment/<int:appointment_id>", methods=['GET'])
def get_by_appointment_id(appointment_id):
    try:
        appointment_id = int(appointment_id)
        appointment = Appointment.query.filter_by(appointment_id=appointment_id).first()
        if appointment:
            return jsonify(
                {
                    "code": 200,
                    "data": appointment.json()
                }
            )
        return jsonify(
            {
                "code": 404,
                "data": {
                    "appointment_id": appointment_id
                },
                "message": "Appointment not found."
            }
        ), 404
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "appointment.py internal error: " + str(e)
            }
        ), 500

# Get Patient's Appointment history
@app.route("/appointment/patient/<int:patient_id>", methods=['GET'])
def get_by_patient_id(patient_id):
    try:
        patient_id = int(patient_id)
        appointmentlist = Appointment.query.filter_by(patient_id=patient_id).all()
        if len(appointmentlist):
            return jsonify(
                {
                    "code": 200,
                    "data": {
                        "appointment": [appointment.json() for appointment in appointmentlist]
                    }
                }
            )
        return jsonify(
            {
                "code": 404,
                "message": "There are no appointments."
            }
        ), 404
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "appointment.py internal error: " + str(e)
            }
        ), 500

# Change an Appointment
@app.route("/appointment/<int:appointment_id>", methods=['POST'])
def update_appointment(appointment_id):
    try:
        appointment_id = int(appointment_id)
        appointment = Appointment.query.filter_by(appointment_id=appointment_id).first()
        if not appointment:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "appointment_id": appointment_id
                    },
                    "message": "Appointment not found."
                }
            ), 404
        
        data = request.get_json()
        patient_id = request.json.get('patient_id', None)
        doctor_id = request.json.get('doctor_id', None)
        date = request.json.get('date', None)
        time = request.json.get('time', None)

        #check if appointment timing is available
        conflictDoctor,conflictPatient = checkAppointmentConflict(date, time, doctor_id, patient_id, appointment_id)
        
        if conflictDoctor:
            return jsonify(
                {
                    "code": 400,
                    "message": "Timeslot is already taken"
                }
            ), 400
        elif conflictPatient:
            return jsonify(
                {
                    "code": 400,
                    "message": "You have an existing appointment at that timing"
                }
            ), 400
        else:
            # update appointment
            # if 'doctor_id' in data:
            appointment.doctor_id = data['doctor_id']
            # if 'date' in data:
            appointment.date = data['date']
            # if 'time' in data:
            appointment.time = data['time']

            db.session.commit()
            return jsonify(
                {
                    "code": 200,
                    "data": appointment.json()
                }
            ), 200
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "appointment_id": appointment_id
                },
                "message": "An error occurred while updating the appointment. " + str(e)
            }
        ), 500

# Validate an Appointment if it is conflicting with other Appointments
@app.route("/check_conflict", methods=['POST'])
def check_conflict():
    try:
        if request.is_json:
            expected_fields = ['date','time','doctor_id','patient_id']
            optional_fields = ['appointment_id']
            if not check_input(request.get_json(),expected_fields,optional=optional_fields):
                return jsonify({
                    "code": 400,
                    "message": "Invalid input fields: [" + ' '.join(list(request.get_json().keys())) + "] , expecting " + ' '.join(expected_fields) + ' (optional '+' '.join(optional_fields)+')'
                }), 400
        else:
            # if reached here, not a JSON request.
            return jsonify({
                "code": 400,
                "message": "Invalid JSON input: " + str(request.get_data())
            }), 400

        appointment = request.get_json()
        try:
            # Convert date string to datetime.date
            date_inp = appointment['date']
            time_inp = int(appointment['time'])
            doctor_id = appointment['doctor_id']
            patient_id = appointment['patient_id']
            
            if "appointment_id" in appointment:
                appointment_id = appointment['appointment_id']
                conflictDoctor,conflictPatient = checkAppointmentConflict(date_inp,time_inp,doctor_id,patient_id,appointment_id)
            else: 
                conflictDoctor,conflictPatient = checkAppointmentConflict(date_inp,time_inp,doctor_id,patient_id)

            return jsonify(
                    {
                        "code": 200,
                        "data": {
                            "conflict_with_doctor_appt":conflictDoctor,
                            "conflict_with_patient_appt":conflictPatient
                        }
                    }
                ), 200
            
        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "message": "An error occurred while validating the appointment. " + str(e)
                }
            ), 500
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "appointment.py internal error: " + str(e)
            }
        ), 500

def check_input(json,fields,optional=[]):
    return set(fields).issubset(set(json.keys())) and set(json.keys()).issubset(set(fields).union(set(optional)))

if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage appointments ...")
    app.run(host='0.0.0.0', port=5001, debug=True)
