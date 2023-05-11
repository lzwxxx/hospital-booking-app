from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

import requests
from invokes import invoke_http

from datetime import datetime

import amqp_setup
import pika
import json

from os import environ

app = Flask(__name__)
CORS(app)

appointment_URL = environ.get('appointment_service_URL')+"/appointment" 
appointment_validation_URL = environ.get('appointment_service_URL')+"/check_conflict" 
doctor_URL = environ.get('doctor_service_URL')+"/doctor"
patient_URL = environ.get('patient_service_URL')+"/patient"

class ServiceInvocationError(Exception):
    """Exception raised for errors encountered during invocation of other microservices.

    Attributes:
        response -- JSON response to be bubbled up to route handler
        message -- explanation of the error
    """

    def __init__(self, response):
        self.response = response
        self.message = response['message']
        super().__init__(self.message)

# Get appointments with doctor names joined by patient_id
@app.route("/appointments", methods=['GET'])
def aggregate_appointments():
    patient_id = request.args.get('patient_id')
    try:
        if patient_id == None:
            return {
            "code": 400,
            "message": "Missing patient_id"
            },400
        else:
            appointments = invoke_microservice(appointment_URL,"GET","appointment.error","Appointment","Fail to retrieve appointments by patient",True,params={'patient_id':patient_id})
            
            if appointments['code'] == 404:
                return jsonify(
                {
                    "code": 404,
                    "message": "No appointments found"
                }
                ),404
            
            doctors = invoke_microservice(doctor_URL,"GET","doctor.error","Doctor","Fail to retrieve Doctors")

            doctor_dict = {}
            for doc in doctors['data']['doctors']:
                doctor_dict[doc['doctor_id']] = doc['doctor_name']

            for appt in appointments['data']['appointments']:
                appt['doctor_name'] = doctor_dict[appt['doctor_id']]

            return jsonify(
            {
                "code": 200,
                "data": {
                    "appointments": appointments['data']['appointments']
                }
            }
        )

    except ServiceInvocationError as se:
        return se.response,500
    except Exception as e:
        # Unexpected error in code
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
        print(ex_str)

        error_response = {
            "code": 500,
            "message": "appointment_booking.py internal error: " + ex_str
        }

        # Inform error microservice
        publish_error(error_response,"book_appointment.error","Book Appointment Internal Error")

        return jsonify(error_response), 500

# Patient Books new Appointment
@app.route("/book_appointment", methods=['POST'])
def book_appointment():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        expected_fields = ['name','nric','sex','email','date','time','doctor_id']
        if not check_input(request.get_json(),expected_fields):
            return jsonify({
                "code": 400,
                "message": "Invalid input fields: [" + ' '.join(list(request.get_json().keys())) + "] , expecting "+' '.join(expected_fields)
            }), 400
        try:
            appointment = request.get_json()
            print("\nReceived an appointment in JSON:", appointment)

            # Send appointment info
            result = processAppointment(appointment, 'add')
            print('\n------------------------')
            print('\nresult: ', result)
            return jsonify(result), result["code"]
        except ServiceInvocationError as se:
            return se.response,500
        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            error_response = {
                "code": 500,
                "message": "appointment_booking.py internal error: " + ex_str
            }

            # Inform error microservice
            publish_error(error_response,"book_appointment.error","Book Appointment Internal Error")

            return jsonify(error_response), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


# Patient Modifies Existing Appointment
@app.route("/edit_appointment", methods=['POST'])
def edit_appointment():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        expected_fields = ['date','time','doctor_id','appointment_id']
        if not check_input(request.get_json(),expected_fields):
            return jsonify({
                "code": 400,
                "message": "Invalid input fields: [" + ' '.join(list(request.get_json().keys())) + "] , expecting "+' '.join(expected_fields)
            }), 400
        try:
            appointment = request.get_json()
            print("\nReceived an appointment in JSON:", appointment)
            
            # Send appointment info
            result = processAppointment(appointment, 'edit')
            print('\n------------------------')
            print('\nresult: ', result)
            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            error_response = {
                "code": 500,
                "message": "appointment_booking.py internal error: " + ex_str
            }

            # Inform error microservice
            publish_error(error_response,"book_appointment.error","Edit Appointment Internal Error")

            return jsonify(error_response), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def check_input(json,fields):
    return set(fields) == set(json.keys())

