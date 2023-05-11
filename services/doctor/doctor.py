#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import os
from tracemalloc import start
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ

# from datetime import datetime
import json

app = Flask(__name__)

# RMB TO CHANGE CONFIG BASED ON DB
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('doctor_dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

CORS(app)  

class Doctor(db.Model):
    __tablename__ = 'doctor'

    doctor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_nric = db.Column(db.String(9), nullable=False)
    doctor_name = db.Column(db.String(), nullable=False)
    doctor_sex = db.Column(db.String(), nullable=False)
    start_time = db.Column(db.Integer, nullable=False)
    end_time = db.Column(db.Integer, nullable=False)

    def __init__(self, doctor_id, doctor_nric, doctor_name, doctor_sex, start_time, end_time):
        self.doctor_id = doctor_id
        self.doctor_nric = doctor_nric
        self.doctor_name = doctor_name 
        self.doctor_sex = doctor_sex 
        self.start_time = start_time 
        self.end_time = end_time

    def json(self):
        return {"doctor_id": self.doctor_id, "doctor_nric": self.doctor_nric, "doctor_name": self.doctor_name, "doctor_sex": self.doctor_sex, "start_time": self.start_time, "end_time": self.end_time}

#Get all doctors 
@app.route("/doctor", methods=['GET'])
def get_all():
    try:
        #Retrieve all records from the doctor table and store it as a list in the doctorlist
        doctorlist = Doctor.query.all()
        #Check if the doctorlist is empty 
        if len(doctorlist):
            #The doctorlist is not empty 
            return jsonify(
                {   
                    #Return the corresponding HTTP status code 200 and list of doctors in the JSON representation
                    "code" : 200,
                    "data" : {
                        "doctors": [doctor.json() for doctor in doctorlist]
                    }
                }
            )

        #The doctorlist is empty 
        return jsonify(
            {
                #Return an error message in JSON and HTTP status code 404 - Not Found
                "code": 404,
                "message": "There are no doctors."
            }
        ), 404 

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "doctor.py internal error: " + str(e)
            }
        ), 500



#Get the information of a doctor by doctor_id 
@app.route("/doctor/<int:doctor_id>", methods=['GET'])
def find_by_doctor_id(doctor_id):
    try:
        #Check if the doctor_id already exists in the patient table 
        doctor = Doctor.query.filter_by(doctor_id=doctor_id).first()
        if doctor:
            #The doctor_id exist 
            return jsonify(
                {
                    #Return doctor's information in JSON with HTTP status code 200 - Ok
                    "code": 200,
                    "data": doctor.json()
                }
            )

        #The doctor_id does not exist 
        return jsonify(
            {
                #Return doctor_id and error message in JSON with HTTP status code 404 - Not Found 
                "code": 404,
                "data": {
                    "doctor_id": doctor_id
                },
                "message": "Doctor not found."
            }
        ), 404
    
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "doctor.py internal error: " + str(e)
            }
        ), 500

# Add a doctor
@app.route("/add_doctor", methods=['POST'])
def add_doctor():
    
    try:
        #Get the doctor_nric from the request received 
        doctor_nric = request.json.get('doctor_nric', None)

        #Check if the doctor_nric already exists in the doctor table 
        doctor = Doctor.query.filter_by(doctor_nric=doctor_nric).first()
        if doctor:
            #The doctor_nric exist 

            #Return doctor_id and an error message in JSON with HTTP status code 400 - Bad Request 
            return jsonify(
                {
                    "code": 400,
                    "data": {
                        "doctor_nric": doctor_nric
                    },
                    "message": "Doctor already exists."
                }
            ), 400

        #The doctor_nric does not exist

        #Checking start time and end time 
        start_time = request.json.get('start_time', None)
        end_time = request.json.get('end_time', None)

        if not(start_time >= 0 and start_time <= 23 and end_time >= 0 and end_time <= 23):
            start_invalid = not(start_time >= 0 and start_time <= 23)
            end_invalid = not(end_time >= 0 and end_time <= 23)
            
            if start_invalid and end_invalid:
                errata = "Both Start and End time"
            else:
                errata = "Start time" if start_invalid else "End time"
            return jsonify(
                    {
                        "code": 400,
                        "data": {
                            "start_time": start_time,
                        },
                        "message": f"{errata} has to be within the working hours (0 to 23)"
                    }
                ), 400
        
        if not(start_time < end_time):
            return jsonify(
                {
                    "code": 400,
                    "data": {
                        "start_time": start_time,
                        "end_time": end_time
                    },
                    "message": "End time should be greater than start time"
                }
            ), 400
        
        #Request does not contain doctor_id as it is auto increment so doctor_id is set to 'None'
        doctor_id = None

        #Get all the data from the request received 
        data = request.get_json()
        #Create an instance of a doctor using doctor_id and the attributes sent in the request 
        doctor = Doctor(doctor_id, **data)

        try:
            #Add the record of the new doctor to the doctor table
            db.session.add(doctor)
            #Commit the changes 
            db.session.commit()
        except:
            #Return doctor_nric and an error message in JSON with HTTP status code 500 - Internal Server error if an exception occurs.
            return jsonify(
                {
                    "code": 500,
                    "data": {
                        "doctor_nric": doctor_nric
                    },
                    "message": "An error occurred while creating the doctor."
                }
            ), 500

        #If there is no exception, return the JSON representation of the doctor added with HTTP status code 201 - created.
        return jsonify(
            {
                "code": 201,
                "data": doctor.json()
            }
        ), 201
    
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "doctor.py internal error: " + str(e)
            }
        ), 500

