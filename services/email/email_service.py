#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import amqp_setup
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *
from flask import Flask, request
import json

app = Flask(__name__)

monitorBindingKey = '*.email'
SENDGRID_API_KEY = os.environ.get(
    "SENDGRID_API_KEY") or "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"

def receiveNotification():
    amqp_setup.check_setup()

    queue_name = 'Email'

    # set up a consumer and start to wait for coming messages
    amqp_setup.channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)
    # an implicit loop waiting to receive messages;
    amqp_setup.channel.start_consuming()
    # it doesn't exit by default. Use Ctrl+C in the command window to terminate it.

# required signature for the callback; no return
def callback(channel, method, properties, body):
    print("\nReceived an email request by " + __file__)
    try:
        print(body)
        mail(json.loads(body))
    except Exception as e:
        processError(body,e)

def processError(errorMsg,e):
    print("Printing the error message:")
    print(e)
    try:
        error = json.loads(errorMsg)
        print("--JSON:", error)
    except Exception as e:
        print("--NOT JSON:", e)
        print("--DATA:", errorMsg)
    print()

def format_time(time):
    time = int(time)
    if(time == 0):
        return "12 am"
    elif(time < 12):
        return str(time)+" am"
    elif(time == 12):
        return "12 pm"
    else:
        return str(time-12)+" pm"
    
def format_email(data):
    # Retrieve data from json payload
    patient_name = str(data["patient_name"])
    doctor_name = str(data["doctor_name"])
    time = str(format_time(data["time"]))
    appointment_link = str(data["appointment_link"])
    profile_link = str(data["profile_link"])

    # Email content
    header = "<h4>Hello " + patient_name + "!</h4>"
    body = (f'<p>Here are your appointment details:</p><p>Doctor Name: <strong> {doctor_name} </strong></p>' + 
            f'<p>Time: <strong> {time} </strong></p>')
    end = (f'<p>Click <a href="{appointment_link}">here</a> to view or edit your appointment</p>' +
            f'<p>View past appointments <a href="{profile_link}">here</a></p>')    

    return header + body + end

def mail(json_msg):
    # email address, subject and body
    email_content = format_email(json_msg)
    appointment_type = str(json_msg["appointment_type"]) # either new appointment or edited appointment
    patient_email = str(json_msg["patient_email"])
    
    if appointment_type == "new":
        subject = "New Appointment Confirmed"
    elif appointment_type == "edit":
        subject = "Appointment Change Confirmed"

    message = Mail(
        from_email= From('wjng.2018@business.smu.edu.sg', 'SMU Hospital'),
        to_emails= patient_email,
        subject= subject,
        html_content=email_content)

    # sending email and printing status
    try:
        print(SENDGRID_API_KEY)
        sendgrid_client = SendGridAPIClient(SENDGRID_API_KEY)
        response = sendgrid_client.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)

    except Exception as e:
        print(e)

if __name__ == "__main__":
    print("\nThis is " + os.path.basename(__file__), end='')
    print(": monitoring routing key '{}' in exchange '{}' ...".format(
        monitorBindingKey, amqp_setup.exchangename))
    receiveNotification()

