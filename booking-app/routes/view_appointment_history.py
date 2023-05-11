from crypt import methods
from flask import Flask, request, render_template, abort
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
import jwt
from invokes import invoke_http
from os import environ

# Import app instance from main file
from __main__ import app

# Singpass configs
sp_api_params_server = {
    "authLevel": environ.get('SINGPASS_AUTHLEVEL'),
    "authApiUrl": environ.get('SINGPASS_AUTH_API_URL'),
    "tokenApiUrl": environ.get('SINGPASS_TOKEN_API_URL'),
    "personApiUrl": environ.get('SINGPASS_PERSON_API_URL'),
    "redirectUrl": environ.get('SINGPASS_REDIRECT_API_URL'),
    "clientId" : environ.get('SINGPASS_CLIENTID'),
    "clientSecret" : environ.get('SINGPASS_CLIENTSECRET'),
    "attributes" : 'uinfin', # Only request nric for auth
    "publicCert" : environ.get('SINGPASS_MYINFO_PUBLIC_CERT')
}

sp_api_params_client = {
    "authLevel": environ.get('SINGPASS_AUTHLEVEL'),
    "authApiUrl": environ.get('SINGPASS_AUTH_API_URL'),
    "redirectUrl": environ.get('SINGPASS_REDIRECT_API_URL'),
    "clientId" : environ.get('SINGPASS_CLIENTID'),
    "attributes" : 'uinfin', # Only request nric for auth
}

# Microservice endpoints
get_patient_api = environ.get('patient_service_URL')+'/patient'
get_appointment_api = environ.get('appointment_booking_service_URL')+'/appointments'

class MyInfoError(Exception):
    """Exception raised for errors encountered during invocation of MyInfo API.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self):
        super().__init__("My Info Error")

@app.route('/viewAppointmentHistory/<string:guid>')
def view_appointment_history(guid):
    if guid is None:
        abort(404)
    code = request.args.get('code')
    state = "page_history__guid_"+guid

    # Request singpass retrieval
    if code is None:
        try:
            return render_template('profile_auth.html',api=sp_api_params_client,state=state)
        except Exception as e:
            return render_template('profile_auth.html',api=sp_api_params_client,error=e,state=state)
    else:
        try:
            nric_inp = retrieve_myinfo(code)
            patient = invoke_http(url=get_patient_api,params={"patient_guid":guid})
            patient_nric = patient['data']['patient_nric']
            # print(nric_inp,patient_nric,nric_inp==patient_nric)
            if patient_nric != nric_inp:
                abort(403) #return forbidden page
            else:
                appointments = retrieve_appointments(patient)
                return render_template('view_appointment_history.html',appointments=appointments)
        except MyInfoError as me:
            return render_template('profile_auth.html',api=sp_api_params_client,error="Access Token Expired!",state=state)
        except Exception as e:
            return render_template('profile_auth.html',api=sp_api_params_client,error=e,state=state)

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


# Retrieve appointment by patient id
def retrieve_appointments(patient):
    try:
        patient_id = patient['data']['patient_id']
        appointments = invoke_http(url=get_appointment_api,params={"patient_id":patient_id})

        for appt in appointments['data']['appointments']:
            appt['time'] = format_time(appt['time'])
            
        return appointments['data']['appointments']
    except Exception as e:
        raise e

# START OF SINGPASS FUNCTIONS

# retrieve from myinfo apis, after obtaining Auth code from Consent platform callback
def retrieve_myinfo(code):
    #auth headers
    # app.logger.info(sp_api_params_server)
    if sp_api_params_server['authLevel'] == "L0":
        pass
    try:
        # call token api
        token_params = {
                "code":code,
                "grant_type":'authorization_code',
                "client_secret":sp_api_params_server['clientSecret'],
                "client_id":sp_api_params_server['clientId'],
                "redirect_uri":sp_api_params_server['redirectUrl'],
                "state":123
            }
        # app.logger.info(token_params)
        
        token_res = invoke_http(
            url=sp_api_params_server['tokenApiUrl'],
            method='POST',
            data=token_params,
            headers={"Content-Type":"application/x-www-form-urlencoded","Cache-Control":"no-cache"}
        )
        # app.logger.info(token_res)

        access_token = token_res['access_token']
        sub = decodeToken(access_token)

        #call person api
        person_res = callPersonAPI(sub,access_token)

        return person_res["uinfin"]['value']

    except Exception as e:
        raise MyInfoError()

# Decode JWT token obtained from TokenAPI
def decodeToken(token_string):
    with open(sp_api_params_server["publicCert"], "rb") as f:
        cert = f.read()
        cert_obj = load_pem_x509_certificate(cert,default_backend())

        public_key = cert_obj.public_key()

        decoded = jwt.decode(token_string, key=public_key, algorithms=['RS256'], options  = {"verify_nbf":False,"verify_aud":False})
        
        # app.logger.info("token sub",decoded['sub'])
        
        return decoded['sub']

# Retrieve data from PersonAPI
def callPersonAPI(sub,validToken):
    person_params = {
        "client_id":sp_api_params_server['clientId'],
        "attributes":sp_api_params_server['attributes'],
    }

    person_api_endpoint = sp_api_params_server['personApiUrl']+"/"+sub+"/"
    person_api_headers = {"Cache-Control":"no-cache","Authorization": f"Bearer {validToken}"}
    
    person_res = invoke_http(
        url=person_api_endpoint,
        method='GET',
        params=person_params,
        headers=person_api_headers
    )
    # app.logger.info(person_api_endpoint)
    # app.logger.info(person_params)
    # app.logger.info(person_api_headers)

    # app.logger.info(person_res)
    return person_res

# END OF SINGPASS CODE