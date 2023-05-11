#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ

import uuid

# from datetime import datetime
import json

app = Flask(__name__)

# RMB TO CHANGE CONFIG BASED ON DB
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('patient_dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

CORS(app)  

class Patient(db.Model):
    __tablename__ = 'patient'

    patient_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_nric = db.Column(db.String(9), nullable=False)
    patient_name = db.Column(db.String(), nullable=False)
    patient_sex = db.Column(db.String(), nullable=False)
    patient_email = db.Column(db.String(), nullable=False)
    patient_guid = db.Column(db.String(), nullable=False)

    def __init__(self, patient_id, patient_nric, patient_name, patient_sex, patient_email, patient_guid):
        self.patient_id = patient_id
        self.patient_nric = patient_nric 
        self.patient_name = patient_name
        self.patient_sex = patient_sex
        self.patient_email = patient_email
        self.patient_guid = patient_guid

    def json(self):
        return {"patient_id": self.patient_id, "patient_nric": self.patient_nric, "patient_name": self.patient_name, "patient_sex": self.patient_sex, "patient_email":self.patient_email, "patient_guid":self.patient_guid}
        #dto = {
            #'patient_id': self.patient_id,
            #'patient_nric': self.patient_nric,
            #'patient_name': self.patient_name,
            #'patient_email': self.patient_email,
        #}

        #dto['patient'] = []
        #for oi in self.patient:
            #dto['patient'].append(oi.json())

        #return dto
       

#Register new patients
#@app.route("/patient", methods=['POST'])
#def add_patient():

    #patient_id = request.json.get('patient_id', None)
    #patient_nric = request.json.get('patient_nric', None)
    #patient_name = request.json.get('patient_name', None)
    #patient_sex = request.json.get('patient_sex', None)
    #patient_email = request.json.get('patient_email', None)
    #patient = Patient(patient_id=patient_id, patient_nric=patient_nric, patient_name=patient_name, patient_sex=patient_sex,
    #patient_email=patient_email)
    #try:
        #db.session.add(patient)
        #db.session.commit()
    #except Exception as e:
        #return jsonify(
            #{
                #"code": 500,
                #"message": "An error occurred while creating the patient. " + str(e)
            #}
        #), 500
    
    #print(json.dumps(patient.json(), default=str)) # convert a JSON object to a string and print
    #print()

    #return jsonify(
        #{
            #"code": 201,
            #"data": patient.json()
        #}
    #), 201

#Get the information of a patient by patient_id 
@app.route("/patient/<int:patient_id>", methods=['GET'])
def find_by_patient_id(patient_id):
    try:
        #Check if the patient_id already exists in the patient table 
        patient = Patient.query.filter_by(patient_id=patient_id).first()
        if patient:
            #The patient_id exist
            return jsonify(
                {
                    #Return patient's information in JSON with HTTP status code 200 - Ok
                    "code": 200,
                    "data": patient.json()
                }
            )

        #The patient_id does not exist 
        return jsonify(
            {   
                #return patient_id and error message in JSON with HTTP status code 404 - Not Found 
                "code": 404,
                "data": {
                    "patient_id": patient_id
                },
                "message": "Patient not found."
            }
        ), 404

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "patient.py internal error: " + str(e)
            }
        ), 500

#Get patient's information using guid
@app.route("/patient", methods=['GET'])
def find_by_patient_guid():

    try:
        #Get the value of the patient_guid key. If patient_guid key doesn't exist, returns None
        patient_guid = format(request.args.get('patient_guid'))

        #Check if the patient_guid already exists in the patient table 
        patient = Patient.query.filter_by(patient_guid=patient_guid).first()
        if patient:
            #The patient_guid exist
            return jsonify(
                {
                    #Return patient's information in JSON with HTTP status code 200 - Ok
                    "code": 200,
                    "data": patient.json()
                }
            )
        #The patient_guid does not exist 
        return jsonify(
            {
                #return patient_guid and error message in JSON with HTTP status code 404 - Not Found 
                "code": 404,
                "data": {
                    "patient_guid": patient_guid
                },
                "message": "Patient with this guid not found."
            }
        ), 404

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "patient.py internal error: " + str(e)
            }
        ), 500

#Getsert patient 
@app.route("/patient", methods=['POST'])
def getsert():

    try:

        #Get the patient_nric from the request received 
        patient_nric = request.json.get('patient_nric', None)

        #Check if the patient_nric already exists in the patient table 
        patient = Patient.query.filter_by(patient_nric=patient_nric).first()
        if patient:
            #The patient_nric exist

            patient_email_input = request.json.get('patient_email', None)

            # Update patient if email supplied is different
            if patient.patient_email != patient_email_input:
                try:
                    patient.patient_email = patient_email_input
                    db.session.commit()
                    return jsonify (
                        {
                            "code": 200,
                            "data": patient.json(),
                            "message": "Returning updated patient."
                        }
                        
                    ), 200
                except Exception as e:
                    #Return patient_nric and an error message in JSON with HTTP status code 500 - Internal Server error if an exception occurs.
                    return jsonify(
                        {
                            "code": 500,
                            "data": {
                                "patient_nric": patient_nric
                            },
                            "message" : "An error occurred while updating the patient"
                        }
                    ), 500
            
            # Returning existing patient
            else:
                return jsonify (
                    {
                        "code": 200,
                        "data": patient.json(),
                        "message": "Returning existing patient."
                    }
                    
                ), 200

        #The patient_nric does not exist
        else:
            #Request does not contain patient_id as it is auto increment so patient_id is set to 'None'
            patient_id = None 

            #Get all the data from the request received 
            data = request.get_json()

            data["patient_guid"] = generate_guid()

            #Create an instance of a patient using patient_id and the attributes sent in the request 
            patient = Patient(patient_id, **data)

            try:
                #Add the record of the new patient to the patient table
                db.session.add(patient)
                #Commit the changes 
                db.session.commit()
            except Exception as e:
                #Return patient_nric and an error message in JSON with HTTP status code 500 - Internal Server error if an exception occurs.
                return jsonify(
                    {
                        "code": 500,
                        "data": {
                            "patient_nric": patient_nric
                        },
                        "message" : "An error occurred while creating the patient"
                    }
                ), 500
            
            #If there is no exception, return the JSON representation of the patient added with HTTP status code 201 - created.
            return jsonify(
                {
                    "code": 201,
                    "data": patient.json()
                }
            ), 201
    
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "patient.py internal error: " + str(e)
            }
        ), 500


def generate_guid():
    myguid = uuid.uuid4()
    return str(myguid)


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage patients ...")
    app.run(host='0.0.0.0', port=5001, debug=True)
