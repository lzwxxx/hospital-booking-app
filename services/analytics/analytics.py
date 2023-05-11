from this import d
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ

from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('analytics_dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

dbURL = environ.get('analytics_dbURL')

db = SQLAlchemy(app)
CORS(app)
    
# Table 1
class Weekly_average_patient(db.Model):
    __tablename__ = 'weekly_average_patient'
    
    hour = db.Column(db.Integer, primary_key=True, nullable=False)
    average_num_patients = db.Column(db.Integer, nullable=False)
    
    def __init__(self, hour, average_num_patients):
        self.hour = hour
        self.average_num_patients = average_num_patients

    def json(self):
        return {"hour": self.hour, "average_num_patients": self.average_num_patients}
    

# Table 2
class Weekly_average_patient_snapshots(db.Model):
    __tablename__ = 'weekly_average_patient_snapshots'
    
    hour = db.Column(db.Integer, primary_key=True, nullable=False)
    average_num_patients = db.Column(db.Integer, nullable=False)
    snapshot_timestamp = db.Column(db.DateTime, primary_key=True, nullable=False)
    
    def __init__(self, hour, average_num_patients, snapshot_timestamp):
        self.hour = hour
        self.average_num_patients = average_num_patients
        self.snapshot_timestamp = snapshot_timestamp

    def json(self):
        return {"hour": self.hour, "average_num_patients": self.average_num_patients, "snapshot_timestamp": self.snapshot_timestamp}

   
# WEEKLY_AVERAGE_PATIENT TABLE ----------------------------------

# 1. Update average number of patients consulted
@app.route("/weekly_average_patient", methods=['POST'])
def update_avg_num_patients_consulted():
    try:
        data = request.json.get('average_patients')

        for row in data:
            hour = row['hour']
            
            avg_num_patients_consulted = Weekly_average_patient.query.filter_by(hour=hour).first()
        
            if not avg_num_patients_consulted:
                return jsonify(
                    {
                        "code": 404,
                        "data": {
                            "hour": hour
                        },
                        "message": "hour not found."
                    }
                ), 404
            
            if row['average_num_patients']:
                avg_num_patients_consulted.average_num_patients = row['average_num_patients']
            
                db.session.commit()
            
        return jsonify(
            {
                "code": 200,
                "message": "Update is successful!"
            }
        ), 200
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "hour": hour
                },
                "message": "analytics.py internal error: " + str(e)
            }
        ), 500
    
# 2. Get average number of patients for ALL hours
@app.route("/weekly_average_patient/all",  methods=['GET'])
def get_all():
    try:
        avg_patients_list = Weekly_average_patient.query.all()
        if len(avg_patients_list):
            return jsonify(
                {
                    "code": 200,
                    "data": {
                        "average_patients": [avg_patients.json() for avg_patients in avg_patients_list]
                    }
                }
            )
        return jsonify(
            {
                "code": 404,
                "message": "There are no patients."
            }
        ), 404
            
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "analytics.py internal error: " + str(e)
            }
        ), 500

# 3. Get average number of patients for EACH hours
@app.route("/weekly_average_patient/hour/<int:hour>", methods=['GET'])
def find_by_hour_2(hour):
    try: 
        weekly_average_patient = Weekly_average_patient.query.filter_by(hour=hour).all()
        
        if len(weekly_average_patient):
            return jsonify(
                {
                    "code": 200,
                    "data": {
                        "weekly_average_patient": [average.json() for average in weekly_average_patient]
                    }
                }
            )
        return jsonify(
            {
                "code": 404,
                "message": "Hour does not exist."
            }
        ), 404
        
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "analytics.py internal error:" + str(e)
            }
        ), 500

# weekly_average_patient_snapshots TABLE ----------------------------------
# 4. insert snapshots into weekly_average_patient_snapshots table
@app.route("/snapshot_weekly_average_patient", methods=['POST'])
def post_weekly_avg_patient_snapshot():
    try: 
        try:
            data = request.json.get('snapshot')

            for row in data:
                hour = row['hour']
                average_num_patients = row['average_num_patients']
                snapshot_timestamp = row['snapshot_timestamp']
                
                weekly_snapshots = Weekly_average_patient_snapshots(hour=hour, average_num_patients=average_num_patients, snapshot_timestamp=snapshot_timestamp)

                db.session.add(weekly_snapshots)
                db.session.commit()
        except Exception as e:
            print(e)
            return jsonify(
                {
                    "code": 500,
                    "message": "An error occurred while inserting the data. " + str(e)
                }
            ), 500

        return jsonify(
            {
                "code": 201,
                "data": weekly_snapshots.json()
            }
        ), 201
        
    except Exception as e:
            print(e)
            return jsonify(
                {
                    "code": 500,
                    "message": "analytics.py internal error " + str(e)
                }
            ), 500

# 5. get all snapshots in weekly_average_patient_snapshots table
@app.route("/snapshot_weekly_average_patient/all",  methods=['GET'])
def get_all_snapshots():
    try: 
        weekly_average_patient_snapshots = Weekly_average_patient_snapshots.query.all()
        if len(weekly_average_patient_snapshots):
            return jsonify(
                {
                    "code": 200,
                    "data": {
                        "average_patients": [weekly_snapshots.json() for weekly_snapshots in weekly_average_patient_snapshots]
                    }
                }
            )
        return jsonify(
            {
                "code": 404,
                "message": "There are no snapshots."
            }
        ), 404
        
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "appointment.py internal error: " + str(e)
            }
        ), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)