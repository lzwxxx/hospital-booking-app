import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *

def format_email():
    patient_name = "Patient Name"
    doctor_name = "Doctor Name"
    time = "time"
    appointment_link = "www.google.com"
    profile_link = "https://www.smu.edu.sg/"
    
    header = "<h4>Hello " + patient_name + "!</h4>"
    body = (f'<p>Here are your appointment details:</p><p>Doctor Name: <strong> {doctor_name} </strong></p>' + 
            f'<p>Time: <strong> {time} </strong></p>')
    end = (f'<p>Click <a href="{appointment_link}">here</a> to view or edit your appointment</p>' +
            f'<p>View past appointments <a href="{profile_link}">here</a></p>')       
    
    return header + body + end

message = Mail(
        from_email= From('wjng.2018@business.smu.edu.sg', 'SMU Hospital'),
        to_emails= input("Input email: "),
        subject= 'Sendgrid Test',
        html_content= format_email())

# sending email and printing status
try:
    SENDGRID_API_KEY = os.environ.get(
        "SENDGRID_API_KEY") or "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"
    sendgrid_client = SendGridAPIClient(SENDGRID_API_KEY)
    response = sendgrid_client.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)

except Exception as e:
    print(e.message)