def processAppointment(appointment, action):
    # 1. Retrieval and Validation
    # Add
    if action == 'add':
        # Getsert patient
        print('\n\n-----Invoking Patient microservice-----')    
        patient_input = {
            "patient_name":appointment['name'],
            "patient_nric":appointment['nric'],
            "patient_sex":appointment['sex'],
            "patient_email":appointment['email']
        }
        patient_result = processPatient(patient_input,action)
        # Get Doctor
        print('\n\n-----Invoking Doctor microservice-----')
        doctor_input = {
            "doctor_id":appointment['doctor_id']
        }   
        doctor_result = processDoctor(doctor_input)
    # Edit
    elif action == 'edit':
        # Get Doctor
        print('\n\n-----Invoking Doctor microservice-----')
        doctor_input = {
            "doctor_id":appointment['doctor_id']
        }   
        doctor_result = processDoctor(doctor_input)

        # Get existing appointment by id
        print('\n\n-----Invoking Appointment microservice-----')
        existing_appointment_result = retrieveAppointment(appointment['appointment_id'])
        # Retrieve patient
        print('\n\n-----Invoking Patient microservice-----')    
        patient_result = retrievePatient(existing_appointment_result['data']['patient_id'])

    patient_id = patient_result['data']['patient_id'] if action == 'add' else existing_appointment_result['data']['patient_id']

    print('\n\n-----Validating Appointment Input-----')  
    appointment_input = {
        "patient_id":patient_id,
        "doctor_id":appointment['doctor_id'],
        "date":appointment['date'],
        "time":appointment['time'],
    }
    
    # Pass appointment id for edit action
    if action == 'edit' : 
        appointment_input['appointment_id'] = appointment['appointment_id'] 

    is_appointment_valid,reasons = validateAppointment(appointment_input,doctor_result['data'],action)

    if not is_appointment_valid:
        # Not valid appointment
        return {
            "code": 400,
            "message": "Appointment timing not available ("+','.join(reasons)+")",
            "data": {
                "reasons":reasons
            }
        }

    # 2.Create appointment record
    # Invoke the appointment microservic
    print(f'\n-----Invoking appointment microservice ({action} appointment) -----')
    if(action == 'add'):
        appointment_input = {
            "patient_id":patient_result['data']['patient_id'],
            "doctor_id":appointment['doctor_id'],
            "date":appointment['date'],
            "time":appointment['time'],
        }
        appointment_result = invoke_microservice(appointment_URL,'POST',
                                            "appointment.error","Appointment","Appointment creation failure sent for error handling.",
                                            json=appointment_input)
    elif(action == 'edit'):
        appointment_input = {
            "doctor_id":appointment['doctor_id'],
            "date":appointment['date'],
            "time":appointment['time'],
        }
        appointment_result = invoke_microservice(appointment_URL+f"/{appointment['appointment_id']}",'POST',
                                            "appointment.error","Appointment","Appointment editing failure sent for error handling.",
                                            json=appointment_input)

    
    #Invoke Email Microservice
    client_url_edit_appt = os.environ.get('client_URL_edit_appt')
    client_url_past_appt = os.environ.get('client_URL_past_appt')

    apptLink = client_url_edit_appt+f"/{appointment_result['data']['appointment_id']}"
    profileLink = client_url_past_appt+f"/{patient_result['data']['patient_guid']}"
    appointmentType = 'new' if action == 'add' else 'edit'

    payload = {
            "patient_name":patient_result['data']['patient_name'],
			"doctor_name":doctor_result['data']['doctor_name'],
			"time":appointment_result['data']['time'],
			"appointment_link":apptLink,
            "profile_link":profileLink,
			"appointment_type":appointmentType,
			"patient_email":patient_result['data']['patient_email']
    }

    publish_email(content=payload,routing_key='appointment.email',message_name=f'{action.capitalize()} Appointment')
    
    if action == 'add':
        resp = {
        "code": 201,
        "data": {
            "appointment_result": appointment_result,
            "patient_result": patient_result,
            "doctor_result": doctor_result
            }
        }
    else:
        resp = {
        "code": 201,
        "data": {
            "old_appointment": existing_appointment_result,
            "new_appointment": appointment_result,
            "doctor_result": doctor_result
            }
        }
    # Return created appointment
    return resp