#Edit a doctor
@app.route("/update_doctor/<int:doctor_id>", methods=['PUT'])
def update_doctor(doctor_id):
    
    try:
        #Check if the doctor_id already exists in the doctor table 
        doctor = Doctor.query.filter_by(doctor_id=doctor_id).first()
        if doctor:
            #The doctor_id exist 

            #Get all the data from the request recieved and store into the respective variables
            doctor_nric = request.json.get('doctor_nric', None)
            doctor_name = request.json.get('doctor_name', None)
            doctor_sex = request.json.get('doctor_sex', None)
            start_time = request.json.get('start_time', None)
            end_time = request.json.get('end_time', None)

            #Checking start time and end time 
            start_time = request.json.get('start_time', None)
            end_time = request.json.get('end_time', None)

            if not(start_time >= 0 and start_time <= 23 and end_time >= 0 and end_time <= 23):
                start_invalid = not(start_time >= 0 and start_time <= 23)
                end_invalid = not(end_time >= 0 and end_time <= 23)
                
                if start_invalid and end_invalid:
                    errata = "Both Start and End time"
                else:
                    errata = "Start time" if start_invalid else "End time"
                return jsonify(
                        {
                            "code": 400,
                            "data": {
                                "start_time": start_time,
                            },
                            "message": f"{errata} has to be within the working hours (0 to 23)"
                        }
                    ), 400
            
            if not(start_time < end_time):
                return jsonify(
                    {
                        "code": 400,
                        "data": {
                            "start_time": start_time,
                            "end_time": end_time
                        },
                        "message": "End time should be greater than start time"
                    }
                ), 400
            

            try:   
                #Check if the variable is not equal to "None" before updating the value of the respective attribute in the database
                if doctor_nric != None:
                    doctor.doctor_nric = doctor_nric

                if doctor_name != None:
                    doctor.doctor_name = doctor_name
                
                if doctor_sex != None:
                    doctor.doctor_sex = doctor_sex 
                
                if start_time != None:
                    doctor.start_time = start_time

                if end_time != None:
                    doctor.end_time = end_time

                #Commit the changes 
                db.session.commit()

                #If there is no exception, return doctor's information in JSON with HTTP status code 200 - Ok
                return jsonify(
                    {
                        "code": 200,
                        "data": doctor.json()
                    }
                ), 200

            except:
                #Return doctor_id and an error message in JSON with HTTP status code 500 - Internal Server error if an exception occurs.
                return jsonify(
                    {
                        "code": 500,
                        "data": {
                            "doctor_id": doctor_id
                        },
                        "message": "An error occurred while updating the doctor."
                    }
                ), 500

        #The doctor_id does not exist 
        return jsonify(
            {
                #Return doctor_id and error message in JSON with HTTP status code 404 - Not Found 
                "code": 404,
                "data": {
                    "doctor_id": doctor_id
                },
                "message": "Doctor not found."
            }
        ), 404
    
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "doctor.py internal error: " + str(e)
            }
        ), 500
    

if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage doctors ...")
    app.run(host='0.0.0.0', port=5001, debug=True)