def validateAppointment(appointment,doctor,action):
    # Validate if
    # - hours between doctor's availability
    # - date not during weekend
    # - not conflicting with any of doctor's appointment 
    # - not conflicting with any of patient's appointment 

    withinDoctorAvail = int(appointment['time']) >= doctor['start_time'] and int(appointment['time']) < doctor['end_time']
    
    date_inp = datetime.strptime(appointment['date'], '%Y-%m-%d').date()
    isWeekend = date_inp.weekday() > 4 # Check if date is a weekend

    # Invoking Appointment service
    print('\n-----Invoking appointment microservice (Check Appointment Conflict) -----')

    #check if conflict exists
    conflict_input = {
                    "doctor_id":appointment['doctor_id'],
                    "patient_id":appointment['patient_id'],
                    "time":appointment['time'],
                    "date":appointment['date'],
                    }

    if action == 'edit':
        conflict_input['appointment_id'] = appointment['appointment_id']

    conflict_res = invoke_microservice(appointment_validation_URL,'POST',"appointment.error", "Appointment", "Failed to check Appointment conflict", 
                                        json=conflict_input)

    conflictDoctor = conflict_res['data']['conflict_with_doctor_appt']
    conflictPatient = conflict_res['data']['conflict_with_patient_appt']
    
    # Compile errors
    errors = []
    if withinDoctorAvail is False:
        errors.append("Appointment time is outside of doctor's available hours")
    if isWeekend is True:
        errors.append("Requested time is on an off day (weekends)")
    if conflictDoctor is True:
        errors.append("Requested time is in conflict with another existing appointment")
    if conflictPatient is True:
        errors.append("You have an existing appointment in conflict with requested time")
    
    return withinDoctorAvail and (not isWeekend) and (not conflictDoctor) and (not conflictPatient),errors

#check if patient exists in db, add to db if doesnt
def processPatient(patient,action):
    if action == 'add':
        #Getsert patient
        patient_result = invoke_microservice(patient_URL,'POST',"patient.error", "Patient", "Fail to register Patient", acceptNone=False, json=patient)
    elif action == 'edit':
        id = patient['patient_id']
        patient_result = invoke_microservice(patient_URL+f'/{id}','GET',"patient.error", "Patient", "Fail to retrieve Patient", acceptNone=False )
    return patient_result

# Check if doctor exists in db
def processDoctor(appointment):
    # Invoke the Doctor microservice
    id = appointment['doctor_id']
    doctor_results = invoke_microservice(doctor_URL+f'/{id}','GET',"doctor.error", "Doctor", "Failed to retrieve Doctor", acceptNone=False )
    return doctor_results

# Retrieve existing appointment
def retrieveAppointment(id):
    # Invoke the Appointment microservice
    appt_results = invoke_microservice(appointment_URL+f'/{id}','GET',"appointment.error", "ExistingAppointment", "Failed to retrieve Appointment", acceptNone=False )
    return appt_results

# Retrieve existing patient
def retrievePatient(id):
    # Invoke the Appointment microservice
    patient_results = invoke_microservice(patient_URL+f'/{id}','GET',"appointment.error", "ExistingPatient", "Failed to retrieve Patient", acceptNone=False )
    return patient_results

#Invoke microservices and handle any error received
def invoke_microservice(service_url,method,error_routing_key, entity, error_message, acceptNone=False, **kwargs):
    result = invoke_http(service_url,method,**kwargs)
    print(f"{entity.lower()}_results:", result, '\n')

    # Check the result; if a failure, send it to the error microservice.
    code = result["code"]
    code_range = list(range(200, 300))+[404] if acceptNone else list(range(200, 300))
    if code not in code_range:
        # Inform the error microservice
        publish_error(result,error_routing_key,entity)
        # Return error
        raise ServiceInvocationError({
            "code": 500,
            "data": {
                f"{entity.lower()}_result": result
            },
            "message": error_message
        }) 
    return result

def publish_email(content,routing_key,message_name):
    print(f'-----Publishing the ({message_name} email) message with routing_key={routing_key}-----')
    message = json.dumps(content)
    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key=routing_key, 
        body=message, properties=pika.BasicProperties(delivery_mode = 2))

    print("Email published to the RabbitMQ Exchange:"+message)

# publish error to message broker
def publish_error(results,routing_key,message_name):
    print(f'-----Publishing the ({message_name} error) message with routing_key={routing_key}-----')
    message = json.dumps(results)
    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key=routing_key, 
        body=message, properties=pika.BasicProperties(delivery_mode = 2))

    print("{} Status ({:d}) published to the RabbitMQ Exchange:".format(
        message_name, results['code']), results)

# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for making an appointment...")
    app.run(host="0.0.0.0", port=5001, debug=True)
    # Notes for the parameters: 
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program, and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.
